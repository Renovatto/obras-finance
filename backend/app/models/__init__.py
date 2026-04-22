"""
Modelos ORM – SQLAlchemy (assíncrono / SQLite via aiosqlite)
=============================================================
Adaptações para SQLite (sem tipos nativos UUID, DECIMAL ou ENUM):

  • UUIDs       → CHAR(36) + TypeDecorator que converte uuid.UUID ↔ str
  • Decimal     → TEXT     + TypeDecorator que converte Decimal ↔ str
                  (precisão total preservada; sem arredondamento de float)
  • Enum        → TEXT     (validação feita pelos schemas Pydantic)
  • FKs         → RESTRICT emulado pelo PRAGMA foreign_keys=ON (database.py)
  • Optional[X] é usado em vez de X | None  (compatibilidade Python 3.9)
"""
import uuid
import enum
from datetime import date
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    types,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ══════════════════════════════════════════════════════════════
#  TypeDecorators customizados
# ══════════════════════════════════════════════════════════════

class UUIDType(types.TypeDecorator):
    """
    Armazena UUID como CHAR(36) no SQLite.
    Retorna sempre uuid.UUID no Python.

    Uso: mapped_column(UUIDType(), primary_key=True, default=uuid.uuid4)
    """
    impl = types.CHAR(36)
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        # Aceita string UUID já formatada
        return str(uuid.UUID(str(value)))

    def process_result_value(self, value: Any, dialect: Any) -> Optional[uuid.UUID]:
        if value is None:
            return None
        return uuid.UUID(str(value))


class DecimalType(types.TypeDecorator):
    """
    Armazena Decimal como TEXT no SQLite para precisão total.
    Elimina qualquer imprecisão de ponto flutuante – crucial para valores
    monetários.

    Uso: mapped_column(DecimalType(), nullable=False)
    """
    impl = types.TEXT
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> Optional[str]:
        if value is None:
            return None
        # Converte para Decimal primeiro para normalizar e depois para str
        return str(Decimal(str(value)))

    def process_result_value(self, value: Any, dialect: Any) -> Optional[Decimal]:
        if value is None:
            return None
        return Decimal(value)


# ══════════════════════════════════════════════════════════════
#  ENUMs Python  →  TEXT no SQLite (validação via Pydantic)
# ══════════════════════════════════════════════════════════════

class TipoLancamento(str, enum.Enum):
    receita = "Receita"
    despesa = "Despesa"


class StatusLancamento(str, enum.Enum):
    pago = "Pago"
    pendente = "Pendente"


# ══════════════════════════════════════════════════════════════
#  Tabelas Auxiliares
# ══════════════════════════════════════════════════════════════

class Categoria(Base):
    """Categorias de lançamentos (ex: Material, Mão-de-Obra)."""

    __tablename__ = "categorias"

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    lancamentos: Mapped[list["LancamentoFinanceiro"]] = relationship(
        back_populates="categoria"
    )


class FormaPagamento(Base):
    """Formas de pagamento (ex: PIX, Boleto, Transferência)."""

    __tablename__ = "formas_pagamento"

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    lancamentos: Mapped[list["LancamentoFinanceiro"]] = relationship(
        back_populates="forma_pagamento"
    )


class Responsavel(Base):
    """Responsáveis / pessoas vinculadas a lançamentos."""

    __tablename__ = "responsaveis"

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)

    lancamentos: Mapped[list["LancamentoFinanceiro"]] = relationship(
        back_populates="responsavel"
    )


# ══════════════════════════════════════════════════════════════
#  Obra
# ══════════════════════════════════════════════════════════════

class Obra(Base):
    """Entidade principal – representa uma obra / projeto."""

    __tablename__ = "obras"

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_cliente: Mapped[str] = mapped_column(String(255), nullable=False)
    # DecimalType: armazena como TEXT → sem imprecisão de float
    custo_estimado: Mapped[Decimal] = mapped_column(DecimalType(), nullable=False)
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    lancamentos: Mapped[list["LancamentoFinanceiro"]] = relationship(
        back_populates="obra", cascade="all, delete-orphan"
    )


# ══════════════════════════════════════════════════════════════
#  Lançamento Financeiro
# ══════════════════════════════════════════════════════════════

class LancamentoFinanceiro(Base):
    """Receitas e Despesas – núcleo financeiro do sistema."""

    __tablename__ = "lancamentos_financeiros"

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType(), primary_key=True, default=uuid.uuid4
    )
    # TEXT no SQLite; Pydantic valida que só aceita 'Receita' | 'Despesa'
    tipo: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    data: Mapped[date] = mapped_column(Date, nullable=False)
    # DecimalType: precisão financeira total preservada como TEXT
    valor: Mapped[Decimal] = mapped_column(DecimalType(), nullable=False)
    # TEXT no SQLite; Pydantic valida 'Pago' | 'Pendente'
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=StatusLancamento.pendente.value
    )
    descricao: Mapped[str] = mapped_column(String(60), nullable=False)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── FKs (RESTRICT via PRAGMA foreign_keys=ON em database.py) ──
    fk_categoria: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("categorias.id", ondelete="RESTRICT"),
        nullable=False,
    )
    fk_forma_pagamento: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("formas_pagamento.id", ondelete="RESTRICT"),
        nullable=False,
    )
    fk_responsavel: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        ForeignKey("responsaveis.id", ondelete="RESTRICT"),
        nullable=False,
    )
    # Obra é opcional – lançamentos gerais não precisam de obra
    fk_obra: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType(),
        ForeignKey("obras.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Relationships ──────────────────────────────────────────
    categoria: Mapped["Categoria"] = relationship(back_populates="lancamentos")
    forma_pagamento: Mapped["FormaPagamento"] = relationship(
        back_populates="lancamentos"
    )
    responsavel: Mapped["Responsavel"] = relationship(back_populates="lancamentos")
    obra: Mapped[Optional["Obra"]] = relationship(back_populates="lancamentos")


# ══════════════════════════════════════════════════════════════
#  Configuração do Sistema  (singleton – id sempre = 1)
# ══════════════════════════════════════════════════════════════

class ConfiguracaoSistema(Base):
    """
    Tabela singleton que centraliza todos os ajustes de sistema.
    
    Campos:
      • database_path   – caminho do arquivo SQLite
      • port            – porta do servidor interno
      • welcome_message – True quando o tour de boas-vindas já foi exibido
    """

    __tablename__ = "configuracao_sistema"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    database_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    port: Mapped[int] = mapped_column(Integer, nullable=False, default=8000)
    # False = tour ainda não foi visto; True = tour já foi concluído/pulado
    welcome_message: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
