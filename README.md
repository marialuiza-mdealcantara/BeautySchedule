# BeautySchedule — SaaS de Agendamento para Salões de Beleza

## 1. Visão Geral

O **BeautySchedule** é um projeto acadêmico desenvolvido para a disciplina de **SaaS Infrastructure**. A proposta é oferecer um sistema de gerenciamento de agendamentos para salões de beleza estruturado em uma arquitetura de **3 camadas** (Apresentação, Aplicação/Negócio e Persistência/Dados) e modelo **SaaS Multi-Tenant**.

O sistema é utilizado internamente pelos funcionários dos salões (recepcionistas, atendentes e gestores), que cadastram clientes, configuram o catálogo de serviços (com duração e preço) e administram os agendamentos recebidos por **telefone, WhatsApp ou presencialmente**.

> **Nota de Escopo:** Não há agendamento público realizado diretamente pelo cliente final nesta versão; a operação é centralizada na equipe interna do salão.

---

## 2. Problema que Resolve

Salões de beleza frequentemente realizam o controle de clientes e agendamentos de forma descentralizada, utilizando agendas físicas de papel, planilhas ou trocas de mensagens sem consolidação.

Isso dificulta:
- Organização dos horários de atendimento conforme a duração real de cada procedimento;
- Consulta rápida da disponibilidade da agenda por data;
- Gerenciamento do cadastro e do histórico de clientes;
- Reagendamento ou cancelamento de horários com atualização imediata da disponibilidade;
- Prevenção de conflitos (choques de horário) e agendamentos fora do horário de funcionamento;
- Visão consolidada sobre os serviços mais demandados e a movimentação da agenda.

O **BeautySchedule** centraliza todas essas operações em uma única aplicação web integrada a uma API REST em Python (FastAPI) e banco de dados relacional MySQL 8.4.

---

## 3. Objetivos do Projeto

### 3.1. Objetivo Geral
Desenvolver uma aplicação web SaaS para **gerenciamento de clientes, serviços, agenda e relatórios de salões de beleza**, utilizando uma arquitetura de três camadas e infraestrutura preparada para execução em máquina virtual Ubuntu Linux com MySQL 8.4.

### 3.2. Objetivos Específicos
- Modelar e implementar o banco de dados relacional multi-tenant (`salao_id`) no MySQL 8.4.
- Garantir isolamento de dados entre diferentes salões no nível da aplicação e do banco de dados.
- Implementar gerenciamento completo de **Clientes** (cadastro, consulta, edição, inativação/reativação e histórico).
- Implementar gerenciamento completo de **Serviços** (cadastro com duração em minutos e preço, consulta, edição e inativação/reativação).
- Implementar gerenciamento completo de **Agendamentos** (criação, consulta, reagendamento, cancelamento, confirmação e conclusão).
- Impedir automaticamente **conflitos de horários** e validar **horários de funcionamento** do salão por dia da semana.
- Disponibilizar consulta de **Agenda Diária** e **Relatórios Operacionais**.
- Assegurar qualidade por meio de testes automatizados com **Pytest**.

---

## 4. Funcionalidades Implementadas

### Clientes
- Cadastrar clientes (nome, telefone/WhatsApp, e-mail e observações).
- Consultar e filtrar clientes por nome, telefone, e-mail e status (ativos/inativos).
- Editar informações cadastrais.
- Inativar e reativar clientes (exclusão lógica preservando integridade histórica).
- Consultar histórico completo de agendamentos por cliente.

### Serviços
- Cadastrar serviços informando nome, descrição, duração em minutos e preço (`R$`).
- Consultar e buscar serviços por nome, descrição e status.
- Editar serviços (nome, descrição, duração e preço).
- Inativar e reativar serviços do catálogo.

### Agendamentos e Agenda
- Criar agendamentos vinculando cliente ativo e serviço ativo, com cálculo automático do horário de término (`hora_fim = hora_inicio + duracao_minutos`).
- Consultar agendamentos com filtros por data, período, cliente, serviço e status (`AGENDADO`, `CONFIRMADO`, `CONCLUIDO`, `CANCELADO`).
- Reagendar atendimentos validando disponibilidade e expediente na nova data/horário.
- Cancelar agendamentos (liberando imediatamente o horário na agenda).
- Consultar **Agenda por Data** com resumo do dia, status do expediente e grade visual de disponibilidade (blocos de 30 minutos).
- **Impedir conflitos de horários** (interseção total ou parcial no mesmo salão e data).
- **Validar horários de funcionamento** (impedindo agendamentos em dias fechados ou fora do expediente de abertura/fechamento).

### Relatórios e Dashboard
- Visão executiva (Dashboard) e tela dedicada de Relatórios com filtro por período.
- Indicadores de agendamentos ativos, taxa de cancelamento, receita realizada (`CONCLUIDO`) e receita prevista (`AGENDADO + CONFIRMADO + CONCLUIDO`).
- Desempenho por serviço (quantidade de atendimentos, cancelamentos e receita estimada).
- Movimentação diária da agenda e distribuição por status e canal de origem (`WHATSAPP`, `TELEFONE`, `PRESENCIAL`).

