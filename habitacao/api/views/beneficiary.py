"""
Views de beneficiários
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from habitacao.models import Beneficiary
from habitacao.api.serializers import (
    BeneficiaryListSerializer,
    BeneficiaryDetailSerializer,
    BeneficiaryCreateSerializer,
    BeneficiaryUpdateSerializer,
    WorkflowActionSerializer,
    ApplicationActionHistorySerializer,
)
from habitacao.api.services.beneficiary import BeneficiaryService
from habitacao.api.services.workflow import WorkflowService
from habitacao.api.permissions.roles import IsAnalyst, IsClerkOrHigher, IsMunicipalityScoped
from habitacao.api.utils.response import success_response, error_response
from habitacao.api.utils.pagination import StandardResultsSetPagination
from habitacao.api.utils.filters import BeneficiaryFilter


class BeneficiaryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para beneficiários (CRUD completo + workflow)
    """
    queryset = Beneficiary.objects.all()
    permission_classes = [IsAuthenticated, IsMunicipalityScoped]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BeneficiaryFilter
    search_fields = ['full_name', 'cpf', 'protocol_number', 'email']
    ordering_fields = ['created_at', 'submitted_at', 'full_name', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return BeneficiaryListSerializer
        elif self.action == 'create':
            return BeneficiaryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BeneficiaryUpdateSerializer
        return BeneficiaryDetailSerializer

    def get_queryset(self):
        """Aplica escopo de município"""
        service = BeneficiaryService()
        return service.list(user=self.request.user)

    def get_permissions(self):
        """Permissões específicas por action"""
        if self.action == 'create':
            return [IsClerkOrHigher(), IsMunicipalityScoped()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAnalyst(), IsMunicipalityScoped()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """POST /api/v1/beneficiaries/ - Cria beneficiário"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            beneficiary = serializer.save()
            result_serializer = BeneficiaryDetailSerializer(beneficiary, context={'request': request})
            return success_response(result_serializer.data, status_code=status.HTTP_201_CREATED)
        except ValueError as e:
            return error_response(str(e), code="VALIDATION_ERROR")

    def update(self, request, *args, **kwargs):
        """PUT/PATCH /api/v1/beneficiaries/{id}/ - Atualiza beneficiário"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            beneficiary = BeneficiaryService.update(
                instance.id,
                serializer.validated_data,
                request.user
            )
            result_serializer = BeneficiaryDetailSerializer(beneficiary, context={'request': request})
            return success_response(result_serializer.data)
        except ValueError as e:
            return error_response(str(e), code="VALIDATION_ERROR")

    def list(self, request, *args, **kwargs):
        """GET /api/v1/beneficiaries/ - Lista beneficiários"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """GET /api/v1/beneficiaries/{id}/ - Detalhes do beneficiário"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)

    # ============================================================
    # WORKFLOW ACTIONS
    # ============================================================

    @swagger_auto_schema(
        method='post',
        responses={200: BeneficiaryDetailSerializer, 400: 'Erro de workflow'}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAnalyst])
    def submit(self, request, pk=None):
        """POST /api/v1/beneficiaries/{id}/submit - Submete inscrição"""
        try:
            beneficiary = WorkflowService.submit(pk, request.user)
            serializer = BeneficiaryDetailSerializer(beneficiary, context={'request': request})
            return success_response(serializer.data)
        except ValueError as e:
            return error_response(str(e), code="WORKFLOW_ERROR")
        except Beneficiary.DoesNotExist:
            return error_response("Beneficiário não encontrado", code="NOT_FOUND", status_code=404)

    @swagger_auto_schema(
        method='post',
        responses={200: BeneficiaryDetailSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAnalyst], url_path='start-review')
    def start_review(self, request, pk=None):
        """POST /api/v1/beneficiaries/{id}/start-review - Inicia análise"""
        try:
            beneficiary = WorkflowService.start_review(pk, request.user)
            serializer = BeneficiaryDetailSerializer(beneficiary, context={'request': request})
            return success_response(serializer.data)
        except ValueError as e:
            return error_response(str(e), code="WORKFLOW_ERROR")
        except Beneficiary.DoesNotExist:
            return error_response("Beneficiário não encontrado", code="NOT_FOUND", status_code=404)

    @swagger_auto_schema(
        method='post',
        request_body=WorkflowActionSerializer,
        responses={200: BeneficiaryDetailSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAnalyst], url_path='request-correction')
    def request_correction(self, request, pk=None):
        """POST /api/v1/beneficiaries/{id}/request-correction - Solicita correções"""
        serializer = WorkflowActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            beneficiary = WorkflowService.request_correction(
                pk,
                request.user,
                serializer.validated_data.get('message', '')
            )
            result_serializer = BeneficiaryDetailSerializer(beneficiary, context={'request': request})
            return success_response(result_serializer.data)
        except ValueError as e:
            return error_response(str(e), code="WORKFLOW_ERROR")
        except Beneficiary.DoesNotExist:
            return error_response("Beneficiário não encontrado", code="NOT_FOUND", status_code=404)

    @swagger_auto_schema(
        method='post',
        request_body=WorkflowActionSerializer,
        responses={200: BeneficiaryDetailSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAnalyst])
    def approve(self, request, pk=None):
        """POST /api/v1/beneficiaries/{id}/approve - Aprova inscrição"""
        serializer = WorkflowActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            beneficiary = WorkflowService.approve(
                pk,
                request.user,
                serializer.validated_data.get('message')
            )
            result_serializer = BeneficiaryDetailSerializer(beneficiary, context={'request': request})
            return success_response(result_serializer.data)
        except ValueError as e:
            return error_response(str(e), code="WORKFLOW_ERROR")
        except Beneficiary.DoesNotExist:
            return error_response("Beneficiário não encontrado", code="NOT_FOUND", status_code=404)

    @swagger_auto_schema(
        method='post',
        request_body=WorkflowActionSerializer,
        responses={200: BeneficiaryDetailSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAnalyst])
    def reject(self, request, pk=None):
        """POST /api/v1/beneficiaries/{id}/reject - Rejeita inscrição"""
        serializer = WorkflowActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data.get('message')
        if not message:
            return error_response(
                "Mensagem de justificativa é obrigatória",
                code="VALIDATION_ERROR"
            )

        try:
            beneficiary = WorkflowService.reject(pk, request.user, message)
            result_serializer = BeneficiaryDetailSerializer(beneficiary, context={'request': request})
            return success_response(result_serializer.data)
        except ValueError as e:
            return error_response(str(e), code="WORKFLOW_ERROR")
        except Beneficiary.DoesNotExist:
            return error_response("Beneficiário não encontrado", code="NOT_FOUND", status_code=404)

    @swagger_auto_schema(
        method='get',
        responses={200: ApplicationActionHistorySerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='actions')
    def get_actions(self, request, pk=None):
        """GET /api/v1/beneficiaries/{id}/actions - Lista histórico de ações"""
        beneficiary = self.get_object()
        actions = beneficiary.action_history.select_related('created_by').order_by('-created_at')
        serializer = ApplicationActionHistorySerializer(actions, many=True)
        return success_response(serializer.data)

    @swagger_auto_schema(
        method='post',
        request_body=WorkflowActionSerializer,
        responses={200: 'Nota adicionada'}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAnalyst], url_path='actions/note')
    def add_note(self, request, pk=None):
        """POST /api/v1/beneficiaries/{id}/actions/note - Adiciona observação interna"""
        from habitacao.models import ApplicationActionHistory
        from habitacao.choices import ApplicationAction as ActionType

        serializer = WorkflowActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data.get('message')
        if not message:
            return error_response("Mensagem é obrigatória", code="VALIDATION_ERROR")

        try:
            beneficiary = self.get_object()

            action = ApplicationActionHistory.objects.create(
                beneficiary=beneficiary,
                action=ActionType.NOTE,
                from_status=beneficiary.status,
                to_status=beneficiary.status,
                message=message,
                created_by=request.user
            )

            action_serializer = ApplicationActionHistorySerializer(action)
            return success_response(action_serializer.data)
        except Beneficiary.DoesNotExist:
            return error_response("Beneficiário não encontrado", code="NOT_FOUND", status_code=404)
