# Guia de Instalação e Execução - ObrasFinance

Este guia descreve como configurar o ambiente de desenvolvimento e rodar o projeto do zero.

## Pré-requisitos
- **Desenvolvimento**: Node.js (v18+) e Python (3.11+).
- **SO**: Funciona em Windows, macOS e Linux.

## Passo 1: Configuração do Backend
Entre na pasta `backend/`:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Passo 2: Configuração do Frontend
Na raiz do projeto:
```bash
npm install
```

## Passo 3: Execução em Desenvolvimento
Você precisará de dois terminais abertos:

**Terminal 1 (Backend):**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
npm run dev
```
Acesse: `http://localhost:5173`

## Comandos Úteis
- **Build de Produção Frontend**: `npm run build` (gera a pasta `dist` que o backend serve no modo portátil).
- **Linting e Check**: `npm run check` (Svelte-check).
