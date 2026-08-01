"""
Script de medición y validación de latencia de inferencia para ITACA - SIAE.
Ejecución: python scripts/medir_latencia.py
"""
import sys
import time
import statistics
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.api.dependencies import container
from src.utils.logger import get_logger

logger = get_logger("MedicionLatencia")

def medir_latencia(iterations: int = 20, max_allowed_sec: float = 3.0):
    logger.info("Iniciando carga de artefactos...")
    container.load_artifacts()

    # Muestra representativa de prueba
    sample = {
        "sector": "Tecnología",
        "tamano_empresa": "Micro",
        "porcentaje_procesos_documentados": 0.05,
        "presupuesto_anual_tecnologia": 3000000.0,
        "respuesta_texto": "El trabajo es muy empírico, no hay documentación formal de los procesos."
    }

    logger.info("Ejecutando inferencia de warm-up (descartada del benchmark)...")
    start_warmup = time.perf_counter()
    _ = container.predict_sample(**sample)
    warmup_time = time.perf_counter() - start_warmup
    logger.info(f"Tiempo de warm-up: {warmup_time:.4f} s")

    logger.info(f"Ejecutando benchmark de {iterations} inferencias consecutivas...")
    times = []
    for i in range(1, iterations + 1):
        t0 = time.perf_counter()
        _ = container.predict_sample(**sample)
        elapsed = time.perf_counter() - t0
        times.append(elapsed)

    media = statistics.mean(times)
    mediana = statistics.median(times)
    max_val = max(times)
    min_val = min(times)

    print("\n" + "="*50)
    print("      REPORTE DE LATENCIA DE INFERENCIA")
    print("="*50)
    print(f"Iteraciones        : {iterations}")
    print(f"Tiempo Mínimo      : {min_val:.4f} s")
    print(f"Tiempo Máximo      : {max_val:.4f} s")
    print(f"Media (Promedio)   : {media:.4f} s")
    print(f"Mediana            : {mediana:.4f} s")
    print("-" * 50)

    cumple = max_val < max_allowed_sec
    dictamen = "CUMPLE < 3.0s" if cumple else f"NO CUMPLE (Máx {max_val:.4f}s >= {max_allowed_sec}s)"
    print(f"Meta de Latencia   : < {max_allowed_sec:.1f} s")
    print(f"Dictamen Final     : {dictamen}")
    print("="*50 + "\n")

    return cumple, times

if __name__ == "__main__":
    cumple, _ = medir_latencia()
    if not cumple:
        sys.exit(1)
