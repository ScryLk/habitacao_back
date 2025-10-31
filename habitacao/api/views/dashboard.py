"""
Views de dashboard e estatísticas
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from habitacao.api.services.dashboard import DashboardService
from habitacao.api.permissions.roles import IsAnalyst
from habitacao.api.utils.response import success_response


@swagger_auto_schema(
    method='get',
    responses={200: 'Estatísticas do dashboard'}
)
@api_view(['GET'])
@permission_classes([IsAnalyst])
def dashboard_overview(request):
    """
    GET /api/v1/dashboard
    Retorna visão geral do sistema
    """
    data = DashboardService.get_overview(request.user)
    return success_response(data)


@swagger_auto_schema(
    method='get',
    responses={200: 'Estatísticas por município'}
)
@api_view(['GET'])
@permission_classes([IsAnalyst])
def municipality_statistics(request):
    """
    GET /api/v1/dashboard/municipality/{id}
    Estatísticas por município
    """
    municipality_id = request.query_params.get('municipality_id')
    data = DashboardService.get_statistics_by_municipality(municipality_id)
    return success_response(data)


@swagger_auto_schema(
    method='get',
    responses={200: 'Atribuições do usuário'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_assignments(request):
    """
    GET /api/v1/dashboard/my-assignments
    Retorna atribuições do usuário logado
    """
    data = DashboardService.get_user_assignments(request.user)
    return success_response(data)
