-- ============================================================================
-- Projeto: BeautySchedule (SaaS de Agendamento para Salões de Beleza)
-- Script: 03_insert_data.sql
-- Banco de Dados: MySQL 8.4
-- Descrição: Inserção de dados fictícios para demonstração do conceito SaaS
--            (2 salões isolados, funcionários, horários de funcionamento,
--            clientes, serviços e agendamentos em diferentes status).
-- ============================================================================

USE beauty_schedule;

-- ----------------------------------------------------------------------------
-- 1. Salões (Tenants do SaaS)
-- ----------------------------------------------------------------------------
INSERT INTO saloes (id, nome, cnpj, telefone, email, endereco, ativo) VALUES
(1, 'Studio Belle & Co.', '12.345.678/0001-90', '(11) 98765-4321', 'contato@studiobelle.com.br', 'Av. Paulista, 1500 - Sala 42, São Paulo - SP', 1),
(2, 'Espaço Lumière Estética', '98.765.432/0001-10', '(11) 91234-5678', 'agenda@espacolumiere.com.br', 'Rua Oscar Freire, 820, São Paulo - SP', 1);

-- ----------------------------------------------------------------------------
-- 2. Usuários (Funcionários / Operadores internos de cada salão)
-- ----------------------------------------------------------------------------
INSERT INTO usuarios (id, salao_id, nome, email, cargo, senha_hash, ativo) VALUES
(1, 1, 'Camila Mendes', 'camila@studiobelle.com.br', 'Recepcionista / Gestora', '$2b$12$demo_hash_studiobelle_camila', 1),
(2, 1, 'Juliana Rocha', 'juliana@studiobelle.com.br', 'Cabeleireira Sênior', '$2b$12$demo_hash_studiobelle_juliana', 1),
(3, 2, 'Renata Martins', 'renata@espacolumiere.com.br', 'Administradora', '$2b$12$demo_hash_lumiere_renata', 1);

-- ----------------------------------------------------------------------------
-- 3. Horários de Funcionamento (0 = Segunda a 6 = Domingo)
-- ----------------------------------------------------------------------------
-- Salão 1: Segunda a Sábado das 08:00 às 20:00; Domingo fechado
INSERT INTO horarios_funcionamento (salao_id, dia_semana, hora_abertura, hora_fechamento, aberto) VALUES
(1, 0, '08:00:00', '20:00:00', 1),
(1, 1, '08:00:00', '20:00:00', 1),
(1, 2, '08:00:00', '20:00:00', 1),
(1, 3, '08:00:00', '20:00:00', 1),
(1, 4, '08:00:00', '20:00:00', 1),
(1, 5, '08:00:00', '20:00:00', 1),
(1, 6, '09:00:00', '14:00:00', 0),
-- Salão 2: Terça a Sábado das 09:00 às 19:00
(2, 0, '09:00:00', '18:00:00', 0),
(2, 1, '09:00:00', '19:00:00', 1),
(2, 2, '09:00:00', '19:00:00', 1),
(2, 3, '09:00:00', '19:00:00', 1),
(2, 4, '09:00:00', '19:00:00', 1),
(2, 5, '09:00:00', '19:00:00', 1),
(2, 6, '09:00:00', '14:00:00', 0);

-- ----------------------------------------------------------------------------
-- 4. Clientes
-- ----------------------------------------------------------------------------
INSERT INTO clientes (id, salao_id, nome, telefone, email, observacoes, ativo) VALUES
(1, 1, 'Ana Beatriz Silva', '(11) 99111-2233', 'ana.silva@email.com', 'Prefere atendimento pela manhã. Alergia a esmalte com tolueno.', 1),
(2, 1, 'Mariana Costa Oliveira', '(11) 99222-3344', 'mariana.costa@email.com', 'Cliente recorrente de escova e hidratação.', 1),
(3, 1, 'Fernanda Lima Souza', '(11) 99333-4455', 'fernanda.lima@email.com', 'Solicita lembrete via WhatsApp um dia antes.', 1),
(4, 1, 'Patrícia Gomes', '(11) 99444-5566', 'patricia.gomes@email.com', 'Cliente mudou de cidade temporariamente.', 0),
(5, 2, 'Carolina Vasconcelos', '(11) 99555-6677', 'carol.v@email.com', 'Cliente exclusiva do Espaço Lumière.', 1);

-- ----------------------------------------------------------------------------
-- 5. Serviços
-- ----------------------------------------------------------------------------
INSERT INTO servicos (id, salao_id, nome, descricao, duracao_minutos, preco, ativo) VALUES
(1, 1, 'Corte Feminino & Finalização', 'Lavagem especial, corte personalizado e finalização com escova.', 60, 120.00, 1),
(2, 1, 'Escova Modelada', 'Lavagem e escova lisa ou modelada.', 45, 75.00, 1),
(3, 1, 'Hidratação Profunda Capilar', 'Tratamento nutritivo intensivo com máscara reconstrutora.', 60, 140.00, 1),
(4, 1, 'Manicure e Pedicure Tradicional', 'Cutilagem, hidratação e esmaltação completa mãos e pés.', 60, 85.00, 1),
(5, 1, 'Coloração Completa', 'Aplicação de coloração profissional, lavagem e finalização.', 90, 210.00, 1),
(6, 1, 'Design de Sobrancelhas', 'Modelagem com pinça e higienização.', 30, 50.00, 1),
(7, 2, 'Limpeza de Pele Facial', 'Extração e máscara calmante.', 60, 160.00, 1);

-- ----------------------------------------------------------------------------
-- 6. Agendamentos
-- ----------------------------------------------------------------------------
INSERT INTO agendamentos (
    id, salao_id, cliente_id, servico_id, usuario_id,
    data, hora_inicio, hora_fim, status, canal_origem, observacoes, valor_cobrado
) VALUES
(1, 1, 1, 1, 2, '2026-11-09', '09:00:00', '10:00:00', 'CONFIRMADO', 'WHATSAPP', 'Confirmado com a cliente por mensagem.', 120.00),
(2, 1, 2, 2, 2, '2026-11-09', '10:30:00', '11:15:00', 'AGENDADO', 'TELEFONE', 'Agendado por ligação na recepção.', 75.00),
(3, 1, 3, 4, 1, '2026-11-09', '14:00:00', '15:00:00', 'CONCLUIDO', 'PRESENCIAL', 'Atendimento realizado sem atrasos.', 85.00),
(4, 1, 1, 3, 2, '2026-11-10', '11:00:00', '12:00:00', 'AGENDADO', 'WHATSAPP', 'Retorno para hidratação.', 140.00),
(5, 1, 2, 5, 2, '2026-11-10', '15:00:00', '16:30:00', 'CANCELADO', 'TELEFONE', 'Cliente precisou viajar a trabalho.', 210.00),
(6, 2, 5, 7, 3, '2026-11-09', '10:00:00', '11:00:00', 'CONFIRMADO', 'WHATSAPP', 'Agendamento do salão 2.', 160.00);
