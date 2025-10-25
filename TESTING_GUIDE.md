# Guia de Testes - API Sistema Habitação MCMV

## ✅ Checklist de Testes Manuais

### 1. Setup Inicial

```bash
# Instalar dependências
pip install -r requirements.txt

# Criar banco de dados
mysql -u root -p
CREATE DATABASE habitacao_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Executar migrations
python3 manage.py migrate

# Criar superusuário
python3 manage.py createsuperuser
# Email: admin@example.com
# Password: admin123

# Carregar dados iniciais
python3 manage.py load_initial_data

# Rodar servidor
python3 manage.py runserver
```

### 2. Acessar Swagger

Abra no navegador:
```
http://localhost:8000/api/v1/swagger/
```

### 3. Testes de Autenticação

#### 3.1 Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

**Salve o token retornado:**
```bash
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

#### 3.2 Obter Dados do Usuário
```bash
curl -X GET http://localhost:8000/api/v1/me \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Testes de Beneficiários

#### 4.1 Criar Município (via Admin ou shell)

Acesse http://localhost:8000/admin/ e crie um município ou use o shell:

```python
python3 manage.py shell

from habitacao.models import Municipality
mun = Municipality.objects.create(
    ibge_code='3550308',
    name='São Paulo',
    uf='SP'
)
print(f"Município criado: {mun.id}")
```

#### 4.2 Criar Beneficiário
```bash
curl -X POST http://localhost:8000/api/v1/beneficiaries/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "João da Silva Teste",
    "cpf": "111.444.777-35",
    "birth_date": "1985-05-15",
    "email": "joao@test.com",
    "phones": {
      "primary": "(11) 99999-9999"
    },
    "address": {
      "line": "Rua Teste",
      "number": "123",
      "municipality_id": 1,
      "uf": "SP",
      "cep": "01234-567"
    },
    "economy": {
      "gross_family_income": 2500.00
    },
    "family": {
      "family_size": 4
    },
    "housing": {
      "pays_rent": true,
      "rent_value": 800.00
    }
  }'
```

**Salve o ID retornado:**
```bash
export BEN_ID=1
```

#### 4.3 Listar Beneficiários
```bash
curl -X GET "http://localhost:8000/api/v1/beneficiaries/" \
  -H "Authorization: Bearer $TOKEN"
```

#### 4.4 Ver Detalhes
```bash
curl -X GET "http://localhost:8000/api/v1/beneficiaries/$BEN_ID/" \
  -H "Authorization: Bearer $TOKEN"
```

#### 4.5 Atualizar
```bash
curl -X PATCH "http://localhost:8000/api/v1/beneficiaries/$BEN_ID/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_primary": "(11) 98888-8888"
  }'
```

### 5. Testes de Documentos

#### 5.1 Criar Arquivo de Teste
```bash
echo "Este é um documento de teste" > test_doc.txt
```

#### 5.2 Upload
```bash
curl -X POST http://localhost:8000/api/v1/documents/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "beneficiary_id=$BEN_ID" \
  -F "document_type_id=1" \
  -F "file=@test_doc.txt"
```

**Salve o ID do documento:**
```bash
export DOC_ID=1
```

#### 5.3 Listar Documentos do Beneficiário
```bash
curl -X GET "http://localhost:8000/api/v1/documents/?beneficiary_id=$BEN_ID" \
  -H "Authorization: Bearer $TOKEN"
```

#### 5.4 Validar Documento
```bash
curl -X PATCH "http://localhost:8000/api/v1/documents/$DOC_ID/validate/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "validated": true,
    "notes": "Documento aprovado"
  }'
```

### 6. Testes de Workflow

#### 6.1 Submeter Inscrição
```bash
curl -X POST "http://localhost:8000/api/v1/beneficiaries/$BEN_ID/submit/" \
  -H "Authorization: Bearer $TOKEN"
```

✅ **Verifique que o `protocol_number` foi gerado!**

#### 6.2 Iniciar Análise
```bash
curl -X POST "http://localhost:8000/api/v1/beneficiaries/$BEN_ID/start-review/" \
  -H "Authorization: Bearer $TOKEN"
```

#### 6.3 Solicitar Correção
```bash
curl -X POST "http://localhost:8000/api/v1/beneficiaries/$BEN_ID/request-correction/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Por favor anexe comprovante de renda atualizado"
  }'
```

#### 6.4 Ver Histórico de Ações
```bash
curl -X GET "http://localhost:8000/api/v1/beneficiaries/$BEN_ID/actions/" \
  -H "Authorization: Bearer $TOKEN"
```

#### 6.5 Voltar para Análise (se necessário)
```bash
# Primeiro, atualize manualmente o status via admin ou shell
curl -X POST "http://localhost:8000/api/v1/beneficiaries/$BEN_ID/start-review/" \
  -H "Authorization: Bearer $TOKEN"
```

