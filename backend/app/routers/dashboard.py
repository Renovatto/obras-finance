"""
Router: /api/dashboard  –  Endpoints para visualização de dados
=============================================================
Fornece KPIs consolidados e dados para gráficos mensais e por categoria.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import (
    DashboardKPIs, DashboardMonthlyPL, DashboardCategoryExpenses
)
from app.services.dashboard_service import DashboardService
import uuid
from typing import Optional
from fastapi import Query

router = APIRouter()


@router.get("/kpis", response_model=DashboardKPIs)
async def obter_kpis(
    periodo: Optional[str] = Query(None),
    fk_categoria: Optional[uuid.UUID] = Query(None),
    fk_responsavel: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Retorna os indicadores principais com filtros."""
    return await DashboardService.get_kpis(db, periodo, fk_categoria, fk_responsavel)


@router.get("/grafico-mensal", response_model=list[DashboardMonthlyPL])
async def obter_grafico_mensal(
    periodo: Optional[str] = Query(None),
    fk_categoria: Optional[uuid.UUID] = Query(None),
    fk_responsavel: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Retorna dados de Receita e Despesa filtrados."""
    return await DashboardService.get_monthly_pl(db, periodo, fk_categoria, fk_responsavel)


@router.get("/grafico-categorias", response_model=list[DashboardCategoryExpenses])
async def obter_grafico_categorias(
    periodo: Optional[str] = Query(None),
    fk_categoria: Optional[uuid.UUID] = Query(None),
    fk_responsavel: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Retorna a distribuição de despesas filtrada."""
    return await DashboardService.get_category_expenses(db, periodo, fk_categoria, fk_responsavel)


@router.get("/periodos", response_model=list[str])
async def get_available_periods(db: AsyncSession = Depends(get_db)):
    """Lista todos os períodos (YYYY-MM) que possuem lançamentos."""
    return await DashboardService.get_available_periods(db)
