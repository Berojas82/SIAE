import sys
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, confusion_matrix

# Inclusión del directorio raíz en el path para resolver importaciones relativas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.models.hybrid_model import ITACAHybridClassifier


class ITACAModelEvaluator:
    """Módulo de evaluación multimodal, auditoría de equidad y exportación de artefactos."""

    def __init__(self, model, max_fairness_delta=0.05):
        self.model = model
        self.max_fairness_delta = max_fairness_delta

    def evaluate_and_audit(self, X_tab_test: np.ndarray, X_text_test: np.ndarray, y_test: np.ndarray, sectores: np.ndarray) -> dict:
        y_pred = self.model.predict(X_tab_test, X_text_test)
        y_prob = self.model.predict_proba(X_tab_test, X_text_test)[:, 1]

        # 1. Métricas Globales
        acc = float(accuracy_score(y_test, y_pred))
        f1_macro = float(f1_score(y_test, y_pred, average='macro'))
        auc = float(roc_auc_score(y_test, y_prob))
        cm = confusion_matrix(y_test, y_pred).tolist()

        # 2. Auditoría de Equidad (Fairness) por Sector
        df_sec = pd.DataFrame({'y_true': y_test, 'y_pred': y_pred, 'sector': sectores})
        f1_by_sector = {}

        for sec in np.unique(sectores):
            sub = df_sec[df_sec['sector'] == sec]
            f1_sec = float(f1_score(sub['y_true'], sub['y_pred'], average='macro'))
            f1_by_sector[sec] = round(f1_sec, 4)

        max_delta = max(f1_by_sector.values()) - min(f1_by_sector.values())
        fairness_pass = max_delta <= self.max_fairness_delta

        results = {
            "global_metrics": {
                "accuracy": round(acc, 4),
                "f1_macro": round(f1_macro, 4),
                "roc_auc": round(auc, 4),
                "confusion_matrix": cm
            },
            "fairness_audit": {
                "f1_by_sector": f1_by_sector,
                "max_delta": round(max_delta, 4),
                "fairness_passed": fairness_pass
            }
        }

        self._print_log(results)
        return results

    def _print_log(self, res: dict):
        g, f = res["global_metrics"], res["fairness_audit"]
        print("\n=== EXECUTION LOG: EVALUATION & FAIRNESS AUDIT ===")
        print(f"Accuracy Global     : {g['accuracy']:.4f}")
        print(f"F1-Score Macro      : {g['f1_macro']:.4f}")
        print(f"ROC-AUC             : {g['roc_auc']:.4f}")
        print(f"\nMatriz de Confusión :\n TN: {g['confusion_matrix'][0][0]} | FP: {g['confusion_matrix'][0][1]}")
        print(f" FN: {g['confusion_matrix'][1][0]} | TP: {g['confusion_matrix'][1][1]}")
        print("\n--- AUDITORÍA DE EQUIDAD POR SECTOR ---")
        for sec, score in f['f1_by_sector'].items():
            print(f" Sector {sec:12s} | F1-Macro: {score:.4f}")
        print(f"\nDisparidad Máxima ΔF1: {f['max_delta']*100:.2f}% (Límite: {self.max_fairness_delta*100:.1f}%)")
        print(f"Estado de Equidad    : {'[APROBADO]' if f['fairness_passed'] else '[RECHAZADO]'}")
        print("===================================================\n")

    def export_artifacts(self, model_path="model_itaca.joblib", metrics_path="metrics_report.json", metrics_data=None):
        joblib.dump(self.model, model_path)
        if metrics_data:
            with open(metrics_path, "w", encoding="utf-8") as f:
                json.dump(metrics_data, f, indent=4, ensure_ascii=False)
        print(f"📦 Artefactos exportados: '{model_path}' y '{metrics_path}'")


if __name__ == "__main__":
    np.random.seed(42)
    n_test = 150

    # Datos sintéticos para validación de entrada
    X_tab_test = np.random.randn(n_test, 5)
    X_text_test = np.random.randn(n_test, 16)
    sectores = np.random.choice(['Servicios', 'Manufactura', 'Comercio'], size=n_test, p=[0.4, 0.35, 0.25])
    y_test = np.random.choice([0, 1], size=n_test, p=[0.55, 0.45])

    # Ajuste del modelo importado
    model = ITACAHybridClassifier(C=0.5).fit(X_tab_test, X_text_test, y_test)

    # Evaluación y exportación
    evaluator = ITACAModelEvaluator(model, max_fairness_delta=0.05)
    metrics = evaluator.evaluate_and_audit(X_tab_test, X_text_test, y_test, sectores)
    evaluator.export_artifacts(metrics_data=metrics)
