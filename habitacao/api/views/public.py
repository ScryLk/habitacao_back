"""
Views públicas (sem autenticação)
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from habitacao.api.services.public import PublicService
from habitacao.api.services.document import DocumentService
from habitacao.api.utils.response import success_response, error_response
from habitacao.api.serializers import BeneficiaryCreateSerializer, BeneficiaryDetailSerializer
from habitacao.models import Beneficiary


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('protocol', openapi.IN_QUERY, description="Número do protocolo", type=openapi.TYPE_STRING),
        openapi.Parameter('cpf', openapi.IN_QUERY, description="CPF do beneficiário", type=openapi.TYPE_STRING),
    ],
    responses={
        200: 'Status da inscrição',
        404: 'Inscrição não encontrada'
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def public_status(request):
    """
    GET /api/v1/public/status?protocol=XXXX-XX-XXXXXX
    ou
    GET /api/v1/public/status?cpf=000.000.000-00

    Consulta pública de status de inscrição
    """
    protocol = request.query_params.get('protocol')
    cpf = request.query_params.get('cpf')

    if not protocol and not cpf:
        return error_response(
            "Informe o protocolo ou CPF para consulta",
            code="VALIDATION_ERROR"
        )

    try:
        result = PublicService.get_status_by_protocol_or_cpf(
            protocol=protocol,
            cpf=cpf
        )

        if not result:
            return error_response(
                "Inscrição não encontrada",
                code="NOT_FOUND",
                status_code=404
            )

        return success_response(result)

    except ValueError as e:
        return error_response(str(e), code="VALIDATION_ERROR")


@swagger_auto_schema(
    method='post',
    request_body=BeneficiaryCreateSerializer,
    responses={
        201: BeneficiaryDetailSerializer,
        400: 'Erro de validação'
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def public_create_beneficiary(request):
    """
    POST /api/v1/public/beneficiaries

    Endpoint público para cadastro de beneficiários (sem autenticação).
    Permite que cidadãos se inscrevam diretamente no programa.
    """
    serializer = BeneficiaryCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return error_response(
            serializer.errors,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        beneficiary = serializer.save()
        result_serializer = BeneficiaryDetailSerializer(beneficiary, context={'request': request})
        return success_response(
            result_serializer.data,
            status_code=status.HTTP_201_CREATED
        )
    except ValueError as e:
        return error_response(
            str(e),
            code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return error_response(
            f"Erro ao criar beneficiário: {str(e)}",
            code="SERVER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('beneficiary_id', openapi.IN_FORM, description="ID do beneficiário", type=openapi.TYPE_INTEGER, required=True),
        openapi.Parameter('document_type_id', openapi.IN_FORM, description="ID do tipo de documento", type=openapi.TYPE_INTEGER, required=True),
        openapi.Parameter('file', openapi.IN_FORM, description="Arquivo do documento", type=openapi.TYPE_FILE, required=True),
        openapi.Parameter('notes', openapi.IN_FORM, description="Observações sobre o documento", type=openapi.TYPE_STRING, required=False),
    ],
    responses={
        201: 'Documento enviado com sucesso',
        400: 'Erro de validação',
        404: 'Beneficiário não encontrado'
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def public_upload_document(request):
    """
    POST /api/v1/public/documents

    Endpoint público para upload de documentos de beneficiários (sem autenticação).
    Permite que cidadãos anexem documentos aos seus cadastros.
    """
    beneficiary_id = request.data.get('beneficiary_id')
    document_type_id = request.data.get('document_type_id')
    file = request.FILES.get('file')
    notes = request.data.get('notes', '')

    # Validações básicas
    if not beneficiary_id:
        return error_response(
            "ID do beneficiário é obrigatório",
            code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if not document_type_id:
        return error_response(
            "ID do tipo de documento é obrigatório",
            code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if not file:
        return error_response(
            "Arquivo é obrigatório",
            code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Verificar se o beneficiário existe
        try:
            beneficiary = Beneficiary.objects.get(id=beneficiary_id)
        except Beneficiary.DoesNotExist:
            return error_response(
                "Beneficiário não encontrado",
                code="NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Fazer upload do documento
        document = DocumentService.upload(
            beneficiary_id=int(beneficiary_id),
            file=file,
            document_type_id=int(document_type_id),
            user=None  # Sem usuário autenticado no modo público
        )

        return success_response(
            {
                'id': document.id,
                'beneficiary_id': document.beneficiary_id,
                'document_type_id': document.document_type_id,
                'file_name': document.file_name,
                'file_size': document.size_bytes,
                'uploaded_at': document.uploaded_at.isoformat(),
            },
            status_code=status.HTTP_201_CREATED
        )

    except ValueError as e:
        import traceback
        print("❌ ValueError no upload de documento:")
        print(traceback.format_exc())
        return error_response(
            str(e),
            code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        import traceback
        print("❌ Exception no upload de documento:")
        print(traceback.format_exc())
        return error_response(
            f"Erro ao fazer upload do documento: {str(e)}",
            code="SERVER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
