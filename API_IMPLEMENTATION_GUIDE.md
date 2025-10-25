# Guia Completo de Implementação da API REST

## Status Atual

✅ **Concluído:**
- Configuração do Django REST Framework
- Configuração do JWT (Simple JWT)
- Configuração do CORS
- Configuração do Swagger/OpenAPI
- Exception handler customizado
- Permissões baseadas em roles
- Serializers completos:
  - Base (Municipality, PriorityCriteria, etc)
  - User & Authentication
  - Beneficiary (completo com nested data)

## Estrutura de Diretórios Criada

```
habitacao/
├── api/
│   ├── __init__.py
│   ├── exceptions.py          ✅ CRIADO
│   ├── permissions/
│   │   ├── __init__.py
│   │   └── roles.py           ✅ CRIADO
│   ├── serializers/
│   │   ├── __init__.py        ✅ CRIADO
│   │   ├── base.py            ✅ CRIADO
│   │   ├── user.py            ✅ CRIADO
│   │   └── beneficiary.py     ✅ CRIADO
│   ├── services/              ⚠️ A IMPLEMENTAR
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── beneficiary.py
│   │   ├── workflow.py
│   │   ├── document.py
│   │   ├── assignment.py
│   │   ├── priority.py
│   │   ├── social_benefit.py
│   │   ├── dashboard.py
│   │   ├── report.py
│   │   └── public.py
│   ├── views/                 ⚠️ A IMPLEMENTAR
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── beneficiary.py
│   │   ├── workflow.py
│   │   ├── document.py
│   │   ├── base.py
│   │   ├── dashboard.py
│   │   └── public.py
│   ├── utils/                 ⚠️ A IMPLEMENTAR
│   │   ├── __init__.py
│   │   ├── response.py
│   │   ├── pagination.py
│   │   └── filters.py
│   └── urls.py                ⚠️ A IMPLEMENTAR
```

## Próximos Passos de Implementação

### 1. Criar Utilitários (utils/)

#### utils/response.py
```python
"""
Padronização de respostas da API
"""
from rest_framework.response import Response


def success_response(data, meta=None):
    """
    Resposta de sucesso padrão
    {
        "data": {...},
        "error": null,
        "meta": {...}
    }
    """
    response_data = {
        "data": data,
        "error": None,
    }

    if meta:
        response_data["meta"] = meta

    return Response(response_data)


def error_response(message, code="ERROR", details=None, status=400):
    """
    Resposta de erro padrão
    """
    response_data = {
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details or {}
        }
    }

    return Response(response_data, status=status)
```

#### utils/pagination.py
```python
"""
Paginação customizada
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'per_page'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'error': None,
            'meta': {
                'page': self.page.number,
                'per_page': self.page.paginator.per_page,
                'total': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
            }
        })
```

### 2. Criar Services (Camada de Lógica de Negócio)

#### services/auth.py
```python
"""
Serviço de autenticação
"""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from habitacao.models import UserProfile


class AuthService:
    """Serviço de autenticação"""

    @staticmethod
    def login(email, password):
        """
        Autentica usuário e retorna tokens JWT
        """
        user = authenticate(username=email, password=password)

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
```

