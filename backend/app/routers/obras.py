"""
Router: /api/obras  –  CRUD completo (via ObraService)
=======================================================
Verbos HTTP:
  POST   /api/obras/          → criar obra
  GET    /api/obras/          → listar (paginação + filtro nome_cliente)
  GET    /api/obras/{id}      → obter por ID
  PUT    /api/obras/{id}      → substituir todos os campos (PUT semântico)
  PATCH  /api/obras/{id}      → atualizar campos parciais
  DELETE /api/obras/{id}      → remover
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import ObraCreate, ObraRead, ObraUpdate
from app.services.obra_service import ObraService

router = APIRouter()


@router.post("/", response_model=ObraRead, status_code=status.HTTP_201_CREATED)
async def criar_obra(
    payload: ObraCreate,
    db: AsyncSession = Depends(get_db),
):
    """Cria uma nova obra."""
    return await ObraService.criar(db, payload)


@router.get("/", response_model=list[ObraRead])
async def listar_obras(
    skip: int = Query(0, ge=0, description="Offset da paginação"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros"),
    nome_cliente: Optional[str] = Query(None, description="Filtro parcial por nome do cliente"),
    db: AsyncSession = Depends(get_db),
):
    """Lista obras com paginação e filtro opcional por nome_cliente."""
    return await ObraService.listar(db, skip=skip, limit=limit, nome_cliente=nome_cliente)


@router.get("/{obra_id}", response_model=ObraRead)
async def obter_obra(
    obra_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retorna uma obra pelo ID."""
    return await ObraService.obter(db, obra_id)


@router.put("/{obra_id}", response_model=ObraRead)
async def substituir_obra(
    obra_id: uuid.UUID,
    payload: ObraCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Substitui todos os campos da obra (PUT).
    Requer o payload completo – campos não enviados voltam ao valor padrão/null.
    """
    return await ObraService.substituir(db, obra_id, payload)


@router.patch("/{obra_id}", response_model=ObraRead)
async def atualizar_obra(
    obra_id: uuid.UUID,
    payload: ObraUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Atualiza apenas os campos fornecidos (PATCH)."""
    return await ObraService.atualizar(db, obra_id, payload)


@router.delete("/{obra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_obra(
    obra_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Remove uma obra permanentemente."""
    await ObraService.deletar(db, obra_id)
