"""
Router: /api/v1/onboarding
===========================
Gerencia o status do tour de boas-vindas (welcome_message).

Endpoints:
  GET   /api/v1/onboarding/status    → retorna { welcome_message: bool }
  POST  /api/v1/onboarding/concluir  → marca o tour como visto (welcome_message = True)
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import ConfiguracaoSistema

router = APIRouter()


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


class OnboardingStatus(BaseModel):
    welcome_message: bool


@router.get(
    "/status",
    response_model=OnboardingStatus,
    summary="Verifica se o tour de boas-vindas já foi exibido",
)
async def get_onboarding_status(db: AsyncSession = Depends(get_db)):
    """
    Retorna { welcome_message: false } na primeira abertura do sistema.
    O frontend usa isso para decidir se deve exibir o tour interativo.
    """
    config = await _get_or_create_config(db)
    return OnboardingStatus(welcome_message=config.welcome_message)


@router.post(
    "/concluir",
    summary="Marca o tour de boas-vindas como concluído",
)
async def concluir_onboarding(db: AsyncSession = Depends(get_db)):
    """
    Chamado quando o usuário conclui ou pula o tour.
    Define welcome_message = True para que o tour não seja exibido novamente.
    """
    config = await _get_or_create_config(db)
    config.welcome_message = True
    await db.commit()
    return {"ok": True, "message": "Tour de boas-vindas marcado como concluído."}
