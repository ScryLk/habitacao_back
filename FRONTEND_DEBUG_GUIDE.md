# 🔍 Guia de Depuração - Frontend Lista de Beneficiários

> **Status**: ✅ Backend testado e funcionando
> **Problema**: Frontend não está exibindo os beneficiários
> **Data**: 2025-10-26

---

## 📊 Situação Confirmada

### ✅ Backend está OK

O backend foi testado e **está funcionando perfeitamente**:

```bash
# ✅ API retornando 6 beneficiários corretamente
curl -X GET "http://localhost:8000/api/v1/beneficiaries/" \
  -H "Authorization: Bearer <TOKEN>"
```

**Resposta**:
```json
{
  "data": [
    {
      "id": 17,
      "protocol_number": null,
      "full_name": "Maria Silva Santos",
      "cpf": "48984097500",
      "municipality": null,
      "uf": "",
      "status": "DRAFT",
      "status_display": "Rascunho",
      "age": 40,
      "submitted_at": null,
      "created_at": "2025-10-26T22:36:10-0300",
      "updated_at": "2025-10-26T22:36:10-0300"
    }
    // ... mais 5 beneficiários
  ],
  "error": null,
  "meta": {
    "page": 1,
    "per_page": 25,
    "total": 6,
    "total_pages": 1
  }
}
```

### ❌ Frontend NÃO está exibindo

- URL: `http://localhost:5173/painel/beneficiarios`
- Problema: Beneficiários não aparecem na lista
- Banco de dados: 6 beneficiários confirmados

---

## 🐛 Causas Prováveis

### 1. **Problema de Autenticação** (Mais Provável)

#### ❌ Token não está sendo enviado

**Como verificar**:
1. Abra o DevTools do navegador (F12)
2. Vá na aba **Network**
3. Recarregue a página
4. Procure pela requisição para `http://localhost:8000/api/v1/beneficiaries/`
5. Clique na requisição
6. Vá em **Headers** → **Request Headers**
7. Verifique se existe o header: `Authorization: Bearer <token>`

**Se NÃO existir o header Authorization**:

**Causa**: O token não está sendo armazenado ou recuperado do localStorage.

**Solução**: Verifique o arquivo `src/services/api.service.ts`:

```typescript
// ❌ ERRADO - Não está pegando o token
const token = null; // ou ausente

// ✅ CORRETO - Deve pegar o token do localStorage
const token = localStorage.getItem('access_token');
```

**Arquivo completo correto** ([api.service.ts](src/services/api.service.ts)):

