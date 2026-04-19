from typing import List
from decimal import Decimal
from sqlalchemy import select, func, cast, Numeric, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Obra, LancamentoFinanceiro, TipoLancamento
from app.schemas import RelatorioObraBudget

class RelatoriosService:
    @staticmethod
    async def get_obras_budget(db: AsyncSession) -> List[RelatorioObraBudget]:
        """
        Retorna o cruzamento entre as Obras ativas e a somatória 
        de todos os seus lançamentos financeiros do tipo Despesa.
        """
        # Obter a sumatória aggreagada por obra_id usando CTE / Subquery
        st_despesas = (
            select(
                LancamentoFinanceiro.fk_obra,
                func.sum(cast(LancamentoFinanceiro.valor, Numeric)).label("total_gasto")
            )
            .where(LancamentoFinanceiro.tipo == TipoLancamento.despesa.value)
            .group_by(LancamentoFinanceiro.fk_obra)
            .subquery()
        )

        # Construir o Join
        stmt = (
            select(
                Obra.id,
                Obra.nome,
                Obra.nome_cliente,
                Obra.custo_estimado,
                func.coalesce(st_despesas.c.total_gasto, 0).label("total_gasto")
            )
            .outerjoin(st_despesas, Obra.id == st_despesas.c.fk_obra)
            .order_by(desc("total_gasto"))
        )

        result = await db.execute(stmt)
        rows = result.all()

        relatorios = []
        for r in rows:
            custo_estimado = Decimal(str(r.custo_estimado or "0.00"))
            total_gasto = Decimal(str(r.total_gasto or "0.00"))
            
            # Cálculo de progressão
            progresso = Decimal("0.00")
            if custo_estimado > 0:
                progresso = (total_gasto / custo_estimado) * 100
                progresso = round(progresso, 2)
            else:
                # Se o custo estimado é 0, a regra é exibir a obra,
                # e o % vai depender: se gastou algo e custo era 0 estourou infinitamente.
                # Para evitar erro visual / NaN setar logicamente.
                if total_gasto > 0:
                    progresso = Decimal("100.00") 
                else:
                    progresso = Decimal("0.00")

            relatorios.append(RelatorioObraBudget(
                id=r.id,
                nome_obra=r.nome,
                gerente=r.nome_cliente,
                custo_estimado=custo_estimado,
                total_gasto=total_gasto,
                progresso_porcentagem=progresso
            ))
            
        return relatorios
