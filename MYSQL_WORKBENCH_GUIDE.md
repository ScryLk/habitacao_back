# 🔌 Guia de Conexão MySQL Workbench - Habitação MCMV

> **Status**: ✅ Configurações validadas e testadas

## 📋 Informações de Conexão

### Dados da Conexão (baseado no seu `.env`)

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| **Host** | `localhost` ou `127.0.0.1` | Endereço do servidor |
| **Port** | `3307` | Porta mapeada do Docker |
| **Database** | `habitacao_db` | Nome do banco de dados |
| **Username** | `habitacao_user` | Usuário do banco |
| **Password** | `dFZKZiTvuMosfx-Zn7-7rxnHF-WhxFkAkiwdcaoD4d0` | Senha do usuário |

### Usuário Root (Opcional)

| Parâmetro | Valor |
|-----------|-------|
| **Username** | `root` |
| **Password** | `dFZKZiTvuMosfx-Zn7-7rxnHF-WhxFkAkiwdcaoD4d0` |

⚠️ **Importante**: A porta é **3307** (não a padrão 3306) porque o Docker está mapeando a porta 3306 do container para a porta 3307 do host.

---

## 🚀 Passo a Passo - MySQL Workbench

### **Passo 1: Verificar se o Docker está Rodando**

Antes de conectar, certifique-se de que os containers estão ativos:

```bash
docker compose ps
```

**Saída esperada**:
```
NAME               STATUS          PORTS
habitacao_mysql    Up 2 hours      0.0.0.0:3307->3306/tcp
habitacao_web      Up 2 hours      0.0.0.0:8000->8000/tcp
habitacao_nginx    Up 2 hours      0.0.0.0:80->80/tcp
habitacao_redis    Up 2 hours      0.0.0.0:6379->6379/tcp
```

✅ Verifique se `habitacao_mysql` está **UP** e mapeado na porta **3307**.

---

### **Passo 2: Abrir MySQL Workbench**

1. Abra o **MySQL Workbench**
2. Na tela inicial, clique em **[+]** ao lado de "MySQL Connections" para criar uma nova conexão

---

### **Passo 3: Configurar a Nova Conexão**

Preencha os campos conforme abaixo:

#### **Aba "Parameters"**

| Campo | Valor | Obrigatório |
|-------|-------|-------------|
| **Connection Name** | `Habitacao MCMV - Local` | ✅ |
| **Connection Method** | `Standard (TCP/IP)` | ✅ |
| **Hostname** | `127.0.0.1` ou `localhost` | ✅ |
| **Port** | `3307` | ✅ |
| **Username** | `habitacao_user` | ✅ |
| **Password** | Clique em "Store in Vault..." | ✅ |
| **Default Schema** | `habitacao_db` | ⭐ Recomendado |

**Captura de Tela (exemplo)**:
```
╔═══════════════════════════════════════════════════════════╗
║  Connection Name:  Habitacao MCMV - Local                ║
║  Connection Method: Standard (TCP/IP)                     ║
║  Hostname:         127.0.0.1                              ║
║  Port:             3307                                   ║
║  Username:         habitacao_user                         ║
║  Password:         [Store in Vault...]                    ║
║  Default Schema:   habitacao_db                           ║
╚═══════════════════════════════════════════════════════════╝
```

#### **Inserir a Senha**

1. Clique no botão **"Store in Vault..."** ao lado do campo Password
2. Digite a senha: `dFZKZiTvuMosfx-Zn7-7rxnHF-WhxFkAkiwdcaoD4d0`
3. Clique em **OK**

---

### **Passo 4: Testar a Conexão**

1. Clique no botão **"Test Connection"** no canto inferior da janela
2. Aguarde a validação

**Resultado esperado**:
```
✅ Successfully made the MySQL connection

Information related to this connection:
  Host: 127.0.0.1
  Port: 3307
  User: habitacao_user
  SSL: not enabled
```

Se aparecer essa mensagem, está tudo certo! ✅

---

### **Passo 5: Salvar e Conectar**

1. Clique em **OK** para salvar a conexão
2. Na tela inicial do Workbench, clique duas vezes na nova conexão **"Habitacao MCMV - Local"**
3. Aguarde a conexão ser estabelecida

---

## 📊 Explorando o Banco de Dados

Após conectar, você verá o banco **habitacao_db** na barra lateral esquerda.

### **Principais Tabelas**

```
habitacao_db
├── beneficiaries              ← Beneficiários (principal)
├── municipalities             ← Municípios brasileiros
├── priority_criteria          ← Critérios de priorização
├── social_benefit_types       ← Tipos de benefícios sociais
├── document_types             ← Tipos de documentos
├── users                      ← Usuários do sistema
├── beneficiary_priority       ← Critérios aplicados aos beneficiários
├── beneficiary_social_benefits ← Benefícios dos beneficiários
├── beneficiary_documents      ← Documentos anexados
├── application_assignments    ← Atribuições de inscrições
├── application_actions        ← Histórico de ações
└── search_audit               ← Auditoria de buscas
```

### **Consultas Úteis**

#### Ver todos os beneficiários