#### 6.6 Aprovar
```bash
curl -X POST "http://localhost:8000/api/v1/beneficiaries/$BEN_ID/approve/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Inscrição aprovada - família atende todos os critérios"
  }'
```

#### 6.7 Adicionar Nota
```bash
curl -X POST "http://localhost:8000/api/v1/beneficiaries/$BEN_ID/actions/note/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Beneficiário entrou em contato confirmando dados"
  }'
```

### 7. Testes de Dashboard

#### 7.1 Visão Geral
```bash
curl -X GET "http://localhost:8000/api/v1/dashboard" \
  -H "Authorization: Bearer $TOKEN"
```

#### 7.2 Minhas Atribuições
```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/my-assignments" \
  -H "Authorization: Bearer $TOKEN"
```

### 8. Testes de Consulta Pública (Sem Auth)

#### 8.1 Por Protocolo
```bash
# Pegue um protocol_number real do beneficiário criado
curl -X GET "http://localhost:8000/api/v1/public/status?protocol=2025-10-A3F2B1"
```

#### 8.2 Por CPF
```bash
curl -X GET "http://localhost:8000/api/v1/public/status?cpf=111.444.777-35"
```

### 9. Testes de Filtros

#### 9.1 Por Status
```bash
curl -X GET "http://localhost:8000/api/v1/beneficiaries/?status=APPROVED" \
  -H "Authorization: Bearer $TOKEN"
```

#### 9.2 Por Município
```bash
curl -X GET "http://localhost:8000/api/v1/beneficiaries/?municipality_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

#### 9.3 Por Data
```bash
curl -X GET "http://localhost:8000/api/v1/beneficiaries/?submitted_from=2025-01-01&submitted_to=2025-12-31" \
  -H "Authorization: Bearer $TOKEN"
```

#### 9.4 Busca
```bash
curl -X GET "http://localhost:8000/api/v1/beneficiaries/?search=João" \
  -H "Authorization: Bearer $TOKEN"
```

### 10. Testes de Listas Base

#### 10.1 Municípios
```bash
curl -X GET "http://localhost:8000/api/v1/municipalities/" \
  -H "Authorization: Bearer $TOKEN"
```

#### 10.2 Critérios de Priorização
```bash
curl -X GET "http://localhost:8000/api/v1/priority-criteria/" \
  -H "Authorization: Bearer $TOKEN"
```

#### 10.3 Tipos de Benefícios
```bash
curl -X GET "http://localhost:8000/api/v1/social-benefits/" \
  -H "Authorization: Bearer $TOKEN"
```

#### 10.4 Tipos de Documentos
```bash
curl -X GET "http://localhost:8000/api/v1/document-types/" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🐛 Troubleshooting

### Erro: "Access denied for user 'root'@'localhost'"
Ajuste a senha do MySQL em `core/settings.py`:
```python
'PASSWORD': 'sua_senha_mysql',
```

### Erro: "No such table: habitacao_beneficiary"
Execute as migrations:
```bash
python3 manage.py migrate
```

### Erro: "Token inválido"
Faça login novamente para obter um novo token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

### Erro: "Documentos obrigatórios faltando" ao submeter
Certifique-se de que todos os documentos marcados como `required=True` foram anexados.

Verifique os tipos obrigatórios:
```bash
curl -X GET "http://localhost:8000/api/v1/document-types/?required=true" \
  -H "Authorization: Bearer $TOKEN"
```

### Erro: "CORS not allowed"
Se estiver testando de um frontend em outra porta, adicione a origem em `core/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    # Adicione suas origens aqui
]
```

---

## ✨ Testes Automatizados (TODO)

Para criar testes automatizados, use:

```bash
# Criar arquivo de testes
touch habitacao/tests/test_api.py
```

Exemplo básico:
```python
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User

class BeneficiaryAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Criar usuário de teste
        # Fazer login
        # ...

    def test_create_beneficiary(self):
        # Testar criação de beneficiário
        pass

    def test_workflow_submit(self):
        # Testar submissão
        pass
```

Executar testes:
```bash
python3 manage.py test habitacao
```

---

## 📊 Validação de Dados de Teste

### CPFs Válidos para Teste
- 111.444.777-35
- 123.456.789-09
- 987.654.321-00

**Nunca use CPFs reais em desenvolvimento!**

Use geradores de CPF válidos online para testes.

### Datas Válidas
- birth_date: YYYY-MM-DD (ex: 1985-05-15)
- submitted_from/to: YYYY-MM-DD

---

## 🎯 Próximos Passos

1. ✅ Todos os endpoints implementados
2. ⚠️ Testar manualmente cada endpoint
3. ⚠️ Criar testes automatizados
4. ⚠️ Testar upload de arquivos grandes
5. ⚠️ Testar paginação com muitos registros
6. ⚠️ Testar permissões por papel
7. ⚠️ Testar escopo de município

---

**Happy Testing! 🚀**
