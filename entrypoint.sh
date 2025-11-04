#!/bin/bash
# Entrypoint script para o container Django

set -e

echo "=================================================="
echo "Sistema Habitação MCMV - Iniciando Container"
echo "=================================================="

# Aguardar o MySQL estar pronto
echo "⏳ Aguardando MySQL estar disponível..."
while ! nc -z $DB_HOST $DB_PORT; do
    sleep 1
done
echo "✅ MySQL está pronto!"

# Executar migrations
echo "🔄 Executando migrations..."
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# Criar superusuário se não existir
echo "👤 Verificando superusuário..."
python manage.py shell << EOF
from django.contrib.auth.models import User
from habitacao.models import UserProfile
import os

username = os.getenv('ADMIN_USERNAME', 'admin')
email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
password = os.getenv('ADMIN_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f'✅ Superusuário criado: {username}')

    # Criar UserProfile para o admin
    UserProfile.objects.create(
        user=user,
        cpf='00000000000',  # CPF fictício para admin
        role='ADMIN',
        is_active=True
    )
    print(f'✅ UserProfile criado para {username}')
else:
    print(f'ℹ️  Superusuário "{username}" já existe')

    # Verificar se tem UserProfile
    user = User.objects.get(username=username)
    if not hasattr(user, 'profile'):
        print(f'⚠️  Criando UserProfile para {username}...')
        UserProfile.objects.create(
            user=user,
            cpf='00000000000',  # CPF fictício para admin
            role='ADMIN',
            is_active=True
        )
        print(f'✅ UserProfile criado para {username}')
    else:
        print(f'ℹ️  UserProfile já existe para {username}')
EOF

# Carregar dados iniciais (opcional)
if [ "$LOAD_INITIAL_DATA" = "true" ]; then
    echo "📊 Carregando dados iniciais..."
    python manage.py load_initial_data || true
fi

echo "=================================================="
echo "✅ Inicialização concluída!"
echo "=================================================="

# Executar o comando passado ao container
exec "$@"
