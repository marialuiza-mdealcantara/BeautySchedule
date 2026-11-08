# Referência da API REST — BeautySchedule

Quando a aplicação estiver em execução, a documentação interativa OpenAPI (Swagger UI) também pode ser acessada diretamente em:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 1. Infraestrutura e Contexto do Salão

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/health` | Verifica status da API, versão e motor de banco configurado (`mysql` ou `sqlite`). |
| `GET` | `/api/salao` | Retorna os dados do salão (tenant) ativo na sessão, operador e horários de funcionamento. |
| `GET` | `/api/salao/horarios` | Lista os horários de funcionamento de segunda a domingo (`dia_semana` 0 a 6). |

---

## 2. Clientes (`/api/clientes`)

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/clientes` | Lista clientes do salão. Suporta `?apenas_ativos=true\|false` e `?busca=termo`. |
| `GET` | `/api/clientes/{id}` | Obtém detalhes de um cliente do salão. |
| `GET` | `/api/clientes/{id}/agendamentos` | Consulta o histórico completo de agendamentos de um cliente. |
| `POST` | `/api/clientes` | Cadastra um novo cliente (`nome`, `telefone`, `email`, `observacoes`). |
| `PUT` | `/api/clientes/{id}` | Edita as informações cadastrais de um cliente. |
| `PATCH` | `/api/clientes/{id}/inativar` | Inativa logicamente um cliente preservando seu histórico. |
| `PATCH` | `/api/clientes/{id}/reativar` | Reativa um cliente anteriormente inativado. |

---

## 3. Serviços (`/api/servicos`)

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/servicos` | Lista os serviços do catálogo do salão (`?apenas_ativos=true\|false`, `?busca=termo`). |
| `GET` | `/api/servicos/{id}` | Consulta detalhes de um serviço específico. |
| `POST` | `/api/servicos` | Cadastra novo serviço informando `nome`, `descricao`, `duracao_minutos` e `preco`. |
| `PUT` | `/api/servicos/{id}` | Atualiza nome, descrição, duração em minutos ou preço do serviço. |
| `PATCH` | `/api/servicos/{id}/inativar` | Inativa um serviço para que não receba novos agendamentos. |
| `PATCH` | `/api/servicos/{id}/reativar` | Reativa um serviço no catálogo do salão. |

---

## 4. Agendamentos e Agenda (`/api/agendamentos` e `/api/agenda`)

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/agendamentos` | Lista agendamentos com filtros (`data`, `data_inicio`, `data_fim`, `cliente_id`, `servico_id`, `status`). |
| `GET` | `/api/agendamentos/{id}` | Obtém detalhes de um agendamento específico. |
| `POST` | `/api/agendamentos` | Cria agendamento validando cliente ativo, serviço ativo, expediente do salão e conflitos de horário. |
| `PUT` | `/api/agendamentos/{id}/reagendar` | Reagenda para nova data/horário (e opcionalmente serviço), validando expediente e conflitos. |
| `PATCH` | `/api/agendamentos/{id}/cancelar` | Cancela o agendamento (`status = CANCELADO`), liberando o horário na agenda. |
| `PATCH` | `/api/agendamentos/{id}/status` | Atualiza o status (`CONFIRMADO`, `CONCLUIDO`, `CANCELADO`). |
| `GET` | `/api/agenda?data=YYYY-MM-DD` | Retorna a agenda consolidada da data: expediente, resumo do dia, atendimentos e grade de 30 em 30 min. |

---

## 5. Relatórios (`/api/relatorios`)

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/relatorios/resumo` | Retorna indicadores gerais, contagem por status e canal, ranking de serviços e movimentação por data. |
