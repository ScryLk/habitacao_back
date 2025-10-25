"""
Admin configuration para o app Habitação
"""
from django.contrib import admin
from .models import (
    Municipality,
    PriorityCriteria,
    SocialBenefitType,
    DocumentType,
    UserProfile,
    Beneficiary,
    BeneficiaryPriority,
    BeneficiarySocialBenefit,
    BeneficiaryDocument,
    ApplicationAssignment,
    ApplicationActionHistory,
    SearchAudit,
)


# ============================================================
# ADMIN CONFIGURATIONS BASE
# ============================================================

@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ['ibge_code', 'name', 'uf']
    list_filter = ['uf']
    search_fields = ['name', 'ibge_code']
    ordering = ['uf', 'name']


@admin.register(PriorityCriteria)
class PriorityCriteriaAdmin(admin.ModelAdmin):
    list_display = ['code', 'label', 'group_tag', 'active']
    list_filter = ['active', 'group_tag']
    search_fields = ['code', 'label']
    ordering = ['group_tag', 'label']


@admin.register(SocialBenefitType)
class SocialBenefitTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'label', 'active']
    list_filter = ['active']
    search_fields = ['code', 'label']
    ordering = ['label']


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'label', 'required', 'active']
    list_filter = ['required', 'active']
    search_fields = ['code', 'label']
    ordering = ['label']


# ============================================================
# USER PROFILE ADMIN
# ============================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'cpf', 'role', 'municipality', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'municipality']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'cpf']
    raw_id_fields = ['user', 'municipality']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


# ============================================================
# BENEFICIARY ADMIN
# ============================================================

class BeneficiaryPriorityInline(admin.TabularInline):
    model = BeneficiaryPriority
    extra = 1
    raw_id_fields = ['criteria']


class BeneficiarySocialBenefitInline(admin.TabularInline):
    model = BeneficiarySocialBenefit
    extra = 1
    raw_id_fields = ['benefit']


class BeneficiaryDocumentInline(admin.TabularInline):
    model = BeneficiaryDocument
    extra = 0
    readonly_fields = ['uploaded_at', 'uploaded_by', 'validated_at', 'validated_by']
    fields = ['document_type', 'file_name', 'file_path', 'validated', 'notes']


class ApplicationActionHistoryInline(admin.TabularInline):
    model = ApplicationActionHistory
    extra = 0
    readonly_fields = ['created_at', 'created_by']
    fields = ['action', 'from_status', 'to_status', 'message', 'created_at', 'created_by']
    can_delete = False


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = [
        'protocol_number', 'full_name', 'cpf', 'municipality',
        'status', 'submitted_at', 'created_at'
    ]
    list_filter = [
        'status', 'has_cadunico', 'municipality', 'uf',
        'has_elderly', 'has_children', 'has_disability_or_tea',
        'pays_rent', 'no_own_house'
    ]
    search_fields = ['full_name', 'cpf', 'protocol_number', 'email']
    raw_id_fields = ['municipality', 'submitted_by', 'last_reviewed_by']
    readonly_fields = [
        'protocol_number', 'created_at', 'updated_at',
        'submitted_at', 'last_review_at', 'age'
    ]

    fieldsets = (
        ('Protocolo e Status', {
            'fields': ('protocol_number', 'status', 'created_at', 'updated_at')
        }),
        ('Dados Pessoais', {
            'fields': (
                'full_name', 'cpf', 'rg', 'birth_date', 'marital_status'
            )
        }),
        ('Contatos', {
            'fields': ('phone_primary', 'phone_secondary', 'email')
        }),
        ('Endereço', {
            'fields': (
                'address_line', 'address_number', 'address_complement',
                'neighborhood', 'municipality', 'cep', 'uf'
            )
        }),
        ('Cônjuge/Companheiro', {
            'fields': ('spouse_name', 'spouse_rg', 'spouse_birth_date'),
            'classes': ('collapse',)
        }),
        ('Econômico / CadÚnico', {
            'fields': (
                'main_occupation', 'gross_family_income',
                'has_cadunico', 'nis_number'
            )
        }),
        ('Composição Familiar', {
            'fields': (
                'family_size', 'household_head_gender', 'family_in_cadunico_updated',
                'has_elderly', 'elderly_count',
                'has_children', 'children_count',
                'has_disability_or_tea', 'disability_or_tea_count'
            )
        }),
        ('Situação Habitacional', {
            'fields': (
                'no_own_house', 'precarious_own_house', 'cohabitation',
                'improvised_dwelling', 'pays_rent', 'rent_value',
                'other_housing_desc'
            )
        }),
        ('Observações', {
            'fields': ('notes',)
        }),
        ('Auditoria', {
            'fields': (
                'submitted_at', 'submitted_by',
                'last_review_at', 'last_reviewed_by'
            ),
            'classes': ('collapse',)
        }),
    )

    inlines = [
        BeneficiaryPriorityInline,
        BeneficiarySocialBenefitInline,
        BeneficiaryDocumentInline,
        ApplicationActionHistoryInline,
    ]

    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    def age(self, obj):
        return obj.age
    age.short_description = 'Idade'


# ============================================================
# DOCUMENTS ADMIN
# ============================================================

@admin.register(BeneficiaryDocument)
class BeneficiaryDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'beneficiary', 'document_type', 'file_name',
        'validated', 'uploaded_at', 'uploaded_by'
    ]
    list_filter = ['validated', 'document_type', 'uploaded_at']
    search_fields = ['beneficiary__full_name', 'beneficiary__cpf', 'file_name']
    raw_id_fields = ['beneficiary', 'uploaded_by', 'validated_by']
    readonly_fields = ['uploaded_at', 'uploaded_by']
    ordering = ['-uploaded_at']
    date_hierarchy = 'uploaded_at'


# ============================================================
# ASSIGNMENTS AND ACTIONS ADMIN
# ============================================================

@admin.register(ApplicationAssignment)
class ApplicationAssignmentAdmin(admin.ModelAdmin):
    list_display = ['beneficiary', 'assigned_to', 'assigned_at', 'active']
    list_filter = ['active', 'assigned_at']
    search_fields = [
        'beneficiary__full_name', 'beneficiary__cpf',
        'assigned_to__username', 'assigned_to__first_name', 'assigned_to__last_name'
    ]
    raw_id_fields = ['beneficiary', 'assigned_to']
    ordering = ['-assigned_at']
    date_hierarchy = 'assigned_at'


@admin.register(ApplicationActionHistory)
class ApplicationActionHistoryAdmin(admin.ModelAdmin):
    list_display = ['beneficiary', 'action', 'from_status', 'to_status', 'created_at', 'created_by']
    list_filter = ['action', 'from_status', 'to_status', 'created_at']
    search_fields = ['beneficiary__full_name', 'beneficiary__cpf', 'message']
    raw_id_fields = ['beneficiary', 'created_by']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


# ============================================================
# AUDIT ADMIN
# ============================================================

@admin.register(SearchAudit)
class SearchAuditAdmin(admin.ModelAdmin):
    list_display = ['user', 'query', 'created_at']
    list_filter = ['created_at']
    search_fields = ['query', 'user__username']
    raw_id_fields = ['user']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
