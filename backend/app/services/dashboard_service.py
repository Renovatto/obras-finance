"""
Service: DashboardService
=========================
Inteligência analítica agregando dados financeiros para o Dashboard.
Otimizado para SQLite usando funções de agregação e strftime.
"""
from __future__ import annotations

from decimal import Decimal
from datetime import datetime
from typing import Sequence

from sqlalchemy import select, func, cast, Numeric, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LancamentoFinanceiro, TipoLancamento, Categoria
from app.schemas import (
    DashboardKPIs, DashboardMonthlyPL, DashboardCategoryExpenses
)


class DashboardService:

    @staticmethod
    def _apply_filters(
        query,
        periodo: Optional[str] = None,
        fk_categoria: Optional[uuid.UUID] = None,
        fk_responsavel: Optional[uuid.UUID] = None
    ):
        """Aplica filtros comuns de dashboard."""
        if fk_categoria:
            query = query.where(LancamentoFinanceiro.fk_categoria == fk_categoria)
        if fk_responsavel:
            query = query.where(LancamentoFinanceiro.fk_responsavel == fk_responsavel)
        
        if periodo and periodo != "todos":
            try:
                ano, mes = map(int, periodo.split("-"))
                query = query.where(
                    func.strftime("%Y", LancamentoFinanceiro.data) == str(ano),
                    func.strftime("%m", LancamentoFinanceiro.data) == f"{mes:02d}"
                )
            except ValueError:
                pass
        return query

    @staticmethod
    async def get_kpis(
        db: AsyncSession,
        periodo: Optional[str] = None,
        fk_categoria: Optional[uuid.UUID] = None,
        fk_responsavel: Optional[uuid.UUID] = None
    ) -> DashboardKPIs:
        """Calcula totais gerais e saldo com filtros."""
        
        q_receitas = select(func.sum(cast(LancamentoFinanceiro.valor, Numeric))).where(
            LancamentoFinanceiro.tipo == TipoLancamento.receita.value
        )
        q_despesas = select(func.sum(cast(LancamentoFinanceiro.valor, Numeric))).where(
            LancamentoFinanceiro.tipo == TipoLancamento.despesa.value
        )

        # Aplicar filtros
        q_receitas = DashboardService._apply_filters(q_receitas, periodo, fk_categoria, fk_responsavel)
        q_despesas = DashboardService._apply_filters(q_despesas, periodo, fk_categoria, fk_responsavel)

        receitas = await db.scalar(q_receitas) or Decimal("0.00")
        despesas = await db.scalar(q_despesas) or Decimal("0.00")
        
        return DashboardKPIs(
            total_receitas=Decimal(str(receitas)),
            total_despesas=Decimal(str(despesas)),
            saldo=Decimal(str(receitas)) - Decimal(str(despesas))
        )

    @staticmethod
    async def get_monthly_pl(
        db: AsyncSession,
        periodo: Optional[str] = None,
        fk_categoria: Optional[uuid.UUID] = None,
        fk_responsavel: Optional[uuid.UUID] = None
    ) -> list[DashboardMonthlyPL]:
        """
        Gera o gráfico de P&L mensal. 
        Se periodo='todos', mostra histórico. Caso contrário, foca no ano do período ou ano atual.
        """
        if periodo and periodo != "todos":
            ano_alvo = periodo.split("-")[0]
        else:
            ano_alvo = str(datetime.now().year)

        # Base para as queries
        q_receitas = (
            select(
                func.strftime("%Y-%m", LancamentoFinanceiro.data).label("mes"),
                func.sum(cast(LancamentoFinanceiro.valor, Numeric)).label("total")
            )
            .where(LancamentoFinanceiro.tipo == TipoLancamento.receita.value)
        )
        q_despesas = (
            select(
                func.strftime("%Y-%m", LancamentoFinanceiro.data).label("mes"),
                func.sum(cast(LancamentoFinanceiro.valor, Numeric)).label("total")
            )
            .where(LancamentoFinanceiro.tipo == TipoLancamento.despesa.value)
        )

        # Filtro de ano corporativo (se não for periodo='todos')
        if periodo != "todos":
            q_receitas = q_receitas.where(func.strftime("%Y", LancamentoFinanceiro.data) == ano_alvo)
            q_despesas = q_despesas.where(func.strftime("%Y", LancamentoFinanceiro.data) == ano_alvo)

        # Filtros adicionais (categoria/responsavel)
        q_receitas = DashboardService._apply_filters(q_receitas, None, fk_categoria, fk_responsavel)
        q_despesas = DashboardService._apply_filters(q_despesas, None, fk_categoria, fk_responsavel)

        q_receitas = q_receitas.group_by("mes")
        q_despesas = q_despesas.group_by("mes")

        res_receitas = await db.execute(q_receitas)
        res_despesas = await db.execute(q_despesas)
        
        mapa_receitas = {r.mes: r.total for r in res_receitas}
        mapa_despesas = {d.mes: d.total for d in res_despesas}
        
        # Mesclar todos os meses encontrados
        todos_meses = sorted(list(set(mapa_receitas.keys()) | set(mapa_despesas.keys())))
        
        pl_data = []
        for mes in todos_meses:
            r = mapa_receitas.get(mes, Decimal("0.00"))
            d = mapa_despesas.get(mes, Decimal("0.00"))
            pl_data.append(DashboardMonthlyPL(
                mes=mes,
                receita=Decimal(str(r)),
                despesa=Decimal(str(d)),
                lucro=Decimal(str(r)) - Decimal(str(d))
            ))
            
        return pl_data

    @staticmethod
    async def get_category_expenses(
        db: AsyncSession,
        periodo: Optional[str] = None,
        fk_categoria: Optional[uuid.UUID] = None,
        fk_responsavel: Optional[uuid.UUID] = None
    ) -> list[DashboardCategoryExpenses]:
        """Gera o gráfico de despesas por categoria com filtros."""
        query = (
            select(
                Categoria.nome.label("categoria"),
                func.sum(cast(LancamentoFinanceiro.valor, Numeric)).label("total")
            )
            .join(LancamentoFinanceiro.categoria)
            .where(LancamentoFinanceiro.tipo == TipoLancamento.despesa.value)
        )

        query = DashboardService._apply_filters(query, periodo, fk_categoria, fk_responsavel)
        
        query = query.group_by(Categoria.nome).order_by(desc("total"))
        
        result = await db.execute(query)
        return [
            DashboardCategoryExpenses(categoria=r.categoria, total=Decimal(str(r.total)))
            for r in result
        ]

    @staticmethod
    async def get_available_periods(db: AsyncSession) -> list[str]:
        """Retorna lista de meses/anos únicos disponíveis (formato YYYY-MM)."""
        query = (
            select(func.strftime("%Y-%m", LancamentoFinanceiro.data).label("periodo"))
            .distinct()
            .order_by(desc("periodo"))
        )
        result = await db.execute(query)
        return [r.periodo for r in result if r.periodo]
