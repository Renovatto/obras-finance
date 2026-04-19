import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Localização padrão das configurações
CONFIG_DIR = Path.home() / "Documents" / "ObrasFinance"
CONFIG_FILE = CONFIG_DIR / "config.json"

class SystemConfig(BaseModel):
    database_path: str
    port: int = 8000

def get_default_config():
    db_path = str(CONFIG_DIR / "database.db")
    return SystemConfig(database_path=db_path)

def read_config() -> SystemConfig:
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config = get_default_config()
        save_config(config)
        return config
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return SystemConfig(**data)
    except Exception:
        return get_default_config()

def save_config(config: SystemConfig):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config.dict(), f, indent=4, ensure_ascii=False)

@router.get("/")
async def get_config():
    return read_config()

@router.post("/")
async def update_config(config: SystemConfig):
    save_config(config)
    return {"message": "Configuração salva com sucesso. Reinicie o aplicativo para aplicar as mudanças."}
