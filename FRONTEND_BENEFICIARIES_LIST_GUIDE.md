# 📋 Guia de Listagem de Beneficiários - Frontend

> **Status**: ✅ Documentação completa para implementação de listagem

## 🎯 TL;DR (Resumo Executivo)

O endpoint de listagem suporta:
- ✅ **Paginação** automática (20 itens por página)
- ✅ **Filtros avançados** (status, município, CadÚnico, etc)
- ✅ **Busca** por nome, CPF, protocolo ou email
- ✅ **Ordenação** por data, nome ou status
- ✅ **Escopo de município** (usuários veem apenas seu município)

---

## 📡 Endpoint Base

```
GET /api/v1/beneficiaries/
```

**Autenticação**: Obrigatória (Bearer Token)

**Resposta**: Lista paginada de beneficiários

---

## 📊 Estrutura da Resposta

### Resposta Paginada (Padrão)

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/beneficiaries/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "protocol_number": "2025-01-ABC123",
      "full_name": "Maria Silva Santos",
      "cpf": "12345678901",
      "municipality": 1,
      "municipality_name": "São Paulo",
      "uf": "SP",
      "status": "SUBMITTED",
      "status_display": "Submetida",
      "age": 38,
      "submitted_at": "2025-01-20T14:30:00Z",
      "created_at": "2025-01-20T10:15:00Z",
      "updated_at": "2025-01-20T14:30:00Z"
    },
    {
      "id": 2,
      "protocol_number": "2025-01-XYZ789",
      "full_name": "João Pereira",
      "cpf": "98765432100",
      "municipality": 1,
      "municipality_name": "São Paulo",
      "uf": "SP",
      "status": "UNDER_REVIEW",
      "status_display": "Em Análise",
      "age": 35,
      "submitted_at": "2025-01-19T16:45:00Z",
      "created_at": "2025-01-19T09:20:00Z",
      "updated_at": "2025-01-20T11:00:00Z"
    }
  ]
}
```

### Campos da Listagem

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `id` | number | ID único do beneficiário | `1` |
| `protocol_number` | string \| null | Protocolo (gerado após submissão) | `"2025-01-ABC123"` |
| `full_name` | string | Nome completo | `"Maria Silva Santos"` |
| `cpf` | string | CPF (sem formatação) | `"12345678901"` |
| `municipality` | number \| null | ID do município | `1` |
| `municipality_name` | string \| null | Nome do município | `"São Paulo"` |
| `uf` | string | Sigla do estado | `"SP"` |
| `status` | string | Status da inscrição | `"SUBMITTED"` |
| `status_display` | string | Status em português | `"Submetida"` |
| `age` | number \| null | Idade calculada | `38` |
| `submitted_at` | string \| null | Data/hora da submissão | `"2025-01-20T14:30:00Z"` |
| `created_at` | string | Data/hora de criação | `"2025-01-20T10:15:00Z"` |
| `updated_at` | string | Data/hora da última atualização | `"2025-01-20T14:30:00Z"` |

---

## 🔍 Parâmetros de Query

### 1. Paginação

| Parâmetro | Tipo | Descrição | Padrão | Exemplo |
|-----------|------|-----------|--------|---------|
| `page` | number | Número da página | `1` | `?page=2` |
| `page_size` | number | Itens por página | `20` | `?page_size=50` |

**Exemplo**:
```bash
GET /api/v1/beneficiaries/?page=2&page_size=50
```

### 2. Busca (Search)

Busca por nome, CPF, protocolo ou email:

```bash
GET /api/v1/beneficiaries/?search=Maria
GET /api/v1/beneficiaries/?search=123.456
GET /api/v1/beneficiaries/?search=2025-01
```

### 3. Filtros

#### Status da Inscrição

```bash
GET /api/v1/beneficiaries/?status=SUBMITTED
GET /api/v1/beneficiaries/?status=UNDER_REVIEW
GET /api/v1/beneficiaries/?status=APPROVED
```

**Valores possíveis**:
- `DRAFT` - Rascunho
- `SUBMITTED` - Submetida
- `UNDER_REVIEW` - Em Análise
- `CORRECTION_REQUESTED` - Correção Solicitada
- `APPROVED` - Aprovada
- `REJECTED` - Rejeitada
- `ON_HOLD` - Em Espera

#### Município

```bash
GET /api/v1/beneficiaries/?municipality_id=1
```

#### UF (Estado)

```bash
GET /api/v1/beneficiaries/?uf=SP
GET /api/v1/beneficiaries/?uf=RJ
```

#### CPF (busca parcial)

```bash
GET /api/v1/beneficiaries/?cpf=123456
```

#### Protocolo (busca parcial)

```bash
GET /api/v1/beneficiaries/?protocol=2025-01
```

#### CadÚnico

```bash
GET /api/v1/beneficiaries/?has_cadunico=true
GET /api/v1/beneficiaries/?has_cadunico=false
```

#### Composição Familiar

```bash
# Possui idosos
GET /api/v1/beneficiaries/?has_elderly=true

