# Plan de Implementación: Backend, Configuración de Docker, Latencia de Inferencia y API Local (Proyecto ITACA - SIAE)

Basado en la auditoría técnica verificada del documento **`ITACA_Estado_Real_y_Plan_de_Accion.pdf`** (Equipo Mythos 6 / Capstone SIC 2025), este plan establece la hoja de ruta técnica precisa para corregir los hallazgos críticos del Backend, optimizar el empaquetado Docker, realizar la medición de latencia y asegurar el funcionamiento robusto de la API REST local.

---

## 🎯 Objetivos Principales del Backend

1. **Corrección Crítica de Empaquetado Docker (`Dockerfile.api` & `docker-compose.yml`)**:
   - Copiar la carpeta `scripts/` al contenedor para evitar el fallo de arranque `can't open file '/app/scripts/serve.py'`.
   - Reemplazar el comando `python scripts/serve.py` por ejecutor directo de `uvicorn src.api.main:app --host 0.0.0.0 --port 8000` en producción, evitando el modo `--reload`.
   - Incorporar `healthcheck` en la API en `docker-compose.yml` para asegurar que el frontend espere a que la API y los modelos estén verdaderamente cargados antes de iniciar (`condition: service_healthy`).
2. **Medición Rigurosa de Latencia de Inferencia (< 3 segundos)**:
   - Crear el script [`scripts/medir_latencia.py`](file:///c:/Users/Rodriguez/Desktop/Samsung%20innovation%20campus/Curso%20Ia/capstone/proyeco/SIAE/scripts/medir_latencia.py) para evaluar el tiempo de respuesta del modelo en 20 iteraciones (descartando la 1ª inferencia por carga perezosa de Transformer) y verificar que cumpla la meta de latencia < 3.0 s.
3. **Manejo Seguro de Errores en la API REST Local**:
   - En [`src/api/endpoints.py`](file:///c:/Users/Rodriguez/Desktop/Samsung%20innovation%20campus/Curso%20Ia/capstone/proyeco/SIAE/src/api/endpoints.py), evitar la filtración de detalles internos de excepciones (`str(e)`) hacia el cliente HTTP. Registrar los rastreos detallados en los logs del servidor con `logger.exception()` y retornar mensajes de error genéricos y seguros (`HTTP 500`).
4. **Prueba de Humo (Smoke Test) de Punta a Punta**:
   - Ejecutar la secuencia completa de preparación, entrenamiento local (`python scripts/train.py`), levantamiento de la API y verificación de la prueba de humo desde un clon limpio.

---

## ⚠️ User Review Required

> [!IMPORTANT]
> **Estrategia de Distribución de Artefactos**:
> Los archivos en `artifacts/` (`model.keras`, `tabular_preprocessor.joblib`, etc.) están ignorados en `.gitignore` por su tamaño binario. Se adoptará la **Opción 1 recomendada por el informe**: el script de entrenamiento `python scripts/train.py` debe ser ejecutado al clonar el repositorio antes de construir las imágenes de Docker.

> [!WARNING]
> **Arranque de Contenedores y Carga de Modelo**:
> La carga inicial del modelo Keras y los embeddings de `SentenceTransformer` toma entre 10 y 30 segundos. Se configurará un `start_period: 90s` en el `healthcheck` del contenedor API en Docker Compose para garantizar que `nginx` (frontend) no intente direccionar peticiones antes de que la API reporte `ONLINE`.

---

## ❓ Open Questions

> [!NOTE]
> 1. ¿Desea que generemos también un script `.bat` o `.ps1` para automatizar la prueba de humo local en Windows con un solo clic?
> 2. ¿Desea congelar las versiones de las dependencias (`requirements.lock.txt` con versiones exactas `==`) en esta misma iteración de Backend?

---

## 🛠️ Proposed Changes

### Componente 1: Empaquetado y Orquestación Docker (`docker/`)

#### [MODIFY] [Dockerfile.api](file:///c:/Users/Rodriguez/Desktop/Samsung%20innovation%20campus/Curso%20Ia/capstone/proyeco/SIAE/docker/Dockerfile.api)
- Incluir `COPY scripts/ ./scripts/` para disponibilizar los scripts en el directorio del contenedor `/app`.
- Cambiar el `CMD` final a ejecución directa mediante Uvicorn sin `--reload`:
  ```dockerfile
  CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

#### [MODIFY] [docker-compose.yml](file:///c:/Users/Rodriguez/Desktop/Samsung%20innovation%20campus/Curso%20Ia/capstone/proyeco/SIAE/docker/docker-compose.yml)
- Agregar bloque `healthcheck` al servicio `api` consultando `http://localhost:8000/health`.
- Configurar la dependencia del `frontend` para aguardar por `service_healthy`.

---

### Componente 2: API REST Local y Manejo de Errores (`src/api/`)

#### [MODIFY] [endpoints.py](file:///c:/Users/Rodriguez/Desktop/Samsung%20innovation%20campus/Curso%20Ia/capstone/proyeco/SIAE/src/api/endpoints.py)
- Refactorizar el bloque `try...except` del endpoint `POST /predict`.
- Registrar la excepción con `logger.exception("Fallo durante la inferencia")` y retornar `HTTPException(status_code=500, detail="Error interno al generar el diagnostico. Intente nuevamente.")`.

---

### Componente 3: Scripts de Medición y Validación de Latencia (`scripts/`)

#### [NEW] [medir_latencia.py](file:///c:/Users/Rodriguez/Desktop/Samsung%20innovation%20campus/Curso%20Ia/capstone/proyeco/SIAE/scripts/medir_latencia.py)
- Crear script CLI para cargar artefactos en memoria con [`ModelContainer`](file:///c:/Users/Rodriguez/Desktop/Samsung%20innovation%20campus/Curso%20Ia/capstone/proyeco/SIAE/src/api/dependencies.py#L57-L156).
- Ejecutar una inferencia *warm-up* para descartar la latencia de carga inicial del Transformer.
- Medir con `time.perf_counter()` 20 predicciones consecutivas.
- Calcular media, mediana, valor máximo y validar la condición `max(tiempos) < 3.0 s`.

---

## 🧪 Verification Plan

### Automated Tests
1. **Verificación de Pruebas Unitarias de API**:
   - Ejecutar la suite de tests en entorno Python local:
     ```powershell
     python -m pytest tests/test_api.py
     ```
2. **Medición Automatizada de Latencia**:
   - Ejecutar el script de latencia:
     ```powershell
     python scripts/medir_latencia.py
     ```
   - Confirmar salida con métricas de media, mediana, máximo y dictamen de cumplimiento (`CUMPLE < 3s`).

### Manual Verification
1. **Construcción y Prueba de Arranque Docker**:
   - Garantizar la existencia de artefactos entrenando con `python scripts/train.py`.
   - Levantar los contenedores con Docker Compose:
     ```powershell
     cd docker
     docker-compose up --build
     ```
   - Verificar logs para comprobar que `itaca_api` arranca sin reiniciar infinitamente y pasa a estado `healthy`.
2. **Prueba HTTP en Local**:
   - Verificar el estado de salud de la API:
     ```powershell
     curl http://localhost:8000/health
     ```
     Respuesta esperada: `{"status": "ONLINE", "artifacts_loaded": true}`.
   - Probar endpoint de inferencia `/predict` enviando un payload de PyME real.
