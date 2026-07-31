"""
Script para iniciar el servidor web FastAPI con Uvicorn.
Ejecución: python scripts/serve.py
"""
import sys
import uvicorn
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

if __name__ == "__main__":
    print("🚀 Iniciando servidor FastAPI de ITACA en http://localhost:8000 ...")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
