# Sistema de Habitação - MCMV Entidades

Sistema para gerenciamento do Programa Minha Casa Minha Vida - Entidades (MCMV).

## Estrutura do Projeto

```
habitacao-back/
├── core/                 # Configurações do projeto Django
├── habitacao/            # App principal
│   ├── models.py        # Models do banco de dados
│   ├── choices.py       # Enums e choices
│   ├── validators.py    # Validadores customizados
│   ├── admin.py         # Configuração do Django Admin
│   └── migrations/      # Migrations do banco de dados
├── media/               # Arquivos de upload (documentos)
└── manage.py
```

## Models Implementadas

### Models Base
- **Municipality**: Municípios brasileiros (código IBGE, nome, UF)
- **PriorityCriteria**: Critérios de priorização para beneficiários
- **SocialBenefitType**: Tipos de benefícios sociais
- **DocumentType**: Tipos de documentos para upload

### Usuários
- **UserProfile**: Perfil estendido do usuário Django com CPF, papel (role) e município de atuação

### Beneficiários
- **Beneficiary**: Model principal com todos os dados do beneficiário
  - Dados pessoais (nome, CPF, RG, data de nascimento, etc.)
  - Contatos (telefones, email)
  - Endereço completo
  - Dados do cônjuge/companheiro
  - Informações econômicas e CadÚnico
  - Composição familiar
  - Situação habitacional
  - Status da inscrição
  - Auditoria (submissão, revisão)

### Relacionamentos
- **BeneficiaryPriority**: Critérios de priorização aplicados ao beneficiário
- **BeneficiarySocialBenefit**: Benefícios sociais recebidos
- **BeneficiaryDocument**: Documentos anexados
- **ApplicationAssignment**: Atribuição de inscrições para análise
- **ApplicationActionHistory**: Histórico de ações e mudanças de status
- **SearchAudit**: Auditoria de buscas no sistema

## Configuração

### 1. Pré-requisitos

- Python 3.12+
- MySQL 8.0+
- pip

### 2. Instalação de Dependências

```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install django mysqlclient
```

### 3. Configuração do Banco de Dados

Edite o arquivo `core/settings.py` e ajuste as credenciais do MySQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'habitacao_db',
        'USER': 'seu_usuario',      # Ajuste aqui
        'PASSWORD': 'sua_senha',    # Ajuste aqui
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```

### 4. Criar o Banco de Dados

```bash
mysql -u root -p
```

```sql
CREATE DATABASE habitacao_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Executar Migrations

```bash
# Aplicar migrations do Django (auth, admin, etc)
python3 manage.py migrate

# A migration do app habitacao já foi criada em:
# habitacao/migrations/0001_initial.py
```

### 6. Criar Superusuário

```bash
python3 manage.py createsuperuser
```

### 7. Executar o Servidor

```bash
python3 manage.py runserver
```

Acesse o admin em: http://localhost:8000/admin

## Funcionalidades Principais

### Validações Implementadas

- **CPF**: Validação completa com dígitos verificadores
- **NIS**: Validação de NIS/PIS/PASEP
- **CEP**: Validação de formato (8 dígitos)
- **Telefone**: Validação de telefone brasileiro (10 ou 11 dígitos)
- **Renda**: Validação de valores positivos

### Geração Automática de Protocolo

Ao submeter uma inscrição (status = SUBMITTED), o sistema gera automaticamente um número de protocolo no formato:

```
AAAA-MM-XXXXXX
```

Exemplo: `2025-10-A3F2B1`

### Status da Inscrição

- **DRAFT**: Rascunho
- **SUBMITTED**: Submetida
- **UNDER_REVIEW**: Em Análise
- **CORRECTION_REQUESTED**: Correção Solicitada
- **APPROVED**: Aprovada
- **REJECTED**: Rejeitada

### Papéis de Usuário

- **ADMIN**: Administrador
- **COORDINATOR**: Coordenador
- **ANALYST**: Analista
- **CLERK**: Atendente

## Upload de Documentos

Os documentos são organizados automaticamente no seguinte padrão:

```
media/beneficiarios/{cpf}/{tipo_documento}/{arquivo}
```

Exemplo:
```
media/beneficiarios/12345678900/RG_CPF/documento.pdf
```

## Histórico e Auditoria

Todas as ações importantes são registradas em `ApplicationActionHistory`:
- Submissão
- Início de análise
- Solicitação de correção
- Aprovação/Rejeição
- Upload de documentos
- Validação de documentos
- Edições

## Próximos Passos

1. Configurar autenticação e permissões
2. Criar APIs REST com Django REST Framework
3. Implementar frontend
4. Adicionar testes automatizados
5. Configurar deploy em produção
6. Implementar notificações por email
7. Adicionar relatórios e dashboards

## Estrutura das Tabelas MySQL

Após executar as migrations, as seguintes tabelas serão criadas:

- `municipalities` - Municípios
- `priority_criteria` - Critérios de priorização
- `social_benefit_types` - Tipos de benefícios sociais
- `document_types` - Tipos de documentos
- `users` - Perfis de usuários
- `beneficiaries` - Beneficiários (tabela principal)
- `beneficiary_priority` - Prioridades dos beneficiários
- `beneficiary_social_benefits` - Benefícios sociais dos beneficiários
- `beneficiary_documents` - Documentos anexados
- `application_assignments` - Atribuições de análise
- `application_actions` - Histórico de ações
- `search_audit` - Auditoria de buscas

## Suporte

Para dúvidas ou problemas, consulte a documentação do Django em: https://docs.djangoproject.com/
