"""
Models para o Programa Minha Casa Minha Vida - Entidades (MCMV)
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from .validators import validate_cpf, validate_nis, validate_cep, validate_phone, validate_positive_income
from .choices import ApplicationStatus, UserRole, MaritalStatus, Gender, UF, ApplicationAction
import uuid


# ============================================================
# MODELS BASE
# ============================================================

class Municipality(models.Model):
    """Municípios brasileiros"""
    ibge_code = models.CharField(max_length=7, unique=True, verbose_name='Código IBGE')
    name = models.CharField(max_length=120, verbose_name='Nome')
    uf = models.CharField(max_length=2, choices=UF.choices, verbose_name='UF')

    class Meta:
        db_table = 'municipalities'
        verbose_name = 'Município'
        verbose_name_plural = 'Municípios'
        ordering = ['uf', 'name']
        indexes = [
            models.Index(fields=['uf', 'name']),
        ]

    def __str__(self):
        return f"{self.name}/{self.uf}"


class PriorityCriteria(models.Model):
    """Critérios de priorização para beneficiários"""
    code = models.CharField(max_length=40, unique=True, verbose_name='Código')
    label = models.CharField(max_length=160, verbose_name='Descrição')
    group_tag = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        verbose_name='Grupo',
        help_text='Ex: social, saúde, vulnerabilidade'
    )
    active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        db_table = 'priority_criteria'
        verbose_name = 'Critério de Priorização'
        verbose_name_plural = 'Critérios de Priorização'
        ordering = ['group_tag', 'label']

    def __str__(self):
        return self.label


class SocialBenefitType(models.Model):
    """Tipos de benefícios sociais"""
    code = models.CharField(max_length=40, unique=True, verbose_name='Código')
    label = models.CharField(max_length=120, verbose_name='Descrição')
    active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        db_table = 'social_benefit_types'
        verbose_name = 'Tipo de Benefício Social'
        verbose_name_plural = 'Tipos de Benefícios Sociais'
        ordering = ['label']

    def __str__(self):
        return self.label


class DocumentType(models.Model):
    """Tipos de documentos para upload"""
    code = models.CharField(max_length=40, unique=True, verbose_name='Código')
    label = models.CharField(max_length=120, verbose_name='Descrição')
    required = models.BooleanField(default=False, verbose_name='Obrigatório')
    active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        db_table = 'document_types'
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documentos'
        ordering = ['label']

    def __str__(self):
        return self.label


# ============================================================
# USUÁRIOS E PERFIS
# ============================================================

class UserProfile(models.Model):
    """Perfil estendido do usuário Django"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cpf = models.CharField(max_length=14, unique=True, validators=[validate_cpf], verbose_name='CPF')
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.ANALYST,
        verbose_name='Papel'
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Município de Atuação',
        help_text='Escopo de atuação do usuário, se aplicável'
    )
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='Último login')

    class Meta:
        db_table = 'users'
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['municipality']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"


# ============================================================
# BENEFICIÁRIOS (MODEL PRINCIPAL)
# ============================================================

