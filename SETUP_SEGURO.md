# 🔒 Guia de Setup Seguro - Sistema Habitação MCMV

## ✅ Implementação Concluída

As seguintes medidas de segurança foram implementadas no sistema:

### 1. Variáveis de Ambiente (.env)

✅ **Arquivo `.env` criado** com:
- SECRET_KEY única gerada aleatoriamente
- Senhas fortes para banco de dados
- Credenciais de admin seguras
- Configurações de JWT
- Todas as variáveis sensíveis isoladas

✅ **Arquivo `.env.example`** - Template para desenvolvimento
✅ **Arquivo `.env.production.example`** - Template para produção

### 2. Proteção no Git

✅ `.env` adicionado ao `.gitignore`
✅ Arquivos de logs, secrets e backups ignorados
✅ Permissão 600 (apenas owner) no arquivo `.env`

### 3. Configurações do Django (settings.py)

✅ Todas as configurações sensíveis usando `python-decouple`
✅ Configurações de segurança para produção:
- SSL/HTTPS
- HSTS
- Security Headers
- CSRF Protection
- XSS Protection

✅ Logging configurável
✅ Upload de arquivos com limite de tamanho

### 4. Docker

✅ `docker-compose.yml` atualizado para usar `.env`
✅ Variáveis de ambiente segregadas por serviço
✅ Health checks configurados
✅ `entrypoint.sh` usando variáveis do `.env`

### 5. Documentação

✅ **[SECURITY.md](SECURITY.md)** - Guia completo de segurança com:
- Gestão de variáveis de ambiente
- Configurações de segurança
- Autenticação e autorização
- Proteção de dados (LGPD)
- Checklist para produção
- Procedimentos de backup
- Resposta a incidentes

### 6. Ferramentas

✅ **[check_security.py](check_security.py)** - Script de verificação de segurança
- Verifica configurações críticas
- Valida arquivo .env
- Checa permissões de arquivos
- Detecta configurações inseguras

---

## 🚀 Como Começar

### 1. Desenvolvimento Local

```bash
# O arquivo .env já está configurado para desenvolvimento
# Você pode usar as credenciais atuais

# Verificar segurança
python3 check_security.py

# Iniciar com Docker
docker-compose up -d --build

# Ver logs
docker-compose logs -f
```

**Credenciais padrão (desenvolvimento):**
- **Admin**: admin / NnzDf7SOVZ8Snu-UiV8n6aSH0_YbQyq_QUdwvbnxw7E
- **Database**: habitacao_user / dFZKZiTvuMosfx-Zn7-7rxnHF-WhxFkAkiwdcaoD4d0

### 2. Preparar para Produção

```bash
# 1. Copiar template de produção
cp .env.production.example .env

# 2. Editar .env com suas configurações
nano .env

# 3. Gerar nova SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 4. Gerar senhas fortes
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 5. Configurar variáveis OBRIGATÓRIAS:
#    - SECRET_KEY (nova, única)
#    - DB_PASSWORD (forte)
#    - MYSQL_ROOT_PASSWORD (forte)
#    - ADMIN_PASSWORD (forte)
#    - ALLOWED_HOSTS (seu domínio)
#    - DEBUG=False
#    - Configurações SSL (True)

# 6. Verificar segurança
python3 check_security.py

# 7. Ajustar permissões
chmod 600 .env

# 8. Deploy
docker-compose up -d --build
```

---

## 🔍 Verificação de Segurança

### Executar Verificação

```bash
python3 check_security.py
```

O script verifica:
- ✅ Existência do arquivo .env
- ✅ Variáveis críticas configuradas
- ✅ Valores não padrão/inseguros
- ✅ Modo DEBUG
- ✅ ALLOWED_HOSTS
- ✅ Configurações SSL
- ✅ .gitignore
- ✅ Permissões de arquivos
- ✅ Arquivos necessários

### Resultado Esperado

```
✓ Arquivo .env: OK
✓ Modo DEBUG: OK
✓ ALLOWED_HOSTS: OK
✓ Configurações SSL: OK
✓ .gitignore: OK
✓ Permissões: OK
✓ Arquivos necessários: OK

Resultado: 7/7 verificações passaram
✓ Todas as verificações passaram!
Sistema pronto para produção.
```

---

## ⚠️ IMPORTANTE - Checklist Antes do Deploy

### Configurações Obrigatórias

- [ ] `DEBUG=False` no .env
- [ ] `SECRET_KEY` única e forte (50+ caracteres)
- [ ] `DB_PASSWORD` forte (16+ caracteres)
- [ ] `MYSQL_ROOT_PASSWORD` forte (16+ caracteres)
- [ ] `ADMIN_PASSWORD` forte (16+ caracteres)
- [ ] `ALLOWED_HOSTS` com domínios corretos (sem localhost)
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] `SECURE_HSTS_SECONDS=31536000`
- [ ] `CORS_ALLOWED_ORIGINS` apenas domínios confiáveis
- [ ] `CSRF_TRUSTED_ORIGINS` apenas domínios HTTPS

### Segurança

- [ ] Arquivo `.env` com permissão 600
- [ ] `.env` está no `.gitignore`
- [ ] Certificado SSL/TLS configurado no Nginx
- [ ] Firewall configurado (apenas portas 22, 80, 443)
- [ ] Backup automático configurado
- [ ] Logs sendo monitorados
- [ ] Script de verificação passou todas as verificações

