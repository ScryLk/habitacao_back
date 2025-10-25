# Guia de Segurança - Sistema Habitação MCMV

## 📋 Índice

1. [Variáveis de Ambiente](#variáveis-de-ambiente)
2. [Configurações de Segurança](#configurações-de-segurança)
3. [Autenticação e Autorização](#autenticação-e-autorização)
4. [Proteção de Dados Sensíveis](#proteção-de-dados-sensíveis)
5. [Boas Práticas](#boas-práticas)
6. [Checklist de Segurança para Produção](#checklist-de-segurança-para-produção)
7. [Monitoramento e Logs](#monitoramento-e-logs)
8. [Backup e Recuperação](#backup-e-recuperação)

---

## 🔐 Variáveis de Ambiente

### Arquivo .env

**NUNCA compartilhe o arquivo `.env` ou faça commit dele no Git!**

O arquivo `.env` contém informações sensíveis do sistema. Um arquivo `.env.example` está disponível como template.

### Variáveis Críticas

#### 1. SECRET_KEY

```bash
SECRET_KEY=sua-chave-secreta-aqui
```

**Importância:** Usada para criptografia, assinatura de tokens e proteção CSRF.

**Geração segura:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**⚠️ NUNCA use a SECRET_KEY padrão em produção!**

#### 2. Senhas do Banco de Dados

```bash
DB_PASSWORD=senha-forte-do-banco
MYSQL_ROOT_PASSWORD=senha-forte-root
```

**Requisitos:**
- Mínimo 16 caracteres
- Letras maiúsculas e minúsculas
- Números e caracteres especiais
- Não use palavras do dicionário

**Geração segura:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 3. Senha do Admin

```bash
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@habitacao.gov.br
ADMIN_PASSWORD=senha-muito-forte
```

**⚠️ Mude a senha padrão imediatamente após o primeiro acesso!**

---

## 🛡️ Configurações de Segurança

### Desenvolvimento vs Produção

#### Desenvolvimento (.env)

```bash
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

#### Produção (.env)

```bash
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### Headers de Segurança

O sistema implementa automaticamente:

- ✅ **X-Content-Type-Options**: `nosniff` - Previne MIME type sniffing
- ✅ **X-Frame-Options**: `DENY` - Previne clickjacking
- ✅ **X-XSS-Protection**: `1; mode=block` - Proteção contra XSS
- ✅ **HSTS**: HTTP Strict Transport Security (em produção)
- ✅ **CSRF Protection**: Proteção contra Cross-Site Request Forgery

---

## 🔑 Autenticação e Autorização

### JWT (JSON Web Tokens)

#### Configuração dos Tokens

```bash
# Tempo de expiração do token de acesso (em minutos)
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60

# Tempo de expiração do token de refresh (em dias)
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

#### Segurança dos Tokens

- ✅ Tokens são assinados com a SECRET_KEY
- ✅ Tokens expiram automaticamente
- ✅ Refresh tokens são rotacionados após uso
- ✅ Tokens antigos são incluídos em blacklist

#### Exemplo de Uso

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "sua-senha"}'

# Usar token
curl -X GET http://localhost:8000/api/v1/beneficiaries \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Níveis de Permissão

| Papel | Descrição | Permissões |
|-------|-----------|------------|
| **ADMIN** | Administrador do sistema | Acesso total, todos os municípios |
| **COORDINATOR** | Coordenador municipal | Gerenciar inscrições do município |
| **ANALYST** | Analista | Revisar e aprovar/rejeitar inscrições |
| **CLERK** | Atendente | Criar e editar inscrições |

---

## 🔒 Proteção de Dados Sensíveis

### Dados Pessoais (LGPD)

O sistema armazena dados sensíveis incluindo:

- CPF
- RG
- NIS
- Dados familiares
- Informações de renda
- Documentos digitalizados

#### Medidas de Proteção

1. **Criptografia em Trânsito**
   - Use HTTPS em produção (SSL/TLS)
   - Certificados válidos e atualizados

2. **Criptografia em Repouso**
   - Banco de dados com senha forte
   - Backups criptografados
   - Volumes Docker isolados

3. **Controle de Acesso**
   - Autenticação obrigatória
   - Autorização baseada em papéis
   - Escopo por município

4. **Logs e Auditoria**
   - Todas as ações são registradas
   - Logs de acesso e modificações
   - Rastreabilidade completa

### Upload de Documentos

```bash
# Tamanho máximo de upload (em MB)
MAX_UPLOAD_SIZE_MB=100
```

**Tipos de arquivos permitidos:**
- PDF
- Imagens (JPG, PNG)
- Documentos do Office

**Armazenamento:**
```
media/
└── beneficiarios/
    └── {cpf}/
        └── {tipo_documento}/
            └── {arquivo}
```

---

## ✅ Boas Práticas

### 1. Senhas Fortes

- **Mínimo 12 caracteres**
- Combinação de letras, números e símbolos
- Não reutilize senhas
- Use gerenciadores de senhas

### 2. Atualizações

```bash
# Atualizar dependências regularmente
pip list --outdated
pip install --upgrade -r requirements.txt

# Atualizar imagens Docker
docker-compose pull
docker-compose up -d --build
```

### 3. Backup Regular

```bash
# Backup do banco de dados
docker-compose exec db mysqldump -u root -p habitacao_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup dos arquivos de mídia
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
```

### 4. Monitoramento

- Monitore logs de erro
- Configure alertas para falhas de login
- Revise logs de acesso regularmente

### 5. Princípio do Menor Privilégio

- Conceda apenas as permissões necessárias
- Revise permissões periodicamente
- Desative contas não utilizadas

---

## 📝 Checklist de Segurança para Produção

### Antes do Deploy

- [ ] Alterar `DEBUG=False` no .env
- [ ] Definir `ALLOWED_HOSTS` com domínios corretos
- [ ] Gerar nova `SECRET_KEY` única
- [ ] Configurar senhas fortes para banco de dados
- [ ] Alterar senha padrão do admin
- [ ] Ativar SSL/TLS (HTTPS)
- [ ] Configurar `SECURE_SSL_REDIRECT=True`
- [ ] Configurar `SESSION_COOKIE_SECURE=True`
- [ ] Configurar `CSRF_COOKIE_SECURE=True`
- [ ] Ativar HSTS (`SECURE_HSTS_SECONDS=31536000`)
- [ ] Configurar CORS para domínios específicos
- [ ] Configurar firewall no servidor
- [ ] Configurar backup automático
- [ ] Testar recuperação de backup
- [ ] Configurar monitoramento de logs
- [ ] Revisar permissões de arquivos
- [ ] Desabilitar portas desnecessárias
- [ ] Configurar rate limiting
- [ ] Implementar IDS/IPS se possível
- [ ] Documentar procedimentos de emergência

### Configurações de Servidor

```bash
# Firewall - Permitir apenas portas necessárias
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable

# Desabilitar root SSH
# Editar /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no  # Use chaves SSH
```

### Nginx com SSL

```nginx
server {
    listen 443 ssl http2;
    server_name seu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Resto da configuração...
}

# Redirect HTTP para HTTPS
server {
    listen 80;
    server_name seu-dominio.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 📊 Monitoramento e Logs

### Configuração de Logs

O sistema gera logs em dois níveis:

#### 1. Logs de Console (Desenvolvimento)

```bash
# Ver logs em tempo real
docker-compose logs -f web
```

#### 2. Logs de Arquivo (Produção)

```bash
# Localização
logs/django_errors.log
docker/nginx/logs/access.log
docker/nginx/logs/error.log
```

#### Nível de Log

```bash
# .env
LOG_LEVEL=INFO
# Opções: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Auditoria

O sistema registra automaticamente:

- **SearchAudit**: Todas as consultas públicas por CPF/protocolo
- **ApplicationActionHistory**: Todas as mudanças de status
- Logs de autenticação (login/logout)
- Modificações em inscrições

```python
# Consultar histórico de ações
from habitacao.models import ApplicationActionHistory

# Ações de um beneficiário
history = ApplicationActionHistory.objects.filter(
    beneficiary_id=1
).order_by('-created_at')
```

### Alertas Recomendados

Configure alertas para:

- ❗ Falhas de login múltiplas (possível ataque)
- ❗ Erros 500 (problemas no servidor)
- ❗ Uso de disco acima de 80%
- ❗ Alta taxa de requisições (possível DDoS)
- ❗ Erros de banco de dados

---

## 💾 Backup e Recuperação

### Estratégia de Backup

#### 1. Backup do Banco de Dados

```bash
# Backup manual
docker-compose exec db mysqldump \
  -u root -p${MYSQL_ROOT_PASSWORD} \
  --single-transaction \
  --routines \
  --triggers \
  habitacao_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup compactado
docker-compose exec db mysqldump \
  -u root -p${MYSQL_ROOT_PASSWORD} \
  habitacao_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

#### 2. Backup dos Arquivos

```bash
# Backup de mídia (documentos)
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/

# Backup completo (incluindo configurações)
tar -czf full_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  media/ \
  .env \
  docker-compose.yml \
  logs/
```

#### 3. Backup Automatizado

Crie um cron job para backups diários:

```bash
# Editar crontab
crontab -e

# Adicionar linha para backup diário às 2h da manhã
0 2 * * * /path/to/backup_script.sh
```

**Script de backup (`backup_script.sh`):**

```bash
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup do banco
docker-compose exec -T db mysqldump \
  -u root -p${MYSQL_ROOT_PASSWORD} \
  habitacao_db | gzip > ${BACKUP_DIR}/db_${DATE}.sql.gz

# Backup de mídia
tar -czf ${BACKUP_DIR}/media_${DATE}.tar.gz media/

# Manter apenas últimos 30 dias
find ${BACKUP_DIR} -name "*.gz" -mtime +30 -delete

echo "Backup concluído: ${DATE}"
```

### Restauração

#### Restaurar Banco de Dados

```bash
# Descompactar se necessário
gunzip backup_20250124.sql.gz

# Restaurar
docker-compose exec -T db mysql \
  -u root -p${MYSQL_ROOT_PASSWORD} \
  habitacao_db < backup_20250124.sql
```

#### Restaurar Arquivos de Mídia

```bash
# Extrair backup
tar -xzf media_backup_20250124.tar.gz

# Reiniciar container web para recarregar arquivos
docker-compose restart web
```

### Teste de Recuperação

**Execute testes mensais de recuperação:**

1. Criar backup
2. Restaurar em ambiente de teste
3. Verificar integridade dos dados
4. Testar funcionalidades críticas
5. Documentar tempo de recuperação

---

## 🚨 Incidentes de Segurança

### Em Caso de Violação

1. **Isolar o sistema imediatamente**
   ```bash
   docker-compose down
   ```

2. **Investigar logs**
   ```bash
   tail -n 1000 logs/django_errors.log
   docker-compose logs web
   ```

3. **Alterar todas as credenciais**
   - SECRET_KEY
   - Senhas de banco de dados
   - Senhas de usuários

4. **Restaurar de backup confiável**

5. **Notificar autoridades competentes** (se dados pessoais foram expostos)

6. **Documentar o incidente**

---

## 📞 Contatos de Emergência

Configure uma lista de contatos para emergências:

- **Responsável técnico**
- **Administrador de sistemas**
- **Responsável pela LGPD**
- **Equipe de suporte**

---

## 📚 Recursos Adicionais

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [LGPD - Lei Geral de Proteção de Dados](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)

---

## 📝 Histórico de Revisões

| Data | Versão | Descrição |
|------|--------|-----------|
| 2025-01-24 | 1.0 | Versão inicial do guia de segurança |

---

**⚠️ IMPORTANTE: Este documento deve ser revisado e atualizado regularmente.**

**Última atualização:** 2025-01-24
