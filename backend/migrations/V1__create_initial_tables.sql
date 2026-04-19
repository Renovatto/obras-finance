-- ============================================================
--  Script SQL de Criação Manual das Tabelas
--  Sistema de Controle Financeiro de Obras
--  Gerado como referência – use Alembic em produção
-- ============================================================

-- Extensão UUID (necessária no PostgreSQL < 13 para gen_random_uuid())
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── ENUMs ────────────────────────────────────────────────────
DO $$ BEGIN
    CREATE TYPE tipo_lancamento AS ENUM ('Receita', 'Despesa');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE status_lancamento AS ENUM ('Pago', 'Pendente');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ── Tabelas Auxiliares ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categorias (
    id   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS formas_pagamento (
    id   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS responsaveis (
    id   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL
);

-- ── Obras ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS obras (
    id              UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    nome            VARCHAR(255)   NOT NULL,
    nome_cliente    VARCHAR(255)   NOT NULL,
    custo_estimado  DECIMAL(12, 2) NOT NULL CHECK (custo_estimado >= 0),
    data_inicio     DATE           NOT NULL,
    data_fim        DATE,
    descricao       TEXT
);

-- ── Lançamentos Financeiros ───────────────────────────────────
CREATE TABLE IF NOT EXISTS lancamentos_financeiros (
    id                 UUID              PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo               tipo_lancamento   NOT NULL,
    data               DATE              NOT NULL,
    valor              DECIMAL(12, 2)    NOT NULL CHECK (valor >= 0),
    status             status_lancamento NOT NULL DEFAULT 'Pendente',
    descricao          VARCHAR(255)      NOT NULL,
    comentarios        TEXT,
    fk_categoria       UUID              NOT NULL REFERENCES categorias(id)       ON DELETE RESTRICT,
    fk_forma_pagamento UUID              NOT NULL REFERENCES formas_pagamento(id) ON DELETE RESTRICT,
    fk_responsavel     UUID              NOT NULL REFERENCES responsaveis(id)     ON DELETE RESTRICT,
    fk_obra            UUID                       REFERENCES obras(id)            ON DELETE SET NULL
);

-- ── Índices para performance ──────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_lancamentos_fk_obra       ON lancamentos_financeiros(fk_obra);
CREATE INDEX IF NOT EXISTS idx_lancamentos_tipo          ON lancamentos_financeiros(tipo);
CREATE INDEX IF NOT EXISTS idx_lancamentos_status        ON lancamentos_financeiros(status);
CREATE INDEX IF NOT EXISTS idx_lancamentos_data          ON lancamentos_financeiros(data);
CREATE INDEX IF NOT EXISTS idx_lancamentos_fk_categoria  ON lancamentos_financeiros(fk_categoria);
