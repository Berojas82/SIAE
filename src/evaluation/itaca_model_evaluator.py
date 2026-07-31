"""
Evaluador de modelos e instalador de auditoría de equidad (Fairness) por sector económico.
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report

from ..utils.constants import CLASSES
from ..utils.logger import get_logger

logger = get_logger("ITACAModelEvaluator")

class ITACAModelEvaluator:
    """Evaluación multimodal y auditoría de equidad por sector."""

    def __init__(self, max_fairness_delta: float = 0.05, class_names: List[str] = CLASSES):
        self.max_fairness_delta = max_fairness_delta
        self.class_names = class_names

    def evaluate_and_audit(
        self,
        y_true_indices: np.ndarray | Any,
        y_pred_indices: np.ndarray | Any,
        y_probs: np.ndarray | Any,
        sectores: pd.Series | np.ndarray | Any
    ) -> Dict[str, Any]:
        acc = float(accuracy_score(y_true_indices, y_pred_indices))
        f1_macro = float(f1_score(y_true_indices, y_pred_indices, average="macro"))
        cm = confusion_matrix(y_true_indices, y_pred_indices).tolist()
        report = classification_report(y_true_indices, y_pred_indices, target_names=self.class_names, output_dict=True)

        # Auditoría de Equidad (Fairness) por Sector
        df_sec = pd.DataFrame({"y_true": y_true_indices, "y_pred": y_pred_indices, "sector": sectores})
        f1_by_sector = {}

        unique_sectors = np.unique(sectores)
        for sec in unique_sectors:
            sub = df_sec[df_sec["sector"] == sec]
            if len(sub) > 0:
                f1_sec = float(f1_score(sub["y_true"], sub["y_pred"], average="macro"))
                f1_by_sector[str(sec)] = round(f1_sec, 4)

        if f1_by_sector:
            max_delta = max(f1_by_sector.values()) - min(f1_by_sector.values())
        else:
            max_delta = 0.0

        fairness_pass = max_delta <= self.max_fairness_delta

        results = {
            "global_metrics": {
                "accuracy": round(acc, 4),
                "f1_macro": round(f1_macro, 4),
                "confusion_matrix": cm,
                "classification_report": report
            },
            "fairness_audit": {
                "f1_by_sector": f1_by_sector,
                "max_delta": round(max_delta, 4),
                "fairness_passed": fairness_pass,
                "tolerance_threshold": self.max_fairness_delta
            }
        }

        self._print_audit_log(results)
        return results

    def _print_audit_log(self, res: Dict[str, Any]):
        g, f = res["global_metrics"], res["fairness_audit"]
        logger.info("=== RESULTADOS DE EVALUACIÓN Y AUDITORÍA DE EQUIDAD ===")
        logger.info(f"Accuracy Global     : {g['accuracy']:.4f}")
        logger.info(f"F1-Score Macro      : {g['f1_macro']:.4f}")
        logger.info("--- AUDITORÍA DE EQUIDAD POR SECTOR ---")
        for sec, score in f["f1_by_sector"].items():
            logger.info(f" Sector {sec:12s} | F1-Macro: {score:.4f}")
        logger.info(f"Disparidad Máxima ΔF1: {f['max_delta']*100:.2f}% (Límite: {f['tolerance_threshold']*100:.1f}%)")
        logger.info(f"Estado de Equidad    : {'[APROBADO]' if f['fairness_passed'] else '[RECHAZADO]'}")
        logger.info("===================================================\n")
