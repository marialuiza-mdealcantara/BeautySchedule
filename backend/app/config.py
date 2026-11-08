"""Configurações centralizadas da aplicação BeautySchedule via variáveis de ambiente."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


@dataclass(slots=True)
class Settings:
    """Estrutura imutável de configuração carregada do ambiente."""

    app_env: str = os.getenv("APP_ENV", "development")
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    app_debug: bool = os.getenv("APP_DEBUG", "true").lower() in ("1", "true", "yes")

    # Configuração do Banco de Dados
    # Suporta 'mysql' (padrão para produção/VM Ubuntu com MySQL 8.4)
    # e 'sqlite' (para execução local imediata/testes automatizados sem tocar na VM)
    db_engine: str = os.getenv("DB_ENGINE", "sqlite").lower()
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_name: str = os.getenv("DB_NAME", "beauty_schedule")
    db_user: str = os.getenv("DB_USER", "beauty_user")
    db_password: str = os.getenv("DB_PASSWORD", "")
    sqlite_path: str = os.getenv(
        "SQLITE_PATH", str(BASE_DIR / "backend" / "beauty_schedule_local.db")
    )

    # Isolamento SaaS: resolvido exclusivamente no servidor
    default_salao_id: int = int(os.getenv("DEFAULT_SALAO_ID", "1"))
    default_usuario_id: int = int(os.getenv("DEFAULT_USUARIO_ID", "1"))


def get_settings() -> Settings:
    """Retorna uma instância atualizada das configurações."""
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        app_host=os.getenv("APP_HOST", "0.0.0.0"),
        app_port=int(os.getenv("APP_PORT", "8000")),
        app_debug=os.getenv("APP_DEBUG", "true").lower() in ("1", "true", "yes"),
        db_engine=os.getenv("DB_ENGINE", "sqlite").lower(),
        db_host=os.getenv("DB_HOST", "127.0.0.1"),
        db_port=int(os.getenv("DB_PORT", "3306")),
        db_name=os.getenv("DB_NAME", "beauty_schedule"),
        db_user=os.getenv("DB_USER", "beauty_user"),
        db_password=os.getenv("DB_PASSWORD", ""),
        sqlite_path=os.getenv(
            "SQLITE_PATH", str(BASE_DIR / "backend" / "beauty_schedule_local.db")
        ),
        default_salao_id=int(os.getenv("DEFAULT_SALAO_ID", "1")),
        default_usuario_id=int(os.getenv("DEFAULT_USUARIO_ID", "1")),
    )
