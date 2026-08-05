import sys
import time
import statistics
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.api.dependencies import container

container.load_artifacts()

caso = dict(
    sector="Comercio",
    tamano_empresa="Pequena",
    porcentaje_procesos_documentados=0.35,
    presupuesto_anual_tecnologia=8000000,
    respuesta_texto="Tenemos algunas herramientas digitales pero no estan integradas entre si"
)

# Descartar la 1a inferencia por carga perezosa del transformer
container.predict_sample(**caso)

tiempos = []
for _ in range(20):
    t0 = time.perf_counter()
    container.predict_sample(**caso)
    tiempos.append(time.perf_counter() - t0)

print(f"Media   : {statistics.mean(tiempos):.3f} s")
print(f"Mediana : {statistics.median(tiempos):.3f} s")
print(f"Maximo  : {max(tiempos):.3f} s")
print("REQUISITO < 3 s ->", "CUMPLE" if max(tiempos) < 3 else "NO CUMPLE")
