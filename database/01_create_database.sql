-- ============================================================================
-- Projeto: BeautySchedule (SaaS de Agendamento para Salões de Beleza)
-- Script: 01_create_database.sql
-- Banco de Dados: MySQL 8.4
-- Descrição: Criação não-destrutiva do banco de dados com suporte completo
--            a UTF-8 (utf8mb4) e collation padrão do MySQL 8.4.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS beauty_schedule
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE beauty_schedule;

-- Opcional: exemplo comentado de criação de usuário dedicado de aplicação
-- (Execute manualmente na VM Ubuntu após definir uma senha segura)
-- CREATE USER IF NOT EXISTS 'beauty_user'@'localhost' IDENTIFIED BY ' DefinaUmaSenhaForte ';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON beauty_schedule.* TO 'beauty_user'@'localhost';
-- FLUSH PRIVILEGES;
