"""
Middleware para auditoria automática de ações
"""
from django.utils.deprecation import MiddlewareMixin
from habitacao.models_audit import AuditLog, UserSession
from django.utils import timezone
from datetime import timedelta
import json


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware que registra automaticamente ações relevantes no sistema
    """

    # Métodos HTTP que devem ser auditados
    AUDITED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']

    # Paths que devem ser auditados
    AUDITED_PATHS = [
        '/api/v1/users/',
        '/api/v1/beneficiaries/',
        '/api/v1/documents/',
        '/api/v1/auth/login/',
        '/api/v1/auth/logout/',
    ]

    # Ações sensíveis que sempre devem ser auditadas
    SENSITIVE_ACTIONS = [
        'delete',
        'approve',
        'reject',
        'change-status',
        'upload-document',
        'update-permissions',
    ]

    def process_request(self, request):
        """
        Captura informações da requisição antes de processar
        """
        # Armazena timestamp para calcular duração depois
        request._audit_start_time = timezone.now()

        # Se usuário autenticado, atualiza última atividade da sessão
        if request.user and request.user.is_authenticated:
            session_key = request.session.session_key
            if session_key:
                UserSession.objects.filter(
                    session_key=session_key,
                    is_active=True
                ).update(last_activity=timezone.now())

        return None

    def process_response(self, request, response):
        """
        Registra a ação após processamento da requisição
        """
        # Só audita se usuário autenticado
        if not (request.user and request.user.is_authenticated):
            return response

        # Só audita métodos específicos
        if request.method not in self.AUDITED_METHODS:
            return response

        # Verifica se o path deve ser auditado
        path = request.path
        should_audit = any(path.startswith(audited_path) for audited_path in self.AUDITED_PATHS)

        if not should_audit:
            return response

        # Determina o tipo de ação
        action_type = self._get_action_type(request, response)
        if not action_type:
            return response

        # Cria descrição da ação
        description = self._build_description(request, response)

        # Captura mudanças se disponível
        changes = self._extract_changes(request, response)

        # Registra o log
        try:
            AuditLog.log_action(
                user=request.user,
                action_type=action_type,
                description=description,
                content_object=None,  # Pode ser melhorado para pegar o objeto específico
                changes=changes,
                metadata=self._build_metadata(request, response),
                request=request,
                was_successful=response.status_code < 400,
                error_message=self._get_error_message(response) if response.status_code >= 400 else ''
            )
        except Exception as e:
            # Não deve quebrar a requisição se auditoria falhar
            print(f"❌ Erro ao criar log de auditoria: {e}")

        return response

    def _get_action_type(self, request, response):
        """Determina o tipo de ação baseado no método e path"""
        method = request.method
        path = request.path.lower()

        # Login/Logout
        if 'login' in path:
            return 'LOGIN' if response.status_code < 400 else None
        if 'logout' in path:
            return 'LOGOUT'

        # CRUD básico
        if method == 'POST':
            return 'CREATE'
        elif method in ['PUT', 'PATCH']:
            return 'UPDATE'
        elif method == 'DELETE':
            return 'DELETE'

        # Ações específicas baseadas no path
        if 'approve' in path:
            return 'APPROVE'
        if 'reject' in path:
            return 'REJECT'
        if 'status' in path:
            return 'CHANGE_STATUS'
        if 'document' in path and method == 'POST':
            return 'UPLOAD_DOC'
        if 'document' in path and method == 'DELETE':
            return 'DELETE_DOC'
        if 'permissions' in path or 'role' in path:
            return 'CHANGE_PERMISSIONS'

        return None

    def _build_description(self, request, response):
        """Constrói uma descrição legível da ação"""
        method = request.method
        path = request.path
        user = request.user

        # Remove prefixo da API do path
        clean_path = path.replace('/api/v1/', '')

        # Tenta extrair o recurso
        parts = clean_path.split('/')
        resource = parts[0] if parts else 'recurso'

        # Traduz ações
        action_map = {
            'POST': 'criou',
            'PUT': 'atualizou',
            'PATCH': 'modificou',
            'DELETE': 'excluiu',
        }
        action = action_map.get(method, 'executou ação em')

        description = f"{user.email} {action} {resource}"

        # Adiciona ID se disponível
        if len(parts) > 1 and parts[1].isdigit():
            description += f" (ID: {parts[1]})"

        # Adiciona status code se erro
        if response.status_code >= 400:
            description += f" - Erro {response.status_code}"

        return description

    def _extract_changes(self, request, response):
        """Extrai mudanças do request body"""
        try:
            if hasattr(request, 'body') and request.body:
                body = json.loads(request.body.decode('utf-8'))
                return {'request_data': body}
        except:
            pass
        return None

    def _build_metadata(self, request, response):
        """Constrói metadados da requisição"""
        duration = None
        if hasattr(request, '_audit_start_time'):
            duration = (timezone.now() - request._audit_start_time).total_seconds()

        return {
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_seconds': duration,
            'content_type': request.content_type,
        }

    def _get_error_message(self, response):
        """Extrai mensagem de erro da resposta"""
        try:
            if hasattr(response, 'content'):
                content = json.loads(response.content.decode('utf-8'))
                if isinstance(content, dict):
                    return content.get('error', content.get('detail', str(content)))
        except:
            pass
        return f"HTTP {response.status_code}"


class SessionManagementMiddleware(MiddlewareMixin):
    """
    Middleware para gerenciar sessões de usuários
    - Registra novas sessões
    - Limpa sessões expiradas
    - Força logout se necessário
    """

    def process_request(self, request):
        """Processa requisição e gerencia sessão"""
        # Se usuário autenticado e tem sessão
        if request.user and request.user.is_authenticated:
            session_key = request.session.session_key
            if session_key:
                # Verifica se a sessão está registrada
                try:
                    user_session = UserSession.objects.get(
                        session_key=session_key,
                        user=request.user
                    )

                    # Se foi forçada a terminar, faz logout
                    if not user_session.is_active:
                        from django.contrib.auth import logout
                        logout(request)
                        return None

                except UserSession.DoesNotExist:
                    # Cria registro da sessão se não existe
                    self._create_user_session(request)

        # Periodicamente limpa sessões expiradas (a cada 100 requisições aproximadamente)
        import random
        if random.randint(1, 100) == 1:
            UserSession.cleanup_expired()

        return None

    def _create_user_session(self, request):
        """Cria registro de sessão do usuário"""
        try:
            session_key = request.session.session_key
            if not session_key:
                # Força criação da sessão
                request.session.save()
                session_key = request.session.session_key

            # Define expiração (2 semanas por padrão)
            expires_at = timezone.now() + timedelta(days=14)

            # Obtém informações do dispositivo
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            ip_address = self._get_client_ip(request)

            UserSession.objects.create(
                user=request.user,
                session_key=session_key,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent[:500],
                device_info=self._parse_device_info(user_agent)
            )
        except Exception as e:
            print(f"❌ Erro ao criar sessão de usuário: {e}")

    def _get_client_ip(self, request):
        """Obtém IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip

    def _parse_device_info(self, user_agent):
        """Extrai informações básicas do dispositivo"""
        info = {
            'is_mobile': any(x in user_agent.lower() for x in ['mobile', 'android', 'iphone']),
            'is_tablet': 'tablet' in user_agent.lower() or 'ipad' in user_agent.lower(),
            'browser': 'unknown'
        }

        # Detecta browser
        ua_lower = user_agent.lower()
        if 'chrome' in ua_lower:
            info['browser'] = 'Chrome'
        elif 'firefox' in ua_lower:
            info['browser'] = 'Firefox'
        elif 'safari' in ua_lower:
            info['browser'] = 'Safari'
        elif 'edge' in ua_lower:
            info['browser'] = 'Edge'

        return info
