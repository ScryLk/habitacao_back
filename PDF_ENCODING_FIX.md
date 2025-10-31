# 🔧 Correção de Encoding UTF-8 na Exportação de PDF

> **Problema Identificado**: Caracteres especiais aparecem incorretos no PDF exportado
> **Exemplo**: "CadÜnico" em vez de "CadÚnico"

---

## 🐛 Problema

No PDF exportado, caracteres acentuados estão aparecendo incorretos:
- ❌ `CadÜnico` (incorreto)
- ✅ `CadÚnico` (correto)

**Causa**: O arquivo está sendo gerado sem especificar corretamente o encoding UTF-8 no Blob.

---

## ✅ Solução

### Arquivo Frontend: `src/pages/BeneficiariesListPage.tsx`

**Localização**: Função `generatePDF()` (aproximadamente linha 76)

**ANTES** (Incorreto):
```typescript
const generatePDF = (beneficiary: any) => {
  const content = `
    FICHA DE PESQUISA INDIVIDUAL / PRÉ-CADASTRO

    Número NIS / CadÚnico: ${beneficiary.nis_number || ''}
    ...
  `;

  // ❌ PROBLEMA: Sem encoding UTF-8 explícito
  const blob = new Blob([content], { type: 'text/plain' });

  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `ficha-beneficiario-${beneficiary.cpf}.txt`;
  link.click();
};
```

**DEPOIS** (Correto):
```typescript
const generatePDF = (beneficiary: any) => {
  const content = `
========================================
FICHA DE PESQUISA INDIVIDUAL / PRÉ-CADASTRO
MINHA CASA, MINHA VIDA
========================================

DADOS PESSOAIS
Nome Completo: ${beneficiary.full_name || ''}
CPF: ${formatCPF(beneficiary.cpf) || ''}
RG: ${beneficiary.rg || ''}
Data de Nascimento: ${formatDate(beneficiary.birth_date) || ''}
Idade: ${beneficiary.age || ''} anos
Estado Civil: ${beneficiary.marital_status_display || ''}

CONTATOS
Telefone/WhatsApp 1: ${formatPhone(beneficiary.phone_primary) || ''}
Telefone/WhatsApp 2: ${formatPhone(beneficiary.phone_secondary) || ''}
E-mail: ${beneficiary.email || ''}

ENDEREÇO RESIDENCIAL
Logradouro: ${beneficiary.address_line || ''}
Número: ${beneficiary.address_number || ''}
Complemento: ${beneficiary.address_complement || ''}
Bairro: ${beneficiary.neighborhood || ''}
Município: ${beneficiary.municipality_data?.name || ''}
UF: ${beneficiary.uf || ''}
CEP: ${formatCEP(beneficiary.cep) || ''}

DADOS DO CÔNJUGE/COMPANHEIRO(A)
Nome: ${beneficiary.spouse_name || ''}
RG: ${beneficiary.spouse_rg || ''}
Data de Nascimento: ${formatDate(beneficiary.spouse_birth_date) || ''}

SITUAÇÃO ECONÔMICA
Ocupação Principal: ${beneficiary.main_occupation || ''}
Renda Familiar Bruta: ${formatCurrency(beneficiary.gross_family_income) || 'Não informada'}
Possui CadÚnico: ${beneficiary.has_cadunico ? '☑ Sim' : '☐ Não'}
Número NIS / CadÚnico: ${beneficiary.nis_number || 'Não informado'}

COMPOSIÇÃO FAMILIAR
Número de Pessoas na Família: ${beneficiary.family_size || 1}
Idosos (60+ anos): ${beneficiary.elderly_count || 0}
Crianças (0-17 anos): ${beneficiary.children_count || 0}
Pessoas com Deficiência/TEA: ${beneficiary.disability_or_tea_count || 0}
Responsável Familiar: ${beneficiary.household_head_gender_display || ''}
Família no CadÚnico atualizada: ${beneficiary.family_in_cadunico_updated ? '☑ Sim' : '☐ Não'}

