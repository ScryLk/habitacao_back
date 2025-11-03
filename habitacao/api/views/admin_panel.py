"""
Views para painel administrativo avançado
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Count, Q, Max
from django.utils import timezone
from datetime import timedelta

from habitacao.models_audit import (
    AuditLog, UserSession, PermissionChange, SystemNotification
)
from habitacao.models import Beneficiary, UserProfile
from habitacao.api.serializers.audit import (
    AuditLogSerializer,
    AuditLogSummarySerializer,
    UserSessionSerializer,
    PermissionChangeSerializer,
    SystemNotificationSerializer,
    AdminDashboardStatsSerializer,
    UserActivitySerializer,
    SecurityAlertSerializer,
)
from habitacao.api.permissions.roles import IsAdmin
from habitacao.choices import ApplicationStatus


class AdminPanelViewSet(viewsets.ViewSet):
    """
    ViewSet para funcionalidades administrativas avançadas
    Apenas acessível por administradores
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """
        GET /api/v1/admin/dashboard-stats/
        Retorna estatísticas completas para o dashboard administrativo
        """
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        # Estatísticas de usuários
        total_users = User.objects.count()
        active_users = UserProfile.objects.filter(is_active=True).count()

        # Estatísticas de beneficiários
        total_beneficiaries = Beneficiary.objects.count()
        pending_applications = Beneficiary.objects.filter(
            status=ApplicationStatus.SUBMITTED
        ).count()
        approved_applications = Beneficiary.objects.filter(
            status=ApplicationStatus.APPROVED
        ).count()
        rejected_applications = Beneficiary.objects.filter(
            status=ApplicationStatus.REJECTED
        ).count()

        # Estatísticas de auditoria
        total_audit_logs = AuditLog.objects.count()
        logs_last_24h = AuditLog.objects.filter(timestamp__gte=last_24h).count()
        failed_actions_last_24h = AuditLog.objects.filter(
            timestamp__gte=last_24h,
            was_successful=False
        ).count()

        # Sessões ativas
        active_sessions = UserSession.objects.filter(
            is_active=True,
            last_activity__gte=now - timedelta(minutes=30)
        ).count()
        unique_users_online = UserSession.objects.filter(
            is_active=True,
            last_activity__gte=now - timedelta(minutes=30)
        ).values('user').distinct().count()

        # Notificações
        unread_notifications = SystemNotification.objects.filter(
            is_read=False
        ).count()
        critical_notifications = SystemNotification.objects.filter(
            is_read=False,
            severity='CRITICAL'
        ).count()

        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'total_beneficiaries': total_beneficiaries,
            'pending_applications': pending_applications,
            'approved_applications': approved_applications,
            'rejected_applications': rejected_applications,
            'total_audit_logs': total_audit_logs,
            'logs_last_24h': logs_last_24h,
            'failed_actions_last_24h': failed_actions_last_24h,
            'active_sessions': active_sessions,
            'unique_users_online': unique_users_online,
            'unread_notifications': unread_notifications,
            'critical_notifications': critical_notifications,
        }

        serializer = AdminDashboardStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def audit_logs(self, request):
        """
        GET /api/v1/admin/audit-logs/
        Lista logs de auditoria com filtros
        Query params:
        - user: ID do usuário
        - action_type: Tipo de ação
        - date_from: Data inicial
        - date_to: Data final
        - success: true/false
        """
        queryset = AuditLog.objects.all()

        # Filtros
        user_id = request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        action_type = request.query_params.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)

        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)

        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)

        success_param = request.query_params.get('success')
        if success_param is not None:
            was_successful = success_param.lower() == 'true'
            queryset = queryset.filter(was_successful=was_successful)

        # Paginação
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start = (page - 1) * page_size
        end = start + page_size

        total = queryset.count()
        logs = queryset[start:end]

        serializer = AuditLogSerializer(logs, many=True)

        return Response({
            'data': serializer.data,
            'meta': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size,
            }
        })

    @action(detail=False, methods=['get'])
    def active_sessions(self, request):
        """
        GET /api/v1/admin/active-sessions/
        Lista sessões ativas no sistema
        """
        sessions = UserSession.objects.filter(
            is_active=True
        ).select_related('user').order_by('-last_activity')

        serializer = UserSessionSerializer(
            sessions,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def terminate_session(self, request, pk=None):
        """
        POST /api/v1/admin/terminate-session/{session_id}/
        Força o término de uma sessão específica
        """
        try:
            session = UserSession.objects.get(pk=pk, is_active=True)
            session.terminate(reason='FORCED')

            # Registra ação de auditoria
            AuditLog.log_action(
                user=request.user,
                action_type='CHANGE_PERMISSIONS',
                description=f"Forçou término da sessão de {session.user.email}",
                content_object=session,
                request=request
            )

            return Response({
                'message': f'Sessão de {session.user.email} terminada com sucesso'
            })
        except UserSession.DoesNotExist:
            return Response(
                {'error': 'Sessão não encontrada ou já inativa'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def user_activity(self, request):
        """
        GET /api/v1/admin/user-activity/
        Retorna atividade de todos os usuários
        """
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)

        users = User.objects.filter(
            profile__isnull=False
        ).select_related('profile').annotate(
            last_session=Max('sessions__last_activity')
        )

        activity_data = []
        for user in users:
            # Conta ações do usuário
            actions_today = AuditLog.objects.filter(
                user=user,
                timestamp__gte=today_start
            ).count()

            actions_week = AuditLog.objects.filter(
                user=user,
                timestamp__gte=week_start
            ).count()

            # Sessões ativas
            active_sessions_count = UserSession.objects.filter(
                user=user,
                is_active=True
            ).count()

            # Verifica se está online (ativo nos últimos 15 minutos)
            is_online = UserSession.objects.filter(
                user=user,
                is_active=True,
                last_activity__gte=now - timedelta(minutes=15)
            ).exists()

            activity_data.append({
                'user_id': user.id,
                'user_email': user.email,
                'user_name': user.get_full_name() or user.username,
                'user_role': user.profile.role if hasattr(user, 'profile') else 'UNKNOWN',
                'last_login': user.profile.last_login if hasattr(user, 'profile') else None,
                'last_activity': user.last_session,
                'action_count_today': actions_today,
                'action_count_week': actions_week,
                'active_sessions': active_sessions_count,
                'is_online': is_online,
            })

        serializer = UserActivitySerializer(activity_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def permission_history(self, request):
        """
        GET /api/v1/admin/permission-history/
        Histórico de mudanças de permissões
        Query params:
        - user: ID do usuário alvo
        """
        queryset = PermissionChange.objects.all().select_related(
            'changed_by', 'target_user'
        )

        user_id = request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(target_user_id=user_id)

        # Paginação
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start = (page - 1) * page_size
        end = start + page_size

        total = queryset.count()
        changes = queryset[start:end]

        serializer = PermissionChangeSerializer(changes, many=True)

        return Response({
            'data': serializer.data,
            'meta': {
                'total': total,
                'page': page,
                'page_size': page_size,
            }
        })

    @action(detail=False, methods=['get'])
    def notifications(self, request):
        """
        GET /api/v1/admin/notifications/
        Lista notificações do sistema
        """
        notifications = SystemNotification.objects.filter(
            Q(target_users=request.user) | Q(target_users__isnull=True)
        ).order_by('-created_at')

        serializer = SystemNotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_notification_read(self, request, pk=None):
        """
        POST /api/v1/admin/mark-notification-read/{notification_id}/
        Marca notificação como lida
        """
        try:
            notification = SystemNotification.objects.get(pk=pk)
            notification.mark_as_read(request.user)
            return Response({'message': 'Notificação marcada como lida'})
        except SystemNotification.DoesNotExist:
            return Response(
                {'error': 'Notificação não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def security_alerts(self, request):
        """
        GET /api/v1/admin/security-alerts/
        Detecta e retorna alertas de segurança
        """
        alerts = []
        now = timezone.now()
        last_24h = now - timedelta(hours=24)

        # Detecta múltiplas tentativas de login falhadas
        failed_logins = AuditLog.objects.filter(
            action_type='LOGIN',
            was_successful=False,
            timestamp__gte=last_24h
        ).values('user_email').annotate(
            count=Count('id')
        ).filter(count__gte=5)

        for login in failed_logins:
            alerts.append({
                'alert_type': 'multiple_failed_logins',
                'severity': 'high',
                'user_email': login['user_email'],
                'description': f"Múltiplas tentativas de login falhadas ({login['count']} vezes)",
                'timestamp': now,
                'details': {'count': login['count']}
            })

        # Detecta usuários com múltiplas sessões simultâneas
        multiple_sessions = UserSession.objects.filter(
            is_active=True
        ).values('user__email').annotate(
            count=Count('id')
        ).filter(count__gte=3)

        for session in multiple_sessions:
            alerts.append({
                'alert_type': 'multiple_sessions',
                'severity': 'medium',
                'user_email': session['user__email'],
                'description': f"Usuário com {session['count']} sessões simultâneas",
                'timestamp': now,
                'details': {'count': session['count']}
            })

        serializer = SecurityAlertSerializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def send_notification(self, request):
        """
        POST /api/v1/admin/send-notification/
        Cria uma nova notificação do sistema
        Body: {
            "title": "Título",
            "message": "Mensagem",
            "severity": "INFO|WARNING|ERROR|CRITICAL",
            "category": "SECURITY|SYSTEM|USER|DATA|PERFORMANCE",
            "target_users": [1, 2, 3] // opcional
        }
        """
        data = request.data

        notification = SystemNotification.objects.create(
            title=data.get('title'),
            message=data.get('message'),
            severity=data.get('severity', 'INFO'),
            category=data.get('category', 'SYSTEM'),
            metadata={'created_by': request.user.email}
        )

        # Adiciona usuários alvo se especificados
        target_user_ids = data.get('target_users', [])
        if target_user_ids:
            notification.target_users.set(target_user_ids)

        # Registra ação
        AuditLog.log_action(
            user=request.user,
            action_type='NOTE',
            description=f"Criou notificação: {notification.title}",
            content_object=notification,
            request=request
        )

        serializer = SystemNotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
