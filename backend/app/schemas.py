"""Modelos Pydantic (Schemas de Entrada e Saída) com validações de domínio."""

from __future__ import annotations

import datetime
import re
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

StatusAgendamento = Literal["AGENDADO", "CONFIRMADO", "CONCLUIDO", "CANCELADO"]
CanalOrigem = Literal["TELEFONE", "WHATSAPP", "PRESENCIAL"]

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_DIGITS_REGEX = re.compile(r"\d")


def _validate_phone(value: str) -> str:
    cleaned = value.strip()
    digits = PHONE_DIGITS_REGEX.findall(cleaned)
    if len(digits) < 8 or len(digits) > 15:
        raise ValueError("O telefone deve conter entre 8 e 15 dígitos numéricos.")
    return cleaned


def _validate_email(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    if not EMAIL_REGEX.match(cleaned):
        raise ValueError("Formato de e-mail inválido.")
    return cleaned


def _normalize_time_str(value: str) -> str:
    cleaned = value.strip()
    parts = cleaned.split(":")
    if len(parts) == 2:
        cleaned = f"{int(parts[0]):02d}:{int(parts[1]):02d}:00"
    elif len(parts) == 3:
        cleaned = f"{int(parts[0]):02d}:{int(parts[1]):02d}:{int(parts[2]):02d}"
    else:
        raise ValueError("Horário inválido. Use o formato HH:MM ou HH:MM:SS.")
    try:
        datetime.time.fromisoformat(cleaned)
    except ValueError as exc:
        raise ValueError("Horário inválido. Use valores reais entre 00:00 e 23:59.") from exc
    return cleaned


def _validate_date_str(value: str) -> str:
    cleaned = value.strip()
    try:
        datetime.date.fromisoformat(cleaned)
    except ValueError as exc:
        raise ValueError("Data inválida. Utilize o formato AAAA-MM-DD.") from exc
    return cleaned


# ============================================================================
# Clientes
# ============================================================================

class ClienteCreate(BaseModel):
    """Payload de criação de cliente. Rejeita campos extras como salao_id."""

    model_config = ConfigDict(extra="forbid")

    nome: str = Field(..., min_length=2, max_length=120, description="Nome completo do cliente")
    telefone: str = Field(..., min_length=8, max_length=25, description="Telefone de contato")
    email: str | None = Field(default=None, max_length=120, description="E-mail opcional")
    observacoes: str | None = Field(default=None, max_length=1000)

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("O nome do cliente deve ter pelo menos 2 caracteres.")
        return cleaned

    @field_validator("telefone")
    @classmethod
    def validate_telefone(cls, v: str) -> str:
        return _validate_phone(v)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        return _validate_email(v)


class ClienteUpdate(BaseModel):
    """Payload de edição de cliente."""

    model_config = ConfigDict(extra="forbid")

    nome: str | None = Field(default=None, min_length=2, max_length=120)
    telefone: str | None = Field(default=None, min_length=8, max_length=25)
    email: str | None = Field(default=None, max_length=120)
    observacoes: str | None = Field(default=None, max_length=1000)
    ativo: bool | None = Field(default=None)

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, v: str | None) -> str | None:
        if v is None:
            return None
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("O nome do cliente deve ter pelo menos 2 caracteres.")
        return cleaned

    @field_validator("telefone")
    @classmethod
    def validate_telefone(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return _validate_phone(v)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        return _validate_email(v)


class ClienteResponse(BaseModel):
    """Representação de saída de um cliente."""

    id: int
    salao_id: int
    nome: str
    telefone: str
    email: str | None = None
    observacoes: str | None = None
    ativo: bool
    data_cadastro: str | None = None
    data_atualizacao: str | None = None


# ============================================================================
# Serviços
# ============================================================================

class ServicoCreate(BaseModel):
    """Payload de cadastro de serviço com duração e preço."""

    model_config = ConfigDict(extra="forbid")

    nome: str = Field(..., min_length=2, max_length=120)
    descricao: str | None = Field(default=None, max_length=255)
    duracao_minutos: int = Field(..., gt=0, le=480, description="Duração em minutos (1 a 480)")
    preco: float = Field(..., ge=0.0, description="Preço do serviço em R$")

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("O nome do serviço deve ter pelo menos 2 caracteres.")
        return cleaned


class ServicoUpdate(BaseModel):
    """Payload de atualização de serviço."""

    model_config = ConfigDict(extra="forbid")

    nome: str | None = Field(default=None, min_length=2, max_length=120)
    descricao: str | None = Field(default=None, max_length=255)
    duracao_minutos: int | None = Field(default=None, gt=0, le=480)
    preco: float | None = Field(default=None, ge=0.0)
    ativo: bool | None = Field(default=None)

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, v: str | None) -> str | None:
        if v is None:
            return None
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("O nome do serviço deve ter pelo menos 2 caracteres.")
        return cleaned


class ServicoResponse(BaseModel):
    """Representação de saída de um serviço."""

    id: int
    salao_id: int
    nome: str
    descricao: str | None = None
    duracao_minutos: int
    preco: float
    ativo: bool
    data_cadastro: str | None = None
    data_atualizacao: str | None = None


# ============================================================================
# Agendamentos
# ============================================================================

class AgendamentoCreate(BaseModel):
    """Payload para criar um novo agendamento."""

    model_config = ConfigDict(extra="forbid")

    cliente_id: int = Field(..., gt=0)
    servico_id: int = Field(..., gt=0)
    data: str = Field(..., description="Data no formato YYYY-MM-DD")
    hora_inicio: str = Field(..., description="Horário inicial no formato HH:MM")
    canal_origem: CanalOrigem = Field(default="TELEFONE")
    observacoes: str | None = Field(default=None, max_length=1000)

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: str) -> str:
        return _validate_date_str(v)

    @field_validator("hora_inicio")
    @classmethod
    def validate_hora_inicio(cls, v: str) -> str:
        return _normalize_time_str(v)


class AgendamentoReagendar(BaseModel):
    """Payload específico para reagendamento de data/horário (e opcionalmente serviço)."""

    model_config = ConfigDict(extra="forbid")

    data: str = Field(..., description="Nova data no formato YYYY-MM-DD")
    hora_inicio: str = Field(..., description="Novo horário inicial no formato HH:MM")
    servico_id: int | None = Field(default=None, gt=0)
    observacoes: str | None = Field(default=None, max_length=1000)

    @field_validator("data")
    @classmethod
    def validate_data(cls, v: str) -> str:
        return _validate_date_str(v)

    @field_validator("hora_inicio")
    @classmethod
    def validate_hora_inicio(cls, v: str) -> str:
        return _normalize_time_str(v)


class AgendamentoStatusUpdate(BaseModel):
    """Payload para atualizar status de um agendamento (ex: CONFIRMADO, CONCLUIDO, CANCELADO)."""

    model_config = ConfigDict(extra="forbid")

    status: StatusAgendamento
    observacoes: str | None = Field(default=None, max_length=1000)


class AgendamentoResponse(BaseModel):
    """Representação detalhada de um agendamento."""

    id: int
    salao_id: int
    cliente_id: int
    cliente_nome: str
    cliente_telefone: str
    servico_id: int
    servico_nome: str
    servico_duracao_minutos: int
    usuario_id: int | None = None
    usuario_nome: str | None = None
    data: str
    hora_inicio: str
    hora_fim: str
    status: StatusAgendamento
    canal_origem: str
    observacoes: str | None = None
    valor_cobrado: float
    data_cadastro: str | None = None
    data_atualizacao: str | None = None
