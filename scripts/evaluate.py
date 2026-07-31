"""
Script de evaluación y auditoría para artefactos entrenados.
Ejecución: python scripts/evaluate.py
"""
import sys
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.models.hybrid_model import HybridModel
from src.preprocessing.text.nlp_cleaner import NLPCleaner
from src.preprocessing.text.text_encoder import TextEncoder
from src.data_loader.data_splitter import DataSplitter
from src.evaluation.itaca_model_evaluator import ITACAModelEvaluator
from src.utils.constants import (
    MODEL_KERAS_PATH,
    TABULAR_PREPROCESSOR_PATH,
    LABEL_ENCODER_PATH,
    SPLITS_DIR
)
from src.utils.logger import get_logger

logger = get_logger("EvaluateScript")

def main():
    test_csv_path = SPLITS_DIR / "test.csv"
    if not test_csv_path.exists():
        logger.error(f"No se encontró el conjunto de prueba en {test_csv_path}. Ejecuta `python scripts/train.py` primero.")
        return

    logger.info("Cargando artefactos para evaluación...")
    model = HybridModel.load(str(MODEL_KERAS_PATH))
    tabular_preprocessor = joblib.load(TABULAR_PREPROCESSOR_PATH)
    label_encoder = joblib.load(LABEL_ENCODER_PATH)

    test_df = pd.read_csv(test_csv_path, encoding="utf-8")
    splitter = DataSplitter()
    X_tab_df, X_text_ser, y_ser = splitter.split_features_and_target(test_df)

    y_test_idx = label_encoder.transform(y_ser)
    X_tab = tabular_preprocessor.transform(X_tab_df)

    cleaner = NLPCleaner()
    clean_texts = cleaner.clean_series(X_text_ser)
    encoder = TextEncoder()
    X_text = encoder.encode(clean_texts)

    logger.info("Generando inferencia en batch para evaluación...")
    y_probs = model.predict(X_tab, X_text)
    y_preds = np.argmax(y_probs, axis=1)

    evaluator = ITACAModelEvaluator(class_names=list(label_encoder.classes_))
    results = evaluator.evaluate_and_audit(
        y_true_indices=np.asarray(y_test_idx),
        y_pred_indices=np.asarray(y_preds),
        y_probs=y_probs,
        sectores=np.asarray(test_df["sector"])
    )

    print(json.dumps(results["global_metrics"], indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
