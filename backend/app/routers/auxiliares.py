"""
Router: /api/auxiliares  –  Tabelas auxiliares unificadas
===========================================================
Agrupa Categorias, FormasPagamento e Responsáveis em um único
prefixo, com suporte à criação rápida inline (sem fechar modal).

Endpoints por tabela:
  GET    /api/auxiliares/categorias/           → listar
  POST   /api/auxiliares/categorias/           → criar rápido (só nome)
  GET    /api/auxiliares/categorias/{id}       → obter
  PATCH  /api/auxiliares/categorias/{id}       → atualizar nome
  DELETE /api/auxiliares/categorias/{id}       → remover

  (Idem para /formas-pagamento/ e /responsaveis/)

Endpoint consolidado (útil para popular selects do frontend de uma vez):
  GET    /api/auxiliares/todos                 → retorna as 3 tabelas juntas
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Categoria, FormaPagamento, Responsavel
from app.schemas import (
    CategoriaRead, CategoriaUpdate,
    FormaPagamentoRead, FormaPagamentoUpdate,
    ResponsavelRead, ResponsavelUpdate,
)
from app.services.auxiliar_service import AuxiliarService

router = APIRouter()


# ──────────────────────────────────────────────────────────────
#  Schema de entrada simplificado para criação rápida
# ──────────────────────────────────────────────────────────────
class NomePayload(BaseModel):
    """Payload mínimo compartilhado pelas 3 auxiliares."""
    nome: str = Field(..., min_length=1, max_length=255, examples=["Elétrica"])

    @field_validator('nome')
    @classmethod
    def to_uppercase(cls, v: str) -> str:
        return v.upper() if v else v


# ══════════════════════════════════════════════════════════════
#  Endpoint consolidado  –  alimenta todos os selects de uma vez
# ══════════════════════════════════════════════════════════════
class TodosAuxiliaresResponse(BaseModel):
    categorias: list[CategoriaRead]
    formas_pagamento: list[FormaPagamentoRead]
    responsaveis: list[ResponsavelRead]


@router.get(
    "/todos",
    response_model=TodosAuxiliaresResponse,
    summary="Buscar todas as auxiliares de uma vez",
)
async def listar_todos(db: AsyncSession = Depends(get_db)):
    """
    Retorna categorias, formas de pagamento e responsáveis em uma única
    chamada. Ideal para pré-popular selects/dropdowns do formulário.
    """
    categorias = await AuxiliarService.listar(db, Categoria)
    formas = await AuxiliarService.listar(db, FormaPagamento)
    responsaveis = await AuxiliarService.listar(db, Responsavel)
    return TodosAuxiliaresResponse(
        categorias=categorias,
        formas_pagamento=formas,
        responsaveis=responsaveis,
    )


# ══════════════════════════════════════════════════════════════
#  CATEGORIAS
# ══════════════════════════════════════════════════════════════
@router.get("/categorias/", response_model=list[CategoriaRead], tags=["Categorias"])
async def listar_categorias(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await AuxiliarService.listar(db, Categoria, skip, limit)


@router.post(
    "/categorias/",
    response_model=CategoriaRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Categorias"],
    summary="Criar ou recuperar categoria pelo nome",
)
async def criar_categoria(
    payload: NomePayload, db: AsyncSession = Depends(get_db)
):
    """
    Criação rápida – idempotente.
    Se já existir uma categoria com esse nome, retorna a existente (HTTP 201).
    Permite uso no 'Adicionar Novo' dentro da modal de lançamento.
    """
    return await AuxiliarService.criar_por_nome(db, Categoria, payload.nome)


@router.get("/categorias/{obj_id}", response_model=CategoriaRead, tags=["Categorias"])
async def obter_categoria(obj_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await AuxiliarService._get_or_404(db, Categoria, obj_id)


@router.patch("/categorias/{obj_id}", response_model=CategoriaRead, tags=["Categorias"])
async def atualizar_categoria(
    obj_id: uuid.UUID, payload: NomePayload, db: AsyncSession = Depends(get_db)
):
    return await AuxiliarService.atualizar_nome(db, Categoria, obj_id, payload.nome)


@router.delete(
    "/categorias/{obj_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Categorias"],
)
async def deletar_categoria(obj_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await AuxiliarService.deletar(db, Categoria, obj_id)


# ══════════════════════════════════════════════════════════════
#  FORMAS DE PAGAMENTO
# ══════════════════════════════════════════════════════════════
@router.get(
    "/formas-pagamento/",
    response_model=list[FormaPagamentoRead],
    tags=["Formas de Pagamento"],
)
async def listar_formas(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await AuxiliarService.listar(db, FormaPagamento, skip, limit)


@router.post(
    "/formas-pagamento/",
    response_model=FormaPagamentoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Formas de Pagamento"],
    summary="Criar ou recuperar forma de pagamento pelo nome",
)
async def criar_forma(payload: NomePayload, db: AsyncSession = Depends(get_db)):
    """Criação rápida idempotente. Retorna existente se o nome já existir."""
    return await AuxiliarService.criar_por_nome(db, FormaPagamento, payload.nome)


@router.get(
    "/formas-pagamento/{obj_id}",
    response_model=FormaPagamentoRead,
    tags=["Formas de Pagamento"],
)
async def obter_forma(obj_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await AuxiliarService._get_or_404(db, FormaPagamento, obj_id)


@router.patch(
    "/formas-pagamento/{obj_id}",
    response_model=FormaPagamentoRead,
    tags=["Formas de Pagamento"],
)
async def atualizar_forma(
    obj_id: uuid.UUID, payload: NomePayload, db: AsyncSession = Depends(get_db)
):
    return await AuxiliarService.atualizar_nome(db, FormaPagamento, obj_id, payload.nome)


@router.delete(
    "/formas-pagamento/{obj_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Formas de Pagamento"],
)
async def deletar_forma(obj_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await AuxiliarService.deletar(db, FormaPagamento, obj_id)


# ══════════════════════════════════════════════════════════════
#  RESPONSÁVEIS
# ══════════════════════════════════════════════════════════════
@router.get(
    "/responsaveis/",
    response_model=list[ResponsavelRead],
    tags=["Responsáveis"],
)
async def listar_responsaveis(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await AuxiliarService.listar(db, Responsavel, skip, limit)


@router.post(
    "/responsaveis/",
    response_model=ResponsavelRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Responsáveis"],
    summary="Criar ou recuperar responsável pelo nome",
)
async def criar_responsavel(payload: NomePayload, db: AsyncSession = Depends(get_db)):
    """Criação rápida idempotente. Retorna existente se o nome já existir."""
    return await AuxiliarService.criar_por_nome(db, Responsavel, payload.nome)


@router.get(
    "/responsaveis/{obj_id}",
    response_model=ResponsavelRead,
    tags=["Responsáveis"],
)
async def obter_responsavel(obj_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await AuxiliarService._get_or_404(db, Responsavel, obj_id)


@router.patch(
    "/responsaveis/{obj_id}",
    response_model=ResponsavelRead,
    tags=["Responsáveis"],
)
async def atualizar_responsavel(
    obj_id: uuid.UUID, payload: NomePayload, db: AsyncSession = Depends(get_db)
):
    return await AuxiliarService.atualizar_nome(db, Responsavel, obj_id, payload.nome)


@router.delete(
    "/responsaveis/{obj_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Responsáveis"],
)
async def deletar_responsavel(obj_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await AuxiliarService.deletar(db, Responsavel, obj_id)
