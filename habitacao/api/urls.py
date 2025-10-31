"""
URLs da API v1
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from .views import auth, beneficiary, base, document, dashboard, public as public_views, user  # importa o novo viewset

# Schema para Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="Sistema Habitação - MCMV API",
        default_version='v1',
        description="""
        API REST para gerenciamento do Programa Minha Casa Minha Vida - Entidades (MCMV).

        ## Autenticação
        A API utiliza JWT (JSON Web Tokens) para autenticação.

        Para autenticar:
        1. POST /api/v1/auth/login com email e password
        2. Use o token retornado no header: `Authorization: Bearer <token>`

        ## Papéis de Usuário
        - **ADMIN**: Acesso total ao sistema
        - **COORDINATOR**: Gerencia analistas e visualiza todos os municípios
        - **ANALYST**: Analisa inscrições do seu município
        - **CLERK**: Cadastra beneficiários e anexa documentos

        ## Workflow de Inscrição
        1. **DRAFT** → Rascunho inicial
        2. **SUBMITTED** → Submetida para análise (gera protocolo)
        3. **UNDER_REVIEW** → Em análise por analista
        4. **CORRECTION_REQUESTED** → Correções solicitadas
        5. **APPROVED** → Aprovada
        6. **REJECTED** → Rejeitada
        """,
        contact=openapi.Contact(email="contato@habitacao.gov.br"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'beneficiaries', beneficiary.BeneficiaryViewSet, basename='beneficiary')
router.register(r'municipalities', base.MunicipalityViewSet, basename='municipality')
router.register(r'priority-criteria', base.PriorityCriteriaViewSet, basename='priority-criteria')
router.register(r'social-benefits', base.SocialBenefitTypeViewSet, basename='social-benefit')
router.register(r'document-types', base.DocumentTypeViewSet, basename='document-type')
router.register(r'documents', document.BeneficiaryDocumentViewSet, basename='document')
router.register(r'users', user.UserViewSet, basename='user')

urlpatterns = [
    # ============================================================
    # DOCUMENTATION (Swagger/OpenAPI)
    # ============================================================
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # ============================================================
    # AUTHENTICATION
    # ============================================================
    path('auth/login', auth.login, name='auth-login'),
    path('auth/refresh', auth.refresh_token, name='auth-refresh'),
    path('auth/register', auth.register, name='auth-register'),
    path('me', auth.get_me, name='auth-me'),

    # ============================================================
    # DASHBOARD & STATISTICS
    # ============================================================
    path('dashboard', dashboard.dashboard_overview, name='dashboard-overview'),
    path('dashboard/municipality', dashboard.municipality_statistics, name='dashboard-municipality'),
    path('dashboard/my-assignments', dashboard.user_assignments, name='dashboard-my-assignments'),

    # ============================================================
    # PUBLIC (NO AUTH)
    # ============================================================
    path('public/status', public_views.public_status, name='public-status'),
    path('public/beneficiaries', public_views.public_create_beneficiary, name='public-create-beneficiary'),
    path('public/documents', public_views.public_upload_document, name='public-upload-document'),

    # ============================================================
    # VIEWSETS (Router)
    # ============================================================
    path('', include(router.urls)),
]
