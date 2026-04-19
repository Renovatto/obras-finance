import os
import sys
import socket
import webbrowser
import threading
import time
import uvicorn
from pathlib import Path

# Configurar caminhos para o PyInstaller
if getattr(sys, 'frozen', False):
    # Se rodando do executável
    BASE_PATH = Path(sys._MEIPASS)
    # No executável, forçamos o STATIC_FILES_PATH para onde o PyInstaller o colocou
    os.environ["STATIC_FILES_PATH"] = str(BASE_PATH / "dist")
else:
    # Se rodando do código fonte
    BASE_PATH = Path(__file__).resolve().parent

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_available_port(start_port):
    port = start_port
    while is_port_in_use(port):
        if port >= start_port + 1: # Limite de tentativa (8000 e 8001)
            break
        port += 1
    return port

def open_browser(url):
    # Pequeno delay para garantir que o uvicorn subiu
    time.sleep(1.5)
    webbrowser.open(url)

if __name__ == "__main__":
    port = get_available_port(8000)
    url = f"http://localhost:{port}"
    
    print(f"--- ObrasFinance ---")
    print(f"Iniciando servidor em {url}...")
    
    # Iniciar thread para abrir o navegador
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()
    
    # Rodar o Uvicorn
    # Importante: usar a string 'app.main:app' ou o próprio objeto app
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, log_level="info")
