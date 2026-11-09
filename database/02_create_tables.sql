-- ============================================================================
-- Projeto: BeautySchedule (SaaS de Agendamento para Salões de Beleza)
-- Script: 02_create_tables.sql
-- Banco de Dados: MySQL 8.4
-- Descrição: Criação das tabelas relacionais multi-tenant (SaaS) com chaves
--            primárias, chaves estrangeiras compostas para isolamento entre
--            salões, restrições CHECK e índices de performance.
-- ============================================================================

USE beauty_schedule;

-- ----------------------------------------------------------------------------
-- 1. Tabela: saloes (Tenants do SaaS)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS saloes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    cnpj VARCHAR(20) NULL UNIQUE,
    telefone VARCHAR(25) NOT NULL,
    email VARCHAR(120) NULL,
    endereco VARCHAR(255) NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_saloes_ativo (ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------------------------------
-- 2. Tabela: usuarios (Funcionários/Operadores do Salão)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    salao_id INT NOT NULL,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL,
    cargo VARCHAR(60) NOT NULL DEFAULT 'Atendente',
    senha_hash VARCHAR(255) NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uk_usuarios_salao_email UNIQUE (salao_id, email),
    CONSTRAINT uk_usuarios_id_salao UNIQUE (id, salao_id),
    CONSTRAINT fk_usuarios_salao FOREIGN KEY (salao_id)
        REFERENCES saloes (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_usuarios_salao_ativo (salao_id, ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------------------------------
-- 3. Tabela: clientes (Clientes atendidos por cada salão)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    salao_id INT NOT NULL,
    nome VARCHAR(120) NOT NULL,
    telefone VARCHAR(25) NOT NULL,
    email VARCHAR(120) NULL,
    observacoes TEXT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uk_clientes_id_salao UNIQUE (id, salao_id),
    CONSTRAINT fk_clientes_salao FOREIGN KEY (salao_id)
        REFERENCES saloes (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_clientes_salao_ativo (salao_id, ativo),
    INDEX idx_clientes_salao_nome (salao_id, nome),
    INDEX idx_clientes_salao_telefone (salao_id, telefone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------------------------------
-- 4. Tabela: servicos (Catálogo de serviços com duração e preço por salão)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS servicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    salao_id INT NOT NULL,
    nome VARCHAR(120) NOT NULL,
    descricao VARCHAR(255) NULL,
    duracao_minutos INT NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uk_servicos_id_salao UNIQUE (id, salao_id),
    CONSTRAINT uk_servicos_salao_nome UNIQUE (salao_id, nome),
    CONSTRAINT fk_servicos_salao FOREIGN KEY (salao_id)
        REFERENCES saloes (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_servicos_duracao CHECK (duracao_minutos > 0 AND duracao_minutos <= 480),
    CONSTRAINT chk_servicos_preco CHECK (preco >= 0),
    INDEX idx_servicos_salao_ativo (salao_id, ativo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------------------------------
-- 5. Tabela: horarios_funcionamento (Regras de expediente do salão por dia)
--    dia_semana: 0 = Segunda-feira, 1 = Terça-feira, ..., 6 = Domingo
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS horarios_funcionamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    salao_id INT NOT NULL,
    dia_semana TINYINT NOT NULL,
    hora_abertura TIME NOT NULL,
    hora_fechamento TIME NOT NULL,
    aberto TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT uk_horarios_salao_dia UNIQUE (salao_id, dia_semana),
    CONSTRAINT fk_horarios_salao FOREIGN KEY (salao_id)
        REFERENCES saloes (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_horarios_dia_semana CHECK (dia_semana BETWEEN 0 AND 6),
    CONSTRAINT chk_horarios_intervalo CHECK (aberto = 0 OR hora_fechamento > hora_abertura),
    INDEX idx_horarios_salao (salao_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------------------------------------------------------
-- 6. Tabela: agendamentos (Atendimentos agendados no salão)
--    Utiliza chaves estrangeiras compostas (entidade_id, salao_id) para
--    garantir no nível do SGBD que um agendamento só possa referenciar
--    clientes, serviços e usuários pertencentes ao mesmo salão.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    salao_id INT NOT NULL,
    cliente_id INT NOT NULL,
    servico_id INT NOT NULL,
    usuario_id INT NULL,
    data DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'AGENDADO',
    canal_origem VARCHAR(30) NOT NULL DEFAULT 'TELEFONE',
    observacoes TEXT NULL,
    valor_cobrado DECIMAL(10, 2) NOT NULL,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_agendamentos_salao FOREIGN KEY (salao_id)
        REFERENCES saloes (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_agendamentos_cliente_salao FOREIGN KEY (cliente_id, salao_id)
        REFERENCES clientes (id, salao_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_agendamentos_servico_salao FOREIGN KEY (servico_id, salao_id)
        REFERENCES servicos (id, salao_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_agendamentos_usuario_salao FOREIGN KEY (usuario_id, salao_id)
        REFERENCES usuarios (id, salao_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_agendamentos_status CHECK (status IN ('AGENDADO', 'CONFIRMADO', 'CONCLUIDO', 'CANCELADO')),
    CONSTRAINT chk_agendamentos_horario CHECK (hora_fim > hora_inicio),
    CONSTRAINT chk_agendamentos_valor CHECK (valor_cobrado >= 0),
    INDEX idx_agendamentos_salao_data (salao_id, data, hora_inicio),
    INDEX idx_agendamentos_salao_cliente (salao_id, cliente_id),
    INDEX idx_agendamentos_salao_status (salao_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
