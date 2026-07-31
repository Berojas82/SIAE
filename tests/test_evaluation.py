import pytest
import numpy as np
from src.evaluation.itaca_model_evaluator import ITACAModelEvaluator

def test_evaluator_metrics_and_fairness_audit():
    y_true = np.array([0, 1, 2, 3, 0, 1, 2, 3])
    y_pred = np.array([0, 1, 2, 3, 0, 1, 2, 2])
    y_probs = np.eye(4)[y_pred]
    sectores = np.array(["Tecnología", "Tecnología", "Manufactura", "Manufactura", "Tecnología", "Tecnología", "Manufactura", "Manufactura"])

    evaluator = ITACAModelEvaluator(max_fairness_delta=0.10)
    res = evaluator.evaluate_and_audit(y_true, y_pred, y_probs, sectores)

    assert "global_metrics" in res
    assert "fairness_audit" in res
    assert 0.0 <= res["global_metrics"]["accuracy"] <= 1.0
    assert 0.0 <= res["global_metrics"]["f1_macro"] <= 1.0
    assert "Tecnología" in res["fairness_audit"]["f1_by_sector"]
    assert "Manufactura" in res["fairness_audit"]["f1_by_sector"]