```typescript
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { API_CONFIG } from '../config/api.config';

// Criar instância do axios
export const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de requisição - Adiciona token JWT
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');  // ← CRÍTICO!

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor de resposta - Trata erros
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Se erro 401 e não é retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Tentar renovar token
        const refreshToken = localStorage.getItem('refresh_token');

        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        const response = await axios.post(`${API_CONFIG.BASE_URL}/auth/refresh`, {
          refresh: refreshToken,
        });

        const { access } = response.data.data;
        localStorage.setItem('access_token', access);

        // Atualizar header e reenviar requisição
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access}`;
        }

        return api(originalRequest);
      } catch (refreshError) {
        // Refresh falhou, redirecionar para login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

---

#### ❌ Usuário não está logado

**Como verificar**:
1. Abra o Console do DevTools (F12)
2. Digite: `localStorage.getItem('access_token')`
3. Pressione Enter

**Se retornar `null`**:

**Causa**: Usuário não fez login.

**Solução**:
1. Vá para a página de login: `http://localhost:5173/login`
2. Faça login com as credenciais:
   - **Email**: `test@test.com`
   - **Senha**: `test123`
3. Após login bem-sucedido, o token deve ser salvo no localStorage

**Verifique o código de login** (geralmente em `src/pages/Login.tsx` ou similar):

```typescript
// ✅ CORRETO - Salva tokens após login
const handleLogin = async (email: string, password: string) => {
  try {
    const response = await axios.post('http://localhost:8000/api/v1/auth/login', {
      email,
      password,
    });

    const { access, refresh, user } = response.data.data;

    // Salvar tokens no localStorage
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('user', JSON.stringify(user));

    // Redirecionar para dashboard
    navigate('/painel/beneficiarios');
  } catch (error) {
    console.error('Erro no login:', error);
  }
};
```

---

### 2. **Problema de CORS**

**Como verificar**:
1. Abra o Console do DevTools
2. Procure por erros vermelhos contendo:
   - `CORS`
   - `Access-Control-Allow-Origin`
   - `blocked by CORS policy`

**Se houver erro de CORS**:

**Causa**: Frontend rodando em porta não permitida pelo backend.

**Solução**: Verificar se o frontend está em uma porta permitida no `.env` do backend:

```bash
# Backend .env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:5173
```

✅ **Porta 5173 está permitida** (conforme `.env` atual).

---

### 3. **Problema na Chamada da API**

#### ❌ URL incorreta

**Como verificar**:
1. Vá no DevTools → Network
2. Veja qual URL está sendo chamada

**URLs corretas**:
- ✅ `http://localhost:8000/api/v1/beneficiaries/` (com `/` no final)
- ✅ `http://localhost:8000/api/v1/beneficiaries` (sem `/` no final)

**URLs incorretas**:
- ❌ `http://localhost:8000/beneficiaries/`
- ❌ `http://localhost:5173/api/v1/beneficiaries/`

**Solução**: Verificar `src/config/api.config.ts`:

```typescript
// ✅ CORRETO
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/api/v1',
  TIMEOUT: 30000,
};
```

---

### 4. **Problema no Serviço de Beneficiários**

**Arquivo**: `src/services/beneficiary.service.ts`

**Verificar**:

```typescript
import api from './api.service';
import type { BeneficiaryListResponse, BeneficiaryFilters } from '../types/beneficiary.types';

export const beneficiaryService = {
  // ✅ CORRETO - Chama endpoint correto
  list: async (filters?: BeneficiaryFilters): Promise<BeneficiaryListResponse> => {
    const params = new URLSearchParams();

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value));
        }
      });
    }

    const response = await api.get<BeneficiaryListResponse>(
      `/beneficiaries/?${params.toString()}`  // ← URL correta
    );

    return response.data;
  },
};
```

---

### 5. **Problema no Hook React Query**

**Arquivo**: `src/hooks/useBeneficiaries.ts`

**Verificar**:

```typescript
import { useQuery } from '@tanstack/react-query';
import { beneficiaryService } from '../services/beneficiary.service';
import type { BeneficiaryFilters } from '../types/beneficiary.types';

export const useBeneficiaries = (filters?: BeneficiaryFilters) => {
  return useQuery({
    queryKey: ['beneficiaries', filters],
    queryFn: () => beneficiaryService.list(filters),
    // ✅ Adicione estas opções para debugging
    retry: 1,
    onError: (error) => {
      console.error('Erro ao buscar beneficiários:', error);
    },
    onSuccess: (data) => {
      console.log('Beneficiários carregados:', data);
    },
  });
};
```

---

### 6. **Problema na Renderização do Componente**

**Arquivo**: `src/pages/BeneficiaryList.tsx`

**Verificar**:

```typescript
import { useBeneficiaries } from '../hooks/useBeneficiaries';

export const BeneficiaryList = () => {
  const [filters, setFilters] = useState<BeneficiaryFilters>({});

  const { data, isLoading, error } = useBeneficiaries(filters);

  // ✅ ADICIONE LOGS PARA DEBUGGING
  console.log('Estado do hook:', { data, isLoading, error });
  console.log('Beneficiários:', data?.data);

  if (isLoading) return <div>Carregando...</div>;
  if (error) return <div>Erro: {error.message}</div>;

  // ❌ VERIFIQUE SE ESTÁ ACESSANDO O CAMINHO CORRETO
  const beneficiaries = data?.data || [];  // ← CORRETO
  // const beneficiaries = data || [];      // ← ERRADO

  console.log('Renderizando beneficiários:', beneficiaries.length);

  return (
    <div>
      {beneficiaries.length === 0 ? (
        <p>Nenhum beneficiário encontrado</p>
      ) : (
        beneficiaries.map((b) => (
          <div key={b.id}>{b.full_name}</div>
        ))
      )}
    </div>
  );
};
```

---

### 7. **Problema na Estrutura de Resposta**

#### ❌ Tentando acessar dados em caminho errado

A API retorna dados neste formato:

```json
{
  "data": [ /* array de beneficiários */ ],
  "error": null,
  "meta": { /* paginação */ }
}
```

**Acesso CORRETO**:
```typescript
// ✅ Acessar response.data.data
const response = await api.get('/beneficiaries/');
const beneficiaries = response.data.data;  // Array de beneficiários
const pagination = response.data.meta;     // Dados de paginação
```

**Acesso ERRADO**:
```typescript
// ❌ Acessar response.data diretamente
const beneficiaries = response.data;  // Isso retorna o objeto inteiro!
```

**TypeScript Interface** (`src/types/beneficiary.types.ts`):

```typescript
export interface BeneficiaryListResponse {
  data: Beneficiary[];      // ← Array de beneficiários
  error: null | object;     // ← Sempre null se sucesso
  meta: {                   // ← Dados de paginação
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}
```

---

## 🔧 Passo a Passo de Depuração

### **Passo 1: Verificar se há token**

```javascript
// No console do navegador (F12)
localStorage.getItem('access_token')
```

**Se retornar `null`**:
- Vá para `/login` e faça login novamente

**Se retornar um token**:
- Prossiga para o Passo 2

---

### **Passo 2: Verificar chamada da API**

1. Abra DevTools (F12) → Aba **Network**
2. Recarregue a página
3. Procure pela requisição `beneficiaries/`
4. Clique nela e veja:
   - **Status Code**: Deve ser `200 OK`
   - **Response**: Deve conter array `data` com 6 beneficiários
   - **Request Headers**: Deve conter `Authorization: Bearer <token>`

**Se Status Code for 401 (Unauthorized)**:
- Token expirado ou inválido
- Faça logout e login novamente

**Se Status Code for 200 mas Response está vazia**:
- Problema no backend (improvável, já testado)

**Se não houver nenhuma requisição para `beneficiaries/`**:
- O componente não está chamando a API
- Verifique o hook `useBeneficiaries`

---

### **Passo 3: Adicionar Logs de Depuração**

No arquivo `src/pages/BeneficiaryList.tsx`, adicione:

```typescript
export const BeneficiaryList = () => {
  const { data, isLoading, error } = useBeneficiaries();

  // 🔍 LOGS DE DEBUGGING
  console.log('=== DEBUG BENEFICIARIES ===');
  console.log('1. isLoading:', isLoading);
  console.log('2. error:', error);
  console.log('3. data completo:', data);
  console.log('4. data.data:', data?.data);
  console.log('5. Quantidade:', data?.data?.length || 0);
  console.log('===========================');

  // ... resto do código
};
```

Recarregue a página e veja os logs no console.

---

### **Passo 4: Verificar Estrutura de Acesso**

**ERROS COMUNS**:

```typescript
// ❌ ERRADO 1 - Esqueceu de acessar .data.data
const beneficiaries = data;

// ❌ ERRADO 2 - Acessou só .data
const beneficiaries = data?.data?.beneficiaries;

// ✅ CORRETO
const beneficiaries = data?.data || [];
```

---

### **Passo 5: Testar Requisição Manual**

No console do navegador:

```javascript
// Testar manualmente a chamada
const token = localStorage.getItem('access_token');

fetch('http://localhost:8000/api/v1/beneficiaries/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
  .then(res => res.json())
  .then(data => {
    console.log('✅ Dados recebidos:', data);
    console.log('✅ Beneficiários:', data.data);
    console.log('✅ Total:', data.meta.total);
  })
  .catch(err => console.error('❌ Erro:', err));
```

Se isso funcionar, o problema está no código React.

---

## 📝 Checklist de Verificação

- [ ] Token existe no localStorage (`localStorage.getItem('access_token')`)
- [ ] Requisição aparece no DevTools → Network
- [ ] Status Code da requisição é 200
- [ ] Header `Authorization` está presente na requisição
- [ ] Response contém `data` com array de beneficiários
- [ ] Componente está acessando `data?.data` corretamente
- [ ] Logs de `console.log` mostram os dados
- [ ] Não há erros no Console do navegador
- [ ] URL da API está correta (`http://localhost:8000/api/v1`)
- [ ] Frontend está na porta 5173

---

## 🎯 Solução Rápida

Se você quiser testar rapidamente:

### 1. Faça login via cURL e pegue o token:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}' | python3 -c "import sys, json; data = json.load(sys.stdin); print('Token:', data['data']['access'])"
```

### 2. Copie o token e cole no localStorage:

Abra o console do navegador e execute:

```javascript
localStorage.setItem('access_token', 'COLE_O_TOKEN_AQUI');
localStorage.setItem('refresh_token', 'COLE_O_REFRESH_TOKEN_AQUI');
```

### 3. Recarregue a página

A lista deve aparecer.

---

## 📞 Credenciais de Teste

**Usuário criado para testes**:
- **Email**: `test@test.com`
- **Senha**: `test123`
- **Role**: `ANALYST`

Use estas credenciais para fazer login no frontend.

---

## 🚨 Problemas Conhecidos

### ⚠️ CORS pode bloquear requisições

**Sintoma**: Erro no console tipo:
```
Access to fetch at 'http://localhost:8000/api/v1/beneficiaries/'
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solução**: Verificar se backend tem:
```python
# core/settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # ← Deve estar aqui
]
```

### ⚠️ Token expira em 60 minutos

Se você deixar a página aberta por mais de 1 hora, o token expirará e você precisará fazer login novamente.

**Solução**: Implementar refresh automático de token no interceptor do axios.

---

## 📚 Arquivos de Referência

1. **Backend**: [API_PAYLOAD_STRUCTURE.md](API_PAYLOAD_STRUCTURE.md)
2. **Frontend**: [FRONTEND_LISTAGEM_PASSO_A_PASSO.md](FRONTEND_LISTAGEM_PASSO_A_PASSO.md)
3. **Banco**: [MYSQL_WORKBENCH_GUIDE.md](MYSQL_WORKBENCH_GUIDE.md)

---

## ✅ Teste do Backend (Já Realizado)

O backend foi testado e **está 100% funcional**:

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# Resposta: Token gerado com sucesso ✅

# Listar beneficiários
curl -X GET "http://localhost:8000/api/v1/beneficiaries/" \
  -H "Authorization: Bearer <TOKEN>"

# Resposta: 6 beneficiários retornados ✅
```

**Conclusão**: O problema está **100% no frontend**.

---

**Última atualização**: 2025-10-26
**Status**: Backend OK | Frontend precisa correção
**Total de beneficiários no banco**: 6
