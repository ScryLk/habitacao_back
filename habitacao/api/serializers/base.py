"""
Serializers base e utilitários
"""
from rest_framework import serializers
from habitacao.models import Municipality, PriorityCriteria, SocialBenefitType, DocumentType


class MunicipalitySerializer(serializers.ModelSerializer):
    """Serializer para municípios"""
    class Meta:
        model = Municipality
        fields = ['id', 'ibge_code', 'name', 'uf']


class PriorityCriteriaSerializer(serializers.ModelSerializer):
    """Serializer para critérios de priorização"""
    class Meta:
        model = PriorityCriteria
        fields = ['id', 'code', 'label', 'group_tag', 'active']


class SocialBenefitTypeSerializer(serializers.ModelSerializer):
    """Serializer para tipos de benefícios sociais"""
    class Meta:
        model = SocialBenefitType
        fields = ['id', 'code', 'label', 'active']


class DocumentTypeSerializer(serializers.ModelSerializer):
    """Serializer para tipos de documentos"""
    class Meta:
        model = DocumentType
        fields = ['id', 'code', 'label', 'required', 'active']
