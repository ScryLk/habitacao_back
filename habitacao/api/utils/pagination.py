"""
Paginação customizada
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginação padrão com formato customizado
    """
    page_size = 25
    page_size_query_param = 'per_page'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Retorna resposta paginada no formato padrão:
        {
            "data": [...],
            "error": null,
            "meta": {
                "page": 1,
                "per_page": 25,
                "total": 123,
                "total_pages": 5
            }
        }
        """
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
