# Guia de Acesso ao Sistema Habitacao

## URLs de Acesso

### HTTP (sem SSL)
- http://habitacao.pbi.local
- http://habitacao.pbi.local/api/v1/swagger/
- http://177.22.80.2
- http://localhost

### HTTPS (com SSL auto-assinado)
- https://habitacao.pbi.local
- https://habitacao.pbi.local/api/v1/swagger/
- https://177.22.80.2
- https://localhost

## Redirecionamento Automático

Quando você acessar a raiz do site (por exemplo, `http://habitacao.pbi.local` ou `https://habitacao.pbi.local`), você será automaticamente redirecionado para a documentação Swagger em `/api/v1/swagger/`.

## Certificado SSL Auto-Assinado

O sistema está configurado com um certificado SSL auto-assinado para desenvolvimento. Isso significa que:

1. **Seu navegador vai mostrar um aviso de segurança** na primeira vez que acessar via HTTPS
2. Você precisará aceitar o risco e continuar
3. Isso é normal em ambiente de desenvolvimento

### Como aceitar o certificado:

#### Chrome/Edge:
1. Clique em "Avançado" ou "Advanced"
2. Clique em "Continuar para habitacao.pbi.local (não seguro)" ou "Proceed to habitacao.pbi.local (unsafe)"

#### Firefox:
1. Clique em "Avançado" ou "Advanced"
2. Clique em "Aceitar o risco e continuar" ou "Accept the Risk and Continue"

#### Safari:
1. Clique em "Mostrar detalhes" ou "Show Details"
2. Clique em "visitar este site" ou "visit this website"

## Configuração do DNS Local

Para que `habitacao.pbi.local` funcione, você precisa adicionar uma entrada no arquivo hosts do seu sistema:

### Windows:
1. Abra o Notepad como Administrador
2. Abra o arquivo `C:\Windows\System32\drivers\etc\hosts`
3. Adicione a linha:
   ```
   177.22.80.2  habitacao.pbi.local
   ```
4. Salve o arquivo

### Linux/Mac:
1. Abra o terminal
2. Execute: `sudo nano /etc/hosts`
3. Adicione a linha:
   ```
   177.22.80.2  habitacao.pbi.local
   ```
4. Salve (Ctrl+O, Enter, Ctrl+X)

## Endpoints Disponíveis

### Documentação:
- `/api/v1/swagger/` - Swagger UI
- `/api/v1/redoc/` - ReDoc
- `/api/v1/swagger.json` - OpenAPI Schema JSON

### Autenticação:
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/register` - Registro
- `GET /api/v1/me` - Dados do usuário atual

### Dashboard:
- `GET /api/v1/dashboard` - Overview do dashboard
- `GET /api/v1/dashboard/municipality` - Estatísticas do município
- `GET /api/v1/dashboard/my-assignments` - Minhas atribuições

### Público (sem autenticação):
- `GET /api/v1/public/status` - Status público
- `POST /api/v1/public/beneficiaries` - Criar beneficiário
- `POST /api/v1/public/documents` - Upload de documento

### ViewSets:
- `/api/v1/beneficiaries/` - Gerenciar beneficiários
- `/api/v1/municipalities/` - Municípios
- `/api/v1/priority-criteria/` - Critérios de prioridade
- `/api/v1/social-benefits/` - Benefícios sociais
- `/api/v1/document-types/` - Tipos de documento
- `/api/v1/documents/` - Documentos
- `/api/v1/users/` - Usuários
- `/api/v1/admin/` - Admin panel

## Portas dos Serviços

- **NGINX HTTP**: 80
- **NGINX HTTPS**: 443
- **Django (interno)**: 8000
- **MySQL**: 3307 (mapeado para 3306 interno)
- **Redis**: 6379

## Verificar Status dos Containers

```bash
docker compose ps
```

## Ver Logs

```bash
# Todos os serviços
docker compose logs -f

# Apenas NGINX
docker compose logs -f nginx

# Apenas Django
docker compose logs -f web

# Apenas MySQL
docker compose logs -f db
```

## Reiniciar Serviços

```bash
# Reiniciar todos
docker compose restart

# Reiniciar apenas nginx
docker compose restart nginx

# Reiniciar apenas web
docker compose restart web
```

## Problemas Comuns

### 1. "ERR_CONNECTION_REFUSED"
- Verifique se os containers estão rodando: `docker compose ps`
- Verifique se o nginx está escutando na porta correta: `docker compose logs nginx`

### 2. "404 Not Found"
- Verifique se você está acessando a URL correta com `/api/v1/` no caminho
- Ou simplesmente acesse a raiz (`/`) que será redirecionado automaticamente

### 3. "CSRF verification failed"
- Certifique-se de que o domínio está em `CSRF_TRUSTED_ORIGINS` no arquivo `.env`

### 4. "CORS error"
- Certifique-se de que a origem do frontend está em `CORS_ALLOWED_ORIGINS` no arquivo `.env`

### 5. "SSL Certificate Error"
- Isso é esperado com certificados auto-assinados
- Aceite o risco no navegador (veja instruções acima)

## Credenciais Padrão do Admin

As credenciais estão no arquivo `.env`:
- Username: admin
- Email: admin@habitacao.gov.br
- Password: (veja ADMIN_PASSWORD no .env)

## Frontend

Se você tiver um frontend rodando em `https://177.22.80.2:5174`, ele já está configurado para fazer requisições para este backend via CORS.
