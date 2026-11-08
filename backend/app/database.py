"""Camada de infraestrutura e gerenciamento de conexões com o banco de dados.

Suporta MySQL 8.4 (via PyMySQL) para implantação na VM Ubuntu Linux e
SQLite para execução de testes automatizados (Pytest) e demonstração local
sem executar operações destrutivas ou conectar prematuramente à VM.
"""

from __future__ import annotations

import datetime
import decimal
import sqlite3
from contextlib import contextmanager
from typing import Any, Generator

import pymysql
import pymysql.cursors

from backend.app.config import get_settings


def _normalize_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    """Normaliza tipos retornados pelo MySQL/SQLite (timedelta, Decimal, date, time)."""
    if row is None:
        return None
    normalized: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, datetime.timedelta):
            total_seconds = int(value.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            normalized[key] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        elif isinstance(value, datetime.time):
            normalized[key] = value.strftime("%H:%M:%S")
        elif isinstance(value, datetime.datetime):
            normalized[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, datetime.date):
            normalized[key] = value.strftime("%Y-%m-%d")
        elif isinstance(value, decimal.Decimal):
            normalized[key] = float(value)
        else:
            normalized[key] = value
    return normalized


class DatabaseConnection:
    """Abstração uniforme sobre conexões PyMySQL (MySQL 8.4) e SQLite3."""

    def __init__(self, raw_conn: Any, engine: str) -> None:
        self._conn = raw_conn
        self.engine = engine

    def _prepare_query(self, query: str) -> str:
        if self.engine == "sqlite":
            return query.replace("%s", "?")
        return query

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        sql = self._prepare_query(query)
        cur = self._conn.cursor()
        try:
            cur.execute(sql, params)
            rows = cur.fetchall()
            result: list[dict[str, Any]] = []
            for row in rows:
                as_dict = dict(row) if not isinstance(row, dict) else row
                norm = _normalize_row(as_dict)
                if norm is not None:
                    result.append(norm)
            return result
        finally:
            cur.close()

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        sql = self._prepare_query(query)
        cur = self._conn.cursor()
        try:
            cur.execute(sql, params)
            row = cur.fetchone()
            if row is None:
                return None
            as_dict = dict(row) if not isinstance(row, dict) else row
            return _normalize_row(as_dict)
        finally:
            cur.close()

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        """Executa INSERT/UPDATE/DELETE e retorna o lastrowid (ou rowcount se aplicável)."""
        sql = self._prepare_query(query)
        cur = self._conn.cursor()
        try:
            cur.execute(sql, params)
            self._conn.commit()
            return int(cur.lastrowid or cur.rowcount or 0)
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cur.close()


SQLITE_SCHEMA_AND_SEED = """
CREATE TABLE IF NOT EXISTS saloes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cnpj TEXT UNIQUE,
    telefone TEXT NOT NULL,
    email TEXT,
    endereco TEXT,
    ativo INTEGER NOT NULL DEFAULT 1,
    data_cadastro TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    data_atualizacao TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salao_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    cargo TEXT NOT NULL DEFAULT 'Atendente',
    senha_hash TEXT NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1,
    data_cadastro TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    data_atualizacao TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE (salao_id, email),
    UNIQUE (id, salao_id),
    FOREIGN KEY (salao_id) REFERENCES saloes (id)
);

CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salao_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    telefone TEXT NOT NULL,
    email TEXT,
    observacoes TEXT,
    ativo INTEGER NOT NULL DEFAULT 1,
    data_cadastro TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    data_atualizacao TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE (id, salao_id),
    FOREIGN KEY (salao_id) REFERENCES saloes (id)
);

CREATE TABLE IF NOT EXISTS servicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salao_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    duracao_minutos INTEGER NOT NULL CHECK (duracao_minutos > 0 AND duracao_minutos <= 480),
    preco REAL NOT NULL CHECK (preco >= 0),
    ativo INTEGER NOT NULL DEFAULT 1,
    data_cadastro TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    data_atualizacao TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE (id, salao_id),
    UNIQUE (salao_id, nome),
    FOREIGN KEY (salao_id) REFERENCES saloes (id)
);

CREATE TABLE IF NOT EXISTS horarios_funcionamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salao_id INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL CHECK (dia_semana BETWEEN 0 AND 6),
    hora_abertura TEXT NOT NULL,
    hora_fechamento TEXT NOT NULL,
    aberto INTEGER NOT NULL DEFAULT 1,
    UNIQUE (salao_id, dia_semana),
    FOREIGN KEY (salao_id) REFERENCES saloes (id)
);

CREATE TABLE IF NOT EXISTS agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salao_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    servico_id INTEGER NOT NULL,
    usuario_id INTEGER,
    data TEXT NOT NULL,
    hora_inicio TEXT NOT NULL,
    hora_fim TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'AGENDADO' CHECK (status IN ('AGENDADO', 'CONFIRMADO', 'CONCLUIDO', 'CANCELADO')),
    canal_origem TEXT NOT NULL DEFAULT 'TELEFONE',
    observacoes TEXT,
    valor_cobrado REAL NOT NULL CHECK (valor_cobrado >= 0),
    data_cadastro TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    data_atualizacao TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (salao_id) REFERENCES saloes (id),
    FOREIGN KEY (cliente_id, salao_id) REFERENCES clientes (id, salao_id),
    FOREIGN KEY (servico_id, salao_id) REFERENCES servicos (id, salao_id),
    FOREIGN KEY (usuario_id, salao_id) REFERENCES usuarios (id, salao_id)
);
"""

SQLITE_SEED_DATA = """
INSERT INTO saloes (id, nome, cnpj, telefone, email, endereco, ativo) VALUES
(1, 'Studio Belle & Co.', '12.345.678/0001-90', '(11) 98765-4321', 'contato@studiobelle.com.br', 'Av. Paulista, 1500 - Sala 42, São Paulo - SP', 1),
(2, 'Espaço Lumière Estética', '98.765.432/0001-10', '(11) 91234-5678', 'agenda@espacolumiere.com.br', 'Rua Oscar Freire, 820, São Paulo - SP', 1);

INSERT INTO usuarios (id, salao_id, nome, email, cargo, senha_hash, ativo) VALUES
(1, 1, 'Camila Mendes', 'camila@studiobelle.com.br', 'Recepcionista / Gestora', '$2b$12$demo_hash_studiobelle_camila', 1),
(2, 1, 'Juliana Rocha', 'juliana@studiobelle.com.br', 'Cabeleireira Sênior', '$2b$12$demo_hash_studiobelle_juliana', 1),
(3, 2, 'Renata Martins', 'renata@espacolumiere.com.br', 'Administradora', '$2b$12$demo_hash_lumiere_renata', 1);

INSERT INTO horarios_funcionamento (salao_id, dia_semana, hora_abertura, hora_fechamento, aberto) VALUES
(1, 0, '08:00:00', '20:00:00', 1),
(1, 1, '08:00:00', '20:00:00', 1),
(1, 2, '08:00:00', '20:00:00', 1),
(1, 3, '08:00:00', '20:00:00', 1),
(1, 4, '08:00:00', '20:00:00', 1),
(1, 5, '08:00:00', '20:00:00', 1),
(1, 6, '09:00:00', '14:00:00', 0),
(2, 0, '09:00:00', '18:00:00', 0),
(2, 1, '09:00:00', '19:00:00', 1),
(2, 2, '09:00:00', '19:00:00', 1),
(2, 3, '09:00:00', '19:00:00', 1),
(2, 4, '09:00:00', '19:00:00', 1),
(2, 5, '09:00:00', '19:00:00', 1),
(2, 6, '09:00:00', '14:00:00', 0);

INSERT INTO clientes (id, salao_id, nome, telefone, email, observacoes, ativo) VALUES
(1, 1, 'Ana Beatriz Silva', '(11) 99111-2233', 'ana.silva@email.com', 'Prefere atendimento pela manhã. Alergia a esmalte com tolueno.', 1),
(2, 1, 'Mariana Costa Oliveira', '(11) 99222-3344', 'mariana.costa@email.com', 'Cliente recorrente de escova e hidratação.', 1),
(3, 1, 'Fernanda Lima Souza', '(11) 99333-4455', 'fernanda.lima@email.com', 'Solicita lembrete via WhatsApp um dia antes.', 1),
(4, 1, 'Patrícia Gomes', '(11) 99444-5566', 'patricia.gomes@email.com', 'Cliente mudou de cidade temporariamente.', 0),
(5, 2, 'Carolina Vasconcelos', '(11) 99555-6677', 'carol.v@email.com', 'Cliente exclusiva do Espaço Lumière.', 1);

INSERT INTO servicos (id, salao_id, nome, descricao, duracao_minutos, preco, ativo) VALUES
(1, 1, 'Corte Feminino & Finalização', 'Lavagem especial, corte personalizado e finalização com escova.', 60, 120.00, 1),
(2, 1, 'Escova Modelada', 'Lavagem e escova lisa ou modelada.', 45, 75.00, 1),
(3, 1, 'Hidratação Profunda Capilar', 'Tratamento nutritivo intensivo com máscara reconstrutora.', 60, 140.00, 1),
(4, 1, 'Manicure e Pedicure Tradicional', 'Cutilagem, hidratação e esmaltação completa mãos e pés.', 60, 85.00, 1),
(5, 1, 'Coloração Completa', 'Aplicação de coloração profissional, lavagem e finalização.', 90, 210.00, 1),
(6, 1, 'Design de Sobrancelhas', 'Modelagem com pinça e higienização.', 30, 50.00, 1),
(7, 2, 'Limpeza de Pele Facial', 'Extração e máscara calmante.', 60, 160.00, 1);

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
"""


def init_sqlite_db(sqlite_path: str, seed: bool = True) -> None:
    """Inicializa o banco SQLite local/teste com schema e dados iniciais caso vazio."""
    conn = sqlite3.connect(sqlite_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(SQLITE_SCHEMA_AND_SEED)
        if seed:
            cur = conn.execute("SELECT COUNT(*) FROM saloes")
            count = cur.fetchone()[0]
            if count == 0:
                conn.executescript(SQLITE_SEED_DATA)
        conn.commit()
    finally:
        conn.close()


@contextmanager
def get_db_connection() -> Generator[DatabaseConnection, None, None]:
    """Gerenciador de contexto que entrega uma conexão ativa com MySQL 8.4 ou SQLite."""
    settings = get_settings()
    if settings.db_engine == "mysql":
        raw_conn = pymysql.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
        try:
            yield DatabaseConnection(raw_conn, engine="mysql")
        finally:
            raw_conn.close()
    else:
        init_sqlite_db(settings.sqlite_path, seed=True)
        raw_conn = sqlite3.connect(settings.sqlite_path)
        raw_conn.row_factory = sqlite3.Row
        raw_conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield DatabaseConnection(raw_conn, engine="sqlite")
        finally:
            raw_conn.close()


def get_db() -> Generator[DatabaseConnection, None, None]:
    """Dependência FastAPI para injeção da conexão de banco de dados."""
    with get_db_connection() as conn:
        yield conn
