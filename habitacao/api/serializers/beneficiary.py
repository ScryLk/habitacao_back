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
    marital_status_display = serializers.CharField(source='get_marital_status_display', read_only=True)
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Beneficiary
        fields = [
            # === IDs e Protocolo ===
            'id',
            'protocol_number',
            'status',
            'status_display',

            # === Dados Pessoais ===
            'full_name',
            'cpf',
            'rg',
            'birth_date',
            'marital_status',
            'marital_status_display',
            'age',

            # === Contatos ===
            'phone_primary',
            'email',

            # === Localização ===
            'municipality',
            'municipality_name',
            'uf',

            # === Datas ===
            'submitted_at',
            'created_at',
            'updated_at'
        ]


class BeneficiaryDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes do beneficiário"""
    municipality_data = MunicipalitySerializer(source='municipality', read_only=True)
    municipality_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    marital_status_display = serializers.CharField(source='get_marital_status_display', read_only=True)
    household_head_gender_display = serializers.CharField(source='get_household_head_gender_display', read_only=True)
    age = serializers.IntegerField(read_only=True)

    def get_municipality_name(self, obj):
        """Retorna nome do município a partir da relação ou do campo de texto"""
        if obj.municipality:
            return obj.municipality.name
        # Retorna o campo municipality_name se não estiver vazio
        name = getattr(obj, 'municipality_name', None)
        return name if name else None

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
        fields = [
            # === IDs e Protocolo ===
            'id',
            'protocol_number',
            'status',
            'status_display',

            # === Dados Pessoais ===
            'full_name',
            'cpf',
            'rg',
            'birth_date',
            'age',
            'marital_status',
            'marital_status_display',

            # === Contatos ===
            'phone_primary',
            'phone_secondary',
            'email',

            # === Endereço ===
            'address_line',
            'address_number',
            'address_complement',
            'neighborhood',
            'municipality',
            'municipality_data',
            'municipality_name',
            'cep',
            'uf',

            # === Cônjuge ===
            'spouse_name',
            'spouse_rg',
            'spouse_birth_date',

            # === Econômico / CadÚnico ===
            'main_occupation',
            'gross_family_income',
            'has_cadunico',
            'nis_number',

            # === Composição Familiar ===
            'family_size',
            'has_elderly',
            'elderly_count',
            'has_children',
            'children_count',
            'has_disability_or_tea',
            'disability_or_tea_count',
            'household_head_gender',
            'household_head_gender_display',
            'family_in_cadunico_updated',

            # === Situação Habitacional ===
            'no_own_house',
            'precarious_own_house',
            'cohabitation',
            'improvised_dwelling',
            'pays_rent',
            'rent_value',
            'other_housing_desc',

            # === Documentação Apresentada (Booleans) ===
            'has_rg_cpf',
            'has_birth_certificate',
            'has_address_proof',
            'has_income_proof',
            'has_cadunico_number',

            # === Observações ===
            'notes',

            # === Relacionamentos ===
            'priorities',
            'social_benefits',
            'documents',
            'action_history',

            # === Datas e Auditoria ===
            'created_at',
            'updated_at',
            'submitted_at',
            'submitted_by',
            'submitted_by_name',
            'last_review_at',
            'last_reviewed_by',
            'last_reviewed_by_name',
        ]
        read_only_fields = [
            'protocol_number', 'created_at', 'updated_at',
            'submitted_at', 'submitted_by', 'last_review_at', 'last_reviewed_by'
        ]


class BeneficiaryCreateSerializer(serializers.Serializer):
    """Serializer para criação de beneficiário (aceita dados aninhados OU flat)"""

    # Dados pessoais
    full_name = serializers.CharField(max_length=160)
    cpf = serializers.CharField(max_length=14)
    rg = serializers.CharField(max_length=32, required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    marital_status = serializers.CharField(max_length=20, required=False, allow_blank=True)

    # Contatos (aninhado OU flat)
    phones = serializers.DictField(required=False, child=serializers.CharField(allow_blank=True))
    phone_primary = serializers.CharField(max_length=20, required=False, allow_blank=True)
    phone_secondary = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    # Endereço (aninhado OU flat)
    address = serializers.DictField(required=False)
    address_line = serializers.CharField(max_length=160, required=False, allow_blank=True)
    address_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address_complement = serializers.CharField(max_length=60, required=False, allow_blank=True)
    neighborhood = serializers.CharField(max_length=80, required=False, allow_blank=True)
    municipality_id = serializers.IntegerField(required=False, allow_null=True)
    municipality_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    cep = serializers.CharField(max_length=9, required=False, allow_blank=True)
    uf = serializers.CharField(max_length=2, required=False, allow_blank=True)

    # Cônjuge (aninhado OU flat)
    spouse = serializers.DictField(required=False, allow_null=True)
    spouse_name = serializers.CharField(max_length=160, required=False, allow_blank=True)
    spouse_rg = serializers.CharField(max_length=32, required=False, allow_blank=True)
    spouse_birth_date = serializers.DateField(required=False, allow_null=True)

    # Econômico (aninhado OU flat)
    economy = serializers.DictField(required=False)
    main_occupation = serializers.CharField(max_length=120, required=False, allow_blank=True)
    gross_family_income = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    has_cadunico = serializers.BooleanField(required=False, default=False)
    nis_number = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)

    # Família (aninhado OU flat)
    family = serializers.DictField(required=False)
    family_size = serializers.IntegerField(required=False, default=1)
    has_elderly = serializers.BooleanField(required=False, default=False)
    elderly_count = serializers.IntegerField(required=False, default=0)
    has_children = serializers.BooleanField(required=False, default=False)
    children_count = serializers.IntegerField(required=False, default=0)
    has_disability_or_tea = serializers.BooleanField(required=False, default=False)
    disability_or_tea_count = serializers.IntegerField(required=False, default=0)
    household_head_gender = serializers.CharField(max_length=20, required=False, allow_blank=True)
    family_in_cadunico_updated = serializers.BooleanField(required=False, default=False)

    # Habitação (aninhado OU flat)
    housing = serializers.DictField(required=False)
    no_own_house = serializers.BooleanField(required=False, default=False)
    precarious_own_house = serializers.BooleanField(required=False, default=False)
    cohabitation = serializers.BooleanField(required=False, default=False)
    improvised_dwelling = serializers.BooleanField(required=False, default=False)
    pays_rent = serializers.BooleanField(required=False, default=False)
    rent_value = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    other_housing_desc = serializers.CharField(max_length=200, required=False, allow_blank=True)

    # Documentação Apresentada (apenas flat)
    has_rg_cpf = serializers.BooleanField(required=False, default=False)
    has_birth_certificate = serializers.BooleanField(required=False, default=False)
    has_address_proof = serializers.BooleanField(required=False, default=False)
    has_income_proof = serializers.BooleanField(required=False, default=False)
    has_cadunico_number = serializers.BooleanField(required=False, default=False)

    # Observações
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_cpf(self, value):
        """Valida unicidade do CPF"""
        if Beneficiary.objects.filter(cpf=value).exists():
            raise serializers.ValidationError("Este CPF já está cadastrado.")
        return value

    def create(self, validated_data):
        """Cria beneficiário a partir dos dados aninhados OU flat"""
        from habitacao.api.services.beneficiary import BeneficiaryService

        # Detecta se é estrutura aninhada ou flat
        # Se tiver campos 'phones', 'address', 'economy', etc., é aninhada
        is_nested = any(key in validated_data for key in ['phones', 'address', 'economy', 'family', 'housing'])

        if is_nested:
            # Usa o método original para dados aninhados
            return BeneficiaryService.create_from_nested_data(validated_data)
        else:
            # Usa o novo método para dados flat
            return BeneficiaryService.create_from_flat_data(validated_data)


class BeneficiaryUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização parcial de beneficiário"""

    class Meta:
        model = Beneficiary
        exclude = [
            'protocol_number', 'created_at', 'updated_at',
            'submitted_at', 'submitted_by',
            'last_review_at', 'last_reviewed_by'
        ]

    def validate_nis_number(self, value):
        """
        Garante que NIS vazio seja convertido para None
        Evita IntegrityError no banco de dados
        """
        if value is not None and isinstance(value, str) and value.strip() == '':
            return None
        return value

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
