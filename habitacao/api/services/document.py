"""
Serviço de documentos
"""
from django.db import transaction
from django.utils import timezone
from django.core.files.storage import default_storage
from habitacao.models import BeneficiaryDocument, DocumentType, Beneficiary
from habitacao.choices import ApplicationAction as ActionType
from habitacao.models import ApplicationActionHistory
import os


class DocumentService:
    """Serviço de gerenciamento de documentos"""

    @staticmethod
    def list_types():
        """Lista tipos de documentos ativos"""
        return DocumentType.objects.filter(active=True).order_by('label')

    @staticmethod
    def list_by_beneficiary(beneficiary_id):
        """Lista documentos de um beneficiário"""
        return BeneficiaryDocument.objects.filter(
            beneficiary_id=beneficiary_id
        ).select_related('document_type', 'uploaded_by', 'validated_by').order_by('-uploaded_at')

    @staticmethod
    @transaction.atomic
    def upload(beneficiary_id, file, document_type_id, user=None):
        """
        Upload de documento
        """
        # Valida beneficiário
        beneficiary = Beneficiary.objects.get(id=beneficiary_id)

        # Valida tipo de documento
        document_type = DocumentType.objects.get(id=document_type_id)

        # Valida arquivo
        if not file:
            raise ValueError("Arquivo não fornecido")

        # Extrai informações do arquivo
        file_name = file.name
        mime_type = file.content_type if hasattr(file, 'content_type') else 'application/octet-stream'
        size_bytes = file.size

        # Cria documento
        document = BeneficiaryDocument.objects.create(
            beneficiary=beneficiary,
            document_type=document_type,
            file_name=file_name,
            file_path=file,  # Django cuida do upload via FileField
            mime_type=mime_type,
            size_bytes=size_bytes,
            uploaded_by=user  # Pode ser None em uploads públicos
        )

        # Registra ação (apenas se houver usuário autenticado)
        if user:
            ApplicationActionHistory.objects.create(
                beneficiary=beneficiary,
                action=ActionType.UPLOAD_DOC,
                from_status=beneficiary.status,
                to_status=beneficiary.status,
                message=f"Documento {document_type.label} anexado",
                created_by=user
            )

        return document

    @staticmethod
    def get_document(document_id):
        """Obtém documento por ID"""
        return BeneficiaryDocument.objects.select_related(
            'beneficiary', 'document_type', 'uploaded_by', 'validated_by'
        ).get(id=document_id)

    @staticmethod
    @transaction.atomic
    def validate_document(document_id, validated, notes, user):
        """
        Valida ou invalida documento
        """
        document = BeneficiaryDocument.objects.get(id=document_id)

        document.validated = validated
        document.validated_at = timezone.now()
        document.validated_by = user
        if notes:
            document.notes = notes
        document.save()

        # Registra ação
        action_message = f"Documento {document.document_type.label} "
        action_message += "validado" if validated else "invalidado"
        if notes:
            action_message += f": {notes}"

        ApplicationActionHistory.objects.create(
            beneficiary=document.beneficiary,
            action=ActionType.VALIDATE_DOC,
            from_status=document.beneficiary.status,
            to_status=document.beneficiary.status,
            message=action_message,
            created_by=user
        )

        return document

    @staticmethod
    def delete_document(document_id, user):
        """Deleta documento"""
        document = BeneficiaryDocument.objects.get(id=document_id)

        # Deleta arquivo físico
        if document.file_path:
            try:
                default_storage.delete(document.file_path.name)
            except Exception:
                pass  # Ignora erro se arquivo não existir

        beneficiary = document.beneficiary
        document_type_label = document.document_type.label

        document.delete()

        # Registra ação
        ApplicationActionHistory.objects.create(
            beneficiary=beneficiary,
            action=ActionType.NOTE,
            from_status=beneficiary.status,
            to_status=beneficiary.status,
            message=f"Documento {document_type_label} removido",
            created_by=user
        )

        return True