#### services/beneficiary.py
```python
"""
Serviço de beneficiários
"""
from django.db import transaction
from habitacao.models import Beneficiary, Municipality
from habitacao.choices import ApplicationStatus


class BeneficiaryService:
    """Serviço de gerenciamento de beneficiários"""

    @staticmethod
    def create_from_nested_data(data):
        """
        Cria beneficiário a partir de dados aninhados
        """
        with transaction.atomic():
            # Extrai dados aninhados
            phones = data.pop('phones', {})
            address = data.pop('address', {})
            spouse = data.pop('spouse', {})
            economy = data.pop('economy', {})
            family = data.pop('family', {})
            housing = data.pop('housing', {})

            # Cria beneficiário
            beneficiary = Beneficiary.objects.create(
                # Dados pessoais
                full_name=data.get('full_name'),
                cpf=data.get('cpf'),
                rg=data.get('rg', ''),
                birth_date=data.get('birth_date'),
                marital_status=data.get('marital_status', ''),
                # Contatos
                email=data.get('email', ''),
                phone_primary=phones.get('primary', ''),
                phone_secondary=phones.get('secondary', ''),
                # Endereço
                address_line=address.get('line', ''),
                address_number=address.get('number', ''),
                address_complement=address.get('complement', ''),
                neighborhood=address.get('neighborhood', ''),
                municipality_id=address.get('municipality_id'),
                cep=address.get('cep', ''),
                uf=address.get('uf', ''),
                # Cônjuge
                spouse_name=spouse.get('name', ''),
                spouse_rg=spouse.get('rg', ''),
                spouse_birth_date=spouse.get('birth_date'),
                # Econômico
                main_occupation=economy.get('main_occupation', ''),
                gross_family_income=economy.get('gross_family_income'),
                has_cadunico=economy.get('has_cadunico', False),
                nis_number=economy.get('nis_number', ''),
                # Família
                family_size=family.get('family_size', 1),
                has_elderly=family.get('has_elderly', False),
                elderly_count=family.get('elderly_count', 0),
                has_children=family.get('has_children', False),
                children_count=family.get('children_count', 0),
                has_disability_or_tea=family.get('has_disability_or_tea', False),
                disability_or_tea_count=family.get('disability_or_tea_count', 0),
                household_head_gender=family.get('household_head_gender', ''),
                family_in_cadunico_updated=family.get('cadunico_updated', False),
                # Habitação
                no_own_house=housing.get('no_own_house', False),
                precarious_own_house=housing.get('precarious_own_house', False),
                cohabitation=housing.get('cohabitation', False),
                improvised_dwelling=housing.get('improvised_dwelling', False),
                pays_rent=housing.get('pays_rent', False),
                rent_value=housing.get('rent_value'),
                other_housing_desc=housing.get('other_housing_desc', ''),
                # Outros
                notes=data.get('notes', ''),
                status=ApplicationStatus.DRAFT,
            )

            return beneficiary

    @staticmethod
    def list(filters=None, user=None):
        """
        Lista beneficiários com filtros
        Aplica escopo de município se aplicável
        """
        queryset = Beneficiary.objects.all()

        # Aplica escopo de município
        if user and hasattr(user, 'profile'):
            if user.profile.municipality and user.profile.role != 'ADMIN':
                queryset = queryset.filter(municipality=user.profile.municipality)

        # Aplica filtros
        if filters:
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
            if filters.get('municipality_id'):
                queryset = queryset.filter(municipality_id=filters['municipality_id'])
            if filters.get('cpf'):
                queryset = queryset.filter(cpf__icontains=filters['cpf'])
            if filters.get('protocol'):
                queryset = queryset.filter(protocol_number__icontains=filters['protocol'])

        return queryset.select_related('municipality').order_by('-created_at')
```