SITUAÇÃO HABITACIONAL
${beneficiary.no_own_house ? '☑' : '☐'} Não possui casa própria
${beneficiary.precarious_own_house ? '☑' : '☐'} Casa própria precária
${beneficiary.cohabitation ? '☑' : '☐'} Coabitação (mora com familiares)
${beneficiary.improvised_dwelling ? '☑' : '☐'} Moradia improvisada
${beneficiary.pays_rent ? '☑' : '☐'} Paga aluguel: ${formatCurrency(beneficiary.rent_value) || ''}
Outra situação: ${beneficiary.other_housing_desc || 'Não informado'}

DOCUMENTAÇÃO APRESENTADA
☐ RG e CPF
☐ Certidão de Nascimento/Casamento
☐ Comprovante de residência
☐ Comprovante de renda (quando houver)
☐ Número NIS / CadÚnico

OBSERVAÇÕES:
${beneficiary.notes || 'Sem observações'}

========================================
Data do Cadastro: ${formatDate(beneficiary.created_at)}
Protocolo: ${beneficiary.protocol_number || 'Aguardando submissão'}
Status: ${beneficiary.status_display || ''}
========================================
`;

  // ✅ SOLUÇÃO: Adicionar charset UTF-8
  const blob = new Blob([content], {
    type: 'text/plain;charset=utf-8'
  });

  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `ficha-beneficiario-${beneficiary.cpf}.txt`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(link.href);
};

// Funções auxiliares de formatação
const formatCPF = (cpf: string) => {
  if (!cpf) return '';
  return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
};

const formatPhone = (phone: string) => {
  if (!phone) return '';
  return phone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
};

const formatCEP = (cep: string) => {
  if (!cep) return '';
  return cep.replace(/(\d{5})(\d{3})/, '$1-$2');
};

const formatDate = (date: string) => {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleDateString('pt-BR');
};

const formatCurrency = (value: number | string) => {
  if (!value) return '';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return `R$ ${num.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};
```

---

## 🎯 Mudanças Principais

### 1. **Encoding UTF-8 Explícito** ✅

```typescript
// ANTES
{ type: 'text/plain' }

// DEPOIS
{ type: 'text/plain;charset=utf-8' }
```

### 2. **Funções de Formatação** ✅

Adicionei funções para formatar:
- **CPF**: `123.456.789-00`
- **Telefone**: `(11) 98765-4321`
- **CEP**: `01310-200`
- **Data**: `27/10/2025`
- **Moeda**: `R$ 2.800,00`

### 3. **Checkboxes com Unicode** ✅

```typescript
☑ - Checkbox marcado (U+2611)
☐ - Checkbox vazio (U+2610)
```

### 4. **Cleanup de URL Object** ✅

```typescript
// Boa prática: limpar o objeto URL após uso
document.body.appendChild(link);
link.click();
document.body.removeChild(link);
URL.revokeObjectURL(link.href);
```

---

## 🧪 Como Testar

### 1. Aplicar a correção no frontend

Editar o arquivo `src/pages/BeneficiariesListPage.tsx` com o código corrigido acima.

### 2. Recarregar a página

```bash
# No navegador
Ctrl + Shift + R  # ou Cmd + Shift + R (Mac)
```

### 3. Testar com o beneficiário ID 18

1. Acessar: http://localhost:5173/painel/beneficiarios
2. Localizar "João Pedro da Silva" (ID 18)
3. Clicar no botão PDF
4. Verificar o arquivo exportado

### 4. Verificar caracteres especiais

Abrir o arquivo `.txt` gerado e verificar:
- ✅ `CadÚnico` (correto)
- ✅ `Situação` (correto)
- ✅ `Família` (correto)
- ✅ `☑` e `☐` (checkboxes Unicode)

---

## 📊 Resultado Esperado

```
========================================
FICHA DE PESQUISA INDIVIDUAL / PRÉ-CADASTRO
MINHA CASA, MINHA VIDA
========================================

DADOS PESSOAIS
Nome Completo: João Pedro da Silva
CPF: 123.456.789-00
RG: MG-12.345.678
Data de Nascimento: 10/05/1982
Idade: 43 anos
Estado Civil: Casado(a)

CONTATOS
Telefone/WhatsApp 1: (11) 98765-4321
Telefone/WhatsApp 2: (11) 91234-5678
E-mail: joao.pedro@email.com

ENDEREÇO RESIDENCIAL
Logradouro: Avenida Paulista
Número: 1500
Complemento: Apartamento 203, Bloco B
Bairro: Bela Vista
Município: São Paulo
UF: SP
CEP: 01310-200

