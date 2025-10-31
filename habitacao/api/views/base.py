"""
Views base (municípios, critérios, tipos, etc)
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from habitacao.models import Municipality, PriorityCriteria, SocialBenefitType, DocumentType
from habitacao.api.serializers import (
    MunicipalitySerializer,
    PriorityCriteriaSerializer,
    SocialBenefitTypeSerializer,
    DocumentTypeSerializer,
)
from habitacao.api.utils.response import success_response


class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para municípios (somente leitura) - Acesso público"""
    queryset = Municipality.objects.all().order_by('uf', 'name')
    serializer_class = MunicipalitySerializer
    permission_classes = [AllowAny]  # Permitir acesso público
    search_fields = ['name', 'ibge_code']
    filterset_fields = ['uf']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)


class PriorityCriteriaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para critérios de priorização (somente leitura)"""
    queryset = PriorityCriteria.objects.filter(active=True).order_by('group_tag', 'label')
    serializer_class = PriorityCriteriaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['group_tag', 'active']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)


class SocialBenefitTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para tipos de benefícios sociais (somente leitura)"""
    queryset = SocialBenefitType.objects.filter(active=True).order_by('label')
    serializer_class = SocialBenefitTypeSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)


class DocumentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para tipos de documentos (somente leitura)"""
    queryset = DocumentType.objects.filter(active=True).order_by('label')
    serializer_class = DocumentTypeSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['required']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)
