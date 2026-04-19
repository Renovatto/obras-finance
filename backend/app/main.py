"""
Ponto de entrada da aplicação FastAPI.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.database import engine, Base

# Importar routers (criados progressivamente)
from app.routers import (
    obras, lancamentos, auxiliares, dashboard, relatorios, config
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executa na inicialização e no encerramento da aplicação."""
    # TODO: Remover em produção – use Alembic para migrações
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
app.include_router(obras.router, prefix="/api/v1/obras", tags=["Obras"])
app.include_router(
    lancamentos.router, prefix="/api/v1/lancamentos", tags=["Lançamentos"]
)
app.include_router(
    auxiliares.router, prefix="/api/v1/auxiliares", tags=["Auxiliares"]
)
app.include_router(
    dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"]
)
app.include_router(
    relatorios.router, prefix="/api/v1/relatorios", tags=["Relatórios"]
)
app.include_router(
    config.router, prefix="/api/v1/config", tags=["Configurações"]
)


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# ... routers ... (already included above in the file)

# Montagem dos arquivos estáticos do Frontend (SvelteKit dist)
if settings.STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

    @app.get("/{full_path:path}", tags=["Frontend"])
    async def serve_spa(full_path: str):
        """Serve o index.html para qualquer rota que não seja da API (SPA Fallback)."""
        # Ignora rotas que começam com /api
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
            
        file_path = settings.STATIC_DIR / full_path
        if full_path != "" and file_path.exists():
            return FileResponse(file_path)
            
        return FileResponse(settings.STATIC_DIR / "index.html")

@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint consultado pelo frontend para verificar a saúde da API."""
    return {"status": "ok", "version": settings.APP_VERSION}
