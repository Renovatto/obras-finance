"""
Schemas Pydantic v2
===================
Um módulo por entidade.  Padrão de naming:
  • <Entidade>Base   – campos comuns de escrita
  • <Entidade>Create – payload de criação (herda Base)
  • <Entidade>Update – atualização parcial (todos opcionais)
  • <Entidade>Read   – resposta da API (inclui id + campos computados)
"""
import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import TipoLancamento, StatusLancamento


# ════════════════════════════════════════════════════════════════
#  Tabelas Auxiliares
# ════════════════════════════════════════════════════════════════

# ── Categoria ────────────────────────────────────────────────
class CategoriaBase(BaseModel):
    nome: str = Field(..., max_length=255, examples=["Material"])

    @field_validator('nome')
    @classmethod
    def to_uppercase(cls, v: str) -> str:
        return v.upper() if v else v


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)


class CategoriaRead(CategoriaBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


# ── Forma de Pagamento ───────────────────────────────────────
class FormaPagamentoBase(BaseModel):
    nome: str = Field(..., max_length=255, examples=["PIX"])

    @field_validator('nome')
    @classmethod
    def to_uppercase(cls, v: str) -> str:
        return v.upper() if v else v


class FormaPagamentoCreate(FormaPagamentoBase):
    pass


class FormaPagamentoUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)


class FormaPagamentoRead(FormaPagamentoBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


# ── Responsável ───────────────────────────────────────────────
class ResponsavelBase(BaseModel):
    nome: str = Field(..., max_length=255, examples=["João Silva"])

    @field_validator('nome')
    @classmethod
    def to_uppercase(cls, v: str) -> str:
        return v.upper() if v else v


class ResponsavelCreate(ResponsavelBase):
    pass


class ResponsavelUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)


class ResponsavelRead(ResponsavelBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


# ════════════════════════════════════════════════════════════════
#  Obra
# ════════════════════════════════════════════════════════════════
class ObraBase(BaseModel):
    nome: str = Field(..., max_length=255, examples=["Residência Alto da Serra"])
    nome_cliente: str = Field(default="Não Informado", max_length=255, examples=["Maria Souza"])
    custo_estimado: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
        examples=[Decimal("150000.00")],
    )
    data_inicio: date = Field(default_factory=date.today, examples=["2025-01-10"])
    data_fim: Optional[date] = Field(None, examples=["2025-12-31"])
    descricao: Optional[str] = Field(None, examples=["Construção de sobrado duplex"])


class ObraCreate(ObraBase):
    pass


class ObraUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    nome_cliente: Optional[str] = Field(None, max_length=255)
    custo_estimado: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    descricao: Optional[str] = None


class ObraRead(ObraBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


# ════════════════════════════════════════════════════════════════
#  Lançamento Financeiro
# ════════════════════════════════════════════════════════════════
class LancamentoBase(BaseModel):
    tipo: TipoLancamento = Field(..., examples=[TipoLancamento.despesa])
    data: date = Field(..., examples=["2025-03-15"])
    valor: Decimal = Field(
        ..., ge=0, decimal_places=2, examples=[Decimal("4500.00")]
    )
    status: StatusLancamento = Field(
        StatusLancamento.pendente, examples=[StatusLancamento.pago]
    )
    descricao: str = Field(
        ..., max_length=60, examples=["Compra de cimento – 50 sacos"]
    )
    notas: Optional[str] = Field(
        None, max_length=255, examples=["Nota fiscal nº 12345"]
    )
    fk_categoria: uuid.UUID
    fk_forma_pagamento: uuid.UUID
    fk_responsavel: uuid.UUID
    fk_obra: Optional[uuid.UUID] = None


class LancamentoCreate(LancamentoBase):
    pass


class LancamentoUpdate(BaseModel):
    tipo: Optional[TipoLancamento] = None
    data: Optional[date] = None
    valor: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    status: Optional[StatusLancamento] = None
    descricao: Optional[str] = Field(None, max_length=60)
    notas: Optional[str] = Field(None, max_length=255)
    fk_categoria: Optional[uuid.UUID] = None
    fk_forma_pagamento: Optional[uuid.UUID] = None
    fk_responsavel: Optional[uuid.UUID] = None
    fk_obra: Optional[uuid.UUID] = None


class LancamentoRead(LancamentoBase):
    id: uuid.UUID
    # Embutir objetos relacionados para economizar round-trips
    categoria: CategoriaRead
    forma_pagamento: FormaPagamentoRead
    responsavel: ResponsavelRead
    obra: Optional[ObraRead] = None

    model_config = ConfigDict(from_attributes=True)


# ════════════════════════════════════════════════════════════════
#  DataTable & Dashboard Response Schemas
# ════════════════════════════════════════════════════════════════

class BatchDeletePayload(BaseModel):
    ids: list[uuid.UUID]


class LancamentoStats(BaseModel):
    total_receitas: Decimal = Field(default=Decimal("0.00"))
    total_despesas: Decimal = Field(default=Decimal("0.00"))


class LancamentoPagedResponse(BaseModel):
    items: list[LancamentoRead]
    total: int
    page: int
    page_size: int
    pages: int
    stats: LancamentoStats


class DashboardKPIs(BaseModel):
    total_receitas: Decimal
    total_despesas: Decimal
    saldo: Decimal


class DashboardMonthlyPL(BaseModel):
    mes: str  # YYYY-MM
    receita: Decimal
    despesa: Decimal
    lucro: Decimal


class DashboardCategoryExpenses(BaseModel):
    categoria: str
    total: Decimal


class RelatorioObraBudget(BaseModel):
    id: uuid.UUID
    nome_obra: str
    gerente: str
    custo_estimado: Decimal
    total_gasto: Decimal
    progresso_porcentagem: Decimal
