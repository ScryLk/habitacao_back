# 🐳 Docker - Sistema Habitação MCMV

## 📋 Pré-requisitos

- Docker Engine 20.10+
- Docker Compose 2.0+

### Instalação do Docker

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**MacOS:**
```bash
brew install docker docker-compose
```

**Windows:**
Baixe o Docker Desktop em: https://www.docker.com/products/docker-desktop

---

## 🚀 Início Rápido

### 1. Clone o Repositório

```bash
git clone <repository-url>
cd habitacao-back
```

### 2. Configure as Variáveis de Ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` conforme necessário:

```bash
nano .env
```

**Variáveis importantes:**
- `SECRET_KEY`: Chave secreta do Django (mude em produção!)
- `DEBUG`: `True` para dev, `False` para produção
- `DB_PASSWORD`: Senha do banco de dados
- `ADMIN_PASSWORD`: Senha do superusuário admin

### 3. Inicie os Containers

```bash
# Construir e iniciar todos os serviços
docker-compose up -d --build

# Ver logs
docker-compose logs -f
```

### 4. Acesse a Aplicação

- **API**: http://localhost:8000/api/v1/
- **Swagger**: http://localhost:8000/api/v1/swagger/
- **Django Admin**: http://localhost:8000/admin/
- **MySQL**: localhost:3307 (externo)

**Credenciais padrão:**
- Username: `admin`
- Password: `admin123` (ou o definido em `ADMIN_PASSWORD`)

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                     NGINX (Port 80)                  │
│               Reverse Proxy & Static Files           │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌────────▼────────┐
│   Django Web   │    │   Static/Media  │
│   (Port 8000)  │    │     Volumes     │
└───────┬────────┘    └─────────────────┘
        │
┌───────▼────────┐    ┌─────────────────┐
│   MySQL DB     │    │   Redis Cache   │
│  (Port 3306)   │    │   (Port 6379)   │
└────────────────┘    └─────────────────┘
```

## 📦 Serviços

### 1. **web** - Aplicação Django
- **Imagem**: Construída a partir do Dockerfile
- **Porta**: 8000
- **Comando**: Gunicorn com 3 workers
- **Volumes**:
  - Código da aplicação
  - Media files
  - Static files
  - Logs

### 2. **db** - MySQL 8.0
- **Imagem**: mysql:8.0
- **Porta externa**: 3307
- **Porta interna**: 3306
- **Volume**: mysql_data (persistente)

### 3. **nginx** - Reverse Proxy
- **Imagem**: nginx:alpine
- **Portas**: 80, 443
- **Função**:
  - Servir arquivos estáticos
  - Proxy reverso para Django
  - Compressão gzip
  - Cache de arquivos

### 4. **redis** - Cache (Opcional)
- **Imagem**: redis:7-alpine
- **Porta**: 6379
- **Volume**: redis_data (persistente)

---

## 📝 Comandos Úteis

### Gerenciamento de Containers

```bash
# Iniciar todos os serviços
docker-compose up -d

# Parar todos os serviços
docker-compose down

# Parar e remover volumes (⚠️ apaga dados!)
docker-compose down -v

# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f web
docker-compose logs -f db

# Reiniciar um serviço
docker-compose restart web

# Ver status dos containers
docker-compose ps
```

### Django Management Commands

```bash
# Executar comando Django
docker-compose exec web python manage.py <comando>

# Migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Criar superusuário manualmente
docker-compose exec web python manage.py createsuperuser

# Shell interativo
docker-compose exec web python manage.py shell

# Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Carregar dados iniciais
docker-compose exec web python manage.py load_initial_data
```

### Banco de Dados

```bash
# Acessar MySQL via linha de comando
docker-compose exec db mysql -u habitacao_user -p habitacao_db

# Backup do banco
docker-compose exec db mysqldump -u habitacao_user -p habitacao_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
docker-compose exec -T db mysql -u habitacao_user -p habitacao_db < backup.sql

# Ver logs do MySQL
docker-compose logs -f db
```

### Debugging

```bash
# Acessar shell do container
docker-compose exec web bash
docker-compose exec db bash

# Ver processos em execução
docker-compose exec web ps aux

# Ver variáveis de ambiente
docker-compose exec web env

# Verificar conectividade com MySQL
docker-compose exec web nc -zv db 3306

# Tail de logs em tempo real
docker-compose logs -f --tail=100 web
```

---

## 🔧 Troubleshooting

### Problema: Container web não inicia

**Solução:**
```bash
# Ver logs detalhados
docker-compose logs web

# Verificar se MySQL está pronto
docker-compose exec db mysqladmin ping -h localhost -u root -p

# Reconstruir imagem
docker-compose up -d --build --force-recreate web
```

### Problema: Erro de permissão nos volumes

**Solução:**
```bash
# Ajustar permissões
sudo chown -R $USER:$USER media/ staticfiles/ logs/

# Recriar volumes
docker-compose down -v
docker-compose up -d
```

### Problema: "Access denied for user"

**Solução:**
```bash
# Verificar variáveis de ambiente
docker-compose exec web env | grep DB_

# Recriar banco de dados
docker-compose down -v
docker-compose up -d db
# Aguardar 30 segundos
docker-compose up -d web
```

### Problema: Porta 8000 já em uso

**Solução:**
```bash
# Mudar porta no .env
echo "WEB_PORT=8001" >> .env
docker-compose up -d
```

### Problema: Migrations não aplicadas

**Solução:**
```bash
# Forçar migrations
docker-compose exec web python manage.py migrate --run-syncdb

