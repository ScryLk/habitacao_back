# -*- coding: utf-8 -*-
"""
Management command para criar UserProfile para o usuario admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from habitacao.models import UserProfile


class Command(BaseCommand):
    help = 'Cria UserProfile para o usuario admin se nao existir'

    def handle(self, *args, **options):
        try:
            self.stdout.write('=== Criando UserProfile para admin ===')

            # Buscar usuario admin
            user = User.objects.get(username='admin')
            self.stdout.write(f'Usuario encontrado: {user.username} ({user.email})')

            # Verificar se ja tem profile
            if hasattr(user, 'profile'):
                self.stdout.write(self.style.WARNING('UserProfile ja existe!'))
                self.stdout.write(f'  CPF: {user.profile.cpf}')
                self.stdout.write(f'  Role: {user.profile.role}')
                self.stdout.write(f'  Is active: {user.profile.is_active}')
                return

            # Criar UserProfile
            profile = UserProfile.objects.create(
                user=user,
                cpf='00000000000',  # CPF ficticio
                role='ADMIN',
                is_active=True
            )

            self.stdout.write(self.style.SUCCESS('✅ UserProfile criado com sucesso!'))
            self.stdout.write(f'  CPF: {profile.cpf}')
            self.stdout.write(f'  Role: {profile.role}')
            self.stdout.write(f'  Is active: {profile.is_active}')

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Usuario admin nao encontrado!'))
            self.stdout.write('Execute primeiro: python manage.py createsuperuser')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro: {str(e)}'))