class Beneficiary(models.Model):
    """Beneficiário do Programa MCMV"""

    # Protocolo e controle
    protocol_number = models.CharField(
        max_length=32,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Número de Protocolo',
        help_text='Gerado automaticamente ao submeter (ex: AAAA-MM-XXXXXX)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    # Dados pessoais
    full_name = models.CharField(max_length=160, verbose_name='Nome Completo')
    cpf = models.CharField(
        max_length=14,
        unique=True,
        validators=[validate_cpf],
        verbose_name='CPF',
        help_text='Formato: 000.000.000-00'
    )
    rg = models.CharField(max_length=32, blank=True, verbose_name='RG')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento')
    marital_status = models.CharField(
        max_length=20,
        choices=MaritalStatus.choices,
        blank=True,
        verbose_name='Estado Civil'
    )

    # Contatos
    phone_primary = models.CharField(
        max_length=20,
        blank=True,
        validators=[validate_phone],
        verbose_name='Telefone Principal'
    )
    phone_secondary = models.CharField(
        max_length=20,
        blank=True,
        validators=[validate_phone],
        verbose_name='Telefone Secundário'
    )
    email = models.EmailField(max_length=160, blank=True, verbose_name='E-mail')

    # Endereço
    address_line = models.CharField(max_length=160, blank=True, verbose_name='Logradouro')
    address_number = models.CharField(max_length=20, blank=True, verbose_name='Número')
    address_complement = models.CharField(max_length=60, blank=True, verbose_name='Complemento')
    neighborhood = models.CharField(max_length=80, blank=True, verbose_name='Bairro')
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Município'
    )
    municipality_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nome do Município (texto livre)',
        help_text='Nome do município digitado manualmente ou via CEP'
    )
    cep = models.CharField(
        max_length=9,
        blank=True,
        validators=[validate_cep],
        verbose_name='CEP',
        help_text='Formato: 00000-000'
    )
    uf = models.CharField(max_length=2, choices=UF.choices, blank=True, verbose_name='UF')

    # Cônjuge/Companheiro
    spouse_name = models.CharField(max_length=160, blank=True, verbose_name='Nome do Cônjuge')
    spouse_rg = models.CharField(max_length=32, blank=True, verbose_name='RG do Cônjuge')
    spouse_birth_date = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento do Cônjuge')

    # Econômico / CadÚnico
    main_occupation = models.CharField(max_length=120, blank=True, verbose_name='Ocupação Principal')
    gross_family_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[validate_positive_income],
        verbose_name='Renda Familiar Bruta',
        help_text='Renda familiar mensal bruta em R$'
    )
    has_cadunico = models.BooleanField(default=False, verbose_name='Possui CadÚnico')
    nis_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_nis],
        verbose_name='Número NIS',
        help_text='Quando possui CadÚnico'
    )

    # Composição Familiar
    family_size = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Tamanho da Família'
    )
    has_elderly = models.BooleanField(default=False, verbose_name='Possui Idosos')
    elderly_count = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Quantidade de Idosos')
    has_children = models.BooleanField(default=False, verbose_name='Possui Crianças')
    children_count = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Quantidade de Crianças')
    has_disability_or_tea = models.BooleanField(default=False, verbose_name='Possui PcD ou TEA')
    disability_or_tea_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Quantidade PcD/TEA'
    )
    household_head_gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        blank=True,
        verbose_name='Gênero do Chefe da Família'
    )
    family_in_cadunico_updated = models.BooleanField(
        default=False,
        verbose_name='Família no CadÚnico Atualizada'
    )

    # Situação Habitacional
    no_own_house = models.BooleanField(default=False, verbose_name='Não possui casa própria')
    precarious_own_house = models.BooleanField(default=False, verbose_name='Casa própria precária')
    cohabitation = models.BooleanField(default=False, verbose_name='Coabitação')
    improvised_dwelling = models.BooleanField(default=False, verbose_name='Moradia improvisada')
    pays_rent = models.BooleanField(default=False, verbose_name='Paga aluguel')
    rent_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[validate_positive_income],
        verbose_name='Valor do Aluguel'
    )
    other_housing_desc = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Outra Situação Habitacional'
    )

    # Status
    status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT,
        verbose_name='Status'
    )

    # Observações
    notes = models.TextField(blank=True, verbose_name='Observações')

    # Documentação Apresentada
    has_rg_cpf = models.BooleanField(
        default=False,
        verbose_name='Apresentou RG e CPF',
        help_text='Documentos de identificação pessoal'
    )
    has_birth_certificate = models.BooleanField(
        default=False,
        verbose_name='Apresentou Certidão de Nascimento/Casamento',
        help_text='Certidões de estado civil'
    )
    has_address_proof = models.BooleanField(
        default=False,
        verbose_name='Apresentou Comprovante de Residência',
        help_text='Conta de luz, água, telefone, etc.'
    )
    has_income_proof = models.BooleanField(
        default=False,
        verbose_name='Apresentou Comprovante de Renda',
        help_text='Holerite, declaração, etc. (quando houver)'
    )
    has_cadunico_number = models.BooleanField(
        default=False,
        verbose_name='Apresentou Número NIS / CadÚnico',
        help_text='Comprovante do NIS ou inscrição no CadÚnico'
    )

    # Auditoria
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='Submetido em')
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='beneficiaries_submitted',
        verbose_name='Submetido por'
    )
    last_review_at = models.DateTimeField(null=True, blank=True, verbose_name='Última Revisão em')
    last_reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='beneficiaries_reviewed',
        verbose_name='Última Revisão por'
    )

    class Meta:
        db_table = 'beneficiaries'
        verbose_name = 'Beneficiário'
        verbose_name_plural = 'Beneficiários'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cpf']),
            models.Index(fields=['municipality']),
            models.Index(fields=['status']),
            models.Index(fields=['submitted_at']),
            models.Index(fields=['protocol_number']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.cpf}"

    def save(self, *args, **kwargs):
        """Override save para gerar protocol_number ao submeter"""
        # Se está sendo submetido e ainda não tem protocolo
        if self.status == ApplicationStatus.SUBMITTED and not self.protocol_number:
            self.protocol_number = self.generate_protocol_number()
            if not self.submitted_at:
                self.submitted_at = timezone.now()

        # Converter string vazia em NULL para respeitar unique constraint
        # (permite múltiplos NULL mas não múltiplas strings vazias)
        if self.nis_number == '':
            self.nis_number = None

        super().save(*args, **kwargs)

    def generate_protocol_number(self):
        """Gera número de protocolo único no formato AAAA-MM-XXXXXX"""
        now = timezone.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        unique_id = str(uuid.uuid4().hex[:6].upper())
        return f"{year}-{month}-{unique_id}"

    @property
    def age(self):
        """Calcula idade baseada na data de nascimento"""
        if not self.birth_date:
            return None
        today = timezone.now().date()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )


