from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from habitacao.api.serializers.user import UserSerializer, RegisterSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gerenciar usuários (apenas admin)
    """
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        """Usa RegisterSerializer para criação"""
        if self.action == 'create':
            return RegisterSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        """Cria novo usuário com perfil"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Retorna dados do usuário criado
        user_serializer = UserSerializer(user)
        return Response({
            'data': user_serializer.data,
            'error': None
        }, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Remove usuário e todos os dados relacionados de forma segura"""
        instance = self.get_object()
        try:
            # Exemplo: deletar documentos relacionados antes do usuário
            if hasattr(instance, 'profile'):
                profile = instance.profile
                # Adapte aqui para remover dados relacionados ao perfil, se necessário
                # Exemplo: profile.beneficiaries.all().delete()
                # Se não houver dependências, apenas delete o profile
                profile.delete()
            instance.delete()
            return Response({'data': 'Usuário removido com sucesso', 'error': None}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'data': None, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
