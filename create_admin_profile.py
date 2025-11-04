#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para criar UserProfile para o usuario admin"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from habitacao.models import UserProfile

try:
    print('=== Criando UserProfile para admin ===')

    # Buscar usuario admin
    user = User.objects.get(username='admin')
    print(f'Usuario encontrado: {user.username} ({user.email})')

    # Verificar se ja tem profile
    if hasattr(user, 'profile'):
        print('AVISO: UserProfile ja existe!')
        print(f'  CPF: {user.profile.cpf}')
        print(f'  Role: {user.profile.role}')
        print(f'  Is active: {user.profile.is_active}')
        sys.exit(0)

    # Criar UserProfile
    profile = UserProfile.objects.create(
        user=user,
        cpf='00000000000',  # CPF ficticio
        role='ADMIN',
        is_active=True
    )

    print('✅ UserProfile criado com sucesso!')
    print(f'  CPF: {profile.cpf}')
    print(f'  Role: {profile.role}')
    print(f'  Is active: {profile.is_active}')

except User.DoesNotExist:
    print('ERRO: Usuario admin nao encontrado!')
    print('Execute primeiro: python manage.py createsuperuser')
    sys.exit(1)
except Exception as e:
    print(f'ERRO: {str(e)}')
    sys.exit(1)
