"""
Service: ObraService
=====================
Camada de negócio para a entidade Obra.
Isola toda a lógica de acesso a dados dos routers,
facilitando testes unitários e reutilização.
"""
from __future__ import annotations

import uuid
from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Obra
from app.schemas import ObraCreate, ObraUpdate


class ObraService:

    # ──────────────────────────────────────────────────────
    #  Helpers internos
    # ──────────────────────────────────────────────────────
    @staticmethod
    async def _get_or_404(db: AsyncSession, obra_id: uuid.UUID) -> Obra:
        """Busca pelo ID ou lança 404."""
        obra = await db.get(Obra, obra_id)
        if not obra:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Obra '{obra_id}' não encontrada.",
            )
        return obra

    # ──────────────────────────────────────────────────────
    #  Operações CRUD
    # ──────────────────────────────────────────────────────
    @staticmethod
    async def criar(db: AsyncSession, payload: ObraCreate) -> Obra:
        """Cria uma nova obra e retorna o objeto persistido."""
        obra = Obra(**payload.model_dump())
        db.add(obra)
        await db.flush()
        await db.refresh(obra)
        return obra

    @staticmethod
    async def listar(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        nome_cliente: Optional[str] = None,
    ) -> Sequence[Obra]:
        """Lista obras com paginação e filtro opcional por cliente."""
        query = select(Obra).offset(skip).limit(limit).order_by(Obra.data_inicio.desc())
        if nome_cliente:
            query = query.where(Obra.nome_cliente.ilike(f"%{nome_cliente}%"))
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def obter(db: AsyncSession, obra_id: uuid.UUID) -> Obra:
        """Retorna uma obra por ID ou lança 404."""
        return await ObraService._get_or_404(db, obra_id)

    @staticmethod
    async def atualizar(
        db: AsyncSession, obra_id: uuid.UUID, payload: ObraUpdate
    ) -> Obra:
        """Atualiza campos fornecidos (PATCH semântico) e retorna obra atualizada."""
        obra = await ObraService._get_or_404(db, obra_id)
        campos = payload.model_dump(exclude_unset=True)
        if not campos:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Nenhum campo fornecido para atualização.",
            )
        for campo, valor in campos.items():
            setattr(obra, campo, valor)
        await db.flush()
        await db.refresh(obra)
        return obra

    @staticmethod
    async def substituir(
        db: AsyncSession, obra_id: uuid.UUID, payload: ObraCreate
    ) -> Obra:
        """Substitui todos os campos da obra (PUT semântico)."""
        obra = await ObraService._get_or_404(db, obra_id)
        for campo, valor in payload.model_dump().items():
            setattr(obra, campo, valor)
        await db.flush()
        await db.refresh(obra)
        return obra

    @staticmethod
    async def deletar(db: AsyncSession, obra_id: uuid.UUID) -> None:
        """Remove uma obra permanentemente."""
        obra = await ObraService._get_or_404(db, obra_id)
        await db.delete(obra)
