import sys
import numpy as np
import pandas as pd
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sklearn.preprocessing import LabelEncoder
from tensorflow.keras import layers, models
from tensorflow.keras.utils import to_categorical

from src.preprocessing.text.nlp_cleaner import NLPCleaner
from src.preprocessing.text.text_encoder import TextEncoder
from src.evaluation.itaca_model_evaluator import ITACAModelEvaluator

train = pd.read_csv(repo_root / "data" / "splits" / "train.csv")
val = pd.read_csv(repo_root / "data" / "splits" / "val.csv")
test = pd.read_csv(repo_root / "data" / "splits" / "test.csv")

# --- 1. Etiquetas ---
le = LabelEncoder()
y_tr = le.fit_transform(train["nivel_madurez"])
y_va = le.transform(val["nivel_madurez"])
y_te = le.transform(test["nivel_madurez"])
clases = [str(c) for c in le.classes_]
n_cls = len(clases)

# --- 2. Solo la rama de texto (se descarta TODO lo tabular) ---
limpiador = NLPCleaner(remove_stopwords=True)
codificador = TextEncoder()
X_tr = codificador.encode(limpiador.clean_series(train["respuesta_texto"]))
X_va = codificador.encode(limpiador.clean_series(val["respuesta_texto"]))
X_te = codificador.encode(limpiador.clean_series(test["respuesta_texto"]))

# --- 3. Red densa equivalente a la rama de texto del modelo hibrido ---
entrada = layers.Input(shape=(X_tr.shape[1],), name="text_input")
x = layers.Dense(128, activation="relu")(entrada)
x = layers.BatchNormalization()(x)
x = layers.Dropout(0.3)(x)
x = layers.Dense(64, activation="relu")(x)
salida = layers.Dense(n_cls, activation="softmax")(x)

modelo = models.Model(entrada, salida, name="ITACA_Solo_Texto")
modelo.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
modelo.fit(X_tr, to_categorical(y_tr, n_cls),
           validation_data=(X_va, to_categorical(y_va, n_cls)),
           epochs=30, batch_size=32, verbose=1)

# --- 4. Evaluar con el MISMO auditor del proyecto ---
probs = modelo.predict(X_te, verbose=0)
preds = np.argmax(probs, axis=1)

auditor = ITACAModelEvaluator(max_fairness_delta=0.05, class_names=clases)
resultados = auditor.evaluate_and_audit(
    y_true_indices=y_te, y_pred_indices=preds,
    y_probs=probs, sectores=np.asarray(test["sector"]))

print("\n=== METRICA HONESTA (solo texto, sin la columna con fuga) ===")
print("Accuracy:", resultados["global_metrics"]["accuracy"])
print("F1-macro:", resultados["global_metrics"]["f1_macro"])
print("Equidad :", resultados["fairness_audit"])
