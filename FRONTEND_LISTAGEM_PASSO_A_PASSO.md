# 📋 Listagem de Beneficiários - Passo a Passo para Frontend

> **Guia Prático**: Implementação completa da listagem de beneficiários do zero

## 🎯 O que você vai implementar

- ✅ Listagem de beneficiários com paginação
- ✅ Busca por nome/CPF/protocolo
- ✅ Filtros por status, município, características
- ✅ Ordenação por data, nome, status
- ✅ Loading states e tratamento de erros
- ✅ Design responsivo (desktop + mobile)

---

## 📦 Estrutura de Arquivos Recomendada

```
src/
├── config/
│   └── api.config.ts              # Configuração da API
├── services/
│   ├── api.service.ts             # Cliente HTTP base
│   └── beneficiary.service.ts     # Service de beneficiários
├── hooks/
│   └── useBeneficiaries.ts        # Hook React Query
├── types/
│   └── beneficiary.types.ts       # Tipos TypeScript
├── components/
│   ├── BeneficiaryTable.tsx       # Tabela desktop
│   ├── BeneficiaryCard.tsx        # Card mobile
│   ├── BeneficiaryFilters.tsx     # Filtros
│   ├── Pagination.tsx             # Paginação
│   └── StatusBadge.tsx            # Badge de status
└── pages/
    └── BeneficiaryList.tsx        # Página principal
```

---

## 🚀 Passo 1: Configuração da API

### **Arquivo: `src/config/api.config.ts`**

```typescript
// Configuração base da API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = 'v1';

export const API_CONFIG = {
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
  timeout: 30000,
};

export const API_ENDPOINTS = {
  beneficiaries: '/beneficiaries/',
  beneficiaryDetail: (id: number) => `/beneficiaries/${id}/`,
};
```

### **Arquivo: `.env.development`**

```bash
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🔧 Passo 2: Cliente HTTP (Axios)

### **Arquivo: `src/services/api.service.ts`**

```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { API_CONFIG } from '../config/api.config';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_CONFIG.baseURL,
      timeout: API_CONFIG.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor: Adicionar token em todas as requisições
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Interceptor: Refresh token automático
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            const response = await axios.post(
              `${API_CONFIG.baseURL}/auth/refresh/`,
              { refresh: refreshToken }
            );

            const { access } = response.data;
            localStorage.setItem('access_token', access);

            originalRequest.headers.Authorization = `Bearer ${access}`;
            return this.api(originalRequest);
          } catch (refreshError) {
            localStorage.clear();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.post<T>(url, data, config);
    return response.data;
  }
}

export const apiService = new ApiService();
```

---

## 📝 Passo 3: Tipos TypeScript

### **Arquivo: `src/types/beneficiary.types.ts`**

```typescript
// Tipos para listagem de beneficiários

export interface BeneficiaryListItem {
  id: number;
  protocol_number: string | null;
  full_name: string;
  cpf: string;
  municipality: number | null;
  municipality_name: string | null;
  uf: string;
  status: ApplicationStatus;
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

export interface BeneficiaryListParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: ApplicationStatus;
  municipality_id?: number;
  uf?: string;
  has_cadunico?: boolean;
  has_children?: boolean;
  has_elderly?: boolean;
  has_disability_or_tea?: boolean;
  pays_rent?: boolean;
  no_own_house?: boolean;
  ordering?: string;
  submitted_from?: string;
  submitted_to?: string;
}

export type ApplicationStatus =
  | 'DRAFT'
  | 'SUBMITTED'
  | 'UNDER_REVIEW'
  | 'CORRECTION_REQUESTED'
  | 'APPROVED'
  | 'REJECTED'
  | 'ON_HOLD';

