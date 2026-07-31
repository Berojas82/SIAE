"""
Script de predicción desde línea de comandos (CLI).
Ejecución: python scripts/predict.py
"""
import sys
import json
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.api.dependencies import container

def main():
    container.load_artifacts()

    # Muestra de prueba individual
    sector = "Tecnología"
    tamano = "Micro"
    pct_procesos = 0.05
    presupuesto = 3000000.0
    texto = "El trabajo es muy empírico, no hay documentación de lo que hacemos."

    print("\n--- CONSULTA DE DIAGNÓSTICO EMPRESARIAL ---")
    print(f"Sector             : {sector}")
    print(f"Tamaño             : {tamano}")
    print(f"Procesos Doc. (%)  : {pct_procesos*100}%")
    print(f"Presupuesto Tech   : ${presupuesto:,.2f}")
    print(f"Respuesta Cualit.  : '{texto}'")
    print("-------------------------------------------\n")

    res = container.predict_sample(
        sector=sector,
        tamano_empresa=tamano,
        porcentaje_procesos_documentados=pct_procesos,
        presupuesto_anual_tecnologia=presupuesto,
        respuesta_texto=texto
    )

    print("📌 [RESULTADO DE PREDICCIÓN]:")
    print(json.dumps(res, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