---

## 5. Arquitetura e Tecnologias

O sistema segue uma **arquitetura em 3 camadas**:

```text
┌────────────────────────────────────────────────────────┐
│ Camada 1 — Apresentação                                │
│ Frontend Web (HTML5, CSS3, JavaScript ES6+)            │
│ Telas: Dashboard, Agenda, Agendamentos,                │
│        Clientes, Serviços e Relatórios                 │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / JSON (REST)
                            ▼
┌────────────────────────────────────────────────────────┐
│ Camada 2 — Aplicação e Regras de Negócio               │
│ Backend Python + FastAPI                               │
│ Routers -> Services (Regras SaaS) -> Repositories      │
└───────────────────────────┬────────────────────────────┘
                            │ SQL Parametrizado (PyMySQL)
                            ▼
┌────────────────────────────────────────────────────────┐
│ Camada 3 — Persistência / Dados                        │
│ MySQL 8.4 (Produção / VM Ubuntu Linux)                 │
│ SQLite (Suporte local e execução de testes Pytest)     │
└────────────────────────────────────────────────────────┘
```

### Tecnologias Utilizadas

| Componente | Tecnologia |
|---|---|
| **Frontend (Apresentação)** | HTML5, CSS3, JavaScript (Vanilla ES6+) |
| **Backend (Aplicação)** | Python 3, FastAPI, Uvicorn, Pydantic v2 |
| **Banco de Dados (Dados)** | MySQL 8.4 (`PyMySQL`) + suporte SQLite para testes locais |
| **Testes Automatizados** | Pytest + FastAPI `TestClient` (`httpx`) |
| **Sistema Operacional Alvo** | Ubuntu Linux (systemd + Nginx opcional) |
| **Controle de Versão** | Git e GitHub |

---

## 6. Estrutura de Diretórios

```text
BeautySchedule/
├── backend/
│   ├── app/
│   │   ├── repositories/          # Camada de Persistência (SQL isolado por salao_id)
│   │   │   ├── agendamento_repository.py
│   │   │   ├── cliente_repository.py
│   │   │   ├── salao_repository.py
│   │   │   └── servico_repository.py
│   │   ├── routers/               # Controladores REST FastAPI
│   │   │   ├── agenda.py
│   │   │   ├── agendamentos.py
│   │   │   ├── clientes.py
│   │   │   ├── relatorios.py
│   │   │   ├── salao.py
│   │   │   └── servicos.py
│   │   ├── services/              # Camada de Regras de Negócio
│   │   │   ├── agendamento_service.py
│   │   │   ├── cliente_service.py
│   │   │   ├── relatorio_service.py
│   │   │   └── servico_service.py
│   │   ├── config.py              # Carregamento de variáveis de ambiente (.env)
│   │   ├── database.py            # Conexão MySQL 8.4 e SQLite local/teste
│   │   ├── dependencies.py        # Resolução segura de Tenant (salao_id no servidor)
│   │   ├── exceptions.py          # Exceções de domínio
│   │   ├── main.py                # Aplicação FastAPI e montagem do Frontend
│   │   └── schemas.py             # Contratos e validações Pydantic
│   ├── tests/                     # Suíte de testes automatizados (Pytest)
│   │   ├── conftest.py
│   │   ├── test_agendamentos.py
│   │   ├── test_api_health.py
│   │   ├── test_clientes.py
│   │   ├── test_relatorios_e_agenda.py
│   │   └── test_servicos.py
│   └── requirements.txt
├── frontend/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── api.js
│   │   └── app.js
│   └── index.html
├── database/
│   ├── 01_create_database.sql     # Criação do schema MySQL 8.4 (utf8mb4)
│   ├── 02_create_tables.sql       # Tabelas, PKs, FKs compostas, CHECKs e índices
│   └── 03_insert_data.sql         # Dados fictícios de demonstração multi-salão
├── deploy/
│   ├── beautyschedule.service     # Unidade systemd para Ubuntu Linux
│   ├── beautyschedule-service-proposal.xml # Proposta XML para validação docente
│   ├── nginx-beautyschedule.conf  # Configuração de proxy reverso Nginx
│   └── setup_ubuntu.sh            # Script não-destrutivo de preparação na VM Ubuntu
├── docs/
│   ├── api_endpoints.md
│   ├── arquitetura_e_modelo_dados.md
│   └── implantacao_ubuntu_e_xml.md
├── .env.example
├── .gitignore
├── pytest.ini
└── README.md
```

---

## 7. Modelo de Dados e Conceito SaaS Multi-Tenant

O modelo relacional MySQL 8.4 foi projetado para atender **múltiplos salões na mesma aplicação**, contemplando seis entidades principais:

1. `saloes`: Cadastro dos salões de beleza (tenants do SaaS).
2. `usuarios`: Funcionários/operadores vinculados a um `salao_id`.
3. `clientes`: Clientes atendidos por cada salão (`salao_id`).
4. `servicos`: Catálogo de procedimentos com `duracao_minutos` e `preco` (`salao_id`).
5. `horarios_funcionamento`: Regras de abertura e fechamento por dia da semana (`0 = Segunda` a `6 = Domingo`) para cada `salao_id`.
6. `agendamentos`: Registros de atendimento contendo `salao_id`, `cliente_id`, `servico_id`, `usuario_id`, `data`, `hora_inicio`, `hora_fim`, `status`, `canal_origem`, `observacoes` e `valor_cobrado`.

