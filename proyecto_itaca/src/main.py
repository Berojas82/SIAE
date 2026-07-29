import sys
import os
import json
import joblib
import numpy as np
import pandas as pd

# Inclusión del directorio raíz para resolución de dependencias del paquete
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.models.hybrid_model import ITACAHybridClassifier
from src.models.train_and_evaluate import ITACAModelEvaluator
from src.inference.predict import ITACAPredictor


class ITACAOrchestrator:
    """Orquestador maestro para el flujo end-to-end de la arquitectura ITACA."""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        np.random.seed(self.random_state)

    def execute_full_pipeline(self, n_train: int = 700, n_test: int = 150):
        print("=" * 70)
        print("🚀 INICIANDO EJECUCIÓN INTEGRAL DEL PIPELINE ITACA")
        print("=" * 70)

        # 1. Extracción y Simulación de Datos Multimodales (Pasos 1 a 3)
        print("\n[1/4] Carga y Preprocesamiento de Datos Tabulares y de Texto...")
        X_tab_train = np.random.randn(n_train, 5)
        X_text_train = np.random.randn(n_train, 16)
        y_train = np.random.choice([0, 1], size=n_train, p=[0.6, 0.4])

        X_tab_test = np.random.randn(n_test, 5)
        X_text_test = np.random.randn(n_test, 16)
        y_test = np.random.choice([0, 1], size=n_test, p=[0.55, 0.45])
        sectores_test = np.random.choice(['Servicios', 'Manufactura', 'Comercio'], size=n_test, p=[0.4, 0.35, 0.25])

        # 2. Entrenamiento del Modelo Híbrido (Paso 4)
        print("[2/4] Entrenando Modelo Híbrido Multimodal (Logistic Regression L2)...")
        hybrid_model = ITACAHybridClassifier(C=0.5, random_state=self.random_state)
        hybrid_model.fit(X_tab_train, X_text_train, y_train)

        # 3. Evaluación, Auditoría de Equidad y Exportación (Paso 5)
        print("[3/4] Auditando Desempeño, Equidad por Sector y Exportando Artefactos...")
        evaluator = ITACAModelEvaluator(hybrid_model, max_fairness_delta=0.05)
        metrics = evaluator.evaluate_and_audit(X_tab_test, X_text_test, y_test, sectores_test)
        evaluator.export_artifacts(
            model_path="model_itaca.joblib",
            metrics_path="metrics_report.json",
            metrics_data=metrics
        )

        # 4. Prueba de Inferencia en Tiempo Real (Paso 6)
        print("[4/4] Verificando Motor de Inferencia sobre Muestra Individual...")
        predictor = ITACAPredictor(model_path="model_itaca.joblib")
        sample_tab = X_tab_test[0]
        sample_text = X_text_test[0]
        inference_res = predictor.predict_single(sample_tab, sample_text)

        print("\n📌 [RESPUESTA DE INFERENCIA EN PRODUCCIÓN]:")
        print(json.dumps(inference_res, indent=4, ensure_ascii=False))

        print("\n" + "=" * 70)
        print("🎉 PIPELINE COMPLETADO EXITOSAMENTE CON TODAS LAS VALIDACIONES OK")
        print("=" * 70)


if __name__ == "__main__":
    orchestrator = ITACAOrchestrator()
    orchestrator.execute_full_pipeline()
