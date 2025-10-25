"""
Views públicas (sem autenticação)
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from habitacao.api.services.public import PublicService
from habitacao.api.utils.response import success_response, error_response


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
