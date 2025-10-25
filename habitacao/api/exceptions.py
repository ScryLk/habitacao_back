"""
Custom exception handler para padronizar respostas de erro
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError


def custom_exception_handler(exc, context):
    """
    Padroniza o formato de erro:
    {
        "data": null,
        "error": {
            "code": "ERROR_CODE",
            "message": "Mensagem principal",
            "details": {}
        }
    }
    """
    # Chama o handler padrão do DRF primeiro
    response = exception_handler(exc, context)

    if response is not None:
        # Formata a resposta de erro
        error_response = {
            "data": null,
            "error": {
                "code": get_error_code(exc),
                "message": get_error_message(exc, response.data),
                "details": response.data if isinstance(response.data, dict) else {"detail": response.data}
            }
        }
        response.data = error_response
    else:
        # Trata exceções Django não tratadas pelo DRF
        if isinstance(exc, DjangoValidationError):
            error_response = {
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Erro de validação",
                    "details": {"validation_errors": exc.messages}
                }
            }
            response = Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    return response


def get_error_code(exc):
    """Determina o código de erro baseado no tipo de exceção"""
    exc_class = exc.__class__.__name__

    error_codes = {
        'ValidationError': 'VALIDATION_ERROR',
        'PermissionDenied': 'PERMISSION_DENIED',
        'NotAuthenticated': 'NOT_AUTHENTICATED',
        'AuthenticationFailed': 'AUTHENTICATION_FAILED',
        'NotFound': 'NOT_FOUND',
        'MethodNotAllowed': 'METHOD_NOT_ALLOWED',
        'Throttled': 'TOO_MANY_REQUESTS',
    }

    return error_codes.get(exc_class, 'ERROR')


def get_error_message(exc, data):
    """Extrai a mensagem de erro principal"""
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, dict):
            # Pega a primeira mensagem de erro
            first_key = list(exc.detail.keys())[0]
            first_value = exc.detail[first_key]
            if isinstance(first_value, list):
                return str(first_value[0])
            return str(first_value)
        return str(exc.detail)

    return str(exc)


class WorkflowException(Exception):
    """Exceção customizada para erros de workflow"""
    def __init__(self, message, code="WORKFLOW_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class DocumentException(Exception):
    """Exceção customizada para erros de documentos"""
    def __init__(self, message, code="DOCUMENT_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)
