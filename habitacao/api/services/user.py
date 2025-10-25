"""
Serviço de usuários
"""
from django.contrib.auth.models import User
from habitacao.models import UserProfile
from habitacao.choices import UserRole


class UserService:
    """Serviço de gerenciamento de usuários"""

    @staticmethod
    def get_me(user):
        """Retorna dados do usuário logado"""
        return user

    @staticmethod
    def list_users(filters=None, requesting_user=None):
        """
        Lista usuários
        Apenas Admin e Coordinator podem listar
        """
        queryset = User.objects.filter(profile__isnull=False).select_related('profile')

        # Aplica filtros
        if filters:
            if filters.get('role'):
                queryset = queryset.filter(profile__role=filters['role'])
            if filters.get('municipality_id'):
                queryset = queryset.filter(profile__municipality_id=filters['municipality_id'])
            if filters.get('is_active') is not None:
                queryset = queryset.filter(profile__is_active=filters['is_active'])

        return queryset.order_by('-date_joined')

    @staticmethod
    def update_profile(user_id, data):
        """Atualiza perfil do usuário"""
        user = User.objects.get(id=user_id)

        # Atualiza dados do User
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
            user.username = data['email']  # Mantém consistência

        user.save()

        # Atualiza perfil
        if hasattr(user, 'profile'):
            profile = user.profile
            if 'role' in data:
                profile.role = data['role']
            if 'municipality_id' in data:
                profile.municipality_id = data['municipality_id']
            if 'is_active' in data:
                profile.is_active = data['is_active']

            profile.save()

        return user

    @staticmethod
    def deactivate_user(user_id):
        """Desativa usuário"""
        user = User.objects.get(id=user_id)
        if hasattr(user, 'profile'):
            user.profile.is_active = False
            user.profile.save()
        user.is_active = False
        user.save()
        return user

    @staticmethod
    def activate_user(user_id):
        """Ativa usuário"""
        user = User.objects.get(id=user_id)
        if hasattr(user, 'profile'):
            user.profile.is_active = True
            user.profile.save()
        user.is_active = True
        user.save()
        return user
