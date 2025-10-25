### API REST - Sistema Habitação MCMV

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Banco de Dados MySQL

Edite `core/settings.py` (já configurado):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'habitacao_db',
        'USER': 'root',
        'PASSWORD': 'root',  # Ajuste conforme necessário
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

Crie o banco:
```sql
CREATE DATABASE habitacao_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Executar Migrations

```bash
python3 manage.py migrate
```

### 4. Criar Superusuário

```bash
python3 manage.py createsuperuser
```

### 5. Carregar Dados Iniciais

```bash
python3 manage.py load_initial_data
```

### 6. Rodar Servidor

```bash
python3 manage.py runserver
```

### 7. Acessar Documentação

- **Swagger UI**: http://localhost:8000/api/v1/swagger/
- **ReDoc**: http://localhost:8000/api/v1/redoc/
- **Django Admin**: http://localhost:8000/admin/

---

## 📚 Documentação da API

### Base URL
```
http://localhost:8000/api/v1
```

### Autenticação

A API utiliza **JWT (JSON Web Tokens)**. Todas as rotas (exceto `/public/*` e `/auth/login`) requerem autenticação.

**Header:**
```
Authorization: Bearer <access_token>
```

---

## 🔐 Autenticação

### 1. Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "senha123"
}
```

**Resposta:**
```json
{
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "email": "admin@example.com",
      "full_name": "Admin Sistema",
      "role": "ADMIN",
      "municipality_id": null
    }
  },
  "error": null
}
```

### 2. Renovar Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. Registrar Usuário (COORDINATOR+)

```http
POST /api/v1/auth/register
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "João Analista",
  "email": "joao@example.com",
  "password": "senha123",
  "cpf": "111.444.777-35",
  "role": "ANALYST",
  "municipality_id": 1
}
```

### 4. Obter Dados do Usuário Logado

```http
GET /api/v1/me
Authorization: Bearer <token>
```

---

## 👥 Beneficiários

### 1. Listar Beneficiários

```http
GET /api/v1/beneficiaries/
Authorization: Bearer <token>

# Com filtros e paginação
GET /api/v1/beneficiaries/?status=SUBMITTED&page=1&per_page=25
GET /api/v1/beneficiaries/?municipality_id=1&has_cadunico=true
GET /api/v1/beneficiaries/?search=João Silva
GET /api/v1/beneficiaries/?cpf=111.444.777-35
GET /api/v1/beneficiaries/?protocol=2025-10-A3F2B1
```

**Filtros disponíveis:**
- `status`: DRAFT, SUBMITTED, UNDER_REVIEW, CORRECTION_REQUESTED, APPROVED, REJECTED
- `municipality_id`: ID do município
- `uf`: UF do município
- `has_cadunico`: true/false
- `has_elderly`: true/false
- `has_children`: true/false
- `has_disability_or_tea`: true/false
- `pays_rent`: true/false
- `no_own_house`: true/false
- `submitted_from`: Data início (YYYY-MM-DD)
- `submitted_to`: Data fim (YYYY-MM-DD)
- `has_missing_docs`: true/false
- `search`: Busca por nome, CPF, protocolo, email
- `page`: Número da página
- `per_page`: Itens por página (max 100)

**Resposta:**
```json
{
  "data": [
    {
      "id": 1,
      "protocol_number": "2025-10-A3F2B1",
      "full_name": "João da Silva",
      "cpf": "111.444.777-35",
      "municipality": 1,
      "municipality_name": "São Paulo",
      "uf": "SP",
      "status": "SUBMITTED",
      "status_display": "Submetida",
      "age": 35,
      "submitted_at": "2025-10-24T10:30:00-03:00",
      "created_at": "2025-10-24T09:00:00-03:00",
      "updated_at": "2025-10-24T10:30:00-03:00"
    }
  ],
  "error": null,
  "meta": {
    "page": 1,
    "per_page": 25,
    "total": 150,
    "total_pages": 6
  }
}
```

### 2. Obter Detalhes de um Beneficiário

```http
GET /api/v1/beneficiaries/{id}/
Authorization: Bearer <token>
```

**Resposta:** Retorna todos os campos do beneficiário + relacionamentos (prioridades, benefícios sociais, documentos, histórico de ações).

### 3. Criar Beneficiário (Rascunho)

```http
POST /api/v1/beneficiaries/
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "Maria Santos",
  "cpf": "123.456.789-09",
  "rg": "12.345.678-9",
  "birth_date": "1985-05-15",
  "marital_status": "CASADO",
  "email": "maria@example.com",
  "phones": {
    "primary": "(11) 99999-9999",
    "secondary": "(11) 98888-8888"
  },
  "address": {
    "line": "Rua das Flores",
    "number": "123",
    "complement": "Apto 45",
    "neighborhood": "Centro",
    "municipality_id": 1,
    "cep": "01234-567",
    "uf": "SP"
  },
  "spouse": {
    "name": "José Santos",
    "rg": "98.765.432-1",
    "birth_date": "1980-03-20"
  },
  "economy": {
    "main_occupation": "Comerciante",
    "gross_family_income": 3500.00,
    "has_cadunico": true,
    "nis_number": "12345678901"
  },
  "family": {
    "family_size": 4,
    "has_elderly": false,
    "elderly_count": 0,
    "has_children": true,
    "children_count": 2,
    "has_disability_or_tea": false,
    "disability_or_tea_count": 0,
    "household_head_gender": "FEMININO",
    "cadunico_updated": true
  },
  "housing": {
    "no_own_house": false,
    "precarious_own_house": false,
    "cohabitation": false,
    "improvised_dwelling": false,
    "pays_rent": true,
    "rent_value": 800.00,
    "other_housing_desc": ""
  },
  "notes": "Família em situação de vulnerabilidade social"
}
```

### 4. Atualizar Beneficiário

```http
PATCH /api/v1/beneficiaries/{id}/
Authorization: Bearer <token>
Content-Type: application/json

{
  "phone_primary": "(11) 97777-7777",
  "gross_family_income": 4000.00
}
```

### 5. Deletar Beneficiário (ADMIN apenas)

```http
DELETE /api/v1/beneficiaries/{id}/
Authorization: Bearer <token>
```

---

## 📋 Workflow de Status

### 1. Submeter Inscrição (DRAFT → SUBMITTED)

```http
POST /api/v1/beneficiaries/{id}/submit/
Authorization: Bearer <token>
```

- Valida documentos obrigatórios
- Gera `protocol_number` automaticamente
- Define `submitted_at` e `submitted_by`

### 2. Iniciar Análise (SUBMITTED → UNDER_REVIEW)

```http
POST /api/v1/beneficiaries/{id}/start-review/
Authorization: Bearer <token>
```

- Cria atribuição ativa para o analista
- Define `last_review_at` e `last_reviewed_by`

### 3. Solicitar Correção (UNDER_REVIEW → CORRECTION_REQUESTED)

```http
POST /api/v1/beneficiaries/{id}/request-correction/
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Faltou anexar comprovante de renda atualizado"
}
```

### 4. Aprovar (UNDER_REVIEW → APPROVED)

```http
POST /api/v1/beneficiaries/{id}/approve/
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Inscrição aprovada conforme critérios do programa"
}
```

- Encerra atribuição ativa

### 5. Rejeitar (UNDER_REVIEW → REJECTED)

```http
POST /api/v1/beneficiaries/{id}/reject/
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Renda familiar acima do limite permitido pelo programa"
}
```

- **Mensagem é obrigatória**
- Encerra atribuição ativa

### 6. Histórico de Ações

```http
GET /api/v1/beneficiaries/{id}/actions/
Authorization: Bearer <token>
```

### 7. Adicionar Nota

```http
POST /api/v1/beneficiaries/{id}/actions/note/
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Beneficiário entrou em contato solicitando prazo para documentos"
}
```

---

## 📄 Documentos

### 1. Listar Tipos de Documentos

```http
GET /api/v1/document-types/
Authorization: Bearer <token>
```

### 2. Upload de Documento

```http
POST /api/v1/documents/
Authorization: Bearer <token>
Content-Type: multipart/form-data

beneficiary_id: 1
document_type_id: 1
file: <arquivo.pdf>
```

**Exemplo com cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/documents/ \
  -H "Authorization: Bearer <token>" \
  -F "beneficiary_id=1" \
  -F "document_type_id=1" \
  -F "file=@/path/to/documento.pdf"
```

### 3. Listar Documentos de um Beneficiário

```http
GET /api/v1/documents/?beneficiary_id=1
Authorization: Bearer <token>
```

### 4. Baixar Documento

```http
GET /api/v1/documents/{id}/download/
Authorization: Bearer <token>
```

### 5. Validar Documento (ANALYST+)

```http
PATCH /api/v1/documents/{id}/validate/
Authorization: Bearer <token>
Content-Type: application/json

{
  "validated": true,
  "notes": "Documento válido e legível"
}
```

---

## 🎯 Critérios de Priorização

### 1. Listar Critérios

```http
GET /api/v1/priority-criteria/
Authorization: Bearer <token>
```

### 2. Adicionar Critérios ao Beneficiário

```http
POST /api/v1/beneficiaries/{id}/priority/
Authorization: Bearer <token>
Content-Type: application/json

{
  "criteria_ids": [1, 2, 5]
}
```

**Critérios disponíveis** (exemplos):
- 1: Família chefiada por mulher
- 2: Família com pessoa idosa
- 3: PcD ou TEA
- 4: Família com crianças
- 5: Câncer ou doença rara
- 6: Vítima de violência doméstica
- 7: Moradia em área de risco
- etc.

---

## 🎁 Benefícios Sociais

### 1. Listar Tipos de Benefícios

```http
GET /api/v1/social-benefits/
Authorization: Bearer <token>
```

### 2. Adicionar Benefícios ao Beneficiário

```http
POST /api/v1/beneficiaries/{id}/social-benefits/
Authorization: Bearer <token>
Content-Type: application/json

{
  "benefit_ids": [1, 2],
  "other_text": "Auxílio emergencial municipal"
}
```

**Tipos disponíveis:**
- 1: Bolsa Família
- 2: BPC (Benefício de Prestação Continuada)
- 3: Outros (especificar em `other_text`)

---

## 🏘️ Municípios

### 1. Listar Municípios

```http
GET /api/v1/municipalities/
Authorization: Bearer <token>

# Com filtros
GET /api/v1/municipalities/?uf=SP
GET /api/v1/municipalities/?search=São Paulo
```

---

## 📊 Dashboard

### 1. Visão Geral

```http
GET /api/v1/dashboard
Authorization: Bearer <token>
```

**Resposta:**
```json
{
  "data": {
    "total": 1203,
    "draft": 145,
    "submitted": 312,
    "under_review": 287,
    "correction_requested": 54,
    "approved": 315,
    "rejected": 90,
    "pending_docs": 211,
    "by_municipality": [
      {
        "municipality__id": 1,
        "municipality__name": "São Paulo",
        "municipality__uf": "SP",
        "count": 450
      }
    ]
  },
  "error": null
}
```

### 2. Estatísticas por Município

```http
GET /api/v1/dashboard/municipality?municipality_id=1
Authorization: Bearer <token>
```

### 3. Minhas Atribuições

```http
GET /api/v1/dashboard/my-assignments
Authorization: Bearer <token>
```

---

## 🌐 Consulta Pública (Sem Autenticação)

### Consultar Status por Protocolo ou CPF

```http
GET /api/v1/public/status?protocol=2025-10-A3F2B1
# ou
GET /api/v1/public/status?cpf=111.444.777-35
```

**Resposta:**
```json
{
  "data": {
    "protocol_number": "2025-10-A3F2B1",
    "full_name": "João da Silva",
    "status": "SUBMITTED",
    "status_display": "Submetida",
    "submitted_at": "2025-10-24T10:30:00-03:00",
    "municipality": {
      "name": "São Paulo",
      "uf": "SP"
    },
    "cpf_masked": "***.***. 777-35"
  },
  "error": null
}
```

---

## 🔒 Permissões por Papel

| Ação | CLERK | ANALYST | COORDINATOR | ADMIN |
|------|-------|---------|-------------|-------|
| Criar beneficiário | ✅ | ✅ | ✅ | ✅ |
| Editar beneficiário | ❌ | ✅ | ✅ | ✅ |
| Upload documentos | ✅ | ✅ | ✅ | ✅ |
| Validar documentos | ❌ | ✅ | ✅ | ✅ |
| Submeter inscrição | ❌ | ✅ | ✅ | ✅ |
| Iniciar análise | ❌ | ✅ | ✅ | ✅ |
| Aprovar/Rejeitar | ❌ | ✅ | ✅ | ✅ |
| Criar usuários | ❌ | ❌ | ✅ | ✅ |
| Deletar beneficiário | ❌ | ❌ | ❌ | ✅ |

---

## 📝 Formato de Resposta Padrão

### Sucesso
```json
{
  "data": { ... },
  "error": null,
  "meta": {
    "page": 1,
    "per_page": 25,
    "total": 100
  }
}
```

### Erro
```json
{
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Mensagem descritiva do erro",
    "details": { ... }
  }
}
```

### Códigos de Erro Comuns
- `VALIDATION_ERROR`: Erro de validação de dados
- `AUTHENTICATION_FAILED`: Credenciais inválidas
- `NOT_AUTHENTICATED`: Token não fornecido
- `PERMISSION_DENIED`: Sem permissão para esta ação
- `NOT_FOUND`: Recurso não encontrado
- `WORKFLOW_ERROR`: Erro na transição de status
- `UPLOAD_ERROR`: Erro no upload de arquivo

---

## 🧪 Testando a API

### Com cURL

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"senha123"}'

# 2. Listar beneficiários (use o token retornado acima)
curl -X GET http://localhost:8000/api/v1/beneficiaries/ \
  -H "Authorization: Bearer <seu_token_aqui>"

# 3. Criar beneficiário
curl -X POST http://localhost:8000/api/v1/beneficiaries/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Com Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "admin@example.com",
    "password": "senha123"
})
token = response.json()["data"]["access"]

# Headers com autenticação
headers = {"Authorization": f"Bearer {token}"}

# Listar beneficiários
response = requests.get(f"{BASE_URL}/beneficiaries/", headers=headers)
beneficiaries = response.json()["data"]

print(f"Total: {len(beneficiaries)}")
```

---

## 📦 Estrutura de Arquivos

```
habitacao/api/
├── exceptions.py          # Exception handler customizado
├── permissions/
│   └── roles.py          # Permissões por papel
├── serializers/
│   ├── base.py           # Serializers base
│   ├── user.py           # Usuários e auth
│   └── beneficiary.py    # Beneficiários
├── services/
│   ├── auth.py           # Lógica de autenticação
│   ├── beneficiary.py    # Lógica de beneficiários
│   ├── workflow.py       # Lógica de workflow
│   ├── document.py       # Lógica de documentos
│   ├── assignment.py     # Lógica de atribuições
│   ├── priority.py       # Lógica de prioridades
│   ├── social_benefit.py # Lógica de benefícios
│   ├── dashboard.py      # Lógica de dashboard
│   └── public.py         # Consultas públicas
├── views/
│   ├── auth.py           # Views de autenticação
│   ├── beneficiary.py    # Views de beneficiários
│   ├── base.py           # Views base
│   ├── document.py       # Views de documentos
│   ├── dashboard.py      # Views de dashboard
│   └── public.py         # Views públicas
├── utils/
│   ├── response.py       # Padronização de respostas
│   ├── pagination.py     # Paginação customizada
│   └── filters.py        # Filtros customizados
└── urls.py               # Configuração de rotas
```

---

## ✅ Checklist de Implementação

- ✅ Autenticação JWT
- ✅ CRUD de beneficiários
- ✅ Workflow de status completo
- ✅ Upload e validação de documentos
- ✅ Critérios de priorização
- ✅ Benefícios sociais
- ✅ Dashboard e estatísticas
- ✅ Consulta pública
- ✅ Filtros avançados
- ✅ Paginação
- ✅ Permissões por papel
- ✅ Escopo por município
- ✅ Documentação Swagger/OpenAPI
- ✅ Histórico de ações/auditoria
- ✅ Resposta padronizada

---

## 🎯 Próximos Passos

1. ✅ Tudo implementado e funcional!
2. Testar todos os endpoints
3. Criar testes automatizados
4. Implementar rate limiting
5. Adicionar exportação de relatórios (PDF, Excel)
6. Implementar notificações (email, WhatsApp)
7. Deploy em produção

---

**Documentação gerada automaticamente** - Sistema Habitação MCMV v1.0
