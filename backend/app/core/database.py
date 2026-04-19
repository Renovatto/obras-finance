"""
Configuração da Engine SQLite Assíncrona – aiosqlite
=====================================================
Diferenças em relação ao PostgreSQL:
  • URL: sqlite+aiosqlite:///./database.db  (arquivo local)
  • pool_size / max_overflow removidos  (SQLite usa StaticPool ou NullPool)
  • WAL (Write-Ahead Logging) ativado via listener síncrono on 'connect'
    para permitir concorrência de leitura enquanto há uma escrita ativa.
  • check_same_thread=False é obrigatório para uso com asyncio/threads.
"""
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# ──────────────────────────────────────────────────────────────
#  Engine assíncrona (aiosqlite)
# ──────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    # StaticPool: reutiliza a mesma conexão em testes / processos únicos.
    # Para produção com múltiplos workers troque por NullPool.
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


# ──────────────────────────────────────────────────────────────
#  WAL – listener executado logo após cada nova conexão DBAPI
#  Habilita concorrência de escrita no SQLite.
# ──────────────────────────────────────────────────────────────
@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_wal_mode(dbapi_connection, connection_record):
    """Ativa WAL e FK enforcement a cada nova conexão."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")   # CRUCIAL: SQLite ignora FKs por padrão!
    cursor.close()


# ──────────────────────────────────────────────────────────────
#  Session factory
# ──────────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ──────────────────────────────────────────────────────────────
#  Base declarativa compartilhada por todos os modelos
# ──────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ──────────────────────────────────────────────────────────────
#  Dependency FastAPI
# ──────────────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    """Injetado via Depends(get_db) nas rotas."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
