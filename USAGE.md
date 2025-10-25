# Guia de Uso - Sistema de Habitação MCMV

## 1. Configuração Inicial

### 1.1 Criar o banco de dados MySQL

```bash
mysql -u root -p
```

```sql
CREATE DATABASE habitacao_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON habitacao_db.* TO 'seu_usuario'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 1.2 Configurar credenciais no settings.py

Edite `core/settings.py` e ajuste as configurações do banco:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'habitacao_db',
        'USER': 'seu_usuario',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```

### 1.3 Aplicar migrations

```bash
# Migrations do Django (auth, sessions, admin, etc)
python3 manage.py migrate

# Verificar se tudo foi criado
python3 manage.py showmigrations
```

### 1.4 Criar superusuário

```bash
python3 manage.py createsuperuser
```

Informe:
- Username
- Email
- Password

### 1.5 Carregar dados iniciais

```bash
python3 manage.py load_initial_data
```

Isso irá carregar:
- 5 tipos de documentos
- 3 tipos de benefícios sociais
- 12 critérios de priorização

## 2. Executar o servidor

```bash
python3 manage.py runserver
```

Acesse:
- Admin: http://localhost:8000/admin
- Login com o superusuário criado

## 3. Usando o Django Admin

### 3.1 Cadastrar Municípios

1. Acesse "Municípios" no admin
2. Clique em "Adicionar município"
3. Preencha:
   - Código IBGE (7 dígitos)
   - Nome
   - UF

### 3.2 Criar Perfil de Usuário

1. Primeiro, crie um usuário Django em "Authentication and Authorization > Users"
2. Depois, acesse "Perfis de Usuários" no app Habitação
3. Clique em "Adicionar perfil de usuário"
4. Selecione o usuário Django criado
5. Preencha:
   - CPF (será validado)
   - Papel (Admin, Coordenador, Analista, Atendente)
   - Município de atuação (opcional)
   - Marque como ativo

### 3.3 Cadastrar Beneficiário

1. Acesse "Beneficiários" no admin
2. Clique em "Adicionar beneficiário"
3. Preencha os dados principais:

**Dados Pessoais:**
- Nome completo
- CPF (formato: 000.000.000-00)
- RG
- Data de nascimento
- Estado civil

**Contatos:**
- Telefone principal
- Telefone secundário (opcional)
- Email

**Endereço:**
- Logradouro, número, complemento
- Bairro
- Município (selecione um cadastrado)
- CEP (formato: 00000-000)
- UF

**Econômico:**
- Ocupação principal
- Renda familiar bruta
- Possui CadÚnico?
- Número NIS (se possuir CadÚnico)

**Composição Familiar:**
- Tamanho da família
- Gênero do chefe da família
- Possui idosos? Quantos?
- Possui crianças? Quantas?
- Possui PcD/TEA? Quantos?

**Situação Habitacional:**
- Não possui casa própria
- Casa própria precária
- Coabitação
- Moradia improvisada
- Paga aluguel? Valor?

**Status:**
- Inicie como "Rascunho" (DRAFT)
- Quando pronto, mude para "Submetida" (SUBMITTED)
  - O protocolo será gerado automaticamente!

### 3.4 Adicionar Critérios de Priorização

No formulário do beneficiário, role até a seção "Prioridades":
- Adicione critérios como:
  - Família chefiada por mulher
  - Família com pessoa idosa
  - PcD ou TEA
  - Vítima de violência doméstica
  - etc.

### 3.5 Adicionar Benefícios Sociais

Na seção "Benefícios Sociais":
- Bolsa Família
- BPC
- Outros (especifique)

### 3.6 Upload de Documentos

Na seção "Documentos":
- Selecione o tipo de documento
- Faça upload do arquivo
- O sistema organizará automaticamente em:
  `media/beneficiarios/{cpf}/{tipo_documento}/{arquivo}`

## 4. Fluxo de Trabalho

### 4.1 Criação de Inscrição

