"""
Service: AuxiliarService
=========================
Camada de negócio genérica para as tabelas auxiliares:
  • Categoria
  • FormaPagamento
  • Responsavel

Padrão: recebe a classe ORM como parâmetro, evitando duplicação de código.
"""
from __future__ import annotations

import uuid
from typing import Optional, Sequence, Type, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.models import Categoria, FormaPagamento, Responsavel

# TypeVar para os modelos auxiliares
AuxModel = TypeVar("AuxModel", Categoria, FormaPagamento, Responsavel)


class AuxiliarService:
    """
    Serviço genérico para tabelas auxiliares.
    Uso: AuxiliarService.listar(db, Categoria)
    """

    @staticmethod
    async def _get_or_404(
        db: AsyncSession, model: Type[AuxModel], obj_id: uuid.UUID
    ) -> AuxModel:
        obj = await db.get(model, obj_id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{model.__name__} '{obj_id}' não encontrado(a).",
            )
        return obj

    @staticmethod
    async def listar(
        db: AsyncSession,
        model: Type[AuxModel],
        skip: int = 0,
        limit: int = 200,
    ) -> Sequence[AuxModel]:
        """Lista todos os registros ordenados por nome."""
        result = await db.execute(
            select(model).order_by(model.nome).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def criar_por_nome(
        db: AsyncSession, model: Type[AuxModel], nome: str
    ) -> AuxModel:
        """
        Criação rápida por nome – pensada para os selects do frontend
        com opção 'Adicionar Novo' sem fechar a modal principal.
        Retorna o registro existente se o nome já estiver cadastrado
        (idempotente), evitando erros de unicidade para o usuário.
        """
        # Busca existente (case-insensitive)
        result = await db.execute(
            select(model).where(model.nome.ilike(nome.strip()))
        )
        existente = result.scalar_one_or_none()
        if existente:
            return existente

        obj = model(nome=nome.strip())
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def atualizar_nome(
        db: AsyncSession,
        model: Type[AuxModel],
        obj_id: uuid.UUID,
        nome: str,
    ) -> AuxModel:
        obj = await AuxiliarService._get_or_404(db, model, obj_id)
        obj.nome = nome.strip()
        await db.flush()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def deletar(
        db: AsyncSession, model: Type[AuxModel], obj_id: uuid.UUID
    ) -> None:
        obj = await AuxiliarService._get_or_404(db, model, obj_id)
        await db.delete(obj)