export const STATUS_CONFIG = {
  DRAFT: {
    label: 'Rascunho',
    color: 'gray',
    className: 'bg-gray-100 text-gray-800',
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
} as const;
```

---

## 🔌 Passo 4: Service de Beneficiários

### **Arquivo: `src/services/beneficiary.service.ts`**

```typescript
import { apiService } from './api.service';
import { API_ENDPOINTS } from '../config/api.config';
import type {
  BeneficiaryListResponse,
  BeneficiaryListParams,
  BeneficiaryListItem,
} from '../types/beneficiary.types';

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
   * Obtém um beneficiário por ID
   */
  static async getById(id: number): Promise<BeneficiaryListItem> {
    return apiService.get<BeneficiaryListItem>(
      API_ENDPOINTS.beneficiaryDetail(id)
    );
  }
}
```

---

## ⚛️ Passo 5: Hook React Query

### **Arquivo: `src/hooks/useBeneficiaries.ts`**

```typescript
import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { BeneficiaryService } from '../services/beneficiary.service';
import type {
  BeneficiaryListParams,
  BeneficiaryListResponse,
} from '../types/beneficiary.types';

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
```

---

## 🎨 Passo 6: Componente StatusBadge

### **Arquivo: `src/components/StatusBadge.tsx`**

```typescript
import React from 'react';
import { ApplicationStatus, STATUS_CONFIG } from '../types/beneficiary.types';

interface Props {
  status: ApplicationStatus;
}

export const StatusBadge: React.FC<Props> = ({ status }) => {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.DRAFT;

  return (
    <span
      className={`
        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
        ${config.className}
      `}
    >
      {config.label}
    </span>
  );
};
```

---

## 🔍 Passo 7: Componente de Filtros

### **Arquivo: `src/components/BeneficiaryFilters.tsx`**

```typescript
import React from 'react';
import { ApplicationStatus } from '../types/beneficiary.types';

interface Props {
  search: string;
  status: string;
  uf: string;
  hasCadunico: string;
  onSearchChange: (value: string) => void;
  onStatusChange: (value: string) => void;
  onUfChange: (value: string) => void;
  onCadunicoChange: (value: string) => void;
  onClearFilters: () => void;
}