#### services/workflow.py
```python
"""
Serviço de workflow (transições de status)
"""
from django.db import transaction
from django.utils import timezone
from habitacao.models import (
    Beneficiary, ApplicationActionHistory,
    ApplicationAssignment, DocumentType
)
from habitacao.choices import ApplicationStatus, ApplicationAction as ActionType


class WorkflowService:
    """Serviço de gerenciamento de workflow"""

    @staticmethod
    def validate_documents(beneficiary):
        """Valida se todos documentos obrigatórios foram anexados"""
        required_types = DocumentType.objects.filter(required=True, active=True)
        uploaded_types = beneficiary.documents.values_list('document_type_id', flat=True)

        missing = []
        for doc_type in required_types:
            if doc_type.id not in uploaded_types:
                missing.append(doc_type.label)

        if missing:
            raise ValueError(f"Documentos obrigatórios faltando: {', '.join(missing)}")

    @staticmethod
    @transaction.atomic
    def submit(beneficiary_id, user):
        """
        Submete inscrição para análise
        Gera protocolo e valida documentos
        """
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)

        # Valida status atual
        if beneficiary.status != ApplicationStatus.DRAFT:
            raise ValueError("Apenas rascunhos podem ser submetidos")

        # Valida documentos obrigatórios
        WorkflowService.validate_documents(beneficiary)

        # Atualiza status
        old_status = beneficiary.status
        beneficiary.status = ApplicationStatus.SUBMITTED
        beneficiary.submitted_at = timezone.now()
        beneficiary.submitted_by = user
        beneficiary.save()

        # Registra ação
        ApplicationActionHistory.objects.create(
            beneficiary=beneficiary,
            action=ActionType.SUBMIT,
            from_status=old_status,
            to_status=beneficiary.status,
            message="Inscrição submetida para análise",
            created_by=user
        )

        return beneficiary

    @staticmethod
    @transaction.atomic
    def start_review(beneficiary_id, user):
        """
        Inicia análise
        Cria assignment ativo para o analista
        """
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)

        if beneficiary.status != ApplicationStatus.SUBMITTED:
            raise ValueError("Apenas inscrições submetidas podem entrar em análise")

        # Atualiza status
        old_status = beneficiary.status
        beneficiary.status = ApplicationStatus.UNDER_REVIEW
        beneficiary.last_review_at = timezone.now()
        beneficiary.last_reviewed_by = user
        beneficiary.save()

        # Cria assignment
        ApplicationAssignment.objects.create(
            beneficiary=beneficiary,
            assigned_to=user,
            active=True
        )

        # Registra ação
        ApplicationActionHistory.objects.create(
            beneficiary=beneficiary,
            action=ActionType.START_REVIEW,
            from_status=old_status,
            to_status=beneficiary.status,
            message=f"Análise iniciada por {user.get_full_name()}",
            created_by=user
        )

        return beneficiary

    @staticmethod
    @transaction.atomic
    def request_correction(beneficiary_id, user, message):
        """Solicita correções"""
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)

        if beneficiary.status != ApplicationStatus.UNDER_REVIEW:
            raise ValueError("Apenas inscrições em análise podem solicitar correção")

        old_status = beneficiary.status
        beneficiary.status = ApplicationStatus.CORRECTION_REQUESTED
        beneficiary.last_review_at = timezone.now()
        beneficiary.last_reviewed_by = user
        beneficiary.save()

        ApplicationActionHistory.objects.create(
            beneficiary=beneficiary,
            action=ActionType.REQUEST_CORRECTION,
            from_status=old_status,
            to_status=beneficiary.status,
            message=message,
            created_by=user
        )

        return beneficiary

    @staticmethod
    @transaction.atomic
    def approve(beneficiary_id, user, message=None):
        """Aprova inscrição"""
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)

        if beneficiary.status != ApplicationStatus.UNDER_REVIEW:
            raise ValueError("Apenas inscrições em análise podem ser aprovadas")

        old_status = beneficiary.status
        beneficiary.status = ApplicationStatus.APPROVED
        beneficiary.last_review_at = timezone.now()
        beneficiary.last_reviewed_by = user
        beneficiary.save()

        # Encerra assignment
        ApplicationAssignment.objects.filter(
            beneficiary=beneficiary,
            active=True
        ).update(active=False)

        ApplicationActionHistory.objects.create(
            beneficiary=beneficiary,
            action=ActionType.APPROVE,
            from_status=old_status,
            to_status=beneficiary.status,
            message=message or "Inscrição aprovada",
            created_by=user
        )

        return beneficiary

    @staticmethod
    @transaction.atomic
    def reject(beneficiary_id, user, message):
        """Rejeita inscrição"""
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)

        if beneficiary.status != ApplicationStatus.UNDER_REVIEW:
            raise ValueError("Apenas inscrições em análise podem ser rejeitadas")

        if not message:
            raise ValueError("Mensagem de justificativa é obrigatória")

        old_status = beneficiary.status
        beneficiary.status = ApplicationStatus.REJECTED
        beneficiary.last_review_at = timezone.now()
        beneficiary.last_reviewed_by = user
        beneficiary.save()

        # Encerra assignment
        ApplicationAssignment.objects.filter(
            beneficiary=beneficiary,
            active=True
        ).update(active=False)

        ApplicationActionHistory.objects.create(
            beneficiary=beneficiary,
            action=ActionType.REJECT,
            from_status=old_status,
            to_status=beneficiary.status,
            message=message,
            created_by=user
        )

        return beneficiary
```