1. Atendente cadastra beneficiário com status "Rascunho"
2. Preenche todos os dados obrigatórios
3. Anexa documentos necessários
4. Muda status para "Submetida"
   - **Protocolo é gerado automaticamente** (ex: 2025-10-A3F2B1)
   - Data de submissão é registrada

### 4.2 Atribuição para Análise

1. Coordenador acessa "Atribuições de Inscrições"
2. Cria nova atribuição:
   - Seleciona o beneficiário
   - Seleciona o analista
   - Marca como ativa

### 4.3 Análise

1. Analista acessa sua lista de atribuições
2. Muda status para "Em Análise"
3. Revisa documentos (marca como validado)
4. Pode solicitar correção (status "Correção Solicitada")
5. Aprova ou rejeita

### 4.4 Histórico de Ações

Todas as mudanças são registradas em "Histórico de Ações":
- Quem fez a ação
- Data/hora
- Status anterior e novo
- Mensagem/observação

## 5. Consultas e Filtros

### 5.1 Filtros Disponíveis no Admin

**Beneficiários:**
- Por status
- Por município
- Possui CadÚnico
- Possui idosos/crianças/PcD
- Paga aluguel
- Não possui casa própria
- UF

**Documentos:**
- Validado/não validado
- Tipo de documento
- Data de upload

**Atribuições:**
- Ativas/inativas
- Data de atribuição

**Histórico:**
- Por ação
- Por status
- Data

### 5.2 Busca

Você pode buscar beneficiários por:
- Nome completo
- CPF
- Número de protocolo
- Email

## 6. Exemplos de Dados

### CPFs válidos para teste:
- 111.444.777-35
- 123.456.789-09
- 987.654.321-00

**Importante:** Use geradores de CPF válidos para testes!

### NIS válido para teste:
- 12345678901

## 7. Backup

### 7.1 Backup do banco de dados

```bash
mysqldump -u seu_usuario -p habitacao_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 7.2 Restaurar backup

```bash
mysql -u seu_usuario -p habitacao_db < backup_20251024_120000.sql
```

### 7.3 Backup de arquivos (media)

```bash
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
```

## 8. Comandos Úteis

```bash
# Ver todas as migrations
python3 manage.py showmigrations

# Criar nova migration após mudanças em models
python3 manage.py makemigrations

# Aplicar migrations
python3 manage.py migrate

# Carregar fixtures
python3 manage.py loaddata initial_data.json

# Criar dados de exemplo
python3 manage.py load_initial_data

# Shell interativo do Django
python3 manage.py shell

# Verificar erros
python3 manage.py check
```

## 9. Exemplos via Django Shell

```python
python3 manage.py shell
```

```python
from habitacao.models import *
from django.contrib.auth.models import User

# Criar município
mun = Municipality.objects.create(
    ibge_code='3550308',
    name='São Paulo',
    uf='SP'
)

# Criar beneficiário
ben = Beneficiary.objects.create(
    full_name='João da Silva',
    cpf='111.444.777-35',
    municipality=mun,
    status='DRAFT'
)

# Adicionar critério de priorização
criteria = PriorityCriteria.objects.get(code='WOMAN_HEAD')
BeneficiaryPriority.objects.create(
    beneficiary=ben,
    criteria=criteria
)

# Submeter inscrição (gera protocolo automaticamente)
ben.status = 'SUBMITTED'
ben.save()
print(f"Protocolo gerado: {ben.protocol_number}")

# Listar beneficiários por status
Beneficiary.objects.filter(status='SUBMITTED')

# Contar por município
Beneficiary.objects.filter(municipality__uf='SP').count()
```

## 10. Próximos Passos

- [ ] Implementar API REST
- [ ] Criar painel de relatórios
- [ ] Adicionar notificações por email
- [ ] Implementar autenticação JWT
- [ ] Criar frontend React/Vue
- [ ] Adicionar exportação para Excel/PDF
- [ ] Implementar assinatura digital
- [ ] Integração com sistemas externos (CadÚnico, etc)
