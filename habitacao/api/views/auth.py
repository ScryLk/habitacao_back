"""
Views de autenticação
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from habitacao.api.serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer
)
from habitacao.api.services.auth import AuthService
from habitacao.api.utils.response import success_response, error_response
from habitacao.api.permissions.roles import IsCoordinator


@swagger_auto_schema(
    method='post',
    request_body=LoginSerializer,
    responses={
        200: openapi.Response('Login successful', examples={
            'application/json': {
                'data': {
                    'access': 'eyJ0eXAiOiJKV1QiLCJh...',
                    'refresh': 'eyJ0eXAiOiJKV1QiLC...',
                    'user': {
                        'id': 1,
                        'email': 'user@example.com',
                        'full_name': 'João Silva',
                        'role': 'ANALYST',
                        'municipality_id': 1
                    }
                },
                'error': None
            }
        }),
        401: 'Credenciais inválidas'
    },
    operation_description="Autentica usuário e retorna tokens JWT"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    POST /api/v1/auth/login
    Autentica usuário e retorna tokens JWT
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        auth_data = AuthService.login(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        return success_response(auth_data)
    except ValueError as e:
        return error_response(
            message=str(e),
            code="AUTHENTICATION_FAILED",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['refresh'],
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
        }
    ),
    responses={200: 'Token renovado', 401: 'Token inválido'}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    POST /api/v1/auth/refresh
    Renova access token
    """
    refresh = request.data.get('refresh')
    if not refresh:
        return error_response(
            message="Refresh token é obrigatório",
            code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        auth_data = AuthService.refresh_token(refresh)
        return success_response(auth_data)
    except ValueError as e:
        return error_response(
            message=str(e),
            code="INVALID_TOKEN",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


@swagger_auto_schema(
    method='post',
    request_body=RegisterSerializer,
    responses={201: 'Usuário criado', 400: 'Erro de validação'}
)
@api_view(['POST'])
@permission_classes([IsCoordinator])
def register(request):
    """
    POST /api/v1/auth/register
    Registra novo usuário servidor (ADMIN/COORDINATOR apenas)
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = serializer.save()
        user_serializer = UserSerializer(user)
        return success_response(user_serializer.data, status_code=status.HTTP_201_CREATED)
    except ValueError as e:
        return error_response(
            message=str(e),
            code="REGISTRATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )


@swagger_auto_schema(
    method='get',
    responses={200: UserSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me(request):
    """
    GET /api/v1/me
    Retorna dados do usuário logado
    """
    serializer = UserSerializer(request.user)
    return success_response(serializer.data)