### 3. Criar Views (ViewSets)

#### views/auth.py
```python
"""
Views de autenticação
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from habitacao.api.serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer
)
from habitacao.api.services.auth import AuthService
from habitacao.api.utils.response import success_response, error_response


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
            status=status.HTTP_401_UNAUTHORIZED
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
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        auth_data = AuthService.refresh_token(refresh)
        return success_response(auth_data)
    except ValueError as e:
        return error_response(
            message=str(e),
            code="INVALID_TOKEN",
            status=status.HTTP_401_UNAUTHORIZED
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
```

#### views/beneficiary.py
```python
"""
Views de beneficiários
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from habitacao.models import Beneficiary
from habitacao.api.serializers import (
    BeneficiaryListSerializer,
    BeneficiaryDetailSerializer,
    BeneficiaryCreateSerializer,
    BeneficiaryUpdateSerializer,
    WorkflowActionSerializer,
)
from habitacao.api.services.beneficiary import BeneficiaryService
from habitacao.api.services.workflow import WorkflowService
from habitacao.api.permissions.roles import IsAnalyst, IsClerkOrHigher
from habitacao.api.utils.response import success_response, error_response
from habitacao.api.utils.pagination import StandardResultsSetPagination


class BeneficiaryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para beneficiários
    """
    queryset = Beneficiary.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['status', 'municipality', 'has_cadunico']
    search_fields = ['full_name', 'cpf', 'protocol_number']

    def get_serializer_class(self):
        if self.action == 'list':
            return BeneficiaryListSerializer
        elif self.action == 'create':
            return BeneficiaryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BeneficiaryUpdateSerializer
        return BeneficiaryDetailSerializer

    def get_queryset(self):
        """Aplica filtros e escopo de município"""
        service = BeneficiaryService()
        filters = {
            'status': self.request.query_params.get('status'),
            'municipality_id': self.request.query_params.get('municipality_id'),
            'cpf': self.request.query_params.get('cpf'),
            'protocol': self.request.query_params.get('protocol'),
        }
        return service.list(filters=filters, user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAnalyst])
    def submit(self, request, pk=None):
        """
        POST /api/v1/beneficiaries/{id}/submit
        Submete inscrição
        """
        try:
            beneficiary = WorkflowService.submit(pk, request.user)
            serializer = BeneficiaryDetailSerializer(beneficiary)
            return success_response(serializer.data)
        except ValueError as e:
            return error_response(str(e), code="WORKFLOW_ERROR", status=400)

    @action(detail=True, methods=['post'], permission_classes=[IsAnalyst])
    def start_review(self, request, pk=None):
        """
        POST /api/v1/beneficiaries/{id}/start-review
        Inicia análise
        """
        try:
            beneficiary = WorkflowService.start_review(pk, request.user)
            serializer = BeneficiaryDetailSerializer(beneficiary)
            return success_response(serializer.data)
        except ValueError as e:
            return error_response(str(e), code="WORKFLOW_ERROR", status=400)

    @action(detail=True, methods=['post'], permission_classes=[IsAnalyst])
    def request_correction(self, request, pk=None):
        """
        POST /api/v1/beneficiaries/{id}/request-correction
        Solicita correções
        """
        serializer = WorkflowActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            beneficiary = WorkflowService.request_correction(
                pk,
                request.user,
                serializer.validated_data.get('message', '')
            )
            result_serializer = BeneficiaryDetailSerializer(beneficiary)
            return success_response(result_serializer.data)
        except ValueError as e:
            return error_response(str(e), code="WORKFLOW_ERROR", status=400)

    @action(detail=True, methods=['post'], permission_classes=[IsAnalyst])
    def approve(self, request, pk=None):
        """
        POST /api/v1/beneficiaries/{id}/approve
        Aprova inscrição
        """
        serializer = WorkflowActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            beneficiary = WorkflowService.approve(
                pk,
                request.user,
                serializer.validated_data.get('message')
            )
            result_serializer = BeneficiaryDetailSerializer(beneficiary)
            return success_response(result_serializer.data)
        except ValueError as e:
            return error_response(str(e), code="WORKFLOW_ERROR", status=400)

    @action(detail=True, methods=['post'], permission_classes=[IsAnalyst])
    def reject(self, request, pk=None):
        """
        POST /api/v1/beneficiaries/{id}/reject
        Rejeita inscrição
        """
        serializer = WorkflowActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data.get('message')
        if not message:
            return error_response(
                "Mensagem de justificativa é obrigatória",
                code="VALIDATION_ERROR",
                status=400
            )

        try:
            beneficiary = WorkflowService.reject(pk, request.user, message)
            result_serializer = BeneficiaryDetailSerializer(beneficiary)
            return success_response(result_serializer.data)
        except ValueError as e:
            return error_response(str(e), code="WORKFLOW_ERROR", status=400)
```

