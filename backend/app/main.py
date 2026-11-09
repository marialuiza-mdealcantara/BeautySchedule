"""Ponto de entrada principal da API FastAPI — BeautySchedule."""

from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import pymysql

from backend.app.config import get_settings
from backend.app.exceptions import DomainError
from backend.app.routers import agenda, agendamentos, clientes, relatorios, salao, servicos

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

_initial_settings = get_settings()
_cors_origins = list(_initial_settings.cors_origins)
_allow_credentials = "*" not in _cors_origins

app = FastAPI(
    title="BeautySchedule API",
    description=(
        "SaaS de gerenciamento de agendamentos, clientes e serviços para salões de beleza "
        "em arquitetura de 3 camadas."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(DomainError)
async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
    """Converte exceções de domínio em respostas JSON padronizadas."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "erro": True,
            "mensagem": exc.message,
            "detail": exc.message,
        },
    )


@app.exception_handler(sqlite3.Error)
@app.exception_handler(pymysql.MySQLError)
async def database_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Garante retorno JSON padronizado caso ocorra falha de comunicação ou persistência."""
    msg = "Erro de comunicação com o banco de dados."
    return JSONResponse(
        status_code=500,
        content={
            "erro": True,
            "mensagem": msg,
            "detail": f"{msg} ({exc.__class__.__name__})",
        },
    )


@app.get("/api/health", tags=["Infraestrutura"])
def health_check() -> dict[str, Any]:
    """Verifica a disponibilidade da API e informa o motor de banco configurado."""
    settings = get_settings()
    return {
        "status": "ok",
        "aplicacao": "BeautySchedule",
        "versao": "1.0.0",
        "ambiente": settings.app_env,
        "db_engine": settings.db_engine,
        "cors_origins": list(settings.cors_origins),
    }


# Registro dos roteadores da camada de aplicação
app.include_router(salao.router)
app.include_router(clientes.router)
app.include_router(servicos.router)
app.include_router(agendamentos.router)
app.include_router(agenda.router)
app.include_router(relatorios.router)

# Servir arquivos estáticos do Frontend (Camada de Apresentação)
if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

    @app.get("/", include_in_schema=False)
    def serve_frontend() -> FileResponse:
        return FileResponse(str(FRONTEND_DIR / "index.html"))
