"""
Serviço de beneficiários
"""
from django.db import transaction
from habitacao.models import Beneficiary
from habitacao.choices import ApplicationStatus, UserRole


class BeneficiaryService:
    """Serviço de gerenciamento de beneficiários"""

    @staticmethod
    @transaction.atomic
    def create_from_nested_data(data):
        """
        Cria beneficiário a partir de dados aninhados
        Formato: { full_name, cpf, phones: {}, address: {}, economy: {}, etc }
        """
        # Extrai dados aninhados
        phones = data.pop('phones', {})
        address = data.pop('address', {})
        spouse = data.pop('spouse', {})
        economy = data.pop('economy', {})
        family = data.pop('family', {})
        housing = data.pop('housing', {})

        # Cria beneficiário
        beneficiary = Beneficiary.objects.create(
            # Dados pessoais
            full_name=data.get('full_name'),
            cpf=data.get('cpf'),
            rg=data.get('rg', ''),
            birth_date=data.get('birth_date'),
            marital_status=data.get('marital_status', ''),
            # Contatos
            email=data.get('email', ''),
            phone_primary=phones.get('primary', ''),
            phone_secondary=phones.get('secondary', ''),
            # Endereço
            address_line=address.get('line', ''),
            address_number=address.get('number', ''),
            address_complement=address.get('complement', ''),
            neighborhood=address.get('neighborhood', ''),
            municipality_id=address.get('municipality_id'),
            cep=address.get('cep', ''),
            uf=address.get('uf', ''),
            # Cônjuge
            spouse_name=spouse.get('name', '') if spouse else '',
            spouse_rg=spouse.get('rg', '') if spouse else '',
            spouse_birth_date=spouse.get('birth_date') if spouse else None,
            # Econômico
            main_occupation=economy.get('main_occupation', ''),
            gross_family_income=economy.get('gross_family_income'),
            has_cadunico=economy.get('has_cadunico', False),
            nis_number=economy.get('nis_number', ''),
            # Família
            family_size=family.get('family_size', 1),
            has_elderly=family.get('has_elderly', False),
            elderly_count=family.get('elderly_count', 0),
            has_children=family.get('has_children', False),
            children_count=family.get('children_count', 0),
            has_disability_or_tea=family.get('has_disability_or_tea', False),
            disability_or_tea_count=family.get('disability_or_tea_count', 0),
            household_head_gender=family.get('household_head_gender', ''),
            family_in_cadunico_updated=family.get('cadunico_updated', False),
            # Habitação
            no_own_house=housing.get('no_own_house', False),
            precarious_own_house=housing.get('precarious_own_house', False),
            cohabitation=housing.get('cohabitation', False),
            improvised_dwelling=housing.get('improvised_dwelling', False),
            pays_rent=housing.get('pays_rent', False),
            rent_value=housing.get('rent_value'),
            other_housing_desc=housing.get('other_housing_desc', ''),
            # Outros
            notes=data.get('notes', ''),
            status=ApplicationStatus.DRAFT,
        )

        return beneficiary

    @staticmethod
    def list(filters=None, user=None):
        """
        Lista beneficiários com filtros
        Aplica escopo de município se aplicável
        """
        queryset = Beneficiary.objects.all()

        # Aplica escopo de município
        if user and hasattr(user, 'profile'):
            if user.profile.municipality and user.profile.role not in [UserRole.ADMIN]:
                queryset = queryset.filter(municipality=user.profile.municipality)

        # Aplica filtros adicionais (agora usa django-filter)
        queryset = queryset.select_related('municipality').prefetch_related(
            'priorities', 'social_benefits', 'documents'
        )

        return queryset.order_by('-created_at')

    @staticmethod
    def get_by_id(beneficiary_id, user=None):
        """
        Obtém beneficiário por ID
        Valida escopo de município
        """
        queryset = Beneficiary.objects.select_related('municipality').prefetch_related(
            'priorities__criteria',
            'social_benefits__benefit',
            'documents__document_type',
            'action_history__created_by',
            'assignments__assigned_to'
        )

        beneficiary = queryset.get(id=beneficiary_id)

        # Valida escopo
        if user and hasattr(user, 'profile'):
            if user.profile.municipality and user.profile.role not in [UserRole.ADMIN]:
                if beneficiary.municipality != user.profile.municipality:
                    raise ValueError("Sem permissão para acessar este beneficiário")

        return beneficiary

    @staticmethod
    @transaction.atomic
    def update(beneficiary_id, data, user):
        """Atualiza beneficiário"""
        beneficiary = BeneficiaryService.get_by_id(beneficiary_id, user)

        # Não permite atualizar status diretamente
        if 'status' in data and data['status'] != beneficiary.status:
            raise ValueError("Use os endpoints de workflow para mudar o status")

        # Atualiza campos permitidos
        for field, value in data.items():
            if hasattr(beneficiary, field):
                setattr(beneficiary, field, value)

        beneficiary.save()
        return beneficiary

    @staticmethod
    def soft_delete(beneficiary_id, user):
        """Soft delete (não implementado - requer campo deleted_at)"""
        beneficiary = BeneficiaryService.get_by_id(beneficiary_id, user)
        # TODO: Adicionar campo deleted_at ao model
        # beneficiary.deleted_at = timezone.now()
        # beneficiary.save()
        beneficiary.delete()
        return True
