# Generated manually to fix NIS empty strings issue
from django.db import migrations


def convert_empty_nis_to_null(apps, schema_editor):
    """Converter strings vazias em NULL para o campo nis_number"""
    Beneficiary = apps.get_model('habitacao', 'Beneficiary')
    # Atualizar todos os registros com nis_number vazio para NULL
    Beneficiary.objects.filter(nis_number='').update(nis_number=None)


def reverse_conversion(apps, schema_editor):
    """Reverter: converter NULL de volta para string vazia"""
    Beneficiary = apps.get_model('habitacao', 'Beneficiary')
    # Atualizar todos os registros com nis_number NULL para string vazia
    Beneficiary.objects.filter(nis_number__isnull=True).update(nis_number='')


class Migration(migrations.Migration):
    """
    Migration para corrigir o problema de IntegrityError causado por múltiplas strings vazias
    no campo nis_number que tem constraint unique=True.

    MySQL permite múltiplos NULL em campos unique, mas não múltiplas strings vazias.
    Esta migration converte todas as strings vazias em NULL.
    """

    dependencies = [
        ('habitacao', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            convert_empty_nis_to_null,
            reverse_conversion,
        ),
    ]
