"""
Service: LancamentoService
==========================
Lógica avançada para Lançamentos Financeiros (Receitas e Despesas).
Suporta paginação server-side, filtros complexos e estatísticas em tempo real.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy import select, func, desc, asc, delete, cast, Numeric
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import LancamentoFinanceiro, TipoLancamento, Categoria, FormaPagamento, Responsavel
from app.schemas import (
    LancamentoCreate, LancamentoUpdate, LancamentoPagedResponse, 
    LancamentoRead, LancamentoStats
)


class LancamentoService:

    @staticmethod
    def _get_relations():
        """Relacionamentos a serem carregados via JOIN."""
        return [
            selectinload(LancamentoFinanceiro.categoria),
            selectinload(LancamentoFinanceiro.forma_pagamento),
            selectinload(LancamentoFinanceiro.responsavel),
            selectinload(LancamentoFinanceiro.obra),
        ]

    @staticmethod
    async def listar_paginado(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "data",
        sort_order: str = "desc",
        descricao: Optional[str] = None,
        periodo: Optional[str] = None,  # YYYY-MM
        fk_obra: Optional[uuid.UUID] = None,
        fk_categoria: Optional[uuid.UUID] = None,
        fk_responsavel: Optional[uuid.UUID] = None,
    ) -> LancamentoPagedResponse:
        """
        Listagem com paginação e filtros inteligentes.
        Retorna também metadados e totais (Receita/Despesa) do contexto filtrado.
        """
        offset = (page - 1) * page_size
        
        # 1. Base da Query com Filtros
        query_base = select(LancamentoFinanceiro)
        
        if descricao:
            query_base = query_base.where(LancamentoFinanceiro.descricao.ilike(f"%{descricao}%"))
        
        if fk_obra:
            query_base = query_base.where(LancamentoFinanceiro.fk_obra == fk_obra)
            
        if fk_categoria:
            query_base = query_base.where(LancamentoFinanceiro.fk_categoria == fk_categoria)

        if fk_responsavel:
            query_base = query_base.where(LancamentoFinanceiro.fk_responsavel == fk_responsavel)
            
        if periodo:
            try:
                # periodo no formato YYYY-MM
                ano, mes = map(int, periodo.split("-"))
                # Filtro usando strftime do SQLite
                query_base = query_base.where(
                    func.strftime("%Y", LancamentoFinanceiro.data) == str(ano),
                    func.strftime("%m", LancamentoFinanceiro.data) == f"{mes:02d}"
                )
            except ValueError:
                pass # Ignora formato inválido de período

        # 2. Query para TOTAIS (Contextuais ao filtro)
        # Extraímos a subquery para garantir que os totais respeitem os mesmos filtros
        subq = query_base.subquery()
        
        receitas_total = await db.scalar(
            select(func.sum(cast(subq.c.valor, Numeric)))
            .where(subq.c.tipo == TipoLancamento.receita.value)
        ) or Decimal("0.00")
        
        despesas_total = await db.scalar(
            select(func.sum(cast(subq.c.valor, Numeric)))
            .where(subq.c.tipo == TipoLancamento.despesa.value)
        ) or Decimal("0.00")

        # 3. Query para COUNT TOTAL
        total_records = await db.scalar(
            select(func.count()).select_from(subq)
        ) or 0

        # 4. Executar Query Principal com Paginação e Ordenação
        # Resolve ordenação dinâmica
        order_col = getattr(LancamentoFinanceiro, sort_by, LancamentoFinanceiro.data)
        order_func = desc if sort_order == "desc" else asc
        
        query_main = (
            query_base.options(*LancamentoService._get_relations())
            .order_by(order_func(order_col))
            .offset(offset)
            .limit(page_size)
        )
        
        result = await db.execute(query_main)
        items = result.scalars().all()

        return LancamentoPagedResponse(
            items=[LancamentoRead.model_validate(i) for i in items],
            total=total_records,
            page=page,
            page_size=page_size,
            pages=(total_records + page_size - 1) // page_size if total_records > 0 else 1,
            stats=LancamentoStats(
                total_receitas=Decimal(str(receitas_total)),
                total_despesas=Decimal(str(despesas_total))
            )
        )

    @staticmethod
    async def criar(db: AsyncSession, payload: LancamentoCreate) -> LancamentoFinanceiro:
        """Cria e carrega relacionamentos."""
        lancamento = LancamentoFinanceiro(**payload.model_dump())
        db.add(lancamento)
        await db.flush()
        
        # Recarrega com os objetos relacionados (Categoria, etc) para a resposta Read
        query = (
            select(LancamentoFinanceiro)
            .options(*LancamentoService._get_relations())
            .where(LancamentoFinanceiro.id == lancamento.id)
        )
        result = await db.execute(query)
        return result.scalar_one()

    @staticmethod
    async def obter(db: AsyncSession, lancamento_id: uuid.UUID) -> LancamentoFinanceiro:
        query = (
            select(LancamentoFinanceiro)
            .options(*LancamentoService._get_relations())
            .where(LancamentoFinanceiro.id == lancamento_id)
        )
        result = await db.execute(query)
        lanc = result.scalar_one_or_none()
        if not lanc:
            raise HTTPException(status_code=404, detail="Lançamento não encontrado")
        return lanc

    @staticmethod
    async def atualizar(db: AsyncSession, lancamento_id: uuid.UUID, payload: LancamentoUpdate) -> LancamentoFinanceiro:
        lanc = await LancamentoService.obter(db, lancamento_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(lanc, field, value)
        await db.flush()
        await db.refresh(lanc)
        # Re-obter para garantir relacionamentos carregados
        return await LancamentoService.obter(db, lancamento_id)

    @staticmethod
    async def remover_batch(db: AsyncSession, ids: list[uuid.UUID]) -> int:
        """Remove vários registros de uma vez."""
        stmt = delete(LancamentoFinanceiro).where(LancamentoFinanceiro.id.in_(ids))
        result = await db.execute(stmt)
        return result.rowcount