# Possui crianças
GET /api/v1/beneficiaries/?has_children=true

# Possui PcD/TEA
GET /api/v1/beneficiaries/?has_disability_or_tea=true
```

#### Situação Habitacional

```bash
# Paga aluguel
GET /api/v1/beneficiaries/?pays_rent=true

# Não possui casa própria
GET /api/v1/beneficiaries/?no_own_house=true
```

#### Data de Submissão

```bash
# Submetidos após data
GET /api/v1/beneficiaries/?submitted_from=2025-01-01

# Submetidos até data
GET /api/v1/beneficiaries/?submitted_to=2025-01-31

# Intervalo
GET /api/v1/beneficiaries/?submitted_from=2025-01-01&submitted_to=2025-01-31
```

#### Documentos Faltando

```bash
GET /api/v1/beneficiaries/?has_missing_docs=true
```

### 4. Ordenação

| Parâmetro | Descrição | Exemplo |
|-----------|-----------|---------|
| `ordering=created_at` | Mais antigos primeiro | `?ordering=created_at` |
| `ordering=-created_at` | Mais recentes primeiro (padrão) | `?ordering=-created_at` |
| `ordering=full_name` | Ordem alfabética (A-Z) | `?ordering=full_name` |
| `ordering=-full_name` | Ordem alfabética inversa (Z-A) | `?ordering=-full_name` |
| `ordering=submitted_at` | Submissão mais antiga primeiro | `?ordering=submitted_at` |
| `ordering=-submitted_at` | Submissão mais recente primeiro | `?ordering=-submitted_at` |
| `ordering=status` | Por status | `?ordering=status` |

**Ordenação múltipla**:
```bash
GET /api/v1/beneficiaries/?ordering=-submitted_at,full_name
```

---

## 🔢 Combinando Filtros

Você pode combinar múltiplos filtros:

```bash
# Beneficiários aprovados de São Paulo com crianças
GET /api/v1/beneficiaries/?status=APPROVED&uf=SP&has_children=true

# Beneficiários em análise, com CadÚnico, submetidos em janeiro de 2025
GET /api/v1/beneficiaries/?status=UNDER_REVIEW&has_cadunico=true&submitted_from=2025-01-01&submitted_to=2025-01-31

# Buscar "Maria" entre os submetidos, ordenar por data
GET /api/v1/beneficiaries/?search=Maria&status=SUBMITTED&ordering=-submitted_at
```

---

## 💻 Exemplos de Implementação

### Exemplo 1: Service TypeScript/JavaScript

```typescript
// src/services/beneficiary.service.ts
import { apiService } from './api.service';
import { API_ENDPOINTS } from '../config/api.config';

export interface BeneficiaryListParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: string;
  municipality_id?: number;
  uf?: string;
  has_cadunico?: boolean;
  has_children?: boolean;
  has_elderly?: boolean;
  ordering?: string;
  submitted_from?: string;
  submitted_to?: string;
}

export interface BeneficiaryListItem {
  id: number;
  protocol_number: string | null;
  full_name: string;
  cpf: string;
  municipality: number | null;
  municipality_name: string | null;
  uf: string;
  status: string;
  status_display: string;
  age: number | null;
  submitted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface BeneficiaryListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: BeneficiaryListItem[];
}

export class BeneficiaryService {
  /**
   * Lista beneficiários com filtros e paginação
   */
  static async list(params?: BeneficiaryListParams): Promise<BeneficiaryListResponse> {
    return apiService.get<BeneficiaryListResponse>(
      API_ENDPOINTS.beneficiaries,
      { params }
    );
  }

  /**
   * Busca beneficiários por termo
   */
  static async search(searchTerm: string, page: number = 1): Promise<BeneficiaryListResponse> {
    return this.list({
      search: searchTerm,
      page,
    });
  }

  /**
   * Filtra beneficiários por status
   */
  static async filterByStatus(status: string, page: number = 1): Promise<BeneficiaryListResponse> {
    return this.list({
      status,
      page,
    });
  }

