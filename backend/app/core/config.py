import os
import sys
import json
from pathlib import Path
from pydantic_settings import BaseSettings

# Localização padrão das configurações de sistema
CONFIG_DIR = Path.home() / "Documents" / "ObrasFinance"
CONFIG_FILE = CONFIG_DIR / "config.json"

def get_db_url():
    """Lê o caminho do banco de dados do arquivo config.json ou usa o padrão."""
    default_db = str(CONFIG_DIR / "database.db")
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                path = data.get("database_path", default_db)
                return f"sqlite+aiosqlite:///{path}"
        except Exception:
            pass
    
    # Fallback ou criação do diretório padrão se não existir
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    return f"sqlite+aiosqlite:///{default_db}"

class Settings(BaseSettings):
    # ──────────────────────────────────────────
    #  Ambiente e Infra
    # ──────────────────────────────────────────
    # Detecta se está rodando de dentro de um executável PyInstaller
    IS_PORTABLE: bool = getattr(sys, 'frozen', False)
    
    # Caminho raiz para arquivos estáticos
    @property
    def STATIC_DIR(self) -> Path:
        if self.IS_PORTABLE:
            # No executável único, sys._MEIPASS aponta para a pasta temporária
            return Path(sys._MEIPASS) / "dist"
        
        # Em desenvolvimento, olha para a pasta dist dentro de backend (se gerada)
        base_dir = Path(__file__).resolve().parent.parent.parent
        custom_path = os.getenv("STATIC_FILES_PATH")
        return Path(custom_path) if custom_path else base_dir / "dist"

    # ──────────────────────────────────────────
    #  Database – SQLite via aiosqlite
    # ──────────────────────────────────────────
    DATABASE_URL: str = get_db_url()

    # ──────────────────────────────────────────
    #  App
    # ──────────────────────────────────────────
    APP_NAME: str = "Sistema de Controle Financeiro de Obras"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # ──────────────────────────────────────────
    #  CORS
    # ──────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",  # SvelteKit dev
        "http://localhost:4173",  # SvelteKit preview
        "*"                       # Permitir tudo no executável para facilitar acesso local
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
