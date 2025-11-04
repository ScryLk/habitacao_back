#!/bin/bash
# Script para criar UserProfile para o usuario admin e lucas.kepler

echo "=== Corrigindo perfis de usuarios ==="

# Criar profile para admin
echo "Criando profile para admin..."
docker-compose exec -T web python manage.py shell << 'EOF'
from django.contrib.auth.models import User
from habitacao.models import UserProfile

# Admin user
try:
    user = User.objects.get(username='admin')
    print(f'Usuario admin encontrado: {user.email}')

    if not hasattr(user, 'profile'):
        profile = UserProfile.objects.create(
            user=user,
            cpf='00000000000',
            role='ADMIN',
            is_active=True
        )
        print(f'✅ UserProfile criado para admin')
    else:
        print(f'ℹ️  UserProfile ja existe para admin')
except User.DoesNotExist:
    print('❌ Usuario admin nao encontrado')
except Exception as e:
    print(f'❌ Erro: {str(e)}')

# Lucas user
try:
    if not User.objects.filter(username='lucas.kepler').exists():
        print('\n=== Criando usuario lucas.kepler ===')
        user = User.objects.create_superuser(
            username='lucas.kepler',
            email='lucaskepler991@gmail.com',
            password='00113150Ll',
            first_name='Lucas',
            last_name='Kepler'
        )

        profile = UserProfile.objects.create(
            user=user,
            cpf='00000000001',
            role='ADMIN',
            is_active=True
        )

        print(f'✅ Usuario lucas.kepler criado com sucesso!')
        print(f'   Email: {user.email}')
        print(f'   Senha: 00113150Ll')
    else:
        print('\nUsuario lucas.kepler ja existe')
        user = User.objects.get(username='lucas.kepler')
        if not hasattr(user, 'profile'):
            profile = UserProfile.objects.create(
                user=user,
                cpf='00000000001',
                role='ADMIN',
                is_active=True
            )
            print(f'✅ UserProfile criado para lucas.kepler')
        else:
            print(f'ℹ️  UserProfile ja existe para lucas.kepler')

except Exception as e:
    print(f'❌ Erro ao criar lucas.kepler: {str(e)}')

print('\n=== Listando todos os usuarios ===')
for u in User.objects.all():
    has_profile = hasattr(u, 'profile')
    role = u.profile.role if has_profile else 'N/A'
    print(f'  {u.username} ({u.email}) - Profile: {has_profile} - Role: {role}')
EOF

echo ""
echo "=== Concluido ==="