# ============================================================
# RELACIONAMENTOS MANY-TO-MANY
# ============================================================

class BeneficiaryPriority(models.Model):
    """Critérios de priorização aplicados ao beneficiário"""
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='priorities',
        verbose_name='Beneficiário'
    )
    criteria = models.ForeignKey(
        PriorityCriteria,
        on_delete=models.CASCADE,
        verbose_name='Critério'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        db_table = 'beneficiary_priority'
        verbose_name = 'Prioridade do Beneficiário'
        verbose_name_plural = 'Prioridades dos Beneficiários'
        unique_together = [['beneficiary', 'criteria']]
        indexes = [
            models.Index(fields=['beneficiary', 'criteria']),
        ]

    def __str__(self):
        return f"{self.beneficiary.full_name} - {self.criteria.label}"


class BeneficiarySocialBenefit(models.Model):
    """Benefícios sociais recebidos pelo beneficiário"""
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='social_benefits',
        verbose_name='Beneficiário'
    )
    benefit = models.ForeignKey(
        SocialBenefitType,
        on_delete=models.CASCADE,
        verbose_name='Benefício'
    )
    other_text = models.CharField(
        max_length=160,
        blank=True,
        verbose_name='Outro (especificar)'
    )

    class Meta:
        db_table = 'beneficiary_social_benefits'
        verbose_name = 'Benefício Social do Beneficiário'
        verbose_name_plural = 'Benefícios Sociais dos Beneficiários'
        unique_together = [['beneficiary', 'benefit']]
        indexes = [
            models.Index(fields=['beneficiary', 'benefit']),
        ]

    def __str__(self):
        return f"{self.beneficiary.full_name} - {self.benefit.label}"


