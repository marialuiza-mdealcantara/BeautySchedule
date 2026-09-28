# BeautySchedule

## 1. Visão Geral

O **BeautySchedule** é um projeto acadêmico desenvolvido para a
disciplina de **SaaS Infrastructure**. A proposta é desenvolver, de
forma incremental, um sistema de agendamento para salões de beleza
utilizando uma arquitetura de **3 camadas**.

O projeto será tratado com uma abordagem próxima de um projeto real,
porém com **escopo acadêmico e foco no aprendizado das tecnologias e
conceitos da disciplina**.

------------------------------------------------------------------------

## 2. Problema

Salões de beleza podem realizar o controle de clientes e agendamentos de
forma descentralizada, utilizando agendas físicas, mensagens ou
diferentes ferramentas.

Isso pode dificultar:

-   organização dos horários;
-   consulta dos agendamentos;
-   gerenciamento dos clientes;
-   alteração ou cancelamento de horários;
-   prevenção de conflitos de agenda.

O BeautySchedule busca centralizar essas informações em uma única
aplicação.

------------------------------------------------------------------------

## 3. Objetivo Geral

Desenvolver uma aplicação para **gerenciamento de clientes e
agendamentos de um salão de beleza**, utilizando uma arquitetura de três
camadas e infraestrutura baseada em máquina virtual Linux.

------------------------------------------------------------------------

## 4. Objetivos Específicos

-   Modelar e implementar o banco de dados da aplicação.
-   Criar o cadastro e gerenciamento de clientes.
-   Criar o cadastro e gerenciamento de agendamentos.
-   Permitir consulta, alteração e cancelamento de agendamentos.
-   Estabelecer o relacionamento entre clientes e agendamentos.
-   Desenvolver um backend em Python para comunicação com o banco de
    dados.
-   Utilizar MySQL como sistema de gerenciamento de banco de dados.
-   Executar a infraestrutura inicial em uma VM Linux.
-   Aplicar o conceito de arquitetura de 3 camadas.
-   Evoluir o sistema de forma incremental ao longo da disciplina.

------------------------------------------------------------------------

## 5. Escopo Inicial --- MVP

A primeira versão do sistema terá como foco:

### Clientes

-   Cadastro de cliente.
-   Consulta de cliente.
-   Alteração de dados.
-   Remoção de cliente.

### Agendamentos

-   Cadastro de agendamento.
-   Consulta de agendamentos.
-   Alteração de agendamento.
-   Cancelamento de agendamento.
-   Definição de data, horário, serviço e status.

### Banco de Dados

Inicialmente serão utilizadas pelo menos duas tabelas:

-   `clientes`
-   `agendamentos`

Relacionamento:

``` text
clientes (1) ─────────── (N) agendamentos
```

Um cliente pode possuir vários agendamentos.

------------------------------------------------------------------------

## 6. Regras de Negócio Iniciais

1.  Todo agendamento deve estar associado a um cliente existente.
2.  Cliente deve possuir, no mínimo, nome e telefone.
3.  Todo agendamento deve possuir data, horário, serviço e status.
4.  Um agendamento poderá possuir os status:
    -   `AGENDADO`
    -   `CONFIRMADO`
    -   `CONCLUÍDO`
    -   `CANCELADO`
5.  O sistema deverá evoluir para impedir conflitos de horário.

------------------------------------------------------------------------

## 7. Arquitetura

O sistema seguirá uma arquitetura de três camadas:

``` text
┌─────────────────────────────┐
│ Camada 1 — Apresentação     │
│ Frontend                    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Camada 2 — Aplicação        │
│ Backend / API               │
│ Python                      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Camada 3 — Dados            │
│ MySQL                       │
└─────────────────────────────┘
               │
               ▼
          VM Linux
```

### Tecnologias definidas

  Componente       Tecnologia
  ---------------- ------------
  Infraestrutura   VM Linux
  Banco de dados   MySQL
  Backend          Python
  Arquitetura      3 camadas

O framework do backend poderá ser definido durante a implementação,
conforme os requisitos da disciplina.

------------------------------------------------------------------------

## 8. Banco de Dados Inicial

### `clientes`

  Campo             Tipo       Descrição
  ----------------- ---------- --------------------------
  `id`              INT        Identificador do cliente
  `nome`            VARCHAR    Nome do cliente
  `telefone`        VARCHAR    Telefone
  `email`           VARCHAR    E-mail
  `data_cadastro`   DATETIME   Data do cadastro

### `agendamentos`

  Campo          Tipo      Descrição
  -------------- --------- ------------------------------
  `id`           INT       Identificador do agendamento
  `cliente_id`   INT       Cliente relacionado
  `servico`      VARCHAR   Serviço agendado
  `data`         DATE      Data do atendimento
  `horario`      TIME      Horário
  `status`       VARCHAR   Status do agendamento

------------------------------------------------------------------------

## 9. O que NÃO faz parte do MVP

Para manter o projeto dentro de um escopo adequado à disciplina,
inicialmente não serão implementados:

-   pagamentos;
-   integração com WhatsApp;
-   integração com Google Calendar;
-   emissão de nota fiscal;
-   sistema financeiro;
-   aplicativo mobile;
-   inteligência artificial;
-   integrações externas.

Essas funcionalidades podem ser consideradas como possíveis evoluções
futuras.

------------------------------------------------------------------------

## 10. Objetivo da Etapa Atual

A etapa atual tem como objetivo:

1.  Definir a aplicação.
2.  Levantar o escopo inicial.
3.  Definir os objetivos do projeto.
4.  Modelar o banco de dados.
5.  Criar pelo menos duas tabelas.
6.  Criar o script SQL.
7.  Operacionalizar o banco de dados na VM Linux.
8.  Inserir dados de teste para demonstrar o funcionamento inicial.

------------------------------------------------------------------------

## 11. Evolução Esperada

O projeto será desenvolvido de forma incremental:

``` text
Definição do escopo
        ↓
Modelagem do banco
        ↓
MySQL na VM Linux
        ↓
Backend Python
        ↓
API
        ↓
Frontend
        ↓
Integração das 3 camadas
        ↓
Evolução do SaaS
```

O objetivo não é construir todas as funcionalidades de uma vez, mas
evoluir o sistema conforme os conteúdos da disciplina forem
apresentados.
