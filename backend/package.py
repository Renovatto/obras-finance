import os
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    print(f"Executando: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Erro ao executar comando: {cmd}")
        exit(1)

def build():
    # 1. Obter caminhos
    backend_dir = Path(__file__).resolve().parent
    root_dir = backend_dir.parent
    dist_dir = backend_dir / "dist"
    
    print("--- Iniciando Processo de Empacotamento ---")
    
    # 2. Build do Frontend (SvelteKit)
    # Certificar que o PATH inclui node/npm
    env = os.environ.copy()
    if os.path.exists("/usr/local/bin"):
        env["PATH"] = env["PATH"] + ":/usr/local/bin"
    
    print("Gerando build do Frontend...")
    run_command("npm run build", cwd=str(root_dir))
    
    # 3. Limpar pastas de build anteriores do PyInstaller
    for folder in ["build", "dist_pkg"]:
        path = backend_dir / folder
        if path.exists():
            shutil.rmtree(path)
            
    # 4. Empacotar com PyInstaller
    print("Empacotando com PyInstaller...")
    # --onefile: um único executável
    # --add-data: inclui a pasta dist do frontend
    # --name: Nome do executável
    # --clean: limpa cache
    
    # Nota: No Windows o separador do --add-data é ';', no Mac/Linux é ':'
    sep = ";" if os.name == 'nt' else ":"
    
    # Usar o pyinstaller que está no venv
    venv_pyinstaller = str(backend_dir / ".venv" / "bin" / "pyinstaller")
    if os.name == 'nt':
        venv_pyinstaller = str(backend_dir / ".venv" / "Scripts" / "pyinstaller.exe")

    pyinstaller_cmd = (
        f"{venv_pyinstaller} --onefile "
        f"--add-data \"dist{sep}dist\" "
        f"--name \"ObrasFinance\" "
        f"--clean "
        f"launcher.py"
    )
    
    run_command(pyinstaller_cmd, cwd=str(backend_dir))
    
    print("\n--- SUCESSO! ---")
    print(f"O executável foi gerado em: {backend_dir / 'dist' / 'ObrasFinance'}")

if __name__ == "__main__":
    build()
