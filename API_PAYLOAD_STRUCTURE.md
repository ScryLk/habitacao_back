# 📦 Estrutura de Payload da API - Guia Visual

> **Status**: ✅ Documentação atualizada com estrutura real da API

## 🎯 TL;DR (Resumo Executivo)

A API **habitacao-back** usa estrutura **FLAT** (plana), onde todos os campos ficam no **nível raiz** do JSON.

```typescript
// ✅ CORRETO - Estrutura FLAT
{
  "full_name": "Maria Silva",
  "cpf": "12345678901",
  "has_cadunico": false,
  "nis_number": null
}

// ❌ INCORRETO - Estrutura Nested (não suportada)
{
  "personal": {
    "full_name": "Maria Silva",
    "cpf": "12345678901"
  },
  "economy": {
    "has_cadunico": false,
    "nis_number": null
  }
}
```

---

## 📊 Comparação Visual: FLAT vs NESTED

### ❌ Estrutura NESTED (não funciona)

```json
{
  "personal": {
    "full_name": "Maria Silva Santos",
    "cpf": "123.456.789-01",
    "rg": "12.345.678-9",
    "birth_date": "1985-03-15",
    "marital_status": "married",
    "phone_primary": "(11) 98765-4321",
    "email": "maria@example.com"
  },
  "address": {
    "address_line": "Rua das Flores",
    "address_number": "123",
    "neighborhood": "Centro",
    "cep": "01234-567",
    "uf": "SP"
  },
  "economy": {
    "has_cadunico": false,
    "nis_number": null,
    "gross_family_income": 3500.00
  },
  "family": {
    "family_size": 4,
    "has_children": true,
    "children_count": 2
  },
  "housing": {
    "pays_rent": true,
    "rent_value": 800.00
  }
}
```

**Resultado**: ❌ Erro 400 - Campos não reconhecidos

---

### ✅ Estrutura FLAT (funciona)

```json
{
  "full_name": "Maria Silva Santos",
  "cpf": "12345678901",
  "rg": "123456789",
  "birth_date": "1985-03-15",
  "marital_status": "CASADO",
  "phone_primary": "11987654321",
  "email": "maria@example.com",
  "address_line": "Rua das Flores",
  "address_number": "123",
  "neighborhood": "Centro",
  "cep": "01234567",
  "uf": "SP",
  "has_cadunico": false,
  "nis_number": null,
  "gross_family_income": 3500.00,
  "family_size": 4,
  "has_children": true,
  "children_count": 2,
  "pays_rent": true,
  "rent_value": 800.00
}
```

**Resultado**: ✅ Sucesso 201 Created

---

## 🔑 Campos Obrigatórios vs Opcionais

### Campos Obrigatórios (apenas 2)

```typescript
{
  full_name: string,  // Nome completo
  cpf: string         // CPF (apenas números: "12345678901")
}
```

### Campos Opcionais (todos os outros)

O backend aplica valores padrão automaticamente:

| Tipo | Valor Padrão |
|------|--------------|
| Booleanos | `false` |
| Números (contadores) | `0` |
| Números (tamanho família) | `1` |
| Strings | `""` (vazio) |
| NIS quando vazio | `null` |

---

## ⚠️ Campo Crítico: `nis_number`

### ❌ ERRADO

```typescript
// NÃO faça isso:
{
  has_cadunico: false,
  nis_number: ''  // ❌ String vazia causa IntegrityError
}

{
  has_cadunico: false,
  nis_number: undefined  // ❌ Pode causar problemas
}
```

### ✅ CERTO

```typescript
// Faça assim:
{
  has_cadunico: false,
  nis_number: null  // ✅ Permite múltiplos beneficiários sem NIS
}

{
  has_cadunico: true,
  nis_number: '12345678901'  // ✅ NIS válido quando tem CadÚnico
}
```

### 🔍 Por que `null` e não `""`?

- MySQL/MariaDB permite **múltiplos NULL** em campos UNIQUE ✅
- MySQL/MariaDB **NÃO permite múltiplos `""`** em campos UNIQUE ❌
- Backend converte `""` → `null` automaticamente (segurança)
- Mas é melhor enviar `null` direto do frontend (boas práticas)

---

## 🔢 Formatação de Campos

### CPF

```typescript
// ❌ ERRADO
cpf: '123.456.789-01'      // Com formatação
cpf: '123 456 789 01'      // Com espaços
cpf: '123.456.78901'       // Parcialmente formatado

// ✅ CERTO
cpf: '12345678901'         // Apenas números (11 dígitos)
```

**Código recomendado**:
```typescript
cpf: formData.cpf.replace(/\D/g, '')  // Remove tudo que não é dígito
```

### Telefone

```typescript
// ❌ ERRADO
phone_primary: '(11) 98765-4321'
phone_primary: '(11) 9 8765-4321'

// ✅ CERTO
phone_primary: '11987654321'    // 11 dígitos (celular)
phone_primary: '1134567890'     // 10 dígitos (fixo)
```

### CEP

```typescript
// ❌ ERRADO
cep: '01234-567'

// ✅ CERTO
cep: '01234567'  // 8 dígitos
```

### NIS

```typescript
// ❌ ERRADO
nis_number: '123.456.789-01'
nis_number: ''  // Causa IntegrityError

// ✅ CERTO
nis_number: '12345678901'  // 11 dígitos
nis_number: null           // Quando não tem NIS
```

---

## 📝 Exemplo Completo de Formulário React

