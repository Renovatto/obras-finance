"""
env.py – Alembic assíncrono (SQLite / aiosqlite)
================================================
Usa a engine já configurada no database.py (com WAL listener)
em vez de criar uma engine separada a partir do alembic.ini,
garantindo que as mesmas configurações de PRAGMA se apliquem.
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy.engine import Connection

from alembic import context

# Importa a engine e Base já configuradas (WAL listener incluído)
from app.core.database import engine, Base
import app.models  # noqa: F401  ← registra todos os modelos nos metadados

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Modo offline: gera SQL sem conectar ao banco."""
    from app.core.config import settings
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,   # ← OBRIGATÓRIO para ALTER TABLE no SQLite
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,   # ← OBRIGATÓRIO para ALTER TABLE no SQLite
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Modo online: reutiliza a engine assíncrona do projeto."""
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