### Primeiro Acesso

- [ ] Alterar senha do admin após primeiro login
- [ ] Criar usuários reais (não usar admin)
- [ ] Testar fluxo completo da aplicação
- [ ] Verificar logs de erro
- [ ] Testar backup e restore

---

## 🔐 Arquivos de Configuração

### Estrutura de Segurança

```
habitacao-back/
├── .env                          # ⚠️ NUNCA COMMITAR!
├── .env.example                  # Template desenvolvimento
├── .env.production.example       # Template produção
├── .gitignore                    # Protege arquivos sensíveis
├── SECURITY.md                   # Guia completo de segurança
├── SETUP_SEGURO.md              # Este arquivo
├── check_security.py             # Script de verificação
├── core/
│   └── settings.py              # Usa python-decouple
├── docker-compose.yml            # Usa variáveis do .env
└── entrypoint.sh                # Usa variáveis do .env
```

### Hierarquia de Configuração

1. **Variáveis de ambiente** (mais alta prioridade)
2. **Arquivo .env** (prioridade média)
3. **Valores padrão no settings.py** (fallback)

---

## 📊 Variáveis de Ambiente Disponíveis

### Core Django

| Variável | Descrição | Desenvolvimento | Produção |
|----------|-----------|-----------------|----------|
| `SECRET_KEY` | Chave secreta do Django | Auto-gerada | **OBRIGATÓRIA** |
| `DEBUG` | Modo debug | `True` | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost` | Seu domínio |

### Banco de Dados

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DB_ENGINE` | Engine do Django | `django.db.backends.mysql` |
| `DB_NAME` | Nome do banco | `habitacao_db` |
| `DB_USER` | Usuário | `habitacao_user` |
| `DB_PASSWORD` | Senha | **OBRIGATÓRIA** |
| `DB_HOST` | Host | `localhost` (dev) / `db` (docker) |
| `DB_PORT` | Porta | `3306` |

### Segurança

| Variável | Descrição | Desenvolvimento | Produção |
|----------|-----------|-----------------|----------|
| `SECURE_SSL_REDIRECT` | Redirecionar para HTTPS | `False` | `True` |
| `SESSION_COOKIE_SECURE` | Cookie apenas HTTPS | `False` | `True` |
| `CSRF_COOKIE_SECURE` | CSRF apenas HTTPS | `False` | `True` |
| `SECURE_HSTS_SECONDS` | HSTS | `0` | `31536000` |

### JWT

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | Expiração access token | `60` |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | Expiração refresh token | `7` |

### Aplicação

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `ADMIN_USERNAME` | Username do superuser | `admin` |
| `ADMIN_EMAIL` | Email do superuser | `admin@exemplo.com` |
| `ADMIN_PASSWORD` | Senha do superuser | **OBRIGATÓRIA** |
| `MAX_UPLOAD_SIZE_MB` | Tamanho máximo upload | `100` |
| `LOG_LEVEL` | Nível de log | `INFO` |

---

## 🛡️ Boas Práticas Implementadas

### 1. Segregação de Credenciais
✅ Todas as credenciais em `.env`
✅ Não há senhas hardcoded no código
✅ Templates de exemplo sem valores reais

### 2. Defesa em Profundidade
✅ Autenticação JWT
✅ Autorização baseada em roles
✅ CSRF protection
✅ XSS protection
✅ Security headers
✅ Rate limiting (via Nginx)

### 3. Princípio do Menor Privilégio
✅ Usuário MySQL específico (não root)
✅ Permissões de arquivo restritivas
✅ Roles granulares (ADMIN, COORDINATOR, ANALYST, CLERK)

### 4. Auditabilidade
✅ Logs estruturados
✅ Rastreamento de ações (ApplicationActionHistory)
✅ Auditoria de consultas públicas (SearchAudit)

### 5. Resiliência
✅ Health checks em todos os serviços
✅ Restart automático de containers
✅ Procedimentos de backup documentados

---

## 📞 Suporte

### Documentação

- **[SECURITY.md](SECURITY.md)** - Guia completo de segurança
- **[DOCKER_README.md](DOCKER_README.md)** - Guia do Docker
- **[API_README.md](API_README.md)** - Documentação da API
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Guia de testes

### Comandos Úteis

```bash
# Verificar segurança
python3 check_security.py

# Ver configurações carregadas
docker-compose config

# Ver variáveis de ambiente do container
docker-compose exec web env | grep -E "SECRET|DB_|ADMIN"

# Logs de segurança
docker-compose logs web | grep -i "error\|warning\|security"

# Backup rápido
docker-compose exec db mysqldump -u root -p habitacao_db > backup.sql
```

---

## ⚡ Próximos Passos

1. **Testar em ambiente local**
   ```bash
   docker-compose up -d --build
   python3 check_security.py
   ```

2. **Acessar a aplicação**
   - API: http://localhost:8000/api/v1/
   - Swagger: http://localhost:8000/api/v1/swagger/
   - Admin: http://localhost:8000/admin/

3. **Alterar senha do admin**
   - Login: admin
   - Senha: (veja no .env - ADMIN_PASSWORD)

4. **Criar usuários de teste**
   - Testar diferentes roles
   - Verificar permissões

5. **Preparar para produção**
   - Seguir checklist acima
   - Configurar SSL
   - Configurar backup automático
   - Monitorar logs

---

**✅ Sistema seguro e pronto para uso!**

Última atualização: 2025-01-24
