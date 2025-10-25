"""
Padronização de respostas da API
"""
from rest_framework.response import Response
from rest_framework import status


def success_response(data, meta=None, status_code=status.HTTP_200_OK):
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

    return Response(response_data, status=status_code)


def error_response(message, code="ERROR", details=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Resposta de erro padrão
    {
        "data": null,
        "error": {
            "code": "ERROR_CODE",
            "message": "...",
            "details": {}
        }
    }
    """
    response_data = {
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details or {}
        }
    }

    return Response(response_data, status=status_code)
