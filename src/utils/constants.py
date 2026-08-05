"""
Constantes globales para el proyecto ITACA.
"""
from pathlib import Path

# Rutas
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "raw_data.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "cleaned_data.csv"
SPLITS_DIR = DATA_DIR / "splits"

ARTIFACTS_DIR = BASE_DIR / "artifacts"
MODEL_KERAS_PATH = ARTIFACTS_DIR / "model.keras"
TABULAR_PREPROCESSOR_PATH = ARTIFACTS_DIR / "tabular_preprocessor.joblib"
LABEL_ENCODER_PATH = ARTIFACTS_DIR / "label_encoder.joblib"
METADATA_PATH = ARTIFACTS_DIR / "metadata.json"

# Columnas del Dataset (Se excluye porcentaje_procesos_documentados por fuga de etiqueta determinista)
NUMERICAL_COLS = ["presupuesto_anual_tecnología"]
CATEGORICAL_COLS = ["sector", "tamano_empresa"]
TEXT_COL = "respuesta_texto"
TARGET_COL = "nivel_madurez"

# Clases de Madurez
CLASSES = ["Inicial", "En Desarrollo", "Definido", "Optimizado"]

# SentenceTransformer
TRANSFORMER_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
TEXT_EMBEDDING_DIM = 384
