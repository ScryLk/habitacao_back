#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para criar usuario lucas.kepler"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from habitacao.models import UserProfile

try:
    print('=== Criando usuario lucas.kepler ===')

    # Dados do usuario
    username = 'lucas.kepler'
    email = 'lucaskepler991@gmail.com'
    password = '00113150Ll'
    first_name = 'Lucas'
    last_name = 'Kepler'
    cpf = '00000000001'  # CPF ficticio - ajuste se necessario
    role = 'ADMIN'

    # Verificar se usuario ja existe
    if User.objects.filter(username=username).exists():
        print(f'AVISO: Usuario "{username}" ja existe!')
        user = User.objects.get(username=username)
        print(f'  Email: {user.email}')
        print(f'  Is active: {user.is_active}')
        print(f'  Is superuser: {user.is_superuser}')

        if hasattr(user, 'profile'):
            print(f'  Profile exists: YES')
            print(f'    CPF: {user.profile.cpf}')
            print(f'    Role: {user.profile.role}')
        else:
            print(f'  Profile exists: NO')
        sys.exit(0)

    if User.objects.filter(email=email).exists():
        print(f'ERRO: Email "{email}" ja esta em uso!')
        sys.exit(1)

    # Criar usuario como superuser
    print(f'Criando superusuario: {username}')
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    print('✅ Superusuario criado!')

    # Criar UserProfile
    print('Criando UserProfile...')
    profile = UserProfile.objects.create(
        user=user,
        cpf=cpf,
        role=role,
        is_active=True
    )

    print('✅ Usuario criado com sucesso!')
    print(f'  Username: {user.username}')
    print(f'  Email: {user.email}')
    print(f'  Full name: {user.get_full_name()}')
    print(f'  CPF: {profile.cpf}')
    print(f'  Role: {profile.role}')
    print(f'  Superuser: {user.is_superuser}')
    print()
    print('=== CREDENCIAIS ===')
    print(f'Email: {email}')
    print(f'Senha: {password}')

except Exception as e:
    print(f'ERRO: {str(e)}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
