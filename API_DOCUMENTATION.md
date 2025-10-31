# API Documentation - Sistema Habitação MCMV

## Informações Gerais

**Base URL**: `http://localhost:8000/api/v1/`

**Autenticação**: JWT (JSON Web Tokens)

**Documentação Interativa**:
- Swagger UI: `http://localhost:8000/api/v1/swagger/`
- ReDoc: `http://localhost:8000/api/v1/redoc/`
- OpenAPI JSON: `http://localhost:8000/api/v1/swagger.json`

---

## Índice

1. [Autenticação](#autenticação)
2. [Beneficiários](#beneficiários)
3. [Documentos](#documentos)
4. [Dashboard](#dashboard)
5. [Dados Base](#dados-base)
6. [Públicos](#endpoints-públicos)
7. [Tipos de Dados](#tipos-de-dados)
8. [Tratamento de Erros](#tratamento-de-erros)

---

## Autenticação

### Login
```http
POST /api/v1/auth/login
```

**Body**:
```json
{
  "email": "usuario@example.com",
  "password": "senha123"
}
```

**Response 200**:
```json
{
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJh...",
    "refresh": "eyJ0eXAiOiJKV1QiLC...",
    "user": {
      "id": 1,
      "email": "usuario@example.com",
      "full_name": "João Silva",
      "cpf": "123.456.789-00",
      "role": "ANALYST",
      "municipality_id": 1,
      "municipality_name": "São Paulo/SP",
      "is_active": true
    }
  },
  "error": null
}
```

**Response 401**:
```json
{
  "data": null,
  "error": {
    "message": "Credenciais inválidas",
    "code": "AUTHENTICATION_FAILED"
  }
}
```

---

### Renovar Token
```http
POST /api/v1/auth/refresh
```

**Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLC..."
}
```

**Response 200**:
```json
{
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJh..."
  },
  "error": null
}
```

---

### Registrar Usuário
```http
POST /api/v1/auth/register
```

**Permissão**: `COORDINATOR` ou superior

**Headers**:
```
Authorization: Bearer {access_token}
```

**Body**:
```json
{
  "email": "novo@example.com",
  "password": "senha123",
  "first_name": "Maria",
  "last_name": "Silva",
  "cpf": "987.654.321-00",
  "role": "ANALYST",
  "municipality_id": 1
}
```

**Response 201**:
```json
{
  "data": {
    "id": 2,
    "email": "novo@example.com",
    "full_name": "Maria Silva",
    "cpf": "987.654.321-00",
    "role": "ANALYST",
    "municipality_id": 1,
    "is_active": true
  },
  "error": null
}
```

---

### Dados do Usuário Logado
```http
GET /api/v1/me
```

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response 200**:
```json
{
  "data": {
    "id": 1,
    "email": "usuario@example.com",
    "full_name": "João Silva",
    "cpf": "123.456.789-00",
    "role": "ANALYST",
    "municipality_id": 1,
    "municipality_name": "São Paulo/SP",
    "is_active": true
  },
  "error": null
}
```

---

## Beneficiários

### Listar Beneficiários
```http
GET /api/v1/beneficiaries/
```

**Headers**:
```
Authorization: Bearer {access_token}
```

**Query Parameters**:
- `page` (int): Número da página (padrão: 1)
- `page_size` (int): Itens por página (padrão: 20, máx: 100)
- `search` (string): Busca por nome, CPF, protocolo ou email
- `status` (string): Filtrar por status (DRAFT, SUBMITTED, UNDER_REVIEW, CORRECTION_REQUESTED, APPROVED, REJECTED)
- `municipality` (int): Filtrar por município
- `ordering` (string): Ordenar por campo (-created_at, submitted_at, full_name, status)

**Exemplo**:
```
GET /api/v1/beneficiaries/?page=1&page_size=20&status=SUBMITTED&search=João&ordering=-created_at
```

**Response 200**:
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/beneficiaries/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "protocol_number": "2025-01-A3F5D2",
      "full_name": "João da Silva",
      "cpf": "123.456.789-00",
      "status": "SUBMITTED",
      "status_display": "Submetida",
      "municipality": {
        "id": 1,
        "name": "São Paulo",
        "uf": "SP"
      },
      "created_at": "2025-01-15T10:30:00Z",
      "submitted_at": "2025-01-20T14:00:00Z"
    }
  ]
}
```

---

### Detalhes do Beneficiário
```http
GET /api/v1/beneficiaries/{id}/
```

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response 200**:
```json
{
  "data": {
    "id": 1,
    "protocol_number": "2025-01-A3F5D2",
    "status": "SUBMITTED",
    "status_display": "Submetida",

    "full_name": "João da Silva",
    "cpf": "123.456.789-00",
    "rg": "12.345.678-9",
    "birth_date": "1985-05-15",
    "marital_status": "CASADO",

    "phone_primary": "(11) 98765-4321",
    "phone_secondary": "(11) 3456-7890",
    "email": "joao@example.com",

    "address_line": "Rua das Flores",
    "address_number": "123",
    "address_complement": "Apto 45",
    "neighborhood": "Centro",
    "cep": "01234-567",
    "uf": "SP",
    "municipality": {
      "id": 1,
      "name": "São Paulo",
      "uf": "SP",
      "ibge_code": "3550308"
    },

    "spouse_name": "Maria da Silva",
    "spouse_rg": "98.765.432-1",
    "spouse_birth_date": "1987-08-20",

    "main_occupation": "Vendedor",
    "gross_family_income": "3500.00",
    "has_cadunico": true,
    "nis_number": "12345678901",

    "family_size": 4,
    "has_elderly": false,
    "elderly_count": 0,
    "has_children": true,
    "children_count": 2,
    "has_disability_or_tea": false,
    "disability_or_tea_count": 0,
    "household_head_gender": "MASCULINO",
    "family_in_cadunico_updated": true,

    "no_own_house": true,
    "precarious_own_house": false,
    "cohabitation": false,
    "improvised_dwelling": false,
    "pays_rent": true,
    "rent_value": "800.00",
    "other_housing_desc": "",

    "notes": "Observações gerais",

    "priorities": [
      {
        "id": 1,
        "code": "FAMILIA_NUMEROSA",
        "label": "Família Numerosa",
        "group_tag": "social"
      }
    ],

    "social_benefits": [
      {
        "id": 1,
        "code": "BOLSA_FAMILIA",
        "label": "Bolsa Família",
        "other_text": ""
      }
    ],

    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-20T14:00:00Z",
    "submitted_at": "2025-01-20T14:00:00Z",
    "submitted_by": {
      "id": 2,
      "full_name": "Atendente Silva"
    }
  },
  "error": null
}
```

---

### Criar Beneficiário
```http
POST /api/v1/beneficiaries/
```

**Permissão**: `CLERK` ou superior

**Headers**:
```
Authorization: Bearer {access_token}
```

**Body**:
```json
{
  "full_name": "João da Silva",
  "cpf": "123.456.789-00",
  "rg": "12.345.678-9",
  "birth_date": "1985-05-15",
  "marital_status": "CASADO",

  "phone_primary": "(11) 98765-4321",
  "email": "joao@example.com",

  "address_line": "Rua das Flores",
  "address_number": "123",
  "neighborhood": "Centro",
  "municipality_id": 1,
  "cep": "01234-567",
  "uf": "SP",

  "main_occupation": "Vendedor",
  "gross_family_income": 3500.00,
  "has_cadunico": true,
  "nis_number": "12345678901",

  "family_size": 4,
  "has_children": true,
  "children_count": 2,

  "pays_rent": true,
  "rent_value": 800.00,

  "priority_criteria_ids": [1, 2],
  "social_benefit_ids": [1]
}
```

**Response 201**:
```json
{
  "data": {
    "id": 1,
    "status": "DRAFT",
    ...
  },
  "error": null
}
```

---

### Atualizar Beneficiário
```http
PUT /api/v1/beneficiaries/{id}/
PATCH /api/v1/beneficiaries/{id}/
```

**Permissão**: `ANALYST` ou superior

**Headers**:
```
Authorization: Bearer {access_token}
```

**Body** (PATCH - parcial):
```json
{
  "phone_primary": "(11) 99999-9999",
  "email": "novoemail@example.com"
}
```

**Response 200**:
```json
{
  "data": {
    "id": 1,
    ...
  },
  "error": null
}
```

---

### Workflow Actions

#### Submeter Inscrição
```http
POST /api/v1/beneficiaries/{id}/submit
```

**Permissão**: `ANALYST` ou superior

Muda status de `DRAFT` para `SUBMITTED` e gera número de protocolo.

**Response 200**:
```json
{
  "data": {
    "id": 1,
    "status": "SUBMITTED",
    "protocol_number": "2025-01-A3F5D2",
    ...
  },
  "error": null
}
```

---

#### Iniciar Análise
```http
POST /api/v1/beneficiaries/{id}/start-review
```

**Permissão**: `ANALYST` ou superior

Muda status de `SUBMITTED` para `UNDER_REVIEW`.

**Response 200**:
```json
{
  "data": {
    "id": 1,
    "status": "UNDER_REVIEW",
    ...
  },
  "error": null
}
```

---

#### Solicitar Correção
```http
POST /api/v1/beneficiaries/{id}/request-correction
```

**Permissão**: `ANALYST` ou superior

**Body**:
```json
{
  "message": "Favor atualizar o comprovante de renda. O documento está ilegível."
}
```

**Response 200**:
```json
{
  "data": {
    "id": 1,
    "status": "CORRECTION_REQUESTED",
    ...
  },
  "error": null
}
```

---

#### Aprovar Inscrição
```http
POST /api/v1/beneficiaries/{id}/approve
```

**Permissão**: `ANALYST` ou superior

**Body** (opcional):
```json
{
  "message": "Inscrição aprovada conforme critérios."
}
```

**Response 200**:
```json
{
  "data": {
    "id": 1,
    "status": "APPROVED",
    ...
  },
  "error": null
}
```

---

#### Rejeitar Inscrição
```http
POST /api/v1/beneficiaries/{id}/reject
```

**Permissão**: `ANALYST` ou superior

**Body** (obrigatório):
```json
{
  "message": "Renda familiar acima do limite permitido pelo programa."
}
```

**Response 200**:
```json
{
  "data": {
    "id": 1,
    "status": "REJECTED",
    ...
  },
  "error": null
}
```

---

#### Histórico de Ações
```http
GET /api/v1/beneficiaries/{id}/actions
```

**Response 200**:
```json
{
  "data": [
    {
      "id": 5,
      "action": "APPROVE",
      "action_display": "Aprovar",
      "from_status": "UNDER_REVIEW",
      "to_status": "APPROVED",
      "message": "Inscrição aprovada conforme critérios.",
      "created_at": "2025-01-22T10:30:00Z",
      "created_by": {
        "id": 3,
        "full_name": "Analista Silva"
      }
    },
    {
      "id": 4,
      "action": "START_REVIEW",
      "action_display": "Iniciar Análise",
      "from_status": "SUBMITTED",
      "to_status": "UNDER_REVIEW",
      "message": "",
      "created_at": "2025-01-21T14:00:00Z",
      "created_by": {
        "id": 3,
        "full_name": "Analista Silva"
      }
    }
  ],
  "error": null
}
```

---

#### Adicionar Nota
```http
POST /api/v1/beneficiaries/{id}/actions/note
```

**Permissão**: `ANALYST` ou superior

**Body**:
```json
{
  "message": "Beneficiário entrou em contato por telefone para confirmar dados."
}
```

**Response 200**:
```json
{
  "data": {
    "id": 6,
    "action": "NOTE",
    "message": "Beneficiário entrou em contato por telefone para confirmar dados.",
    "created_at": "2025-01-22T11:00:00Z",
    "created_by": {
      "id": 3,
      "full_name": "Analista Silva"
    }
  },
  "error": null
}
```

---

## Documentos

### Listar Documentos do Beneficiário
```http
GET /api/v1/documents/?beneficiary={beneficiary_id}
```

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response 200**:
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "beneficiary_id": 1,
      "document_type": {
        "id": 1,
        "code": "RG",
        "label": "RG",
        "required": true
      },
      "file_name": "rg_joao.pdf",
      "file_url": "http://localhost:8000/media/beneficiarios/12345678900/RG/rg_joao.pdf",
      "mime_type": "application/pdf",
      "size_bytes": 245678,
      "validated": true,
      "uploaded_at": "2025-01-15T11:00:00Z",
      "uploaded_by": {
        "id": 2,
        "full_name": "Atendente Silva"
      }
    }
  ]
}
```

---

### Upload de Documento
```http
POST /api/v1/documents/
```

**Headers**:
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Body** (form-data):
```
beneficiary_id: 1
document_type_id: 1
file: [arquivo]
```

**Response 201**:
```json
{
  "data": {
    "id": 1,
    "beneficiary_id": 1,
    "document_type": {
      "id": 1,
      "code": "RG",
      "label": "RG"
    },
    "file_name": "rg_joao.pdf",
    "file_url": "http://localhost:8000/media/...",
    "uploaded_at": "2025-01-15T11:00:00Z"
  },
  "error": null
}
```

---

### Validar Documento
```http
POST /api/v1/documents/{id}/validate
```

**Permissão**: `ANALYST` ou superior

**Body** (opcional):
```json
{
  "notes": "Documento validado e conforme."
}
```

**Response 200**:
```json
{
  "data": {
    "id": 1,
    "validated": true,
    "validated_at": "2025-01-22T10:00:00Z",
    "validated_by": {
      "id": 3,
      "full_name": "Analista Silva"
    }
  },
  "error": null
}
```

---

### Deletar Documento
```http
DELETE /api/v1/documents/{id}/
```

**Permissão**: `ANALYST` ou superior

**Response 204**: No Content

---

## Dashboard

### Visão Geral
```http
GET /api/v1/dashboard
```

**Permissão**: `ANALYST` ou superior

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response 200**:
```json
{
  "data": {
    "total_beneficiaries": 1500,
    "by_status": {
      "DRAFT": 200,
      "SUBMITTED": 300,
      "UNDER_REVIEW": 250,
      "CORRECTION_REQUESTED": 150,
      "APPROVED": 400,
      "REJECTED": 200
    },
    "recent_submissions": 45,
    "pending_review": 300,
    "approved_this_month": 80
  },
  "error": null
}
```

---

### Estatísticas por Município
```http
GET /api/v1/dashboard/municipality?municipality_id={id}
```

**Permissão**: `ANALYST` ou superior

**Response 200**:
```json
{
  "data": {
    "municipality": {
      "id": 1,
      "name": "São Paulo",
      "uf": "SP"
    },
    "total_beneficiaries": 500,
    "by_status": {
      "DRAFT": 50,
      "SUBMITTED": 100,
      "UNDER_REVIEW": 80,
      "APPROVED": 200,
      "REJECTED": 70
    }
  },
  "error": null
}
```

---

### Minhas Atribuições
```http
GET /api/v1/dashboard/my-assignments
```

**Response 200**:
```json
{
  "data": {
    "active_assignments": [
      {
        "id": 1,
        "beneficiary": {
          "id": 1,
          "full_name": "João da Silva",
          "protocol_number": "2025-01-A3F5D2",
          "status": "UNDER_REVIEW"
        },
        "assigned_at": "2025-01-21T14:00:00Z"
      }
    ],
    "total_active": 15,
    "completed_this_week": 8
  },
  "error": null
}
```

---

## Dados Base

### Municípios
```http
GET /api/v1/municipalities/
```

**Query Parameters**:
- `uf` (string): Filtrar por UF
- `search` (string): Buscar por nome

**Response 200**:
```json
{
  "count": 5570,
  "results": [
    {
      "id": 1,
      "ibge_code": "3550308",
      "name": "São Paulo",
      "uf": "SP"
    }
  ]
}
```

---

### Critérios de Priorização
```http
GET /api/v1/priority-criteria/
```

**Response 200**:
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "code": "FAMILIA_NUMEROSA",
      "label": "Família Numerosa (4+ membros)",
      "group_tag": "social",
      "active": true
    },
    {
      "id": 2,
      "code": "MULHER_CHEFE_FAMILIA",
      "label": "Mulher Chefe de Família",
      "group_tag": "social",
      "active": true
    }
  ]
}
```

---

### Tipos de Benefícios Sociais
```http
GET /api/v1/social-benefits/
```

**Response 200**:
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "code": "BOLSA_FAMILIA",
      "label": "Bolsa Família",
      "active": true
    },
    {
      "id": 2,
      "code": "BPC",
      "label": "BPC (Benefício de Prestação Continuada)",
      "active": true
    }
  ]
}
```

---

### Tipos de Documentos
```http
GET /api/v1/document-types/
```

**Response 200**:
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "code": "RG",
      "label": "RG",
      "required": true,
      "active": true
    },
    {
      "id": 2,
      "code": "CPF",
      "label": "CPF",
      "required": true,
      "active": true
    },
    {
      "id": 3,
      "code": "COMPROVANTE_RESIDENCIA",
      "label": "Comprovante de Residência",
      "required": true,
      "active": true
    }
  ]
}
```

