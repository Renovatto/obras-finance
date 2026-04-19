import os
import json
from pathlib import Path
from pydantic_settings import BaseSettings

# Localização padrão das configurações de sistema
CONFIG_DIR = Path.home() / "Documents" / "ObrasFinance"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Caminho para os arquivos estáticos do Frontend
# Em desenvolvimento: projetopai/backend/dist
# No executável PyInstaller: _MEIPASS/dist
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = Path(os.getenv("STATIC_FILES_PATH", BASE_DIR / "dist"))

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
    #  CORS – ajuste conforme ambiente
    # ──────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",  # SvelteKit dev
        "http://localhost:4173",  # SvelteKit preview
        "*"                       # Permitir tudo para o executável local
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
