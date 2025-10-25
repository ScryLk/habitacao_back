"""
Views de documentos
"""
from rest_framework import viewsets, status as http_status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import FileResponse, Http404

from habitacao.models import BeneficiaryDocument
from habitacao.api.serializers import BeneficiaryDocumentSerializer
from habitacao.api.services.document import DocumentService
from habitacao.api.permissions.roles import IsAnalyst, IsClerkOrHigher
from habitacao.api.utils.response import success_response, error_response


class BeneficiaryDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet para documentos dos beneficiários"""
    queryset = BeneficiaryDocument.objects.all()
    serializer_class = BeneficiaryDocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Filtra por beneficiário se fornecido"""
        queryset = super().get_queryset()
        beneficiary_id = self.request.query_params.get('beneficiary_id')

        if beneficiary_id:
            queryset = queryset.filter(beneficiary_id=beneficiary_id)

        return queryset.select_related('document_type', 'uploaded_by', 'validated_by')

    def get_permissions(self):
        """Permissões específicas por action"""
        if self.action == 'create':
            return [IsClerkOrHigher()]
        elif self.action in ['validate']:
            return [IsAnalyst()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """
        POST /api/v1/documents/
        Upload de documento (multipart/form-data)
        Campos: beneficiary_id, document_type_id, file
        """
        beneficiary_id = request.data.get('beneficiary_id')
        document_type_id = request.data.get('document_type_id')
        file = request.FILES.get('file')

        if not all([beneficiary_id, document_type_id, file]):
            return error_response(
                "Campos obrigatórios: beneficiary_id, document_type_id, file",
                code="VALIDATION_ERROR"
            )

        try:
            document = DocumentService.upload(
                beneficiary_id=beneficiary_id,
                file=file,
                document_type_id=document_type_id,
                user=request.user
            )

            serializer = self.get_serializer(document)
            return success_response(serializer.data, status_code=http_status.HTTP_201_CREATED)

        except ValueError as e:
            return error_response(str(e), code="UPLOAD_ERROR")
        except Exception as e:
            return error_response(
                f"Erro ao fazer upload: {str(e)}",
                code="UPLOAD_ERROR",
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request, *args, **kwargs):
        """GET /api/v1/documents/ - Lista documentos"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """GET /api/v1/documents/{id}/ - Detalhes do documento"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        """GET /api/v1/documents/{id}/download - Baixa arquivo"""
        try:
            document = self.get_object()

            if not document.file_path:
                raise Http404("Arquivo não encontrado")

            return FileResponse(
                document.file_path.open('rb'),
                as_attachment=True,
                filename=document.file_name
            )

        except Http404:
            return error_response(
                "Arquivo não encontrado",
                code="NOT_FOUND",
                status_code=http_status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['patch'], permission_classes=[IsAnalyst], url_path='validate')
    def validate(self, request, pk=None):
        """
        PATCH /api/v1/documents/{id}/validate
        Valida ou invalida documento
        Body: { "validated": true/false, "notes": "..." }
        """
        validated = request.data.get('validated')
        notes = request.data.get('notes', '')

        if validated is None:
            return error_response(
                "Campo 'validated' é obrigatório",
                code="VALIDATION_ERROR"
            )

        try:
            document = DocumentService.validate_document(
                document_id=pk,
                validated=validated,
                notes=notes,
                user=request.user
            )

            serializer = self.get_serializer(document)
            return success_response(serializer.data)

        except ValueError as e:
            return error_response(str(e), code="VALIDATION_ERROR")
        except BeneficiaryDocument.DoesNotExist:
            return error_response(
                "Documento não encontrado",
                code="NOT_FOUND",
                status_code=http_status.HTTP_404_NOT_FOUND
            )