---

## Endpoints Públicos

### Status da API
```http
GET /api/v1/public/status
```

**Sem autenticação**

**Response 200**:
```json
{
  "data": {
    "status": "operational",
    "version": "1.0.0",
    "timestamp": "2025-01-22T15:30:00Z"
  },
  "error": null
}
```

---

## Tipos de Dados

### Status da Inscrição
```
DRAFT - Rascunho
SUBMITTED - Submetida
UNDER_REVIEW - Em Análise
CORRECTION_REQUESTED - Correção Solicitada
APPROVED - Aprovada
REJECTED - Rejeitada
```

### Papéis de Usuário
```
ADMIN - Administrador (acesso total)
COORDINATOR - Coordenador (gerencia analistas e municípios)
ANALYST - Analista (analisa inscrições)
CLERK - Atendente (cadastra beneficiários)
```

### Estado Civil
```
SOLTEIRO - Solteiro(a)
CASADO - Casado(a)
UNIAO_ESTAVEL - União Estável
VIUVO - Viúvo(a)
DIVORCIADO - Divorciado(a)
SEPARADO - Separado(a)
OUTRO - Outro
```

### Gênero
```
MASCULINO - Masculino
FEMININO - Feminino
OUTRO - Outro
NAO_INFORMADO - Não informado
```