# ============================================================
# DOCUMENTOS
# ============================================================

def beneficiary_document_path(instance, filename):
    """Gera caminho dinâmico para upload de documentos"""
    # Organiza: beneficiarios/{cpf}/{tipo_documento}/{filename}
    cpf_clean = instance.beneficiary.cpf.replace('.', '').replace('-', '')
    return f'beneficiarios/{cpf_clean}/{instance.document_type.code}/{filename}'


class BeneficiaryDocument(models.Model):
    """Documentos anexados pelo beneficiário"""
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Beneficiário'
    )
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Documento'
    )
    file_name = models.CharField(max_length=200, verbose_name='Nome do Arquivo')
    file_path = models.FileField(
        upload_to=beneficiary_document_path,
        max_length=400,
        verbose_name='Arquivo'
    )
    mime_type = models.CharField(max_length=80, blank=True, verbose_name='Tipo MIME')
    size_bytes = models.BigIntegerField(null=True, blank=True, verbose_name='Tamanho (bytes)')

    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Enviado em')
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents_uploaded',
        verbose_name='Enviado por'
    )

    validated = models.BooleanField(default=False, verbose_name='Validado')
    validated_at = models.DateTimeField(null=True, blank=True, verbose_name='Validado em')
    validated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents_validated',
        verbose_name='Validado por'
    )

    notes = models.TextField(blank=True, verbose_name='Observações')

    class Meta:
        db_table = 'beneficiary_documents'
        verbose_name = 'Documento do Beneficiário'
        verbose_name_plural = 'Documentos dos Beneficiários'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['beneficiary', 'document_type']),
        ]

    def __str__(self):
        return f"{self.beneficiary.full_name} - {self.document_type.label}"


# ============================================================
# FLUXO E ATRIBUIÇÕES
# ============================================================

class ApplicationAssignment(models.Model):
    """Atribuição de inscrições para análise"""
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='Beneficiário'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_applications',
        verbose_name='Atribuído para'
    )
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='Atribuído em')
    active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        db_table = 'application_assignments'
        verbose_name = 'Atribuição de Inscrição'
        verbose_name_plural = 'Atribuições de Inscrições'
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['beneficiary', 'active']),
            models.Index(fields=['assigned_to', 'active']),
        ]

    def __str__(self):
        return f"{self.beneficiary.full_name} → {self.assigned_to.get_full_name()}"


class ApplicationActionHistory(models.Model):
    """Histórico de ações realizadas na inscrição"""
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='action_history',
        verbose_name='Beneficiário'
    )
    action = models.CharField(
        max_length=40,
        choices=ApplicationAction.choices,
        verbose_name='Ação'
    )
    from_status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        blank=True,
        verbose_name='Status Anterior'
    )
    to_status = models.CharField(
        max_length=30,
        choices=ApplicationStatus.choices,
        blank=True,
        verbose_name='Novo Status'
    )
    message = models.TextField(blank=True, verbose_name='Mensagem')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actions_created',
        verbose_name='Criado por'
    )

    class Meta:
        db_table = 'application_actions'
        verbose_name = 'Histórico de Ação'
        verbose_name_plural = 'Histórico de Ações'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['beneficiary', 'created_at']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.beneficiary.full_name} - {self.get_action_display()} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"


# ============================================================
# AUDITORIA
# ============================================================

class SearchAudit(models.Model):
    """Auditoria de buscas realizadas no sistema"""
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuário'
    )
    query = models.CharField(max_length=400, verbose_name='Consulta')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        db_table = 'search_audit'
        verbose_name = 'Auditoria de Busca'
        verbose_name_plural = 'Auditorias de Buscas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'Anônimo'
        return f"{user_name} - {self.query[:50]}"


# ============================================================
# IMPORT AUDIT MODELS
# ============================================================
from .models_audit import AuditLog, UserSession, PermissionChange, SystemNotification