  /**
   * Beneficiários com documentos faltando
   */
  static async withMissingDocs(page: number = 1): Promise<BeneficiaryListResponse> {
    return this.list({
      has_missing_docs: true,
      page,
    });
  }
}
```

### Exemplo 2: Hook React com React Query

```typescript
// src/hooks/useBeneficiaries.ts
import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { BeneficiaryService, BeneficiaryListParams, BeneficiaryListResponse } from '../services/beneficiary.service';

export const useBeneficiaries = (
  params?: BeneficiaryListParams
): UseQueryResult<BeneficiaryListResponse, Error> => {
  return useQuery({
    queryKey: ['beneficiaries', params],
    queryFn: () => BeneficiaryService.list(params),
    staleTime: 30000, // 30 segundos
    keepPreviousData: true, // Mantém dados antigos durante loading
  });
};

export const useBeneficiarySearch = (searchTerm: string, page: number = 1) => {
  return useQuery({
    queryKey: ['beneficiaries', 'search', searchTerm, page],
    queryFn: () => BeneficiaryService.search(searchTerm, page),
    enabled: searchTerm.length >= 3, // Só busca com 3+ caracteres
    staleTime: 60000, // 1 minuto
  });
};
```

### Exemplo 3: Componente React com Tabela

```typescript
// src/pages/BeneficiaryList.tsx
import { useState } from 'react';
import { useBeneficiaries } from '../hooks/useBeneficiaries';

export const BeneficiaryList = () => {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    status: '',
    search: '',
    uf: '',
  });

  const { data, isLoading, error } = useBeneficiaries({
    page,
    ...filters,
  });

  if (isLoading) return <div>Carregando...</div>;
  if (error) return <div>Erro: {error.message}</div>;

  return (
    <div className="container">
      {/* Filtros */}
      <div className="filters mb-4">
        <input
          type="text"
          placeholder="Buscar por nome, CPF ou protocolo..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          className="form-control mb-2"
        />

        <select
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          className="form-select mb-2"
        >
          <option value="">Todos os status</option>
          <option value="DRAFT">Rascunho</option>
          <option value="SUBMITTED">Submetida</option>
          <option value="UNDER_REVIEW">Em Análise</option>
          <option value="APPROVED">Aprovada</option>
          <option value="REJECTED">Rejeitada</option>
        </select>

        <select
          value={filters.uf}
          onChange={(e) => setFilters({ ...filters, uf: e.target.value })}
          className="form-select mb-2"
        >
          <option value="">Todos os estados</option>
          <option value="SP">São Paulo</option>
          <option value="RJ">Rio de Janeiro</option>
          <option value="MG">Minas Gerais</option>
          {/* ... outros estados */}
        </select>
      </div>

      {/* Tabela */}
      <table className="table table-striped">
        <thead>
          <tr>
            <th>Protocolo</th>
            <th>Nome</th>
            <th>CPF</th>
            <th>Município</th>
            <th>Status</th>
            <th>Submetido em</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {data?.results.map((beneficiary) => (
            <tr key={beneficiary.id}>
              <td>{beneficiary.protocol_number || '-'}</td>
              <td>{beneficiary.full_name}</td>
              <td>{formatCPF(beneficiary.cpf)}</td>
              <td>{beneficiary.municipality_name || '-'} / {beneficiary.uf}</td>
              <td>
                <span className={`badge bg-${getStatusColor(beneficiary.status)}`}>
                  {beneficiary.status_display}
                </span>
              </td>
              <td>{beneficiary.submitted_at ? formatDate(beneficiary.submitted_at) : '-'}</td>
              <td>
                <button
                  onClick={() => navigate(`/beneficiaries/${beneficiary.id}`)}
                  className="btn btn-sm btn-primary"
                >
                  Ver Detalhes
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Paginação */}
      <div className="pagination">
        <button
          onClick={() => setPage(page - 1)}
          disabled={!data?.previous}
          className="btn btn-secondary"
        >
          Anterior
        </button>

        <span className="mx-3">
          Página {page} de {Math.ceil((data?.count || 0) / 20)}
        </span>

        <button
          onClick={() => setPage(page + 1)}
          disabled={!data?.next}
          className="btn btn-secondary"
        >
          Próxima
        </button>

        <span className="ms-3 text-muted">
          Total: {data?.count} beneficiários
        </span>
      </div>
    </div>
  );
};

// Funções auxiliares
const formatCPF = (cpf: string) => {
  return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pt-BR');
};

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    DRAFT: 'secondary',
    SUBMITTED: 'primary',
    UNDER_REVIEW: 'info',
    APPROVED: 'success',
    REJECTED: 'danger',
    ON_HOLD: 'warning',
  };
  return colors[status] || 'secondary';
};
```

### Exemplo 4: Componente React com Cards (Mobile-Friendly)

```typescript
// src/components/BeneficiaryCard.tsx
import { BeneficiaryListItem } from '../services/beneficiary.service';

