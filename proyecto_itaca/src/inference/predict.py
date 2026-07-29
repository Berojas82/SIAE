import sys
import os
import json
import joblib
import numpy as np
import pandas as pd

# Inclusión del directorio raíz para resolución de dependencias
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

class ITACAPredictor:
    """Motor de inferencia en producción para la arquitectura ITACA."""

    def __init__(self, model_path="model_itaca.joblib", metrics_path="metrics_report.json"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ No se encontró el modelo exportado en: {model_path}")

        self.model = joblib.load(model_path)

        # Carga opcional de reporte para validación de límites
        self.metrics_report = None
        if os.path.exists(metrics_path):
            with open(metrics_path, "r", encoding="utf-8") as f:
                self.metrics_report = json.load(f)

    def predict_single(self, X_tabular_sample: np.ndarray, X_text_sample: np.ndarray) -> dict:
        """Procesa una muestra individual de características y genera la etiqueta y probabilidad."""

        # Validación de dimensiones
        if X_tabular_sample.ndim == 1:
            X_tabular_sample = X_tabular_sample.reshape(1, -1)
        if X_text_sample.ndim == 1:
            X_text_sample = X_text_sample.reshape(1, -1)

        # Generación de score de probabilidad P(Y=1|X)
        prob_alerta = float(self.model.predict_proba(X_tabular_sample, X_text_sample)[0, 1])
        pred_label = int(prob_alerta >= 0.5)

        return {
            "status": "SUCCESS",
            "prediction": pred_label,
            "label": "Alerta" if pred_label == 1 else "Normal",
            "confidence_score": round(prob_alerta, 4),
            "threshold_used": 0.5
        }

if __name__ == "__main__":
    # Simulación de petición de inferencia en caliente (Payload de entrada)
    np.random.seed(99)
    sample_tab = np.random.randn(1, 5)     # Vector tabular preprocesado (d=5)
    sample_text = np.random.randn(1, 16)   # Embedding de texto (d=16)

    predictor = ITACAPredictor(model_path="model_itaca.joblib")
    response = predictor.predict_single(sample_tab, sample_text)

    print("\n=== EXECUTION LOG: INFERENCE ENGINE ===")
    print(json.dumps(response, indent=4, ensure_ascii=False))
    print("=======================================\n")
