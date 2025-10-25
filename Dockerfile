# Dockerfile para Sistema Habitação MCMV
# Python 3.12 baseado em Alpine para imagem mais leve

FROM python:3.12-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p media staticfiles logs

# Dar permissão de execução ao entrypoint
RUN chmod +x /app/entrypoint.sh

# Coletar arquivos estáticos (será executado no entrypoint)
# RUN python manage.py collectstatic --noinput

# Expor porta
EXPOSE 8000

# Definir entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando padrão
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "core.wsgi:application"]