### Garantia de Isolamento SaaS
- **No Banco de Dados**: Chaves estrangeiras compostas (`FOREIGN KEY (cliente_id, salao_id) REFERENCES clientes (id, salao_id)`, etc.) garantem que um agendamento de um salão jamais possa ser associado a clientes, serviços ou usuários de outro salão.
- **No Backend**: O `salao_id` é resolvido exclusivamente no servidor (`get_tenant_context`) e **nunca é aceito do corpo da requisição enviado pelo frontend** (`extra="forbid"` nos schemas Pydantic).

---

## 8. O que NÃO faz parte do MVP

Conforme escopo definido para a disciplina, não fazem parte desta versão:
- Agendamento público aberto ao cliente final;
- Processamento de pagamentos online ou emissão de nota fiscal;
- Integração automatizada com API externa do WhatsApp ou Google Calendar;
- Aplicativo mobile nativo ou módulos de inteligência artificial.

---

## 9. Pré-requisitos e Configuração do Ambiente

### Pré-requisitos
- **Python** 3.10 ou superior
- **MySQL** 8.4 (para o ambiente de produção/VM Ubuntu)
- **Git**

### Configuração das Variáveis de Ambiente
1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```
2. Para rodar **localmente de imediato** (sem precisar de um servidor MySQL local ativo), o `.env.example` já traz por padrão `DB_ENGINE=sqlite` e `CORS_ORIGINS=http://127.0.0.1:8000,http://localhost:8000`. O sistema criará e populará automaticamente um banco local de demonstração.
3. Na **VM Ubuntu Linux com MySQL 8.4**, edite o `.env` ajustando `DB_ENGINE=mysql`, `CORS_ORIGINS` (se aplicável) e as credenciais reais:
   ```env
   APP_ENV=production
   CORS_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
   DB_ENGINE=mysql
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_NAME=beauty_schedule
   DB_USER=beauty_user
   DB_PASSWORD=SUA_SENHA_SEGURA
   DEFAULT_SALAO_ID=1
   DEFAULT_USUARIO_ID=1
   ```

---

## 10. Como Executar Localmente

### No Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

### No Linux (Ubuntu)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse no navegador:
- **Interface Web Completa**: `http://127.0.0.1:8000/`
- **Documentação Interativa da API (Swagger)**: `http://127.0.0.1:8000/docs`

---

## 11. Como Executar os Testes Automatizados

A suíte de testes utiliza **Pytest** com banco temporário isolado por teste, validando clientes, serviços, agendamentos, bloqueio de conflitos de horários, validação de expediente, reagendamento, cancelamento, relatórios e isolamento SaaS:

```bash
pytest -v
```

---

## 12. Como Configurar o MySQL 8.4 e Implantar no Ubuntu Linux

### 12.1. Configuração Controlada do MySQL 8.4 na VM Ubuntu
Após inspecionar os bancos existentes na VM (`sudo mysql -u root -p -e "SHOW DATABASES;"`), execute os scripts SQL na ordem:

```bash
mysql -u root -p < database/01_create_database.sql
mysql -u root -p < database/02_create_tables.sql
mysql -u root -p < database/03_insert_data.sql
```

### 12.2. Implantação do Serviço na VM Ubuntu
1. Execute o script de preparação não-destrutivo (ele sincroniza os arquivos para `/opt/beautyschedule`, cria `.venv` e `.env` nesse diretório e gera a unidade `systemd` já ajustada para o usuário real da VM):
   ```bash
   bash deploy/setup_ubuntu.sh
   ```
2. Configure o arquivo `/opt/beautyschedule/.env` com `DB_ENGINE=mysql` e as credenciais do banco.
3. Registre e inicie o serviço `systemd` usando o arquivo renderizado para o usuário da VM:
   ```bash
   sudo cp /opt/beautyschedule/deploy/beautyschedule.service.rendered /etc/systemd/system/beautyschedule.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now beautyschedule
   ```
4. *(Opcional)* Configure o proxy reverso Nginx utilizando `deploy/nginx-beautyschedule.conf`.

### 12.3. Documentação Complementar e Pendência do Arquivo XML
- Consulte [`docs/arquitetura_e_modelo_dados.md`](docs/arquitetura_e_modelo_dados.md) para detalhes da arquitetura e diagrama ER.
- Consulte [`docs/api_endpoints.md`](docs/api_endpoints.md) para a listagem de todos os endpoints REST.
- Consulte [`docs/implantacao_ubuntu_e_xml.md`](docs/implantacao_ubuntu_e_xml.md) para instruções detalhadas de implantação Linux e análise sobre a diferença entre a unidade `systemd` (`deploy/beautyschedule.service`) e a proposta de arquivo XML acadêmico (`deploy/beautyschedule-service-proposal.xml`).
