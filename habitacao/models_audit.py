"""
Sistema de Auditoria e Logs de Ações Administrativas
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import json


class AuditLog(models.Model):
    """
    Registra todas as ações realizadas por usuários administrativos no sistema
    """

    ACTION_TYPES = [
        ('CREATE', 'Criar'),
        ('UPDATE', 'Atualizar'),
        ('DELETE', 'Excluir'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('EXPORT', 'Exportar'),
        ('APPROVE', 'Aprovar'),
        ('REJECT', 'Rejeitar'),
        ('CHANGE_STATUS', 'Alterar Status'),
        ('UPLOAD_DOC', 'Upload de Documento'),
        ('DELETE_DOC', 'Excluir Documento'),
        ('CHANGE_PERMISSIONS', 'Alterar Permissões'),
        ('PASSWORD_CHANGE', 'Alteração de Senha'),
        ('PASSWORD_RESET', 'Reset de Senha'),
    ]

    # Quem realizou a ação
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name='Usuário'
    )
    user_email = models.EmailField(verbose_name='Email do Usuário', help_text='Backup caso o usuário seja deletado')
    user_role = models.CharField(max_length=20, blank=True, verbose_name='Papel do Usuário')

    # Quando aconteceu
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora', db_index=True)

    # O que aconteceu
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES, verbose_name='Tipo de Ação', db_index=True)
    description = models.TextField(verbose_name='Descrição')

    # Em qual objeto (genérico)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Tipo de Objeto'
    )
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='ID do Objeto')
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=200, blank=True, verbose_name='Representação do Objeto')

    # Dados adicionais
    changes = models.JSONField(null=True, blank=True, verbose_name='Alterações', help_text='Diff das mudanças')
    metadata = models.JSONField(null=True, blank=True, verbose_name='Metadados', help_text='Informações extras')

    # Informações da requisição
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='Endereço IP')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')

    # Status
    was_successful = models.BooleanField(default=True, verbose_name='Sucesso')
    error_message = models.TextField(blank=True, verbose_name='Mensagem de Erro')

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'user']),
            models.Index(fields=['action_type', '-timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.user_email} - {self.get_action_type_display()}"

    @classmethod
    def log_action(cls, user, action_type, description, content_object=None,
                   changes=None, metadata=None, request=None, was_successful=True, error_message=''):
        """
        Método helper para criar logs de auditoria

        Args:
            user: Usuário que realizou a ação
            action_type: Tipo da ação (use as constantes ACTION_TYPES)
            description: Descrição textual da ação
            content_object: Objeto afetado (opcional)
            changes: Dict com as mudanças (antes/depois)
            metadata: Informações extras
            request: Request HTTP (para pegar IP e User-Agent)
            was_successful: Se a ação foi bem sucedida
            error_message: Mensagem de erro se falhou
        """
        user_role = ''
        if hasattr(user, 'profile'):
            user_role = user.profile.role

        ip_address = None
        user_agent = ''
        if request:
            ip_address = cls._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        log = cls.objects.create(
            user=user,
            user_email=user.email,
            user_role=user_role,
            action_type=action_type,
            description=description,
            content_type=ContentType.objects.get_for_model(content_object) if content_object else None,
            object_id=content_object.pk if content_object else None,
            object_repr=str(content_object)[:200] if content_object else '',
            changes=changes,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            was_successful=was_successful,
            error_message=error_message
        )
        return log

    @staticmethod
    def _get_client_ip(request):
        """Obtém o IP real do cliente, considerando proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserSession(models.Model):
    """
    Controla sessões ativas dos usuários para permitir:
    - Limitar número de sessões simultâneas
    - Forçar logout remoto
    - Monitorar atividade
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name='Usuário'
    )
    session_key = models.CharField(max_length=40, unique=True, verbose_name='Chave da Sessão')

    # Informações da sessão
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criada em')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='Última Atividade')
    expires_at = models.DateTimeField(verbose_name='Expira em')

    # Informações do cliente
    ip_address = models.GenericIPAddressField(verbose_name='Endereço IP')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    device_info = models.JSONField(null=True, blank=True, verbose_name='Informações do Dispositivo')

    # Status
    is_active = models.BooleanField(default=True, verbose_name='Ativa')
    terminated_at = models.DateTimeField(null=True, blank=True, verbose_name='Terminada em')
    termination_reason = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('LOGOUT', 'Logout normal'),
            ('EXPIRED', 'Expirou'),
            ('FORCED', 'Forçada pelo admin'),
            ('REPLACED', 'Substituída por nova sessão'),
        ],
        verbose_name='Motivo do Término'
    )

    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'Sessão de Usuário'
        verbose_name_plural = 'Sessões de Usuários'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', '-last_activity']),
            models.Index(fields=['is_active', '-last_activity']),
        ]

    def __str__(self):
        status = 'Ativa' if self.is_active else 'Inativa'
        return f"{self.user.email} - {status} - {self.last_activity.strftime('%Y-%m-%d %H:%M')}"

    def terminate(self, reason='LOGOUT'):
        """Termina a sessão"""
        self.is_active = False
        self.terminated_at = timezone.now()
        self.termination_reason = reason
        self.save()

    @classmethod
    def cleanup_expired(cls):
        """Remove sessões expiradas"""
        now = timezone.now()
        expired = cls.objects.filter(expires_at__lt=now, is_active=True)
        count = expired.count()
        expired.update(is_active=False, terminated_at=now, termination_reason='EXPIRED')
        return count


class PermissionChange(models.Model):
    """
    Registra mudanças de permissões e roles de usuários
    Histórico completo de quem mudou o que e quando
    """
    # Quem mudou
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='permission_changes_made',
        verbose_name='Alterado por'
    )

    # Em quem mudou
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='permission_changes_received',
        verbose_name='Usuário Alvo'
    )

    # Quando
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora')

    # O que mudou
    field_changed = models.CharField(
        max_length=50,
        verbose_name='Campo Alterado',
        help_text='Ex: role, is_active, municipality'
    )
    old_value = models.TextField(blank=True, verbose_name='Valor Anterior')
    new_value = models.TextField(blank=True, verbose_name='Novo Valor')

    # Justificativa
    reason = models.TextField(blank=True, verbose_name='Justificativa')

    class Meta:
        db_table = 'permission_changes'
        verbose_name = 'Alteração de Permissão'
        verbose_name_plural = 'Alterações de Permissões'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['target_user', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.changed_by.email if self.changed_by else 'Sistema'} alterou {self.field_changed} de {self.target_user.email}"


class SystemNotification(models.Model):
    """
    Notificações do sistema para administradores
    Alertas sobre atividades suspeitas, erros, etc.
    """
    SEVERITY_CHOICES = [
        ('INFO', 'Informação'),
        ('WARNING', 'Aviso'),
        ('ERROR', 'Erro'),
        ('CRITICAL', 'Crítico'),
    ]

    CATEGORY_CHOICES = [
        ('SECURITY', 'Segurança'),
        ('SYSTEM', 'Sistema'),
        ('USER', 'Usuário'),
        ('DATA', 'Dados'),
        ('PERFORMANCE', 'Performance'),
    ]

    # Notificação
    title = models.CharField(max_length=200, verbose_name='Título')
    message = models.TextField(verbose_name='Mensagem')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='INFO', verbose_name='Severidade')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Categoria')

    # Timing
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criada em', db_index=True)

    # Para quem
    target_users = models.ManyToManyField(
        User,
        related_name='notifications',
        blank=True,
        verbose_name='Usuários Alvo',
        help_text='Vazio = todos os admins'
    )

    # Status
    is_read = models.BooleanField(default=False, verbose_name='Lida')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Lida em')
    read_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications_read',
        verbose_name='Lida por'
    )

    # Dados extras
    metadata = models.JSONField(null=True, blank=True, verbose_name='Metadados')
    action_url = models.CharField(max_length=200, blank=True, verbose_name='URL da Ação')

    class Meta:
        db_table = 'system_notifications'
        verbose_name = 'Notificação do Sistema'
        verbose_name_plural = 'Notificações do Sistema'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'is_read']),
            models.Index(fields=['severity', '-created_at']),
        ]

    def __str__(self):
        return f"{self.get_severity_display()} - {self.title}"

    def mark_as_read(self, user):
        """Marca a notificação como lida"""
        self.is_read = True
        self.read_at = timezone.now()
        self.read_by = user
        self.save()