### Estados (UF)
```
AC, AL, AP, AM, BA, CE, DF, ES, GO, MA, MT, MS, MG, PA, PB, PR, PE, PI, RJ, RN, RS, RO, RR, SC, SP, SE, TO
```

### Ações de Workflow
```
SUBMIT - Submeter
START_REVIEW - Iniciar Análise
REQUEST_CORRECTION - Solicitar Correção
APPROVE - Aprovar
REJECT - Rejeitar
UPLOAD_DOC - Upload de Documento
VALIDATE_DOC - Validar Documento
NOTE - Adicionar Nota
EDIT - Editar
```

---

## Tratamento de Erros

Todas as respostas seguem o padrão:

**Sucesso**:
```json
{
  "data": { ... },
  "error": null
}
```

**Erro**:
```json
{
  "data": null,
  "error": {
    "message": "Descrição do erro",
    "code": "ERROR_CODE",
    "details": { ... }
  }
}
```

### Códigos de Status HTTP

- `200 OK` - Sucesso
- `201 Created` - Recurso criado
- `204 No Content` - Sucesso sem conteúdo (DELETE)
- `400 Bad Request` - Erro de validação
- `401 Unauthorized` - Não autenticado
- `403 Forbidden` - Sem permissão
- `404 Not Found` - Recurso não encontrado
- `500 Internal Server Error` - Erro no servidor

