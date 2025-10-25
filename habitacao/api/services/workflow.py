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
        DRAFT → SUBMITTED
        Gera protocolo e valida documentos
        """
        beneficiary = Beneficiary.objects.select_for_update().get(id=beneficiary_id)

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
        beneficiary.save()  # O save() gera o protocol_number automaticamente

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
        SUBMITTED → UNDER_REVIEW
        Cria assignment ativo para o analista
        """
        beneficiary = Beneficiary.objects.select_for_update().get(id=beneficiary_id)

        if beneficiary.status != ApplicationStatus.SUBMITTED:
            raise ValueError("Apenas inscrições submetidas podem entrar em análise")

        # Atualiza status
        old_status = beneficiary.status
        beneficiary.status = ApplicationStatus.UNDER_REVIEW
        beneficiary.last_review_at = timezone.now()
        beneficiary.last_reviewed_by = user
        beneficiary.save()

        # Cria assignment ativo
        # Encerra assignments anteriores
        ApplicationAssignment.objects.filter(
            beneficiary=beneficiary,
            active=True
        ).update(active=False)

        # Cria novo
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
        """
        Solicita correções
        UNDER_REVIEW → CORRECTION_REQUESTED
        """
        beneficiary = Beneficiary.objects.select_for_update().get(id=beneficiary_id)

        if beneficiary.status != ApplicationStatus.UNDER_REVIEW:
            raise ValueError("Apenas inscrições em análise podem solicitar correção")

        if not message:
            raise ValueError("Mensagem de solicitação é obrigatória")

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
        """
        Aprova inscrição
        UNDER_REVIEW → APPROVED
        """
        beneficiary = Beneficiary.objects.select_for_update().get(id=beneficiary_id)

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
        """
        Rejeita inscrição
        UNDER_REVIEW → REJECTED
        """
        beneficiary = Beneficiary.objects.select_for_update().get(id=beneficiary_id)

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
