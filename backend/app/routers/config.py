"""
Router: /api/v1/config
========================
Gerencia as configurações de sistema armazenadas na tabela `configuracao_sistema`.
Unifica em um único lugar: caminho do banco, porta e flag de onboarding.

Endpoints:
  GET   /api/v1/config/   → retorna configurações atuais
  POST  /api/v1/config/   → salva configurações (exige reinício para aplicar alterações de banco/porta)
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.models import ConfiguracaoSistema

router = APIRouter()


class SystemConfigPayload(BaseModel):
    database_path: Optional[str] = None
    port: int = 8000
    welcome_message: bool = False


async def _get_or_create_config(db: AsyncSession) -> ConfiguracaoSistema:
    """Retorna o registro singleton de configuração, criando-o se não existir."""
    result = await db.execute(select(ConfiguracaoSistema).where(ConfiguracaoSistema.id == 1))
    config = result.scalar_one_or_none()
    if config is None:
        config = ConfiguracaoSistema(id=1)
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return config


@router.get(
    "/",
    response_model=SystemConfigPayload,
    summary="Buscar configurações de sistema",
)
async def get_config(db: AsyncSession = Depends(get_db)):
    """Retorna as configurações atuais do sistema."""
    config = await _get_or_create_config(db)
    return SystemConfigPayload(
        database_path=config.database_path,
        port=config.port,
        welcome_message=config.welcome_message,
    )


@router.post(
    "/",
    summary="Salvar configurações de sistema",
)
async def update_config(payload: SystemConfigPayload, db: AsyncSession = Depends(get_db)):
    """
    Persiste as configurações de sistema no banco de dados.
    Mudanças de caminho do banco e porta requerem reinicialização do aplicativo.
    """
    config = await _get_or_create_config(db)
    config.database_path = payload.database_path
    config.port = payload.port
    config.welcome_message = payload.welcome_message
    await db.commit()
    return {
        "message": "Configuração salva com sucesso. Reinicie o aplicativo para aplicar mudanças de banco de dados ou porta."
    }
