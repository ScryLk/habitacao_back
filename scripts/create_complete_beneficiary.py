#!/usr/bin/env python
"""
Script para criar beneficiário COMPLETO com TODOS os campos preenchidos
Para testar exportação de PDF
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from habitacao.models import Beneficiary, Municipality
from habitacao.choices import MaritalStatus, Gender, ApplicationStatus, UF

def create_complete_beneficiary():
    """Cria beneficiário com TODOS os campos preenchidos"""

    print("🔧 Criando beneficiário COMPLETO...")

    # Buscar ou criar município
    municipality, created = Municipality.objects.get_or_create(
        name="São Paulo",
        uf=UF.SP,
        defaults={
            'ibge_code': '3550308'
        }
    )
    if created:
        print(f"✅ Município criado: {municipality.name}/{municipality.uf}")

    # Criar beneficiário COMPLETO
    beneficiary = Beneficiary.objects.create(
        # === Dados Pessoais ===
        full_name="João Pedro da Silva",
        cpf="12345678900",  # CPF único
        rg="MG-12.345.678",
        birth_date=date(1982, 5, 10),
        marital_status=MaritalStatus.CASADO,

        # === Contatos ===
        phone_primary="11987654321",
        phone_secondary="11912345678",
        email="joao.pedro@email.com",

        # === Endereço COMPLETO ===
        address_line="Avenida Paulista",
        address_number="1500",
        address_complement="Apartamento 203, Bloco B",
        neighborhood="Bela Vista",
        municipality=municipality,
        cep="01310200",
        uf=UF.SP,

        # === Cônjuge ===
        spouse_name="Maria Aparecida da Silva",
        spouse_rg="MG-98.765.432",
        spouse_birth_date=date(1985, 8, 15),

        # === Situação Econômica ===
        main_occupation="Vendedor Autônomo",
        gross_family_income=Decimal("2800.00"),
        has_cadunico=True,
        nis_number="12345678901",

        # === Composição Familiar ===
        family_size=4,
        has_elderly=False,
        elderly_count=0,
        has_children=True,
        children_count=2,
        has_disability_or_tea=True,
        disability_or_tea_count=1,
        household_head_gender=Gender.FEMININO,
        family_in_cadunico_updated=True,

        # === Situação Habitacional ===
        no_own_house=True,
        precarious_own_house=False,
        cohabitation=False,
        improvised_dwelling=False,
        pays_rent=True,
        rent_value=Decimal("950.00"),
        other_housing_desc="Aluguel em área de risco de enchente",

        # === Status ===
        status=ApplicationStatus.DRAFT,

        # === Observações ===
        notes="Família em situação de vulnerabilidade social. Renda instável devido ao trabalho autônomo. Uma criança com TEA necessita acompanhamento especializado. Moradia em área de risco.",
    )

    print(f"\n✅ Beneficiário COMPLETO criado com sucesso!")
    print(f"   ID: {beneficiary.id}")
    print(f"   Nome: {beneficiary.full_name}")
    print(f"   CPF: {beneficiary.cpf}")
    print(f"\n📋 Dados cadastrados:")
    print(f"   ✅ Dados Pessoais: Nome, CPF, RG, Data Nascimento, Estado Civil")
    print(f"   ✅ Contatos: 2 telefones + email")
    print(f"   ✅ Endereço: Logradouro, número, complemento, bairro, CEP, município, UF")
    print(f"   ✅ Cônjuge: Nome, RG, data de nascimento")
    print(f"   ✅ Economia: Ocupação, renda (R$ 2.800), CadÚnico, NIS")
    print(f"   ✅ Família: 4 pessoas (2 crianças, 1 com TEA)")
    print(f"   ✅ Habitação: Paga aluguel de R$ 950,00")
    print(f"   ✅ Observações: Texto detalhado")
    print(f"\n🔗 Teste a exportação de PDF com este beneficiário:")
    print(f"   http://localhost:5173/painel/beneficiarios")
    print(f"\n📄 Ou teste via API:")
    print(f"   curl -X GET \"http://localhost:8000/api/v1/beneficiaries/{beneficiary.id}/\" \\")
    print(f"     -H \"Authorization: Bearer SEU_TOKEN\"")

    return beneficiary

if __name__ == '__main__':
    try:
        beneficiary = create_complete_beneficiary()
    except Exception as e:
        print(f"\n❌ Erro ao criar beneficiário: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
