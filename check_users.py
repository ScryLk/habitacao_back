#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para verificar usuarios no banco de dados"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from habitacao.models import UserProfile

print('=== VERIFICANDO USUÁRIOS ===')
users = User.objects.all()
print(f'Total de usuários: {users.count()}\n')

for user in users:
    print(f'Usuário: {user.username}')
    print(f'  Email: {user.email}')
    print(f'  Is active: {user.is_active}')
    print(f'  Is superuser: {user.is_superuser}')

    try:
        profile = user.profile
        print(f'  Tem profile: SIM')
        print(f'    CPF: {profile.cpf}')
        print(f'    Role: {profile.role}')
        print(f'    Is active (profile): {profile.is_active}')
        print(f'    Municipality: {profile.municipality_id}')
    except UserProfile.DoesNotExist:
        print(f'  Tem profile: NÃO ❌')

    print()
