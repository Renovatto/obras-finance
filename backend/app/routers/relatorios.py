from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas import RelatorioObraBudget
from app.services.relatorios_service import RelatoriosService

router = APIRouter()

@router.get("/obras-budget", response_model=List[RelatorioObraBudget])
async def obter_obras_budget(db: AsyncSession = Depends(get_db)):
    """Retorna o portfolio de Obras e o saldo vs orçamento."""
    return await RelatoriosService.get_obras_budget(db)