### Códigos de Erro Comuns

- `AUTHENTICATION_FAILED` - Credenciais inválidas
- `INVALID_TOKEN` - Token inválido ou expirado
- `VALIDATION_ERROR` - Erro de validação de dados
- `WORKFLOW_ERROR` - Erro no fluxo de trabalho
- `NOT_FOUND` - Recurso não encontrado
- `PERMISSION_DENIED` - Sem permissão

---

## Exemplos de Integração

### JavaScript/TypeScript (Axios)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1/',
});

// Interceptor para adicionar token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Login
async function login(email, password) {
  const response = await api.post('auth/login', { email, password });
  localStorage.setItem('access_token', response.data.data.access);
  localStorage.setItem('refresh_token', response.data.data.refresh);
  return response.data.data.user;
}

// Listar beneficiários
async function getBeneficiaries(page = 1, filters = {}) {
  const response = await api.get('beneficiaries/', {
    params: { page, ...filters }
  });
  return response.data;
}

// Criar beneficiário
async function createBeneficiary(data) {
  const response = await api.post('beneficiaries/', data);
  return response.data.data;
}

// Aprovar inscrição
async function approveBeneficiary(id, message) {
  const response = await api.post(`beneficiaries/${id}/approve`, { message });
  return response.data.data;
}

