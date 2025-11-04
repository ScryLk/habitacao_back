# -*- coding: utf-8 -*-
"""
Management command para criar um novo usuario com UserProfile
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from habitacao.models import UserProfile


class Command(BaseCommand):
    help = 'Cria um novo usuario com UserProfile'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Username')
        parser.add_argument('--email', type=str, required=True, help='Email')
        parser.add_argument('--password', type=str, required=True, help='Password')
        parser.add_argument('--full-name', type=str, required=True, help='Full name')
        parser.add_argument('--cpf', type=str, required=True, help='CPF')
        parser.add_argument('--role', type=str, default='ADMIN', help='Role (ADMIN, COORDINATOR, ANALYST, OPERATOR)')
        parser.add_argument('--superuser', action='store_true', help='Create as superuser')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        full_name = options['full_name']
        cpf = options['cpf']
        role = options['role']
        is_superuser = options['superuser']

        try:
            # Verificar se usuario ja existe
            if User.objects.filter(username=username).exists():
                raise CommandError(f'Usuario "{username}" ja existe!')

            if User.objects.filter(email=email).exists():
                raise CommandError(f'Email "{email}" ja esta em uso!')

            if UserProfile.objects.filter(cpf=cpf).exists():
                raise CommandError(f'CPF "{cpf}" ja esta cadastrado!')

            # Dividir nome
            name_parts = full_name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            # Criar usuario
            if is_superuser:
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                self.stdout.write(self.style.SUCCESS(f'✅ Superusuario criado: {username}'))
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                self.stdout.write(self.style.SUCCESS(f'✅ Usuario criado: {username}'))

            # Criar UserProfile
            profile = UserProfile.objects.create(
                user=user,
                cpf=cpf,
                role=role,
                is_active=True
            )

            self.stdout.write(self.style.SUCCESS('✅ UserProfile criado com sucesso!'))
            self.stdout.write(f'  Username: {user.username}')
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  Full name: {user.get_full_name()}')
            self.stdout.write(f'  CPF: {profile.cpf}')
            self.stdout.write(f'  Role: {profile.role}')
            self.stdout.write(f'  Superuser: {user.is_superuser}')

        except Exception as e:
            raise CommandError(f'Erro ao criar usuario: {str(e)}')
