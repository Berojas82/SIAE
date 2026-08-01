# SIAE - Sistema Inteligente de Autodiagnóstico Empresarial (Proyecto ITACA)

Motor de IA multimodal híbrido (TensorFlow/Keras + SentenceTransformers) para el autodiagnóstico empresarial de madurez digital.

## Estructura del Repositorio

- `src/`: Código fuente principal (cargador de datos, preprocesamiento multimodal, modelo híbrido, evaluador y API REST).
- `scripts/`: Scripts CLI para entrenamiento (`train.py`), evaluación (`evaluate.py`), inferencia CLI (`predict.py`) y servidor web (`serve.py`).
- `notebooks/`: Notebooks de análisis y preparación (`01_EDA.ipynb`, `02_Preprocesamiento_de_datos.ipynb`, `03_Procesamiento_y_preparación_de_datos.ipynb`, `04_evaluation.ipynb`).
- `frontend/`: Cliente Web interactivo (HTML5/CSS3/JS vanilla con diseño glassmorphism).
- `docker/`: Dockerfiles y `docker-compose.yml` para orquestación de servicios (API y Frontend).
- `tests/`: Suite de pruebas unitarias integradas con `pytest`.
- `data/`: Datasets crudos, procesados (`cleaned_data.csv`) y particiones (`splits/`).
- `artifacts/`: Artefactos serializados del modelo (`model.keras`, `tabular_preprocessor.joblib`, `label_encoder.joblib`, `metadata.json`).

## Uso Rápido

1. Instalar el entorno y dependencias:

```powershell
pip install -r requirements.txt
pip install -e .
```

2. Entrenar el modelo híbrido y generar artefactos:

```powershell
python scripts/train.py
```

3. Iniciar el servidor API local:

```powershell
python scripts/serve.py
```

4. Probar inferencia desde línea de comandos:

```powershell
python scripts/predict.py
```

5. Ejecutar la suite de pruebas unitarias:

```powershell
pytest tests/
```

## Docker Compose

```powershell
cd docker
docker-compose up --build
```
- API REST: `http://localhost:8000`
- Frontend Web: `http://localhost:80`