// Upload de documento
async function uploadDocument(beneficiaryId, documentTypeId, file) {
  const formData = new FormData();
  formData.append('beneficiary_id', beneficiaryId);
  formData.append('document_type_id', documentTypeId);
  formData.append('file', file);

  const response = await api.post('documents/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data.data;
}
```

### React Query Hooks

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './api';

// Hook para listar beneficiários
export function useBeneficiaries(filters = {}) {
  return useQuery({
    queryKey: ['beneficiaries', filters],
    queryFn: () => getBeneficiaries(filters.page, filters),
  });
}

// Hook para criar beneficiário
export function useCreateBeneficiary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createBeneficiary,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['beneficiaries'] });
    },
  });
}

// Hook para aprovar
export function useApproveBeneficiary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, message }) => approveBeneficiary(id, message),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['beneficiaries'] });
    },
  });
}
```

---

## Paginação

Todas as listagens retornam dados paginados:

**Request**:
```
GET /api/v1/beneficiaries/?page=2&page_size=20
```

**Response**:
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/beneficiaries/?page=3&page_size=20",
  "previous": "http://localhost:8000/api/v1/beneficiaries/?page=1&page_size=20",
  "results": [...]
}
```

---

## Filtros e Busca

### Exemplo de Query Parameters

```
GET /api/v1/beneficiaries/?status=SUBMITTED&municipality=1&search=João&ordering=-created_at&page=1&page_size=20
```

**Filtros disponíveis**:
- `status` - Status da inscrição
- `municipality` - ID do município
- `search` - Busca textual (nome, CPF, protocolo, email)
- `ordering` - Ordenação (campos: created_at, submitted_at, full_name, status)
  - Prefixo `-` para ordem descendente
- `page` - Número da página
- `page_size` - Itens por página (máx: 100)

---

## Notas Importantes

1. **Todos os endpoints (exceto públicos) requerem autenticação via JWT**
2. **Tokens expiram após 24 horas** - use o refresh token para renovar
3. **Upload de arquivos limitado a 10MB**
4. **Formatos aceitos para documentos**: PDF, JPG, JPEG, PNG
5. **CPF e NIS devem ser únicos no sistema**
6. **Permissões são validadas por papel de usuário e escopo de município**
7. **Workflow de status é unidirecional e validado**

---

## Suporte

Para mais informações, consulte:
- Swagger UI: `http://localhost:8000/api/v1/swagger/`
- ReDoc: `http://localhost:8000/api/v1/redoc/`
