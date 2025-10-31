#!/usr/bin/env python
"""
Script para listar beneficiários cadastrados
Uso: docker compose exec web python scripts/list_beneficiaries.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from habitacao.models import Beneficiary
from django.db.models import Count, Q


def print_separator(char='=', length=100):
    print(char * length)


def format_cpf(cpf):
    """Formata CPF: 12345678901 → 123.456.789-01"""
    if not cpf or len(cpf) != 11:
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def list_all_beneficiaries():
    """Lista todos os beneficiários"""
    print_separator()
    print("📋 LISTA DE BENEFICIÁRIOS CADASTRADOS")
    print_separator()

    beneficiaries = Beneficiary.objects.all().order_by('-created_at')
    total = beneficiaries.count()

    print(f"\n✅ Total de beneficiários: {total}\n")

    if total == 0:
        print("⚠️  Nenhum beneficiário cadastrado ainda.")
        return

    # Cabeçalho
    print(f"{'ID':>4} | {'Nome':<35} | {'CPF':<15} | {'Status':<20} | {'NIS':<12} | {'Protocolo':<18}")
    print_separator('-')

    # Listar beneficiários
    for b in beneficiaries:
        cpf_formatted = format_cpf(b.cpf)
        nis = b.nis_number if b.nis_number else 'NULL'
        protocol = b.protocol_number if b.protocol_number else '-'

        print(f"{b.id:4d} | {b.full_name:<35.35} | {cpf_formatted:<15} | {b.status:<20} | {nis:<12} | {protocol:<18}")

    print_separator()


def statistics():
    """Estatísticas gerais"""
    print("\n📊 ESTATÍSTICAS\n")
    print_separator('-')

    # Total
    total = Beneficiary.objects.count()
    print(f"Total de beneficiários: {total}")

    # Por status
    print("\n🔹 Por Status:")
    status_counts = Beneficiary.objects.values('status').annotate(count=Count('id')).order_by('-count')
    for item in status_counts:
        print(f"  - {item['status']}: {item['count']}")

    # Com/Sem NIS
    with_nis = Beneficiary.objects.filter(nis_number__isnull=False).count()
    without_nis = Beneficiary.objects.filter(nis_number__isnull=True).count()
    print(f"\n🔹 CadÚnico/NIS:")
    print(f"  - Com NIS: {with_nis}")
    print(f"  - Sem NIS: {without_nis}")

    # Com filhos
    with_children = Beneficiary.objects.filter(has_children=True).count()
    print(f"\n🔹 Composição Familiar:")
    print(f"  - Com crianças: {with_children}")

    # Com idosos
    with_elderly = Beneficiary.objects.filter(has_elderly=True).count()
    print(f"  - Com idosos: {with_elderly}")

    # Pagam aluguel
    pay_rent = Beneficiary.objects.filter(pays_rent=True).count()
    print(f"\n🔹 Situação Habitacional:")
    print(f"  - Pagam aluguel: {pay_rent}")

    print_separator()


def recent_beneficiaries(limit=5):
    """Lista os N beneficiários mais recentes"""
    print(f"\n🆕 ÚLTIMOS {limit} BENEFICIÁRIOS CADASTRADOS\n")
    print_separator('-')

    beneficiaries = Beneficiary.objects.all().order_by('-created_at')[:limit]

    for b in beneficiaries:
        cpf_formatted = format_cpf(b.cpf)
        print(f"ID {b.id:3d} | {b.full_name:<30} | {cpf_formatted} | {b.created_at.strftime('%d/%m/%Y %H:%M')}")

    print_separator()


def search_by_name(name):
    """Busca beneficiários por nome"""
    print(f"\n🔍 BUSCA POR NOME: '{name}'\n")
    print_separator('-')

    beneficiaries = Beneficiary.objects.filter(
        Q(full_name__icontains=name)
    )

    total = beneficiaries.count()
    print(f"Encontrados: {total}\n")

    if total == 0:
        print("⚠️  Nenhum beneficiário encontrado.")
        return

    for b in beneficiaries:
        cpf_formatted = format_cpf(b.cpf)
        print(f"ID {b.id:3d} | {b.full_name:<35} | {cpf_formatted} | Status: {b.status}")

    print_separator()


def filter_by_status(status):
    """Filtra beneficiários por status"""
    print(f"\n📂 FILTRO POR STATUS: '{status}'\n")
    print_separator('-')

    beneficiaries = Beneficiary.objects.filter(status=status).order_by('-created_at')
    total = beneficiaries.count()

    print(f"Total: {total}\n")

    if total == 0:
        print(f"⚠️  Nenhum beneficiário com status '{status}'.")
        return

    for b in beneficiaries:
        cpf_formatted = format_cpf(b.cpf)
        protocol = b.protocol_number if b.protocol_number else '-'
        print(f"ID {b.id:3d} | {b.full_name:<35} | {cpf_formatted} | Protocolo: {protocol}")

    print_separator()


def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Lista beneficiários cadastrados')
    parser.add_argument('--stats', action='store_true', help='Mostrar estatísticas')
    parser.add_argument('--recent', type=int, metavar='N', help='Mostrar N beneficiários mais recentes')
    parser.add_argument('--search', type=str, metavar='NOME', help='Buscar por nome')
    parser.add_argument('--status', type=str, metavar='STATUS', help='Filtrar por status')

    args = parser.parse_args()

    # Se nenhum argumento, mostrar lista completa
    if not any([args.stats, args.recent, args.search, args.status]):
        list_all_beneficiaries()
        statistics()
        return

    # Executar comandos específicos
    if args.stats:
        statistics()

    if args.recent:
        recent_beneficiaries(args.recent)

    if args.search:
        search_by_name(args.search)

    if args.status:
        filter_by_status(args.status)


if __name__ == '__main__':
    main()
