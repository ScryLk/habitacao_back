"""
Permissões baseadas em roles (papéis)
"""
from rest_framework import permissions
from habitacao.choices import UserRole


class IsAdmin(permissions.BasePermission):
    """Apenas administradores"""
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.role == UserRole.ADMIN
        )


class IsCoordinator(permissions.BasePermission):
    """Coordenadores ou superiores"""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and hasattr(request.user, 'profile')):
            return False

        allowed_roles = [UserRole.ADMIN, UserRole.COORDINATOR]
        return request.user.profile.role in allowed_roles


class IsAnalyst(permissions.BasePermission):
    """Analistas ou superiores"""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            print(f"❌ IsAnalyst: User not authenticated")
            return False

        if not hasattr(request.user, 'profile'):
            print(f"❌ IsAnalyst: User {request.user.email} has no profile")
            return False

        allowed_roles = [UserRole.ADMIN, UserRole.COORDINATOR, UserRole.ANALYST]
        has_permission = request.user.profile.role in allowed_roles
        print(f"🔒 IsAnalyst check: user={request.user.email}, role={request.user.profile.role}, allowed={has_permission}")
        return has_permission


class IsClerkOrHigher(permissions.BasePermission):
    """Atendentes ou superiores (qualquer usuário autenticado com perfil)"""
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'profile')
        )


class IsMunicipalityScoped(permissions.BasePermission):
    """
    Valida se o usuário tem acesso ao município do registro
    Administradores têm acesso a todos os municípios
    """
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated and hasattr(request.user, 'profile')):
            return False

        # Admin tem acesso a tudo
        if request.user.profile.role == UserRole.ADMIN:
            return True

        # Se o usuário tem município definido, valida o escopo
        if request.user.profile.municipality:
            # Verifica se o objeto tem município
            if hasattr(obj, 'municipality'):
                return obj.municipality == request.user.profile.municipality
            # Se for um beneficiário
            if hasattr(obj, 'beneficiary') and hasattr(obj.beneficiary, 'municipality'):
                return obj.beneficiary.municipality == request.user.profile.municipality

        # Se o usuário não tem município definido, permite acesso
        return True