DADOS DO CÔNJUGE/COMPANHEIRO(A)
Nome: Maria Aparecida da Silva
RG: MG-98.765.432
Data de Nascimento: 15/08/1985

SITUAÇÃO ECONÔMICA
Ocupação Principal: Vendedor Autônomo
Renda Familiar Bruta: R$ 2.800,00
Possui CadÚnico: ☑ Sim
Número NIS / CadÚnico: 12345678901

COMPOSIÇÃO FAMILIAR
Número de Pessoas na Família: 4
Idosos (60+ anos): 0
Crianças (0-17 anos): 2
Pessoas com Deficiência/TEA: 1
Responsável Familiar: Feminino
Família no CadÚnico atualizada: ☑ Sim

SITUAÇÃO HABITACIONAL
☑ Não possui casa própria
☐ Casa própria precária
☐ Coabitação (mora com familiares)
☐ Moradia improvisada
☑ Paga aluguel: R$ 950,00
Outra situação: Aluguel em área de risco de enchente

DOCUMENTAÇÃO APRESENTADA
☐ RG e CPF
☐ Certidão de Nascimento/Casamento
☐ Comprovante de residência
☐ Comprovante de renda (quando houver)
☐ Número NIS / CadÚnico

OBSERVAÇÕES:
Família em situação de vulnerabilidade social. Renda
instável devido ao trabalho autônomo. Uma criança com
TEA necessita acompanhamento especializado. Moradia
em área de risco.

========================================
Data do Cadastro: 27/10/2025
Protocolo: Aguardando submissão
Status: Rascunho
========================================
```

---

## 🔍 Verificação do Backend

O backend está OK e retornando dados corretamente. Podemos confirmar:

```bash
# Testar endpoint
curl -X GET "http://localhost:8000/api/v1/beneficiaries/18/" \
  -H "Authorization: Bearer TOKEN" | jq '.data'
```

**Resultado esperado**: Todos os campos com acentuação correta no JSON.

---

## 📱 Alternativa: Usar Biblioteca de PDF

Se quiser gerar um PDF real (não TXT), considere usar bibliotecas como:

### 1. **jsPDF** (mais comum)

```bash
npm install jspdf
```

```typescript
import jsPDF from 'jspdf';

const generatePDF = (beneficiary: any) => {
  const doc = new jsPDF();

  doc.setFont('helvetica');
  doc.setFontSize(12);

  doc.text('FICHA DE PESQUISA INDIVIDUAL', 10, 10);
  doc.text(`Nome: ${beneficiary.full_name}`, 10, 20);
  doc.text(`CPF: ${formatCPF(beneficiary.cpf)}`, 10, 30);
  // ... adicionar todos os campos

  doc.save(`ficha-${beneficiary.cpf}.pdf`);
};
```

### 2. **react-pdf** (renderização React)

```bash
npm install @react-pdf/renderer
```

```typescript
import { Document, Page, Text, pdf } from '@react-pdf/renderer';

const BeneficiaryPDF = ({ beneficiary }) => (
  <Document>
    <Page>
      <Text>Nome: {beneficiary.full_name}</Text>
      <Text>CPF: {formatCPF(beneficiary.cpf)}</Text>
    </Page>
  </Document>
);

const generatePDF = async (beneficiary: any) => {
  const blob = await pdf(<BeneficiaryPDF beneficiary={beneficiary} />).toBlob();
  saveAs(blob, `ficha-${beneficiary.cpf}.pdf`);
};
```

---

## 📋 Checklist de Correção

- [ ] Adicionar `charset=utf-8` no Blob
- [ ] Adicionar funções de formatação (CPF, telefone, CEP, data, moeda)
- [ ] Usar checkboxes Unicode (☑ e ☐)
- [ ] Adicionar cleanup de URL object
- [ ] Testar com beneficiário ID 18 (dados completos)
- [ ] Verificar se caracteres acentuados aparecem corretamente
- [ ] (Opcional) Migrar para jsPDF para PDF real

---

**Última atualização**: 2025-10-27
**Problema**: Encoding UTF-8 incorreto
**Solução**: Adicionar `charset=utf-8` no Blob
**Arquivo**: `src/pages/BeneficiariesListPage.tsx` (função `generatePDF`)
