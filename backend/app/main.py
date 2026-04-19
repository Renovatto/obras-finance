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


@app.get("/", tags=["Root"])
async def root():
    """
    Redireciona para a documentação da API em desenvolvimento.
    No executável, esta rota será capturada pelo gerenciador de arquivos estáticos se o mesmo estiver ativo.
    """
    return RedirectResponse(url="/docs")


# ── Servidor de Arquivos Estáticos (Frontend) ──────────────────
# Ativado apenas no modo portátil ou se a pasta dist existir explicitamente
if settings.IS_PORTABLE or settings.STATIC_DIR.exists():
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

    @app.get("/{full_path:path}", tags=["Frontend"])
    async def serve_spa(full_path: str):
        """Serve o index.html para qualquer rota que não seja da API (SPA Fallback)."""
        # Ignora rotas que começam com /api ou documentação
        if full_path.startswith("api/") or full_path in ["docs", "redoc", "openapi.json"]:
            raise HTTPException(status_code=404, detail="Not Found")
            
        file_path = settings.STATIC_DIR / full_path
        if full_path != "" and file_path.exists():
            return FileResponse(file_path)
            
        # Fallback para SPA: entrega o index.html da raiz do frontend
        index_file = settings.STATIC_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        
        raise HTTPException(status_code=404, detail="Frontend não encontrado")

@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint consultado pelo frontend para verificar a saúde da API."""
    return {"status": "ok", "version": settings.APP_VERSION}
