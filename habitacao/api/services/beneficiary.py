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
    def create_from_flat_data(data):
        """
        Cria beneficiário a partir de dados flat (todos os campos no nível raiz)
        Formato usado pelo front-end: { full_name, cpf, phone_primary, address_line, ... }
        """
        from habitacao.models import Municipality

        # Se municipality_id for None ou 0, remove do dict
        municipality_id = data.pop('municipality_id', None)
        municipality = None
        if municipality_id and municipality_id > 0:
            try:
                municipality = Municipality.objects.get(id=municipality_id)
            except Municipality.DoesNotExist:
                raise ValueError(f"Município com ID {municipality_id} não encontrado.")

        # Cria beneficiário direto com campos flat
        beneficiary = Beneficiary.objects.create(
            # Dados pessoais
            full_name=data.get('full_name'),
            cpf=data.get('cpf'),
            rg=data.get('rg', ''),
            birth_date=data.get('birth_date'),
            marital_status=data.get('marital_status', ''),

            # Contatos
            phone_primary=data.get('phone_primary', ''),
            phone_secondary=data.get('phone_secondary', ''),
            email=data.get('email', ''),

            # Endereço
            address_line=data.get('address_line', ''),
            address_number=data.get('address_number', ''),
            address_complement=data.get('address_complement', ''),
            neighborhood=data.get('neighborhood', ''),
            municipality=municipality,
            cep=data.get('cep', ''),
            uf=data.get('uf', ''),

            # Cônjuge
            spouse_name=data.get('spouse_name', ''),
            spouse_rg=data.get('spouse_rg', ''),
            spouse_birth_date=data.get('spouse_birth_date'),

            # Econômico / CadÚnico
            main_occupation=data.get('main_occupation', ''),
            gross_family_income=data.get('gross_family_income'),
            has_cadunico=data.get('has_cadunico', False),
            nis_number=data.get('nis_number') or None,

            # Composição Familiar
            family_size=data.get('family_size', 1),
            has_elderly=data.get('has_elderly', False),
            elderly_count=data.get('elderly_count', 0),
            has_children=data.get('has_children', False),
            children_count=data.get('children_count', 0),
            has_disability_or_tea=data.get('has_disability_or_tea', False),
            disability_or_tea_count=data.get('disability_or_tea_count', 0),
            household_head_gender=data.get('household_head_gender', ''),
            family_in_cadunico_updated=data.get('family_in_cadunico_updated', False),

            # Situação Habitacional
            no_own_house=data.get('no_own_house', False),
            precarious_own_house=data.get('precarious_own_house', False),
            cohabitation=data.get('cohabitation', False),
            improvised_dwelling=data.get('improvised_dwelling', False),
            pays_rent=data.get('pays_rent', False),
            rent_value=data.get('rent_value'),
            other_housing_desc=data.get('other_housing_desc', ''),

            # Documentação Apresentada
            has_rg_cpf=data.get('has_rg_cpf', False),
            has_birth_certificate=data.get('has_birth_certificate', False),
            has_address_proof=data.get('has_address_proof', False),
            has_income_proof=data.get('has_income_proof', False),
            has_cadunico_number=data.get('has_cadunico_number', False),

            # Observações
            notes=data.get('notes', ''),
            status=ApplicationStatus.DRAFT,
        )

        return beneficiary

    @staticmethod
    @transaction.atomic
    def create_from_nested_data(data):
        """
        Cria beneficiário a partir de dados aninhados
        Formato: { full_name, cpf, phones: {}, address: {}, economy: {}, etc }
        """
        from habitacao.models import Municipality

        # Extrai dados aninhados
        phones = data.pop('phones', {})
        address = data.pop('address', {})
        spouse = data.pop('spouse', {})
        economy = data.pop('economy', {})
        family = data.pop('family', {})
        housing = data.pop('housing', {})

        # --- Lógica de busca do Município ---
        from unidecode import unidecode
        municipality = None
        city_name = address.get('city')
        uf_code = address.get('uf')

        if city_name and uf_code:
            # Normaliza o nome da cidade vindo da requisição
            city_name_normalized = unidecode(city_name.strip().lower())

            # 1. Tentativa de busca exata normalizada (mais segura)
            municipalities_in_uf = Municipality.objects.filter(uf__iexact=uf_code)
            found_municipality = None
            for m in municipalities_in_uf:
                if unidecode(m.name.lower()) == city_name_normalized:
                    found_municipality = m
                    break
            
            municipality = found_municipality

            # 2. Se não encontrou, tenta busca com 'icontains' (mais flexível)
            if not municipality:
                municipalities = Municipality.objects.filter(
                    name__icontains=city_name.strip(),
                    uf__iexact=uf_code
                )
                # Só aceita se o resultado for único para evitar ambiguidade
                if municipalities.count() == 1:
                    municipality = municipalities.first()

            # Se ainda não encontrou, lança o erro
            if not municipality:
                raise ValueError(f"Município '{city_name}/{uf_code}' não encontrado ou a busca resultou em ambiguidade.")

        # --- Mapeamento da Situação Habitacional ---
        housing_situation = housing.get('current_housing_situation')
        pays_rent = housing_situation == 'ALUGUEL'
        cohabitation = housing_situation == 'COABITACAO'
        improvised_dwelling = housing_situation == 'IMPROVISADA'
        precarious_own_house = housing.get('housing_precariousness') == 'PRECARIA'
        no_own_house = not housing.get('has_own_property', True)

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
            address_line=address.get('street', ''),
            address_number=address.get('number', ''),
            address_complement=address.get('complement', ''),
            neighborhood=address.get('neighborhood', ''),
            municipality=municipality,
            cep=address.get('zip_code', ''),
            uf=address.get('uf', ''),

            # Cônjuge
            spouse_name=spouse.get('full_name', '') if spouse else '',
            spouse_birth_date=spouse.get('birth_date') if spouse else None,

            # Econômico
            main_occupation=economy.get('main_income_source', ''),
            gross_family_income=family.get('total_family_income'),
            nis_number=economy.get('nis_number') or None,
            has_cadunico=bool(economy.get('nis_number')),

            # Família
            family_size=family.get('number_of_members', 1),
            has_elderly=family.get('has_elderly_person', False),
            children_count=family.get('number_of_minors', 0),
            has_children=family.get('number_of_minors', 0) > 0,
            has_disability_or_tea=family.get('has_disabled_person', False),

            # Situação Habitacional
            pays_rent=pays_rent,
            cohabitation=cohabitation,
            improvised_dwelling=improvised_dwelling,
            precarious_own_house=precarious_own_house,
            no_own_house=no_own_house,

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