export const BeneficiaryFilters: React.FC<Props> = ({
  search,
  status,
  uf,
  hasCadunico,
  onSearchChange,
  onStatusChange,
  onUfChange,
  onCadunicoChange,
  onClearFilters,
}) => {
  const hasFilters = search || status || uf || hasCadunico;

  return (
    <div className="bg-white p-4 rounded-lg shadow mb-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Busca */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Buscar
          </label>
          <input
            type="text"
            placeholder="Nome, CPF ou protocolo..."
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            value={status}
            onChange={(e) => onStatusChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos</option>
            <option value="DRAFT">Rascunho</option>
            <option value="SUBMITTED">Submetida</option>
            <option value="UNDER_REVIEW">Em Análise</option>
            <option value="APPROVED">Aprovada</option>
            <option value="REJECTED">Rejeitada</option>
            <option value="ON_HOLD">Em Espera</option>
          </select>
        </div>

        {/* UF */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Estado
          </label>
          <select
            value={uf}
            onChange={(e) => onUfChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos</option>
            <option value="AC">Acre</option>
            <option value="AL">Alagoas</option>
            <option value="AP">Amapá</option>
            <option value="AM">Amazonas</option>
            <option value="BA">Bahia</option>
            <option value="CE">Ceará</option>
            <option value="DF">Distrito Federal</option>
            <option value="ES">Espírito Santo</option>
            <option value="GO">Goiás</option>
            <option value="MA">Maranhão</option>
            <option value="MT">Mato Grosso</option>
            <option value="MS">Mato Grosso do Sul</option>
            <option value="MG">Minas Gerais</option>
            <option value="PA">Pará</option>
            <option value="PB">Paraíba</option>
            <option value="PR">Paraná</option>
            <option value="PE">Pernambuco</option>
            <option value="PI">Piauí</option>
            <option value="RJ">Rio de Janeiro</option>
            <option value="RN">Rio Grande do Norte</option>
            <option value="RS">Rio Grande do Sul</option>
            <option value="RO">Rondônia</option>
            <option value="RR">Roraima</option>
            <option value="SC">Santa Catarina</option>
            <option value="SP">São Paulo</option>
            <option value="SE">Sergipe</option>
            <option value="TO">Tocantins</option>
          </select>
        </div>

        {/* CadÚnico */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            CadÚnico
          </label>
          <select
            value={hasCadunico}
            onChange={(e) => onCadunicoChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos</option>
            <option value="true">Com CadÚnico</option>
            <option value="false">Sem CadÚnico</option>
          </select>
        </div>
      </div>

      {/* Botão Limpar Filtros */}
      {hasFilters && (
        <div className="mt-4">
          <button
            onClick={onClearFilters}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Limpar filtros
          </button>
        </div>
      )}
    </div>
  );
};
```

---

## 📊 Passo 8: Componente de Paginação

### **Arquivo: `src/components/Pagination.tsx`**

```typescript
import React from 'react';

interface Props {
  currentPage: number;
  totalItems: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  hasNext: boolean;
  hasPrevious: boolean;
}

export const Pagination: React.FC<Props> = ({
  currentPage,
  totalItems,
  pageSize,
  onPageChange,
  hasNext,
  hasPrevious,
}) => {
  const totalPages = Math.ceil(totalItems / pageSize);

  return (
    <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
      <div className="flex-1 flex justify-between sm:hidden">
        {/* Mobile */}
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={!hasPrevious}
          className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Anterior
        </button>
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={!hasNext}
          className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Próxima
        </button>
      </div>

      <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
        {/* Desktop */}
        <div>
          <p className="text-sm text-gray-700">
            Mostrando{' '}
            <span className="font-medium">{(currentPage - 1) * pageSize + 1}</span>
            {' '}-{' '}
            <span className="font-medium">
              {Math.min(currentPage * pageSize, totalItems)}
            </span>
            {' '}de{' '}
            <span className="font-medium">{totalItems}</span>
            {' '}resultados
          </p>
        </div>
        <div>
          <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={!hasPrevious}
              className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Anterior
            </button>

            <span className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
              Página {currentPage} de {totalPages}
            </span>

            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={!hasNext}
              className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Próxima
            </button>
          </nav>
        </div>
      </div>
    </div>
  );
};
```

---

## 📱 Passo 9: Componente de Card (Mobile)

### **Arquivo: `src/components/BeneficiaryCard.tsx`**

```typescript
import React from 'react';
import { BeneficiaryListItem } from '../types/beneficiary.types';
import { StatusBadge } from './StatusBadge';

interface Props {
  beneficiary: BeneficiaryListItem;
  onSelect: (id: number) => void;
}

export const BeneficiaryCard: React.FC<Props> = ({ beneficiary, onSelect }) => {
  const formatCPF = (cpf: string) => {
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  return (
    <div
      onClick={() => onSelect(beneficiary.id)}
      className="bg-white rounded-lg shadow p-4 cursor-pointer hover:shadow-md transition-shadow"
    >
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">
            {beneficiary.full_name}
          </h3>
          <p className="text-sm text-gray-600">
            CPF: {formatCPF(beneficiary.cpf)}
          </p>
        </div>
        <StatusBadge status={beneficiary.status} />
      </div>

      {beneficiary.protocol_number && (
        <p className="text-sm text-gray-600 mb-1">
          Protocolo: <span className="font-medium">{beneficiary.protocol_number}</span>
        </p>
      )}

      <p className="text-sm text-gray-600 mb-2">
        {beneficiary.municipality_name || 'Município não informado'} / {beneficiary.uf || '-'}
      </p>

      {beneficiary.submitted_at && (
        <p className="text-xs text-gray-500">
          Submetido em: {formatDate(beneficiary.submitted_at)}
        </p>
      )}
    </div>
  );
};
```

---

## 📋 Passo 10: Página Principal (Completa)

### **Arquivo: `src/pages/BeneficiaryList.tsx`**

```typescript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useBeneficiaries } from '../hooks/useBeneficiaries';
import { BeneficiaryFilters } from '../components/BeneficiaryFilters';
import { BeneficiaryCard } from '../components/BeneficiaryCard';
import { Pagination } from '../components/Pagination';
import { StatusBadge } from '../components/StatusBadge';

export const BeneficiaryList: React.FC = () => {
  const navigate = useNavigate();

  // Estados dos filtros
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [uf, setUf] = useState('');
  const [hasCadunico, setHasCadunico] = useState('');

  // Query com React Query
  const { data, isLoading, error } = useBeneficiaries({
    page,
    search: search || undefined,
    status: status || undefined,
    uf: uf || undefined,
    has_cadunico: hasCadunico ? hasCadunico === 'true' : undefined,
  });

  // Funções auxiliares
  const formatCPF = (cpf: string) => {
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const handleClearFilters = () => {
    setSearch('');
    setStatus('');
    setUf('');
    setHasCadunico('');
    setPage(1);
  };

  const handleViewDetails = (id: number) => {
    navigate(`/beneficiaries/${id}`);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando beneficiários...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Erro ao carregar dados</h2>
          <p className="text-gray-600 mb-4">{error.message}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Beneficiários</h1>
          <p className="mt-1 text-sm text-gray-600">
            {data?.count || 0} beneficiários cadastrados
          </p>
        </div>

        {/* Filtros */}
        <BeneficiaryFilters
          search={search}
          status={status}
          uf={uf}
          hasCadunico={hasCadunico}
          onSearchChange={setSearch}
          onStatusChange={setStatus}
          onUfChange={setUf}
          onCadunicoChange={setHasCadunico}
          onClearFilters={handleClearFilters}
        />

        {/* Tabela Desktop */}
        <div className="hidden md:block bg-white shadow overflow-hidden sm:rounded-lg">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Protocolo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nome
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CPF
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Município/UF
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Submetido em
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data?.results.map((beneficiary) => (
                <tr key={beneficiary.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {beneficiary.protocol_number || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {beneficiary.full_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatCPF(beneficiary.cpf)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {beneficiary.municipality_name || '-'} / {beneficiary.uf || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <StatusBadge status={beneficiary.status} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(beneficiary.submitted_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleViewDetails(beneficiary.id)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Ver detalhes
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {data?.results.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">Nenhum beneficiário encontrado</p>
            </div>
          )}
        </div>

        {/* Cards Mobile */}
        <div className="md:hidden space-y-4">
          {data?.results.map((beneficiary) => (
            <BeneficiaryCard
              key={beneficiary.id}
              beneficiary={beneficiary}
              onSelect={handleViewDetails}
            />
          ))}

          {data?.results.length === 0 && (
            <div className="text-center py-12 bg-white rounded-lg">
              <p className="text-gray-500">Nenhum beneficiário encontrado</p>
            </div>
          )}
        </div>

        {/* Paginação */}
        {data && data.count > 0 && (
          <div className="mt-6">
            <Pagination
              currentPage={page}
              totalItems={data.count}
              pageSize={20}
              onPageChange={setPage}
              hasNext={!!data.next}
              hasPrevious={!!data.previous}
            />
          </div>
        )}
      </div>
    </div>
  );
};
```

---

## ⚙️ Passo 11: Configuração do React Query

### **Arquivo: `src/main.tsx` ou `src/App.tsx`**

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

// Configurar React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000, // 30 segundos
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
```

---

## 📦 Passo 12: Instalar Dependências

```bash
# Instalar React Query
npm install @tanstack/react-query

# Instalar Axios
npm install axios

# Instalar React Router (se não tiver)
npm install react-router-dom

# Instalar tipos TypeScript
npm install -D @types/react @types/react-dom @types/node
```

---

## 🧪 Passo 13: Testar

1. **Iniciar o backend**:
```bash
cd habitacao-back
docker compose up -d
```

2. **Iniciar o frontend**:
```bash
npm run dev
```

3. **Acessar**: http://localhost:5173/beneficiaries

---

## ✅ Checklist de Implementação

- [ ] Configurar API base (`api.config.ts`)
- [ ] Criar cliente HTTP com Axios (`api.service.ts`)
- [ ] Definir tipos TypeScript (`beneficiary.types.ts`)
- [ ] Criar service de beneficiários (`beneficiary.service.ts`)
- [ ] Criar hook React Query (`useBeneficiaries.ts`)
- [ ] Criar componente StatusBadge
- [ ] Criar componente de Filtros
- [ ] Criar componente de Paginação
- [ ] Criar componente de Card (mobile)
- [ ] Criar página principal de listagem
- [ ] Configurar React Query no App
- [ ] Testar filtros e paginação
- [ ] Testar responsividade (mobile/desktop)

---

## 🎯 Resultado Esperado

- ✅ Listagem funcionando com paginação
- ✅ Busca em tempo real
- ✅ Filtros por status, UF, CadÚnico
- ✅ Design responsivo (tabela desktop + cards mobile)
- ✅ Loading states e tratamento de erros
- ✅ Performance otimizada com React Query

---

**Última atualização**: 2025-01-26
**Status**: ✅ Pronto para implementar
