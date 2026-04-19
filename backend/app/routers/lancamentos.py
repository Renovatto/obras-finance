"""
Router: Lançamentos Financeiros  –  Gestão de Fluxo de Caixa
===========================================================
Implementa DataTable server-side com paginação, filtros e ordenação,
além de operações CRUD e exclusão em lote.
"""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import TipoLancamento, StatusLancamento
from app.schemas import (
    LancamentoCreate, LancamentoRead, LancamentoUpdate, 
    LancamentoPagedResponse, BatchDeletePayload
)
from app.services.lancamento_service import LancamentoService

router = APIRouter()


@router.get("/", response_model=LancamentoPagedResponse)
async def listar_lancamentos(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort_by: str = Query("data", pattern="^(data|valor|descricao|tipo|status)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    descricao: Optional[str] = Query(None, description="Filtro de busca por descrição"),
    periodo: Optional[str] = Query(None, description="Filtro de período (YYYY-MM)"),
    fk_obra: Optional[uuid.UUID] = Query(None, description="Filtrar lançamentos de uma obra específica"),
    fk_categoria: Optional[uuid.UUID] = Query(None, description="Filtrar por categoria específica"),
    fk_responsavel: Optional[uuid.UUID] = Query(None, description="Filtrar por responsável específico"),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista lançamentos com paginação server-side e filtros combináveis.
    Retorna também estatísticas contextuais (Totais de Receitas/Desperas do filtro).
    """
    return await LancamentoService.listar_paginado(
        db, page, page_size, sort_by, sort_order, descricao, periodo, fk_obra, fk_categoria, fk_responsavel
    )


@router.post("/", response_model=LancamentoRead, status_code=status.HTTP_201_CREATED)
async def criar_lancamento(
    payload: LancamentoCreate,
    db: AsyncSession = Depends(get_db),
):
    """Registra um novo lançamento e retorna os dados completos com relacionamentos."""
    return await LancamentoService.criar(db, payload)


@router.get("/{lancamento_id}", response_model=LancamentoRead)
async def obter_lancamento(
    lancamento_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Busca detalhes de um lançamento específico."""
    return await LancamentoService.obter(db, lancamento_id)


@router.put("/{lancamento_id}", response_model=LancamentoRead)
async def atualizar_lancamento(
    lancamento_id: uuid.UUID,
    payload: LancamentoUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Atualiza dados de um lançamento existente."""
    return await LancamentoService.atualizar(db, lancamento_id, payload)


@router.delete("/batch", status_code=status.HTTP_200_OK)
async def deletar_batch(
    payload: BatchDeletePayload,
    db: AsyncSession = Depends(get_db),
):
    """Exclui múltiplos lançamentos de uma só vez."""
    removidos = await LancamentoService.remover_batch(db, payload.ids)
    return {"message": f"{removidos} lançamentos removidos com sucesso."}


@router.delete("/{lancamento_id}", status_code=status.HTTP_200_OK)
async def deletar_lancamento(
    lancamento_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Exclui um único lançamento pelo ID."""
    removidos = await LancamentoService.remover_batch(db, [lancamento_id])
    if removidos == 0:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    return {"message": "Lançamento removido com sucesso."}