### 4. Configurar URLs

#### api/urls.py
```python
"""
URLs da API v1
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from .views import auth, beneficiary, base

# Schema para Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Sistema Habitação - MCMV API",
        default_version='v1',
        description="API REST para gerenciamento do Programa Minha Casa Minha Vida",
        contact=openapi.Contact(email="contato@habitacao.gov.br"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'beneficiaries', beneficiary.BeneficiaryViewSet, basename='beneficiary')
# Adicionar outros viewsets aqui...

urlpatterns = [
    # Swagger/OpenAPI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Auth
    path('auth/login', auth.login, name='auth-login'),
    path('auth/refresh', auth.refresh_token, name='auth-refresh'),
    path('me', auth.get_me, name='auth-me'),

    # Routers
    path('', include(router.urls)),
]
```

#### core/urls.py (atualizar)
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('habitacao.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Comandos para Testar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Executar migrations
```bash
python3 manage.py migrate
```

### 3. Criar superusuário
```bash
python3 manage.py createsuperuser
```

### 4. Rodar servidor
```bash
python3 manage.py runserver
```

### 5. Acessar Swagger
```
http://localhost:8000/api/v1/swagger/
```

## Exemplos de Requisições

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "senha123"
  }'
```

### Listar Beneficiários
```bash
curl -X GET http://localhost:8000/api/v1/beneficiaries/ \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

### Criar Beneficiário
```bash
curl -X POST http://localhost:8000/api/v1/beneficiaries/ \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "João da Silva",
    "cpf": "111.444.777-35",
    "phones": {
      "primary": "(11) 99999-9999"
    },
    "address": {
      "line": "Rua Exemplo",
      "number": "123",
      "municipality_id": 1,
      "uf": "SP",
      "cep": "01234-567"
    },
    "economy": {
      "gross_family_income": 2500.00
    },
    "family": {
      "family_size": 4
    },
    "housing": {
      "pays_rent": true,
      "rent_value": 800.00
    }
  }'
```

## Próximos Arquivos a Implementar

1. ✅ `utils/response.py` - Padronização de respostas
2. ✅ `utils/pagination.py` - Paginação customizada
3. ✅ `services/auth.py` - Lógica de autenticação
4. ✅ `services/beneficiary.py` - Lógica de beneficiários
5. ✅ `services/workflow.py` - Lógica de workflow
6. ⚠️ `services/document.py` - Upload e validação de documentos
7. ⚠️ `services/dashboard.py` - Dados do dashboard
8. ⚠️ `services/report.py` - Geração de relatórios
9. ⚠️ `views/document.py` - Views de documentos
10. ⚠️ `views/dashboard.py` - Views do dashboard
11. ⚠️ `views/public.py` - Consulta pública
12. ⚠️ `api/urls.py` - Configuração de rotas

## Status da Implementação

- ✅ Configuração inicial (100%)
- ✅ Serializers (100%)
- ✅ Permissions (100%)
- ✅ Exception Handler (100%)
- ⚠️ Services (30% - auth, beneficiary, workflow concluídos)
- ⚠️ Views (30% - auth, beneficiary concluídos)
- ⚠️ URLs (0%)
- ⚠️ Documentos/Upload (0%)
- ⚠️ Dashboard/Relatórios (0%)

O código acima fornece os principais arquivos e a estrutura necessária. Você pode copiar os exemplos fornecidos e criar os arquivos restantes seguindo o mesmo padrão.