interface Props {
  beneficiary: BeneficiaryListItem;
  onSelect: (id: number) => void;
}

export const BeneficiaryCard = ({ beneficiary, onSelect }: Props) => {
  return (
    <div className="card mb-3" onClick={() => onSelect(beneficiary.id)}>
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start">
          <div>
            <h5 className="card-title">{beneficiary.full_name}</h5>
            <p className="card-text text-muted mb-1">
              CPF: {formatCPF(beneficiary.cpf)}
            </p>
            {beneficiary.protocol_number && (
              <p className="card-text text-muted mb-1">
                Protocolo: {beneficiary.protocol_number}
              </p>
            )}
            <p className="card-text">
              <small className="text-muted">
                {beneficiary.municipality_name} / {beneficiary.uf}
              </small>
            </p>
          </div>

          <span className={`badge bg-${getStatusColor(beneficiary.status)}`}>
            {beneficiary.status_display}
          </span>
        </div>

        {beneficiary.submitted_at && (
          <div className="mt-2">
            <small className="text-muted">
              Submetido em: {formatDate(beneficiary.submitted_at)}
            </small>
          </div>
        )}
      </div>
    </div>
  );
};
```

---

## 🎨 Badges de Status

Sugestão de cores para exibir status:

```typescript
const statusConfig = {
  DRAFT: {
    label: 'Rascunho',
    color: 'gray',
    className: 'bg-gray-200 text-gray-800',
  },
  SUBMITTED: {
    label: 'Submetida',
    color: 'blue',
    className: 'bg-blue-100 text-blue-800',
  },
  UNDER_REVIEW: {
    label: 'Em Análise',
    color: 'yellow',
    className: 'bg-yellow-100 text-yellow-800',
  },
  CORRECTION_REQUESTED: {
    label: 'Correção Solicitada',
    color: 'orange',
    className: 'bg-orange-100 text-orange-800',
  },
  APPROVED: {
    label: 'Aprovada',
    color: 'green',
    className: 'bg-green-100 text-green-800',
  },
  REJECTED: {
    label: 'Rejeitada',
    color: 'red',
    className: 'bg-red-100 text-red-800',
  },
  ON_HOLD: {
    label: 'Em Espera',
    color: 'purple',
    className: 'bg-purple-100 text-purple-800',
  },
};
```

---

## 🧪 Testes com cURL

### Listar todos (primeira página)

```bash
curl -X GET http://localhost:8000/api/v1/beneficiaries/ \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Buscar por nome

```bash
curl -X GET "http://localhost:8000/api/v1/beneficiaries/?search=Maria" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Filtrar por status

```bash
curl -X GET "http://localhost:8000/api/v1/beneficiaries/?status=SUBMITTED" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Múltiplos filtros

```bash
curl -X GET "http://localhost:8000/api/v1/beneficiaries/?status=APPROVED&uf=SP&has_children=true&page=2" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### Ordenar por nome

```bash
curl -X GET "http://localhost:8000/api/v1/beneficiaries/?ordering=full_name" \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

## ⚠️ Notas Importantes

### 1. Escopo de Município

Usuários com papel `ANALYST` ou `CLERK` **só veem beneficiários do seu município**. Apenas `ADMIN` e `COORDINATOR` veem todos.

### 2. Paginação Padrão

- **Tamanho padrão**: 20 itens por página
- **Máximo**: 100 itens por página
- Se não especificar `page`, retorna a primeira página

### 3. Performance

Para melhor performance:
- Use `page_size` menor se não precisar de muitos itens
- Use filtros específicos em vez de busca geral
- Cache os resultados no frontend (React Query faz isso automaticamente)

### 4. Busca vs Filtros

- **`search`**: Busca em múltiplos campos (nome, CPF, protocolo, email)
- **Filtros específicos**: Mais rápido e preciso (ex: `status`, `municipality_id`)

---

## 📚 Referências

- **Criação de Beneficiário**: [API_PAYLOAD_STRUCTURE.md](./API_PAYLOAD_STRUCTURE.md)
- **Guia Completo da API**: [FRONTEND_INTEGRATION_GUIDE.md](./FRONTEND_INTEGRATION_GUIDE.md)
- **Swagger UI**: http://localhost:8000/api/v1/swagger/
- **ReDoc**: http://localhost:8000/api/v1/redoc/

---

**Última atualização**: 2025-01-26
**Versão**: 1.0.0
**Status**: ✅ Pronto para implementação
