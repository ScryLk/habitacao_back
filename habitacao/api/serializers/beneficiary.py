"""
Serializers para beneficiários
"""
from rest_framework import serializers
from habitacao.models import (
    Beneficiary, BeneficiaryPriority, BeneficiarySocialBenefit,
    BeneficiaryDocument, ApplicationActionHistory
)
from habitacao.choices import ApplicationStatus
from .base import MunicipalitySerializer, PriorityCriteriaSerializer, SocialBenefitTypeSerializer
from .user import UserSerializer


class BeneficiaryPrioritySerializer(serializers.ModelSerializer):
    """Serializer para prioridades do beneficiário"""
    criteria_data = PriorityCriteriaSerializer(source='criteria', read_only=True)

    class Meta:
        model = BeneficiaryPriority
        fields = ['id', 'criteria', 'criteria_data', 'created_at']
        read_only_fields = ['created_at']


class BeneficiarySocialBenefitSerializer(serializers.ModelSerializer):
    """Serializer para benefícios sociais do beneficiário"""
    benefit_data = SocialBenefitTypeSerializer(source='benefit', read_only=True)

    class Meta:
        model = BeneficiarySocialBenefit
        fields = ['id', 'benefit', 'benefit_data', 'other_text']


class BeneficiaryDocumentSerializer(serializers.ModelSerializer):
    """Serializer para documentos do beneficiário"""
    document_type_label = serializers.CharField(source='document_type.label', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    validated_by_name = serializers.CharField(source='validated_by.get_full_name', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = BeneficiaryDocument
        fields = [
            'id', 'document_type', 'document_type_label',
            'file_name', 'file_path', 'file_url', 'mime_type', 'size_bytes',
            'uploaded_at', 'uploaded_by', 'uploaded_by_name',
            'validated', 'validated_at', 'validated_by', 'validated_by_name',
            'notes'
        ]
        read_only_fields = ['uploaded_at', 'uploaded_by', 'validated_at', 'validated_by', 'file_url']

    def get_file_url(self, obj):
        """Retorna URL completa do arquivo"""
        if obj.file_path:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file_path.url)
        return None


class ApplicationActionHistorySerializer(serializers.ModelSerializer):
    """Serializer para histórico de ações"""
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    from_status_display = serializers.CharField(source='get_from_status_display', read_only=True)
    to_status_display = serializers.CharField(source='get_to_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = ApplicationActionHistory
        fields = [
            'id', 'action', 'action_display',
            'from_status', 'from_status_display',
            'to_status', 'to_status_display',
            'message', 'created_at', 'created_by', 'created_by_name'
        ]
        read_only_fields = ['created_at']


class BeneficiaryListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de beneficiários"""
    municipality_name = serializers.CharField(source='municipality.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Beneficiary
        fields = [
            'id', 'protocol_number', 'full_name', 'cpf',
            'municipality', 'municipality_name', 'uf',
            'status', 'status_display', 'age',
            'submitted_at', 'created_at', 'updated_at'
        ]


class BeneficiaryDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes do beneficiário"""
    municipality_data = MunicipalitySerializer(source='municipality', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    marital_status_display = serializers.CharField(source='get_marital_status_display', read_only=True)
    household_head_gender_display = serializers.CharField(source='get_household_head_gender_display', read_only=True)
    age = serializers.IntegerField(read_only=True)

    # Relacionamentos
    priorities = BeneficiaryPrioritySerializer(many=True, read_only=True)
    social_benefits = BeneficiarySocialBenefitSerializer(many=True, read_only=True)
    documents = BeneficiaryDocumentSerializer(many=True, read_only=True)
    action_history = ApplicationActionHistorySerializer(many=True, read_only=True)

    # Auditoria
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    last_reviewed_by_name = serializers.CharField(source='last_reviewed_by.get_full_name', read_only=True)

    class Meta:
        model = Beneficiary
        fields = '__all__'
        read_only_fields = [
            'protocol_number', 'created_at', 'updated_at',
            'submitted_at', 'submitted_by', 'last_review_at', 'last_reviewed_by'
        ]


class BeneficiaryCreateSerializer(serializers.Serializer):
    """Serializer para criação de beneficiário com estrutura aninhada"""

    # Dados pessoais
    full_name = serializers.CharField(max_length=160)
    cpf = serializers.CharField(max_length=14)
    rg = serializers.CharField(max_length=32, required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    marital_status = serializers.CharField(max_length=20, required=False, allow_blank=True)

    # Contatos (aninhado)
    phones = serializers.DictField(required=False, child=serializers.CharField(allow_blank=True))
    email = serializers.EmailField(required=False, allow_blank=True)

    # Endereço (aninhado)
    address = serializers.DictField(required=False)

    # Cônjuge (aninhado)
    spouse = serializers.DictField(required=False, allow_null=True)

    # Econômico (aninhado)
    economy = serializers.DictField(required=False)

    # Família (aninhado)
    family = serializers.DictField(required=False)

    # Habitação (aninhado)
    housing = serializers.DictField(required=False)

    # Observações
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_cpf(self, value):
        """Valida unicidade do CPF"""
        if Beneficiary.objects.filter(cpf=value).exists():
            raise serializers.ValidationError("Este CPF já está cadastrado.")
        return value

    def create(self, validated_data):
        """Cria beneficiário a partir dos dados aninhados"""
        from habitacao.api.services.beneficiary import BeneficiaryService

        service = BeneficiaryService()
        return service.create_from_nested_data(validated_data)


class BeneficiaryUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização parcial de beneficiário"""

    class Meta:
        model = Beneficiary
        exclude = [
            'protocol_number', 'created_at', 'updated_at',
            'submitted_at', 'submitted_by',
            'last_review_at', 'last_reviewed_by'
        ]

    def validate_status(self, value):
        """Impede mudança direta de status (usar endpoints de workflow)"""
        instance = self.instance
        if instance and instance.status != value:
            raise serializers.ValidationError(
                "Use os endpoints de workflow para mudar o status."
            )
        return value


class WorkflowActionSerializer(serializers.Serializer):
    """Serializer para ações de workflow"""
    message = serializers.CharField(required=False, allow_blank=True)


class AssignBeneficiarySerializer(serializers.Serializer):
    """Serializer para atribuir beneficiário a analista"""
    assigned_to = serializers.IntegerField()

    def validate_assigned_to(self, value):
        """Valida se o usuário existe"""
        from django.contrib.auth.models import User
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Usuário não encontrado.")
        return value


class AddPrioritySerializer(serializers.Serializer):
    """Serializer para adicionar critérios de priorização"""
    criteria_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )


class AddSocialBenefitSerializer(serializers.Serializer):
    """Serializer para adicionar benefícios sociais"""
    benefit_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    other_text = serializers.CharField(required=False, allow_blank=True)