```sql
SELECT
    id,
    full_name,
    cpf,
    status,
    has_cadunico,
    nis_number,
    created_at
FROM beneficiaries
ORDER BY created_at DESC;
```

#### Ver beneficiários por status

```sql
SELECT
    status,
    COUNT(*) as total
FROM beneficiaries
GROUP BY status;
```

#### Ver beneficiários com/sem NIS

```sql
-- Com NIS
SELECT
    id,
    full_name,
    nis_number
FROM beneficiaries
WHERE nis_number IS NOT NULL;

-- Sem NIS (NULL)
SELECT
    id,
    full_name,
    nis_number
FROM beneficiaries
WHERE nis_number IS NULL;
```

#### Ver beneficiários submetidos

```sql
SELECT
    id,
    protocol_number,
    full_name,
    cpf,
    status,
    submitted_at
FROM beneficiaries
WHERE status = 'SUBMITTED'
ORDER BY submitted_at DESC;
```

#### Ver estrutura da tabela

```sql
DESCRIBE beneficiaries;
```

ou

```sql
SHOW CREATE TABLE beneficiaries;
```

---

## 🛠️ Solução de Problemas

### ❌ Erro: "Can't connect to MySQL server on '127.0.0.1' (10061)"

**Causa**: O container do MySQL não está rodando.

**Solução**:
```bash
# Verificar status
docker compose ps

# Iniciar containers
docker compose up -d

# Verificar logs do MySQL
docker compose logs db
```

---

### ❌ Erro: "Access denied for user 'habitacao_user'@'...' (using password: YES)"

**Causa**: Senha incorreta.

**Solução**:
1. Verifique a senha no arquivo `.env` (linha 21)
2. Copie exatamente como está
3. Reconfigure a conexão no Workbench com a senha correta

---

### ❌ Erro: "Unknown database 'habitacao_db'"

**Causa**: Banco de dados não foi criado.

**Solução**:
```bash
# Recriar banco de dados
docker compose down
docker compose up -d

# Executar migrations
docker compose exec web python manage.py migrate
```

---

### ❌ Erro: Connection timeout

**Causa**: Porta incorreta ou firewall bloqueando.

**Solução**:
1. Confirme que a porta é **3307** (não 3306)
2. Teste conexão via terminal:
```bash
mysql -h 127.0.0.1 -P 3307 -u habitacao_user -p
# Senha: dFZKZiTvuMosfx-Zn7-7rxnHF-WhxFkAkiwdcaoD4d0
```

---

## 🔐 Conexão com Usuário Root

Se precisar de privilégios administrativos, use o usuário `root`:

| Campo | Valor |
|-------|-------|
| **Username** | `root` |
| **Password** | `dFZKZiTvuMosfx-Zn7-7rxnHF-WhxFkAkiwdcaoD4d0` |

⚠️ **Atenção**: Use root apenas quando necessário (ex: criar usuários, modificar estruturas).

---

## 📱 Alternativas ao MySQL Workbench

Se preferir outras ferramentas:

### **1. DBeaver (Gratuito e Open Source)**

**Download**: https://dbeaver.io/download/

**Configuração**:
- Database: MySQL
- Host: `127.0.0.1`
- Port: `3307`
- Database: `habitacao_db`
- Username: `habitacao_user`
- Password: `dFZKZiTvuMosfx-Zn7-7rxnHF-WhxFkAkiwdcaoD4d0`

### **2. TablePlus (Pago - Mac/Windows)**

**Download**: https://tableplus.com/

**Configuração**: Similar ao Workbench

### **3. phpMyAdmin via Docker (Web-based)**

Adicione ao `docker-compose.yml`:

```yaml
phpmyadmin:
  image: phpmyadmin/phpmyadmin
  container_name: habitacao_phpmyadmin
  environment:
    PMA_HOST: db
    PMA_PORT: 3306
    PMA_USER: habitacao_user
    PMA_PASSWORD: dFZKZiTvuMosfx-Zn7-7rxnHF-WhxFkAkiwdcaoD4d0
  ports:
    - "8081:80"
  networks:
    - habitacao_network
```

Depois acesse: http://localhost:8081

---

## 🎯 Resumo Rápido

### Dados para Copiar/Colar:

```
Host: 127.0.0.1
Port: 3307
Database: habitacao_db
Username: habitacao_user
Password: dFZKZiTvuMosfx-Zn7-7rxnHF-WhxFkAkiwdcaoD4d0
```

### Comando de Teste via Terminal:

```bash
mysql -h 127.0.0.1 -P 3307 -u habitacao_user -pdFZKZiTvuMosfx-Zn7-7rxnHF-WhxFkAkiwdcaoD4d0 habitacao_db
```

---

## 📚 Referências

- **Docker Compose**: [docker-compose.yml](./docker-compose.yml)
- **Variáveis de Ambiente**: [.env](./.env)
- **Script de Consulta**: [scripts/list_beneficiaries.py](./scripts/list_beneficiaries.py)
- **MySQL Workbench**: https://dev.mysql.com/downloads/workbench/

---

**Última atualização**: 2025-01-26
**Versão**: 1.0.0
**Status**: ✅ Testado e funcionando
