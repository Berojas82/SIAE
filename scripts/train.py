"""
Script de entrenamiento end-to-end del proyecto ITACA.
Ejecución: python scripts/train.py
"""
import sys
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.utils import to_categorical  # type: ignore

# Asegurar import de src
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.data_loader.data_loader import DataLoader
from src.data_loader.data_splitter import DataSplitter
from src.preprocessing.text.nlp_cleaner import NLPCleaner
from src.preprocessing.text.text_encoder import TextEncoder
from src.preprocessing.tabular.tabular_preprocessor import TabularPreprocessor
from src.models.hybrid_model import HybridModel
from src.evaluation.itaca_model_evaluator import ITACAModelEvaluator
from src.utils.constants import (
    MODEL_KERAS_PATH,
    TABULAR_PREPROCESSOR_PATH,
    LABEL_ENCODER_PATH,
    METADATA_PATH,
    ARTIFACTS_DIR
)
from src.utils.logger import get_logger

logger = get_logger("TrainScript")

def main():
    logger.info("=" * 70)
    logger.info("🚀 INICIANDO ENTRENAMIENTO DEL MODELO HÍBRIDO ITACA")
    logger.info("=" * 70)

    # 1. Cargar y particionar datos (70% Train, 15% Val, 15% Test)
    loader = DataLoader()
    train_df, val_df, test_df = loader.split_data(save_splits=True)

    # 2. Separar características y target
    splitter = DataSplitter()
    X_tab_train_df, X_text_train_ser, y_train_ser = splitter.split_features_and_target(train_df)
    X_tab_val_df, X_text_val_ser, y_val_ser = splitter.split_features_and_target(val_df)
    X_tab_test_df, X_text_test_ser, y_test_ser = splitter.split_features_and_target(test_df)

    # 3. Label Encoder para target (nivel_madurez -> 0..3)
    assert y_train_ser is not None and y_val_ser is not None and y_test_ser is not None
    label_encoder = LabelEncoder()
    y_train_idx = label_encoder.fit_transform(y_train_ser)
    y_val_idx = label_encoder.transform(y_val_ser)
    y_test_idx = label_encoder.transform(y_test_ser)

    assert label_encoder.classes_ is not None
    classes_list = list(label_encoder.classes_)
    num_classes = len(classes_list)
    y_train_cat = to_categorical(y_train_idx, num_classes=num_classes)
    y_val_cat = to_categorical(y_val_idx, num_classes=num_classes)
    y_test_cat = to_categorical(y_test_idx, num_classes=num_classes)

    # 4. Preprocesar rama Tabular
    logger.info("Ajustando preprocesador tabular...")
    tabular_preprocessor = TabularPreprocessor()
    X_tab_train = tabular_preprocessor.fit_transform(X_tab_train_df)
    X_tab_val = tabular_preprocessor.transform(X_tab_val_df)
    X_tab_test = tabular_preprocessor.transform(X_tab_test_df)

    # 5. Preprocesar rama de Texto
    logger.info("Limpiando y codificando texto con SentenceTransformer...")
    nlp_cleaner = NLPCleaner(remove_stopwords=True)
    text_clean_train = nlp_cleaner.clean_series(X_text_train_ser)
    text_clean_val = nlp_cleaner.clean_series(X_text_val_ser)
    text_clean_test = nlp_cleaner.clean_series(X_text_test_ser)

    text_encoder = TextEncoder()
    X_text_train = text_encoder.encode(text_clean_train)
    X_text_val = text_encoder.encode(text_clean_val)
    X_text_test = text_encoder.encode(text_clean_test)

    # 6. Construir y entrenar el modelo híbrido Keras
    tabular_dim = X_tab_train.shape[1]
    text_dim = X_text_train.shape[1]

    hybrid_model = HybridModel(tabular_input_dim=tabular_dim, text_input_dim=text_dim, num_classes=num_classes)
    logger.info(f"Arquitectura creada: Tabular Dim={tabular_dim}, Text Dim={text_dim}, Clases={num_classes}")

    hybrid_model.train(
        X_tabular_train=X_tab_train,
        X_text_train=X_text_train,
        y_train=y_train_cat,
        X_tabular_val=X_tab_val,
        X_text_val=X_text_val,
        y_val=y_val_cat,
        epochs=30,
        batch_size=32
    )

    # 7. Evaluación y Auditoría de Equidad en Test Set
    logger.info("Evaluando modelo en el conjunto de prueba (Test)...")
    y_probs_test = hybrid_model.predict(X_tab_test, X_text_test)
    y_preds_test = np.argmax(y_probs_test, axis=1)

    evaluator = ITACAModelEvaluator(max_fairness_delta=0.05, class_names=classes_list)
    audit_results = evaluator.evaluate_and_audit(
        y_true_indices=np.asarray(y_test_idx),
        y_pred_indices=np.asarray(y_preds_test),
        y_probs=y_probs_test,
        sectores=np.asarray(test_df["sector"])
    )

    # 8. Exportar Artefactos
    logger.info("Exportando artefactos serializados...")
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    hybrid_model.save(str(MODEL_KERAS_PATH))
    joblib.dump(tabular_preprocessor, TABULAR_PREPROCESSOR_PATH)
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)

    metadata = {
        "num_classes": num_classes,
        "classes": classes_list,
        "tabular_input_dim": tabular_dim,
        "text_input_dim": text_dim,
        "metrics": audit_results
    }
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    logger.info("🎉 ¡ENTRENAMIENTO Y ARTEFACTOS PROCESADOS EXITOSAMENTE!")

if __name__ == "__main__":
    main()