```typescript
import { useState } from 'react';

interface FormData {
  full_name: string;
  cpf: string;
  has_cadunico: boolean;
  nis_number: string;
  // ... outros campos
}

function BeneficiaryForm() {
  const [formData, setFormData] = useState<FormData>({
    full_name: '',
    cpf: '',
    has_cadunico: false,
    nis_number: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // 🔄 Preparar payload (estrutura FLAT)
    const payload = {
      full_name: formData.full_name,
      cpf: formData.cpf.replace(/\D/g, ''),  // Remove formatação
      has_cadunico: formData.has_cadunico,
      nis_number: formData.nis_number?.trim() || null,  // ✅ null se vazio
      // ... outros campos
    };

    // 📤 Enviar para API
    const response = await fetch('http://localhost:8000/api/v1/beneficiaries/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      const data = await response.json();
      console.log('✅ Sucesso:', data);
    } else {
      const error = await response.json();
      console.error('❌ Erro:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={formData.full_name}
        onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
        placeholder="Nome completo"
      />

      <input
        type="text"
        value={formData.cpf}
        onChange={(e) => setFormData({ ...formData, cpf: e.target.value })}
        placeholder="CPF"
      />

      <label>
        <input
          type="checkbox"
          checked={formData.has_cadunico}
          onChange={(e) => setFormData({
            ...formData,
            has_cadunico: e.target.checked,
            nis_number: e.target.checked ? formData.nis_number : '',  // Limpa NIS se desmarcar
          })}
        />
        Possui CadÚnico
      </label>

      {formData.has_cadunico && (
        <input
          type="text"
          value={formData.nis_number}
          onChange={(e) => setFormData({ ...formData, nis_number: e.target.value })}
          placeholder="NIS"
        />
      )}

      <button type="submit">Cadastrar</button>
    </form>
  );
}
```

---

## 🎯 Checklist de Validação Frontend

Antes de enviar para API, verifique:

### ✅ Validações Obrigatórias

- [ ] `full_name` não está vazio
- [ ] `cpf` tem exatamente 11 dígitos (sem formatação)
- [ ] `nis_number` é `null` OU tem 11 dígitos (nunca `""`)

### ✅ Validações de Formato

- [ ] CPF: apenas números, sem `.` ou `-`
- [ ] Telefones: apenas números, sem `()`, ` ` ou `-`
- [ ] CEP: apenas números, sem `-`
- [ ] Valores monetários: tipo `number` (não `string`)

### ✅ Validações de Tipo

- [ ] Booleanos são `true`/`false` (não `"true"`/`"false"`)
- [ ] Números são tipo `number` (não `string`)
- [ ] Datas no formato `YYYY-MM-DD` (string)

### ✅ Validações de Regra de Negócio

- [ ] Se `has_cadunico = true`, então `nis_number` deve ter 11 dígitos
- [ ] Se `has_cadunico = false`, então `nis_number` deve ser `null`
- [ ] Se `pays_rent = true`, então `rent_value` deve ser > 0
- [ ] `family_size` deve ser >= 1

---

## 🔍 Debugging: Como Testar

### Teste 1: Payload Mínimo

```bash
curl -X POST http://localhost:8000/api/v1/beneficiaries/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "full_name": "Teste Mínimo",
    "cpf": "12345678901"
  }'
```

**Resultado esperado**: ✅ 201 Created

### Teste 2: Payload com NIS = null

```bash
curl -X POST http://localhost:8000/api/v1/beneficiaries/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "full_name": "Teste Sem NIS",
    "cpf": "98765432100",
    "has_cadunico": false,
    "nis_number": null
  }'
```

**Resultado esperado**: ✅ 201 Created

### Teste 3: Payload com NIS válido

```bash
curl -X POST http://localhost:8000/api/v1/beneficiaries/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "full_name": "Teste Com NIS",
    "cpf": "11122233344",
    "has_cadunico": true,
    "nis_number": "12345678901"
  }'
```

**Resultado esperado**: ✅ 201 Created

### Teste 4: Múltiplos sem NIS (validar correção)

Execute o **Teste 2** duas vezes seguidas com CPFs diferentes.

**Resultado esperado**: ✅ Ambos cadastram sem erro (antes dava IntegrityError)

---

## 🐛 Erros Comuns e Soluções

### Erro 1: IntegrityError duplicate entry ''

```json
{
  "error": "IntegrityError",
  "message": "(1062, \"Duplicate entry '' for key 'beneficiaries.nis_number'\")"
}
```

**Causa**: `nis_number` enviado como `""`

**Solução**:
```typescript
// ❌ ANTES
nis_number: ''

// ✅ DEPOIS
nis_number: null
```

### Erro 2: Field required

```json
{
  "error": "Validation error",
  "details": {
    "full_name": ["This field is required"],
    "cpf": ["This field is required"]
  }
}
```

**Causa**: Campos obrigatórios não enviados

**Solução**: Sempre envie `full_name` e `cpf`

### Erro 3: Invalid CPF

```json
{
  "error": "Validation error",
  "details": {
    "cpf": ["CPF inválido"]
  }
}
```

**Causa**: CPF com formatação ou dígitos inválidos

**Solução**:
```typescript
cpf: formData.cpf.replace(/\D/g, '')  // Remove formatação
```

### Erro 4: 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Causa**: Token JWT ausente ou inválido

**Solução**:
```typescript
headers: {
  'Authorization': `Bearer ${accessToken}`
}
```

---

## 📚 Referências

- **Guia Completo**: [FRONTEND_INTEGRATION_GUIDE.md](./FRONTEND_INTEGRATION_GUIDE.md)
- **Correção NIS**: [BACKEND_FIX_NIS_NUMBER.md](./BACKEND_FIX_NIS_NUMBER.md)
- **Documentação API**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Swagger**: http://localhost:8000/api/v1/swagger/
- **ReDoc**: http://localhost:8000/api/v1/redoc/

---

**Última atualização**: 2025-01-26
**Versão**: 1.0.0
**Status**: ✅ Documentação validada com API real