# Ver status das migrations
docker-compose exec web python manage.py showmigrations
```

---

## 🔒 Segurança em Produção

### 1. Variáveis de Ambiente

✅ **Nunca commite o arquivo `.env`**

```bash
# Adicione ao .gitignore
echo ".env" >> .gitignore
```

### 2. Secret Key

Gere uma nova secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Adicione ao `.env`:
```
SECRET_KEY=sua-chave-super-secreta-aqui
```

### 3. HTTPS

Descomente a configuração SSL no `docker/nginx/conf.d/habitacao.conf` e adicione certificados:

```bash
# Criar diretório para certificados
mkdir -p docker/nginx/ssl

# Adicionar certificados
cp seu_certificado.crt docker/nginx/ssl/habitacao.crt
cp sua_chave.key docker/nginx/ssl/habitacao.key

# Reiniciar nginx
docker-compose restart nginx
```

### 4. Firewall

```bash
# Permitir apenas portas necessárias
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 5. Debug = False

Em produção, sempre:
```env
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com
```

---

## 📊 Monitoramento

### Health Checks

```bash
# Verificar saúde dos containers
docker-compose ps

# Health check do web
curl http://localhost:8000/api/v1/swagger/

# Health check do nginx
curl http://localhost/health/

# Health check do MySQL
docker-compose exec db mysqladmin ping -h localhost -u root -p

# Health check do Redis
docker-compose exec redis redis-cli ping
```

### Logs

```bash
# Logs centralizados
docker-compose logs -f --tail=100

# Logs do Django
tail -f logs/django.log

# Logs do Nginx
tail -f docker/nginx/logs/access.log
tail -f docker/nginx/logs/error.log
```

### Métricas

```bash
# Uso de recursos
docker stats

# Espaço em disco
docker system df

# Limpeza
docker system prune -a --volumes
```

---

## 🚀 Deploy em Produção

### 1. Preparar Servidor

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clonar e Configurar

```bash
git clone <repository-url>
cd habitacao-back
cp .env.example .env
nano .env  # Configurar variáveis de produção
```

### 3. Iniciar Serviços

```bash
# Build e start
docker-compose -f docker-compose.yml up -d --build

# Verificar status
docker-compose ps
docker-compose logs -f
```

### 4. Configurar SSL (Let's Encrypt)

```bash
# Instalar certbot
sudo apt install certbot

# Gerar certificado
sudo certbot certonly --standalone -d seudominio.com -d www.seudominio.com

# Copiar certificados
sudo cp /etc/letsencrypt/live/seudominio.com/fullchain.pem docker/nginx/ssl/habitacao.crt
sudo cp /etc/letsencrypt/live/seudominio.com/privkey.pem docker/nginx/ssl/habitacao.key

# Recarregar nginx
docker-compose restart nginx
```

### 5. Auto-renovação SSL

```bash
# Adicionar ao crontab
sudo crontab -e

# Adicionar linha:
0 3 * * * certbot renew --quiet && docker-compose -f /path/to/habitacao-back/docker-compose.yml restart nginx
```

---

## 🔄 Backup e Restore

### Backup Completo

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup do banco
docker-compose exec -T db mysqldump -u habitacao_user -p${DB_PASSWORD} habitacao_db > $BACKUP_DIR/database.sql

# Backup dos arquivos
tar -czf $BACKUP_DIR/media.tar.gz media/
tar -czf $BACKUP_DIR/staticfiles.tar.gz staticfiles/

# Backup do .env
cp .env $BACKUP_DIR/

echo "Backup completo em: $BACKUP_DIR"
```

### Restore

```bash
#!/bin/bash
# restore.sh

BACKUP_DIR=$1

# Restore do banco
docker-compose exec -T db mysql -u habitacao_user -p${DB_PASSWORD} habitacao_db < $BACKUP_DIR/database.sql

# Restore dos arquivos
tar -xzf $BACKUP_DIR/media.tar.gz
tar -xzf $BACKUP_DIR/staticfiles.tar.gz

# Reiniciar serviços
docker-compose restart

echo "Restore concluído!"
```

---

## 📚 Volumes Persistentes

```bash
# Listar volumes
docker volume ls | grep habitacao

# Inspecionar volume
docker volume inspect habitacao-back_mysql_data

# Backup de volume
docker run --rm -v habitacao-back_mysql_data:/data -v $(pwd):/backup ubuntu tar czf /backup/mysql_data_backup.tar.gz /data

# Restore de volume
docker run --rm -v habitacao-back_mysql_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/mysql_data_backup.tar.gz -C /data --strip 1
```

---

## 🎯 Checkllist de Deploy

- [ ] Configurar `.env` com valores de produção
- [ ] Gerar nova SECRET_KEY
- [ ] Definir DEBUG=False
- [ ] Configurar ALLOWED_HOSTS correto
- [ ] Definir senhas fortes (DB, ADMIN)
- [ ] Configurar backup automático
- [ ] Configurar SSL/HTTPS
- [ ] Configurar firewall
- [ ] Testar health checks
- [ ] Configurar monitoramento
- [ ] Documentar credenciais em local seguro
- [ ] Testar restore de backup

---

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs: `docker-compose logs -f`
2. Consulte este README
3. Verifique a documentação oficial do Docker

---

**Sistema Habitação MCMV** - Docker Setup v1.0
