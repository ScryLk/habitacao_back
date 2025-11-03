"""
Serializers para sistema de auditoria
"""
from rest_framework import serializers
from habitacao.models_audit import AuditLog, UserSession, PermissionChange, SystemNotification
from django.contrib.auth.models import User


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer para logs de auditoria"""
    user_email = serializers.EmailField(read_only=True)
    user_role_display = serializers.CharField(source='user_role', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    content_type_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'user_email',
            'user_role',
            'user_role_display',
            'timestamp',
            'action_type',
            'action_type_display',
            'description',
            'content_type',
            'content_type_name',
            'object_id',
            'object_repr',
            'changes',
            'metadata',
            'ip_address',
            'user_agent',
            'was_successful',
            'error_message',
        ]
        read_only_fields = fields

    def get_content_type_name(self, obj):
        if obj.content_type:
            return obj.content_type.model
        return None


class AuditLogSummarySerializer(serializers.ModelSerializer):
    """Serializer resumido para listagens"""
    user_email = serializers.EmailField(read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user_email',
            'timestamp',
            'action_type',
            'action_type_display',
            'description',
            'was_successful',
        ]
        read_only_fields = fields


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer para sessões de usuários"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    is_current = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = UserSession
        fields = [
            'id',
            'user',
            'user_email',
            'user_full_name',
            'session_key',
            'created_at',
            'last_activity',
            'expires_at',
            'ip_address',
            'user_agent',
            'device_info',
            'is_active',
            'terminated_at',
            'termination_reason',
            'is_current',
            'duration',
        ]
        read_only_fields = fields

    def get_is_current(self, obj):
        """Verifica se é a sessão atual do usuário fazendo a requisição"""
        request = self.context.get('request')
        if request and request.session:
            return obj.session_key == request.session.session_key
        return False

    def get_duration(self, obj):
        """Calcula duração da sessão em segundos"""
        if obj.terminated_at:
            return (obj.terminated_at - obj.created_at).total_seconds()
        from django.utils import timezone
        return (obj.last_activity - obj.created_at).total_seconds()


class PermissionChangeSerializer(serializers.ModelSerializer):
    """Serializer para mudanças de permissões"""
    changed_by_email = serializers.EmailField(source='changed_by.email', read_only=True)
    target_user_email = serializers.EmailField(source='target_user.email', read_only=True)
    target_user_name = serializers.CharField(source='target_user.get_full_name', read_only=True)

    class Meta:
        model = PermissionChange
        fields = [
            'id',
            'changed_by',
            'changed_by_email',
            'target_user',
            'target_user_email',
            'target_user_name',
            'timestamp',
            'field_changed',
            'old_value',
            'new_value',
            'reason',
        ]
        read_only_fields = fields


class SystemNotificationSerializer(serializers.ModelSerializer):
    """Serializer para notificações do sistema"""
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    read_by_email = serializers.EmailField(source='read_by.email', read_only=True, allow_null=True)

    class Meta:
        model = SystemNotification
        fields = [
            'id',
            'title',
            'message',
            'severity',
            'severity_display',
            'category',
            'category_display',
            'created_at',
            'is_read',
            'read_at',
            'read_by',
            'read_by_email',
            'metadata',
            'action_url',
        ]
        read_only_fields = ['created_at', 'read_at', 'read_by', 'read_by_email']


class AdminDashboardStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas do dashboard administrativo"""
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    total_beneficiaries = serializers.IntegerField()
    pending_applications = serializers.IntegerField()
    approved_applications = serializers.IntegerField()
    rejected_applications = serializers.IntegerField()

    # Estatísticas de auditoria
    total_audit_logs = serializers.IntegerField()
    logs_last_24h = serializers.IntegerField()
    failed_actions_last_24h = serializers.IntegerField()

    # Sessões
    active_sessions = serializers.IntegerField()
    unique_users_online = serializers.IntegerField()

    # Notificações
    unread_notifications = serializers.IntegerField()
    critical_notifications = serializers.IntegerField()


class UserActivitySerializer(serializers.Serializer):
    """Serializer para atividade de usuários"""
    user_id = serializers.IntegerField()
    user_email = serializers.EmailField()
    user_name = serializers.CharField()
    user_role = serializers.CharField()
    last_login = serializers.DateTimeField(allow_null=True)
    last_activity = serializers.DateTimeField(allow_null=True)
    action_count_today = serializers.IntegerField()
    action_count_week = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    is_online = serializers.BooleanField()


class SecurityAlertSerializer(serializers.Serializer):
    """Serializer para alertas de segurança"""
    alert_type = serializers.ChoiceField(choices=[
        ('multiple_failed_logins', 'Múltiplas tentativas de login falhadas'),
        ('unusual_activity', 'Atividade incomum'),
        ('permission_escalation', 'Tentativa de escalação de privilégios'),
        ('suspicious_ip', 'IP suspeito'),
        ('multiple_sessions', 'Múltiplas sessões simultâneas'),
    ])
    severity = serializers.ChoiceField(choices=['low', 'medium', 'high', 'critical'])
    user_email = serializers.EmailField()
    description = serializers.CharField()
    timestamp = serializers.DateTimeField()
    details = serializers.JSONField()
