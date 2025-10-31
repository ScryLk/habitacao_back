#!/usr/bin/env python
"""
Script para criar beneficiário COMPLETO com TODOS os DOCUMENTOS marcados
Para testar exportação de PDF com seção "Documentação Apresentada"
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

def create_beneficiary_with_documents():
    """Cria beneficiário com TODOS os campos e TODOS os documentos marcados"""

    print("🔧 Criando beneficiário COMPLETO com DOCUMENTOS...")

    # Buscar município São Paulo
    municipality = Municipality.objects.filter(name="São Paulo", uf=UF.SP).first()
    if not municipality:
        municipality = Municipality.objects.create(
            name="São Paulo",
            uf=UF.SP,
            ibge_code='3550308'
        )

    # Criar beneficiário COMPLETO com DOCUMENTOS
    beneficiary = Beneficiary.objects.create(
        # === Dados Pessoais ===
        full_name="Ana Paula Ferreira Costa",
        cpf="98765432100",  # CPF único
        rg="SP-98.765.432",
        birth_date=date(1988, 9, 25),
        marital_status=MaritalStatus.CASADO,

        # === Contatos ===
        phone_primary="11976543210",
        phone_secondary="11945678901",
        email="ana.ferreira@email.com",

        # === Endereço COMPLETO ===
        address_line="Rua das Acácias",
        address_number="789",
        address_complement="Casa 3, Fundos",
        neighborhood="Vila Mariana",
        municipality=municipality,
        cep="04101000",
        uf=UF.SP,

        # === Cônjuge ===
        spouse_name="Roberto Carlos da Costa",
        spouse_rg="SP-12.345.987",
        spouse_birth_date=date(1985, 3, 12),

        # === Situação Econômica ===
        main_occupation="Auxiliar de Limpeza",
        gross_family_income=Decimal("2200.00"),
        has_cadunico=True,
        nis_number="98765432109",

        # === Composição Familiar ===
        family_size=5,
        has_elderly=True,
        elderly_count=1,
        has_children=True,
        children_count=3,
        has_disability_or_tea=False,
        disability_or_tea_count=0,
        household_head_gender=Gender.FEMININO,
        family_in_cadunico_updated=True,

        # === Situação Habitacional ===
        no_own_house=True,
        precarious_own_house=False,
        cohabitation=False,
        improvised_dwelling=False,
        pays_rent=True,
        rent_value=Decimal("850.00"),
        other_housing_desc="Aluguel em comunidade",

        # === DOCUMENTAÇÃO APRESENTADA ✅ ===
        has_rg_cpf=True,
        has_birth_certificate=True,
        has_address_proof=True,
        has_income_proof=True,
        has_cadunico_number=True,

        # === Status ===
        status=ApplicationStatus.DRAFT,

        # === Observações ===
        notes="Família numerosa com 3 crianças e 1 idoso. Renda baixa, já cadastrada no CadÚnico. Todos os documentos foram apresentados e estão em ordem. Mora em comunidade com risco de desabamento.",
    )

    print(f"\n✅ Beneficiário COMPLETO com DOCUMENTOS criado!")
    print(f"   ID: {beneficiary.id}")
    print(f"   Nome: {beneficiary.full_name}")
    print(f"   CPF: {beneficiary.cpf}")
    print(f"\n📋 Dados cadastrados:")
    print(f"   ✅ Dados Pessoais: Nome, CPF, RG, Data Nascimento, Estado Civil")
    print(f"   ✅ Contatos: 2 telefones + email")
    print(f"   ✅ Endereço: Rua, número, complemento, bairro, CEP, município, UF")
    print(f"   ✅ Cônjuge: Nome, RG, data de nascimento")
    print(f"   ✅ Economia: Ocupação, renda (R$ 2.200), CadÚnico, NIS")
    print(f"   ✅ Família: 5 pessoas (1 idoso, 3 crianças)")
    print(f"   ✅ Habitação: Paga aluguel de R$ 850,00")
    print(f"   ✅ Observações: Texto detalhado")
    print(f"\n📄 DOCUMENTAÇÃO APRESENTADA:")
    print(f"   ✅ RG e CPF: {beneficiary.has_rg_cpf}")
    print(f"   ✅ Certidão: {beneficiary.has_birth_certificate}")
    print(f"   ✅ Comprovante Residência: {beneficiary.has_address_proof}")
    print(f"   ✅ Comprovante Renda: {beneficiary.has_income_proof}")
    print(f"   ✅ NIS/CadÚnico: {beneficiary.has_cadunico_number}")
    print(f"\n🎯 Teste a exportação de PDF com este beneficiário:")
    print(f"   http://localhost:5173/painel/beneficiarios")
    print(f"\n📄 Ou teste via API:")
    print(f"   curl -X GET \"http://localhost:8000/api/v1/beneficiaries/{beneficiary.id}/\" \\")
    print(f"     -H \"Authorization: Bearer SEU_TOKEN\"")
    print(f"\n🔍 Esperado no PDF:")
    print(f"   Documentação Apresentada")
    print(f"   ===================================")
    print(f"   (X) RG e CPF")
    print(f"   (X) Certidão de Nascimento/Casamento")
    print(f"   (X) Comprovante de residência")
    print(f"   (X) Comprovante de renda (quando houver)")
    print(f"   (X) Número NIS / CadÚnico")

    return beneficiary

if __name__ == '__main__':
    try:
        beneficiary = create_beneficiary_with_documents()
    except Exception as e:
        print(f"\n❌ Erro ao criar beneficiário: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
