# 🏠 Guia de Integração Front-End - API Habitação MCMV

> **Status**: ✅ Backend rodando via Docker | ✅ Problema do NIS corrigido | ✅ Pronto para integração

## 📖 Visão Geral

Este guia completo mostra como integrar o frontend com a API REST do sistema MCMV (Minha Casa Minha Vida) que está rodando em **Docker**.

### 🎯 Links Rápidos

| Recurso | URL | Descrição |
|---------|-----|-----------|
| **API Base** | `http://localhost:8000/api/v1` | Endpoint principal |
| **Swagger UI** | `http://localhost:8000/api/v1/swagger/` | Documentação interativa |
| **ReDoc** | `http://localhost:8000/api/v1/redoc/` | Documentação alternativa |
| **Admin Django** | `http://localhost:8000/admin/` | Painel administrativo |

### ⚠️ Avisos Importantes

1. **✅ Problema do NIS RESOLVIDO**: O campo `nis_number` agora aceita múltiplos `null`, mas você **DEVE** enviar `null` (não `""`) quando não houver NIS. [Ver detalhes](#%EF%B8%8F-campo-nis---correção-crítica-implementada)

2. **📦 Estrutura FLAT**: A API usa payload **flat** (todos os campos no nível raiz, sem agrupamento). [Ver exemplo](#2-criar-beneficiário---payload-completo)

3. **🔐 Autenticação JWT**: Todas as requisições (exceto login) requerem token Bearer. [Ver configuração](#-autenticação)

4. **🔢 Formatação**: Remova formatação de CPF, telefone e CEP - envie apenas números. Exemplo: `"12345678901"` (não `"123.456.789-01"`)

### 📋 Checklist Rápido

```bash
# 1. Backend está rodando?
docker compose ps
# Deve mostrar: habitacao_web (up), habitacao_db (up)

# 2. API está respondendo?
curl http://localhost:8000/api/v1/beneficiaries/
# Deve retornar JSON (mesmo que vazio ou erro de auth)

# 3. Testar login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"sua_senha"}'
# Deve retornar access_token e refresh_token
```

---

## 🚀 Configuração Inicial

### URLs da API (Docker)

```javascript
// Desenvolvimento Local
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Através do Nginx (produção local)
const API_BASE_URL = 'http://localhost/api/v1';
```

### Configuração do Axios

```typescript
// src/config/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para tratar erros
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expirado, tentar refresh
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post('http://localhost:8000/api/v1/auth/refresh', {
            refresh: refreshToken
          });

          localStorage.setItem('access_token', response.data.data.access);

          // Retry original request
          error.config.headers.Authorization = `Bearer ${response.data.data.access}`;
          return axios(error.config);
        } catch (refreshError) {
          // Refresh falhou, redirecionar para login
          localStorage.clear();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## 📝 CRUD de Beneficiários

### 1. Listar Beneficiários (com paginação e filtros)

```typescript
// src/services/beneficiary.service.ts
import api from '@/config/api';

interface BeneficiaryFilters {
  page?: number;
  page_size?: number;
  search?: string;
  status?: string;
  municipality?: number;
  ordering?: string;
}

interface BeneficiaryListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Beneficiary[];
}

export const beneficiaryService = {
  // Listar beneficiários
  async list(filters: BeneficiaryFilters = {}): Promise<BeneficiaryListResponse> {
    const response = await api.get('/beneficiaries/', { params: filters });
    return response.data;
  },

  // Buscar beneficiário por ID
  async getById(id: number) {
    const response = await api.get(`/beneficiaries/${id}/`);
    return response.data.data;
  },

  // Criar beneficiário
  async create(data: CreateBeneficiaryDTO) {
    const response = await api.post('/beneficiaries/', data);
    return response.data.data;
  },

  // Atualizar beneficiário
  async update(id: number, data: UpdateBeneficiaryDTO) {
    const response = await api.patch(`/beneficiaries/${id}/`, data);
    return response.data.data;
  },

  // Deletar beneficiário
  async delete(id: number) {
    await api.delete(`/beneficiaries/${id}/`);
  },
};
```

---

### 2. Criar Beneficiário - Payload Completo

**⚠️ IMPORTANTE**: A API usa estrutura **FLAT** (todos os campos no nível raiz, sem agrupamento).

#### 📊 Estrutura do Payload

```typescript
// ❌ NÃO é assim (nested/aninhada):
{
  personal: { full_name: "...", cpf: "..." },
  address: { address_line: "..." },
  economy: { has_cadunico: false }
}

// ✅ É assim (flat/plana):
{
  full_name: "...",
  cpf: "...",
  address_line: "...",
  has_cadunico: false
}
```

#### 📝 Interface TypeScript Completa

```typescript
// src/types/beneficiary.types.ts

export interface CreateBeneficiaryDTO {
  // === DADOS PESSOAIS === //
  full_name: string;                      // Obrigatório
  cpf: string;                            // Obrigatório - Formato: 000.000.000-00 ou apenas números
  rg?: string;
  birth_date?: string;                    // Formato: YYYY-MM-DD
  marital_status?: 'SOLTEIRO' | 'CASADO' | 'UNIAO_ESTAVEL' | 'VIUVO' | 'DIVORCIADO' | 'SEPARADO' | 'OUTRO';

  // === CONTATOS === //
  phone_primary?: string;                 // Formato: (00) 00000-0000 ou apenas números
  phone_secondary?: string;
  email?: string;

  // === ENDEREÇO === //
  address_line?: string;
  address_number?: string;
  address_complement?: string;
  neighborhood?: string;
  municipality_id?: number | null;        // ID do município
  cep?: string;                           // Formato: 00000-000 ou apenas números
  uf?: string;                            // Sigla do estado (SP, RJ, etc)

  // === CÔNJUGE === //
  spouse_name?: string;
  spouse_rg?: string;
  spouse_birth_date?: string;             // Formato: YYYY-MM-DD

  // === DADOS ECONÔMICOS === //
  main_occupation?: string;
  gross_family_income?: number;           // Decimal
  has_cadunico?: boolean;                 // Default: false
  nis_number?: string | null;             // ✅ IMPORTANTE: null quando não tem NIS, não ''

  // === COMPOSIÇÃO FAMILIAR === //
  family_size?: number;                   // Default: 1, mínimo 1
  has_elderly?: boolean;                  // Default: false
  elderly_count?: number;                 // Default: 0
  has_children?: boolean;                 // Default: false
  children_count?: number;                // Default: 0
  has_disability_or_tea?: boolean;        // Default: false
  disability_or_tea_count?: number;       // Default: 0
  household_head_gender?: 'MASCULINO' | 'FEMININO' | 'OUTRO' | 'NAO_INFORMADO';
  family_in_cadunico_updated?: boolean;   // Default: false

  // === SITUAÇÃO HABITACIONAL === //
  no_own_house?: boolean;                 // Default: false
  precarious_own_house?: boolean;         // Default: false
  cohabitation?: boolean;                 // Default: false
  improvised_dwelling?: boolean;          // Default: false
  pays_rent?: boolean;                    // Default: false
  rent_value?: number;                    // Decimal (se pays_rent = true)
  other_housing_desc?: string;

  // === OBSERVAÇÕES === //
  notes?: string;
}
```

### ⚠️ Campo NIS - Correção Crítica Implementada

**PROBLEMA RESOLVIDO**: O campo `nis_number` causava erro `IntegrityError` quando múltiplos beneficiários eram cadastrados sem NIS.

**✅ Solução implementada no backend**: Strings vazias são convertidas para `NULL` automaticamente.

**🎯 O que o frontend DEVE fazer**:

```typescript
// ❌ INCORRETO - Causa erro
{
  has_cadunico: false,
  nis_number: '',  // ❌ NÃO envie string vazia
}

// ✅ CORRETO - Funciona perfeitamente
{
  has_cadunico: false,
  nis_number: null,  // ✅ Envie null quando não há NIS
}

// ✅ CORRETO - Com NIS
{
  has_cadunico: true,
  nis_number: '12345678901',  // ✅ Envie o NIS quando houver
}
```

**Função auxiliar recomendada**:

```typescript
// src/utils/formatters.ts
export function formatNisNumber(value: string | undefined | null): string | null {
  // Se não há valor ou é string vazia, retorna null
  if (!value || value.trim() === '') {
    return null;
  }
  // Retorna o valor limpo (apenas números)
  return value.replace(/\D/g, '');
}

// Uso no formulário (estrutura FLAT)
const payload: CreateBeneficiaryDTO = {
  full_name: formData.full_name,
  cpf: formData.cpf.replace(/\D/g, ''),  // Remove formatação
  has_cadunico: formData.has_cadunico,
  nis_number: formatNisNumber(formData.nis_number), // ✅ Sempre retorna null ou string válida
  // ... outros campos
};
```

---

### 3. Exemplo Prático - Componente de Cadastro

```typescript
// src/components/BeneficiaryForm.tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { beneficiaryService } from '@/services/beneficiary.service';
import { CreateBeneficiaryDTO } from '@/types/beneficiary.types';

export function BeneficiaryForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<CreateBeneficiaryDTO>();
  const [loading, setLoading] = useState(false);

  const onSubmit = async (data: CreateBeneficiaryDTO) => {
    setLoading(true);
    try {
      const beneficiary = await beneficiaryService.create(data);
      console.log('Beneficiário criado:', beneficiary);
      alert('Beneficiário cadastrado com sucesso!');
      // Redirecionar ou limpar formulário
    } catch (error: any) {
      console.error('Erro ao criar beneficiário:', error);
      alert(error.response?.data?.error?.message || 'Erro ao cadastrar beneficiário');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* DADOS PESSOAIS */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Dados Pessoais</h3>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label>Nome Completo *</label>
            <input
              {...register('full_name', { required: 'Nome é obrigatório' })}
              className="w-full border rounded px-3 py-2"
            />
            {errors.full_name && <span className="text-red-500 text-sm">{errors.full_name.message}</span>}
          </div>

          <div>
            <label>CPF *</label>
            <input
              {...register('cpf', {
                required: 'CPF é obrigatório',
                pattern: {
                  value: /^\d{3}\.\d{3}\.\d{3}-\d{2}$/,
                  message: 'CPF inválido (use formato: 000.000.000-00)'
                }
              })}
              placeholder="000.000.000-00"
              className="w-full border rounded px-3 py-2"
            />
            {errors.cpf && <span className="text-red-500 text-sm">{errors.cpf.message}</span>}
          </div>

          <div>
            <label>RG</label>
            <input
              {...register('rg')}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label>Data de Nascimento</label>
            <input
              type="date"
              {...register('birth_date')}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label>Estado Civil</label>
            <select {...register('marital_status')} className="w-full border rounded px-3 py-2">
              <option value="">Selecione</option>
              <option value="SOLTEIRO">Solteiro(a)</option>
              <option value="CASADO">Casado(a)</option>
              <option value="UNIAO_ESTAVEL">União Estável</option>
              <option value="VIUVO">Viúvo(a)</option>
              <option value="DIVORCIADO">Divorciado(a)</option>
              <option value="SEPARADO">Separado(a)</option>
              <option value="OUTRO">Outro</option>
            </select>
          </div>
        </div>
      </section>

      {/* CONTATOS */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Contatos</h3>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label>Telefone Principal</label>
            <input
              {...register('phone_primary')}
              placeholder="(00) 00000-0000"
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label>Telefone Secundário</label>
            <input
              {...register('phone_secondary')}
              placeholder="(00) 00000-0000"
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label>E-mail</label>
            <input
              type="email"
              {...register('email')}
              className="w-full border rounded px-3 py-2"
            />
          </div>
        </div>
      </section>

      {/* ENDEREÇO */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Endereço</h3>

        <div className="grid grid-cols-4 gap-4">
          <div className="col-span-2">
            <label>Logradouro</label>
            <input
              {...register('address_line')}
              placeholder="Rua, Avenida, etc."
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label>Número</label>
            <input
              {...register('address_number')}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label>Complemento</label>
            <input
              {...register('address_complement')}
              placeholder="Apto, Bloco, etc."
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label>Bairro</label>
            <input
              {...register('neighborhood')}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label>CEP</label>
            <input
              {...register('cep')}
              placeholder="00000-000"
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label>UF</label>
            <select {...register('uf')} className="w-full border rounded px-3 py-2">
              <option value="">Selecione</option>
              <option value="AC">AC</option>
              <option value="AL">AL</option>
              <option value="AM">AM</option>
              <option value="AP">AP</option>
              <option value="BA">BA</option>
              <option value="CE">CE</option>
              <option value="DF">DF</option>
              <option value="ES">ES</option>
              <option value="GO">GO</option>
              <option value="MA">MA</option>
              <option value="MG">MG</option>
              <option value="MS">MS</option>
              <option value="MT">MT</option>
              <option value="PA">PA</option>
              <option value="PB">PB</option>
              <option value="PE">PE</option>
              <option value="PI">PI</option>
              <option value="PR">PR</option>
              <option value="RJ">RJ</option>
              <option value="RN">RN</option>
              <option value="RO">RO</option>
              <option value="RR">RR</option>
              <option value="RS">RS</option>
              <option value="SC">SC</option>
              <option value="SE">SE</option>
              <option value="SP">SP</option>
              <option value="TO">TO</option>
            </select>
          </div>
        </div>
      </section>

      {/* DADOS ECONÔMICOS */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Dados Econômicos</h3>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label>Ocupação Principal</label>
            <input
              {...register('main_occupation')}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label>Renda Familiar Bruta (R$)</label>
            <input
              type="number"
              step="0.01"
              {...register('gross_family_income', { valueAsNumber: true })}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div className="flex items-center space-x-2 pt-6">
            <input
              type="checkbox"
              {...register('has_cadunico')}
              id="has_cadunico"
            />
            <label htmlFor="has_cadunico">Possui CadÚnico</label>
          </div>

          <div className="col-span-2">
            <label>Número NIS (se possui CadÚnico)</label>
            <input
              {...register('nis_number')}
              className="w-full border rounded px-3 py-2"
            />
          </div>
        </div>
      </section>

      {/* COMPOSIÇÃO FAMILIAR */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Composição Familiar</h3>

        <div className="grid grid-cols-4 gap-4">
          <div>
            <label>Tamanho da Família</label>
            <input
              type="number"
              min="1"
              {...register('family_size', { valueAsNumber: true })}
              defaultValue={1}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <input type="checkbox" {...register('has_elderly')} id="has_elderly" />
              <label htmlFor="has_elderly">Possui Idosos</label>
            </div>
            <input
              type="number"
              min="0"
              {...register('elderly_count', { valueAsNumber: true })}
              placeholder="Quantidade"
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <input type="checkbox" {...register('has_children')} id="has_children" />
              <label htmlFor="has_children">Possui Crianças</label>
            </div>
            <input
              type="number"
              min="0"
              {...register('children_count', { valueAsNumber: true })}
              placeholder="Quantidade"
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <input type="checkbox" {...register('has_disability_or_tea')} id="has_disability" />
              <label htmlFor="has_disability">Possui PcD/TEA</label>
            </div>
            <input
              type="number"
              min="0"
              {...register('disability_or_tea_count', { valueAsNumber: true })}
              placeholder="Quantidade"
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label>Gênero Chefe da Família</label>
            <select {...register('household_head_gender')} className="w-full border rounded px-3 py-2">
              <option value="">Selecione</option>
              <option value="MASCULINO">Masculino</option>
              <option value="FEMININO">Feminino</option>
              <option value="OUTRO">Outro</option>
              <option value="NAO_INFORMADO">Não Informado</option>
            </select>
          </div>
        </div>
      </section>

      {/* SITUAÇÃO HABITACIONAL */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Situação Habitacional</h3>

        <div className="grid grid-cols-3 gap-4">
          <div className="flex items-center space-x-2">
            <input type="checkbox" {...register('no_own_house')} id="no_own_house" />
            <label htmlFor="no_own_house">Não possui casa própria</label>
          </div>

          <div className="flex items-center space-x-2">
            <input type="checkbox" {...register('precarious_own_house')} id="precarious" />
            <label htmlFor="precarious">Casa própria precária</label>
          </div>

          <div className="flex items-center space-x-2">
            <input type="checkbox" {...register('cohabitation')} id="cohabitation" />
            <label htmlFor="cohabitation">Coabitação</label>
          </div>

          <div className="flex items-center space-x-2">
            <input type="checkbox" {...register('improvised_dwelling')} id="improvised" />
            <label htmlFor="improvised">Moradia improvisada</label>
          </div>

          <div className="flex items-center space-x-2">
            <input type="checkbox" {...register('pays_rent')} id="pays_rent" />
            <label htmlFor="pays_rent">Paga aluguel</label>
          </div>

          <div>
            <label>Valor do Aluguel (R$)</label>
            <input
              type="number"
              step="0.01"
              {...register('rent_value', { valueAsNumber: true })}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div className="col-span-3">
            <label>Outra Situação Habitacional</label>
            <input
              {...register('other_housing_desc')}
              className="w-full border rounded px-3 py-2"
            />
          </div>
        </div>
      </section>

      {/* OBSERVAÇÕES */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Observações</h3>
        <textarea
          {...register('notes')}
          rows={4}
          className="w-full border rounded px-3 py-2"
          placeholder="Observações adicionais sobre o beneficiário..."
        />
      </section>

      {/* BOTÕES */}
      <div className="flex justify-end space-x-4">
        <button
          type="button"
          onClick={() => window.history.back()}
          className="px-6 py-2 border rounded hover:bg-gray-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 disabled:opacity-50"
        >
          {loading ? 'Salvando...' : 'Salvar Beneficiário'}
        </button>
      </div>
    </form>
  );
}
```

---

## 🔄 Workflow de Status

### Submeter Inscrição

```typescript
export const workflowService = {
  // Submeter inscrição (DRAFT → SUBMITTED)
  async submit(beneficiaryId: number) {
    const response = await api.post(`/beneficiaries/${beneficiaryId}/submit`);
    return response.data.data;
  },

  // Iniciar análise (SUBMITTED → UNDER_REVIEW)
  async startReview(beneficiaryId: number) {
    const response = await api.post(`/beneficiaries/${beneficiaryId}/start-review`);
    return response.data.data;
  },

  // Solicitar correção
  async requestCorrection(beneficiaryId: number, message: string) {
    const response = await api.post(`/beneficiaries/${beneficiaryId}/request-correction`, {
      message
    });
    return response.data.data;
  },

  // Aprovar
  async approve(beneficiaryId: number, message?: string) {
    const response = await api.post(`/beneficiaries/${beneficiaryId}/approve`, {
      message
    });
    return response.data.data;
  },

  // Rejeitar
  async reject(beneficiaryId: number, message: string) {
    const response = await api.post(`/beneficiaries/${beneficiaryId}/reject`, {
      message
    });
    return response.data.data;
  },

  // Histórico de ações
  async getHistory(beneficiaryId: number) {
    const response = await api.get(`/beneficiaries/${beneficiaryId}/actions`);
    return response.data.data;
  },

  // Adicionar nota
  async addNote(beneficiaryId: number, message: string) {
    const response = await api.post(`/beneficiaries/${beneficiaryId}/actions/note`, {
      message
    });
    return response.data.data;
  },
};
```

---

## 📤 Upload de Documentos

```typescript
export const documentService = {
  // Listar documentos de um beneficiário
  async list(beneficiaryId: number) {
    const response = await api.get('/documents/', {
      params: { beneficiary: beneficiaryId }
    });
    return response.data.results;
  },

  // Upload de documento
  async upload(beneficiaryId: number, documentTypeId: number, file: File) {
    const formData = new FormData();
    formData.append('beneficiary_id', beneficiaryId.toString());
    formData.append('document_type_id', documentTypeId.toString());
    formData.append('file', file);

    const response = await api.post('/documents/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.data;
  },

  // Validar documento
  async validate(documentId: number, notes?: string) {
    const response = await api.post(`/documents/${documentId}/validate`, { notes });
    return response.data.data;
  },

  // Deletar documento
  async delete(documentId: number) {
    await api.delete(`/documents/${documentId}/`);
  },
};

// Componente de Upload
export function DocumentUpload({ beneficiaryId }: { beneficiaryId: number }) {
  const [documentTypes, setDocumentTypes] = useState([]);
  const [selectedType, setSelectedType] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    if (!selectedType || !file) {
      alert('Selecione o tipo de documento e o arquivo');
      return;
    }

    setUploading(true);
    try {
      await documentService.upload(beneficiaryId, Number(selectedType), file);
      alert('Documento enviado com sucesso!');
      setFile(null);
      setSelectedType('');
    } catch (error) {
      console.error('Erro ao enviar documento:', error);
      alert('Erro ao enviar documento');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <select
        value={selectedType}
        onChange={(e) => setSelectedType(e.target.value)}
        className="w-full border rounded px-3 py-2"
      >
        <option value="">Selecione o tipo de documento</option>
        {/* Carregar tipos de documentos da API */}
      </select>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        accept=".pdf,.jpg,.jpeg,.png"
        className="w-full"
      />

      <button
        onClick={handleUpload}
        disabled={uploading || !file || !selectedType}
        className="px-4 py-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 disabled:opacity-50"
      >
        {uploading ? 'Enviando...' : 'Enviar Documento'}
      </button>
    </div>
  );
}
```

---

## 📊 Dashboard - Buscar Dados

```typescript
export const dashboardService = {
  // Visão geral
  async getOverview() {
    const response = await api.get('/dashboard');
    return response.data.data;
  },

  // Estatísticas por município
  async getMunicipalityStats(municipalityId: number) {
    const response = await api.get('/dashboard/municipality', {
      params: { municipality_id: municipalityId }
    });
    return response.data.data;
  },

  // Minhas atribuições
  async getMyAssignments() {
    const response = await api.get('/dashboard/my-assignments');
    return response.data.data;
  },
};

// Hook personalizado para dashboard
export function useDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await dashboardService.getOverview();
        setStats(data);
      } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
      } finally {
        setLoading(false);
      }
    }

    loadStats();
  }, []);

  return { stats, loading };
}
```

---

## 🗂️ Dados Base (Municípios, Critérios, etc)

```typescript
export const baseDataService = {
  // Listar municípios
  async getMunicipalities(uf?: string) {
    const response = await api.get('/municipalities/', {
      params: { uf }
    });
    return response.data.results;
  },

  // Listar critérios de priorização
  async getPriorityCriteria() {
    const response = await api.get('/priority-criteria/');
    return response.data.results;
  },

  // Listar benefícios sociais
  async getSocialBenefits() {
    const response = await api.get('/social-benefits/');
    return response.data.results;
  },

  // Listar tipos de documentos
  async getDocumentTypes() {
    const response = await api.get('/document-types/');
    return response.data.results;
  },
};
```

---

## ✅ Validações Importantes

### Campos Obrigatórios Mínimos:
```typescript
const requiredFields = {
  full_name: 'Nome completo é obrigatório',
  cpf: 'CPF é obrigatório e deve ser único',
};
```

### Validações de Formato:
```typescript
const validators = {
  cpf: /^\d{3}\.\d{3}\.\d{3}-\d{2}$/,
  cep: /^\d{5}-\d{3}$/,
  phone: /^\(\d{2}\)\s?\d{4,5}-\d{4}$/,
};
```

### Regras de Negócio:
- Se `has_cadunico = true`, `nis_number` deve ser preenchido
- Se `pays_rent = true`, `rent_value` deve ser maior que 0
- CPF deve ser único no sistema
- NIS deve ser único no sistema (se informado)
- `family_size` deve ser >= 1

---

## 🎨 Status e Badges

```typescript
export const statusConfig = {
  DRAFT: {
    label: 'Rascunho',
    color: 'gray',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-800',
  },
  SUBMITTED: {
    label: 'Submetida',
    color: 'blue',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-800',
  },
  UNDER_REVIEW: {
    label: 'Em Análise',
    color: 'yellow',
    bgColor: 'bg-yellow-100',
    textColor: 'text-yellow-800',
  },
  CORRECTION_REQUESTED: {
    label: 'Correção Solicitada',
    color: 'orange',
    bgColor: 'bg-orange-100',
    textColor: 'text-orange-800',
  },
  APPROVED: {
    label: 'Aprovada',
    color: 'green',
    bgColor: 'bg-green-100',
    textColor: 'text-green-800',
  },
  REJECTED: {
    label: 'Rejeitada',
    color: 'red',
    bgColor: 'bg-red-100',
    textColor: 'text-red-800',
  },
};

// Componente Badge
export function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] || statusConfig.DRAFT;

  return (
    <span className={`px-3 py-1 rounded-full text-sm font-medium ${config.bgColor} ${config.textColor}`}>
      {config.label}
    </span>
  );
}
```

---

## 🚨 Tratamento de Erros

```typescript
// Tratamento global de erros
export function handleApiError(error: any) {
  if (error.response) {
    // Erro retornado pela API
    const { data, status } = error.response;

    switch (status) {
      case 400:
        return data.error?.message || 'Dados inválidos';
      case 401:
        return 'Sessão expirada. Faça login novamente.';
      case 403:
        return 'Você não tem permissão para esta ação';
      case 404:
        return 'Recurso não encontrado';
      case 500:
        return 'Erro no servidor. Tente novamente mais tarde.';
      default:
        return data.error?.message || 'Erro desconhecido';
    }
  } else if (error.request) {
    // Erro de rede
    return 'Erro de conexão. Verifique sua internet.';
  }

  return 'Erro inesperado';
}
```

---

## 🔐 Permissões por Papel

```typescript
export const rolePermissions = {
  ADMIN: {
    canCreate: true,
    canUpdate: true,
    canDelete: true,
    canApprove: true,
    canReject: true,
    canViewAll: true,
  },
  COORDINATOR: {
    canCreate: true,
    canUpdate: true,
    canDelete: true,
    canApprove: true,
    canReject: true,
    canViewAll: true,
  },
  ANALYST: {
    canCreate: true,
    canUpdate: true,
    canDelete: false,
    canApprove: true,
    canReject: true,
    canViewAll: false, // Apenas seu município
  },
  CLERK: {
    canCreate: true,
    canUpdate: true,
    canDelete: false,
    canApprove: false,
    canReject: false,
    canViewAll: false,
  },
};

// Hook para verificar permissões
export function usePermissions() {
  const user = useAuth(); // Seu hook de autenticação

  return rolePermissions[user.role] || rolePermissions.CLERK;
}
```

---

## 📦 Resumo - Checklist de Implementação

✅ **Setup Inicial:**
- [ ] Configurar Axios com interceptors
- [ ] Configurar variáveis de ambiente (API_BASE_URL)
- [ ] Implementar sistema de autenticação JWT

✅ **Serviços:**
- [ ] Criar `beneficiaryService` com CRUD completo
- [ ] Criar `workflowService` para ações de status
- [ ] Criar `documentService` para upload
- [ ] Criar `dashboardService` para estatísticas
- [ ] Criar `baseDataService` para dados auxiliares

✅ **Componentes:**
- [ ] Formulário de cadastro de beneficiário
- [ ] Listagem com paginação e filtros
- [ ] Detalhes do beneficiário
- [ ] Upload de documentos
- [ ] Cards de estatísticas (dashboard)

✅ **Funcionalidades:**
- [ ] Validação de formulários (react-hook-form ou similar)
- [ ] Máscaras de input (CPF, telefone, CEP)
- [ ] Tratamento de erros global
- [ ] Sistema de notificações/toast
- [ ] Loading states

---

## 🐳 Docker - Considerações

### Network entre Front e Back

Se o front-end também rodar em Docker, use network do Docker Compose:

```yaml
# docker-compose.yml do front-end
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://habitacao_web:8000/api/v1
    networks:
      - habitacao_network

networks:
  habitacao_network:
    external: true
    name: habitacao-back_habitacao_network
```

### Variáveis de Ambiente (.env do front)

```bash
# .env
VITE_API_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT=30000
```

---

## 💡 Exemplo Real de Payload Completo

### Exemplo 1: Beneficiário SEM NIS (mais comum)

```json
{
  "full_name": "Maria Silva Santos",
  "cpf": "12345678901",
  "rg": "123456789",
  "birth_date": "1985-03-15",
  "marital_status": "CASADO",
  "phone_primary": "11987654321",
  "phone_secondary": "11345678901",
  "email": "maria.silva@example.com",
  "address_line": "Rua das Flores",
  "address_number": "123",
  "address_complement": "Apto 45",
  "neighborhood": "Centro",
  "municipality_id": 1,
  "cep": "01234567",
  "uf": "SP",
  "spouse_name": "José Santos",
  "spouse_rg": "987654321",
  "spouse_birth_date": "1983-07-20",
  "main_occupation": "Vendedor",
  "gross_family_income": 3500.00,
  "has_cadunico": false,
  "nis_number": null,
  "family_size": 4,
  "has_elderly": false,
  "elderly_count": 0,
  "has_children": true,
  "children_count": 2,
  "has_disability_or_tea": false,
  "disability_or_tea_count": 0,
  "household_head_gender": "FEMININO",
  "family_in_cadunico_updated": false,
  "no_own_house": true,
  "precarious_own_house": false,
  "cohabitation": false,
  "improvised_dwelling": false,
  "pays_rent": true,
  "rent_value": 800.00,
  "other_housing_desc": "",
  "notes": "Família em situação de vulnerabilidade social"
}
```

### Exemplo 2: Beneficiário COM NIS

```json
{
  "full_name": "João Pereira",
  "cpf": "98765432100",
  "birth_date": "1990-08-10",
  "phone_primary": "21998765432",
  "gross_family_income": 1200.00,
  "has_cadunico": true,
  "nis_number": "12345678901",
  "family_size": 3,
  "has_elderly": false,
  "elderly_count": 0,
  "has_children": true,
  "children_count": 1,
  "has_disability_or_tea": false,
  "disability_or_tea_count": 0,
  "family_in_cadunico_updated": true,
  "no_own_house": true,
  "precarious_own_house": false,
  "cohabitation": true,
  "improvised_dwelling": false,
  "pays_rent": false
}
```

### Exemplo 3: Cadastro Mínimo (apenas campos obrigatórios)

```json
{
  "full_name": "Ana Costa",
  "cpf": "11122233344"
}
```

**⚠️ Nota**: Campos opcionais não precisam ser enviados. O backend aplica valores padrão automaticamente:
- Campos booleanos: `false`
- Contadores (`family_size`, `children_count`, etc): `0` ou `1`
- Campos de texto: string vazia `""`
- `nis_number` quando vazio: `null` (convertido automaticamente)

---

## 📞 Suporte

- **Swagger UI**: http://localhost:8000/api/v1/swagger/
- **ReDoc**: http://localhost:8000/api/v1/redoc/
- **Documentação Completa**: Ver `API_DOCUMENTATION.md`
- **Correção NIS**: Ver `BACKEND_FIX_NIS_NUMBER.md`

---

## 🔗 Links Úteis

- **Repositório Backend**: `/habitacao-back`
- **Docker Compose**: `docker compose up -d` para iniciar
- **Logs do Backend**: `docker compose logs -f web`
- **Acessar container**: `docker compose exec web bash`
- **Migrations**: `docker compose exec web python manage.py migrate`
- **Shell Django**: `docker compose exec web python manage.py shell`

---

## 📌 Resumo Rápido para Desenvolvedores

### ✅ Estrutura Correta do Payload

```typescript
// Campos obrigatórios mínimos
{
  full_name: string,
  cpf: string
}

// Payload completo (estrutura FLAT)
{
  // Pessoais
  full_name: "Maria Silva",
  cpf: "12345678901",  // Apenas números

  // Econômicos
  has_cadunico: false,
  nis_number: null,  // ⚠️ null quando vazio, não ""
  gross_family_income: 2500.00,

  // Familiares
  family_size: 4,
  has_children: true,
  children_count: 2,

  // Habitacionais
  pays_rent: true,
  rent_value: 800.00
}
```

### ⚠️ Erros Comuns e Como Evitar

| Erro | Causa | Solução |
|------|-------|---------|
| `IntegrityError: Duplicate entry ''` | `nis_number: ""` | Use `nis_number: null` ✅ |
| `Validation error: This field is required` | Faltando `full_name` ou `cpf` | Sempre envie esses campos ✅ |
| `Invalid CPF format` | CPF com formatação `"123.456.789-01"` | Use apenas números `"12345678901"` ✅ |
| `401 Unauthorized` | Token JWT ausente/expirado | Adicione `Authorization: Bearer {token}` ✅ |

### 🎯 Checklist de Validação no Frontend

Antes de enviar o payload, verifique:

- [ ] `full_name` está preenchido
- [ ] `cpf` contém apenas números (11 dígitos)
- [ ] `nis_number` é `null` ou string com 11 dígitos (não `""`)
- [ ] Telefones contêm apenas números (se preenchidos)
- [ ] CEP contém apenas números (se preenchido)
- [ ] Valores monetários são números (não strings)
- [ ] Campos booleanos são `true` ou `false` (não strings)

### 🚀 Exemplo de Requisição Completa

```typescript
const response = await fetch('http://localhost:8000/api/v1/beneficiaries/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`,
  },
  body: JSON.stringify({
    full_name: formData.full_name,
    cpf: formData.cpf.replace(/\D/g, ''),  // Remove formatação
    has_cadunico: formData.has_cadunico,
    nis_number: formData.nis_number?.trim() || null,  // null se vazio
    // ... outros campos
  }),
});

if (!response.ok) {
  const error = await response.json();
  console.error('Erro:', error);
}

const data = await response.json();
console.log('Beneficiário criado:', data);
```

---

**Última atualização**: 2025-01-26
**Status**: ✅ Documentação corrigida com estrutura FLAT real da API
**Versão da API**: v1
