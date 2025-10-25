"""
Comando para carregar dados iniciais no banco de dados
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Carrega dados iniciais (tipos de documentos, benefícios sociais, critérios de priorização)'

    def handle(self, *args, **options):
        self.stdout.write('Carregando dados iniciais...')

        try:
            call_command('loaddata', 'initial_data.json', app_label='habitacao')
            self.stdout.write(self.style.SUCCESS('✓ Dados iniciais carregados com sucesso!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Erro ao carregar dados: {e}'))
