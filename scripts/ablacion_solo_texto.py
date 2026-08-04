import sys
from typing import Any
import numpy as np
import pandas as pd
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sklearn.preprocessing import LabelEncoder
from tensorflow.keras import layers, models, regularizers  # type: ignore
from tensorflow.keras.utils import to_categorical  # type: ignore

from src.preprocessing.text.nlp_cleaner import NLPCleaner
from src.preprocessing.text.text_encoder import TextEncoder
from src.evaluation.itaca_model_evaluator import ITACAModelEvaluator

def main():
    train_path = repo_root / "data" / "splits" / "train.csv"
    val_path = repo_root / "data" / "splits" / "val.csv"
    test_path = repo_root / "data" / "splits" / "test.csv"

    if not train_path.exists() or not test_path.exists():
        from src.data_loader.data_loader import DataLoader
        loader = DataLoader()
        loader.split_data(save_splits=True)

    train = pd.read_csv(train_path)
    val = pd.read_csv(val_path)
    test = pd.read_csv(test_path)

    # 1. Etiquetas
    le = LabelEncoder()
    y_tr = le.fit_transform(train["nivel_madurez"])
    y_va = le.transform(val["nivel_madurez"])
    y_te = le.transform(test["nivel_madurez"])
    clases = list(le.classes_)
    n_cls = len(clases)

    # 2. Solo la rama de texto (se descarta todo lo tabular)
    limpiador = NLPCleaner(remove_stopwords=True)
    codificador = TextEncoder()
    
    print("Codificando texto con SentenceTransformer...")
    X_tr = codificador.encode(limpiador.clean_series(train["respuesta_texto"]))
    X_va = codificador.encode(limpiador.clean_series(val["respuesta_texto"]))
    X_te = codificador.encode(limpiador.clean_series(test["respuesta_texto"]))

    # 3. Red densa equivalente a la rama de texto del modelo híbrido
    entrada = layers.Input(shape=(X_tr.shape[1],), name="text_input")
    x = layers.Dense(128, activation="relu", kernel_regularizer=regularizers.l2(1e-4))(entrada)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(64, activation="relu", kernel_regularizer=regularizers.l2(1e-4))(x)
    x = layers.BatchNormalization()(x)
    salida = layers.Dense(n_cls, activation="softmax")(x)

    modelo = models.Model(inputs=entrada, outputs=salida, name="ITACA_Solo_Texto")
    modelo.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    
    y_tr_cat = np.asarray(to_categorical(y_tr, n_cls))
    y_va_cat = np.asarray(to_categorical(y_va, n_cls))

    val_data: Any = (X_va, y_va_cat)

    print("Entrenando modelo de ablación solo-texto...")
    modelo.fit(
        X_tr, y_tr_cat,
        validation_data=val_data,
        epochs=30,
        batch_size=32,
        verbose=1
    )

    # 4. Evaluar con el auditor del proyecto
    probs = modelo.predict(X_te, verbose=0)
    preds = np.argmax(probs, axis=1)

    auditor = ITACAModelEvaluator(max_fairness_delta=0.05, class_names=clases)
    resultados = auditor.evaluate_and_audit(
        y_true_indices=y_te,
        y_pred_indices=preds,
        y_probs=probs,
        sectores=np.asarray(test["sector"])
    )

    print("\n" + "="*60)
    print("=== MÉTRICA HONESTA DE ABLACIÓN (SOLO TEXTO) ===")
    print("="*60)
    print("Accuracy:", resultados["global_metrics"]["accuracy"])
    print("F1-macro:", resultados["global_metrics"]["f1_macro"])
    print("Equidad :", resultados["fairness_audit"])

if __name__ == "__main__":
    main()
