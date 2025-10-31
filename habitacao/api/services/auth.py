"""
Serviço de autenticação
"""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from habitacao.models import UserProfile


class AuthService:
    """Serviço de autenticação"""

    @staticmethod
    def login(email, password):
        """
        Autentica usuário e retorna tokens JWT
        """
        # Buscar usuário pelo email primeiro
        try:
            db_user = User.objects.get(email=email)
            username = db_user.username
        except User.DoesNotExist:
            raise ValueError("Credenciais inválidas")

        # Autenticar usando o username
        user = authenticate(username=username, password=password)

        if not user:
            raise ValueError("Credenciais inválidas")

        if not hasattr(user, 'profile'):
            raise ValueError("Usuário sem perfil configurado")

        if not user.profile.is_active:
            raise ValueError("Usuário inativo")

        # Atualiza último login
        user.profile.last_login = timezone.now()
        user.profile.save()

        # Gera tokens
        refresh = RefreshToken.for_user(user)

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.get_full_name(),
                'role': user.profile.role,
                'municipality_id': user.profile.municipality_id,
                'is_superuser': user.is_superuser,  # <-- Adiciona campo
            }
        }

    @staticmethod
    def refresh_token(refresh_token):
        """Renova access token"""
        try:
            refresh = RefreshToken(refresh_token)
            return {
                'access': str(refresh.access_token),
            }
        except Exception as e:
            raise ValueError("Token inválido ou expirado")

    @staticmethod
    def register(full_name, email, password, cpf, role, municipality_id=None):
        """
        Registra novo usuário servidor
        """
        # Valida se email já existe
        if User.objects.filter(email=email).exists():
            raise ValueError("Este email já está em uso")

        # Valida se CPF já existe
        if UserProfile.objects.filter(cpf=cpf).exists():
            raise ValueError("Este CPF já está cadastrado")

        # Divide nome
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Cria usuário Django
        user = User.objects.create_user(
            username=email,  # Usa email como username
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        # Cria perfil
        profile = UserProfile.objects.create(
            user=user,
            cpf=cpf,
            role=role,
            municipality_id=municipality_id
        )

        return user
