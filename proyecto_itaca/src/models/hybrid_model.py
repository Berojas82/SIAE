import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, log_loss

class ITACAHybridClassifier:
    """Modelo híbrido para la integración de vectores tabulares y de texto."""

    def __init__(self, C=0.5, max_iter=200, random_state=42):
        self.C = C
        self.max_iter = max_iter
        self.random_state = random_state
        self.model = LogisticRegression(C=self.C, max_iter=self.max_iter, random_state=self.random_state)
        self.is_trained = False

    def _combine_features(self, X_tabular: np.ndarray, X_text: np.ndarray) -> np.ndarray:
        if X_tabular.shape[0] != X_text.shape[0]:
            raise ValueError(f"Inconsistencia en filas: Tabular ({X_tabular.shape[0]}) vs Texto ({X_text.shape[0]})")
        return np.hstack([X_tabular, X_text])

    def fit(self, X_tabular: np.ndarray, X_text: np.ndarray, y: np.ndarray):
        X_combined = self._combine_features(X_tabular, X_text)
        self.model.fit(X_combined, y)
        self.is_trained = True
        return self

    def predict(self, X_tabular: np.ndarray, X_text: np.ndarray) -> np.ndarray:
        X_combined = self._combine_features(X_tabular, X_text)
        return self.model.predict(X_combined)

    def predict_proba(self, X_tabular: np.ndarray, X_text: np.ndarray) -> np.ndarray:
        X_combined = self._combine_features(X_tabular, X_text)
        return self.model.predict_proba(X_combined)

    def evaluate(self, X_tabular: np.ndarray, X_text: np.ndarray, y_true: np.ndarray) -> dict:
        y_pred = self.predict(X_tabular, X_text)
        y_prob = self.predict_proba(X_tabular, X_text)[:, 1]

        auc = roc_auc_score(y_true, y_prob)
        loss = log_loss(y_true, y_prob)

        print("\n=== EXECUTION LOG: HYBRID MODEL EVALUATION ===")
        print(f"Muestras en test/val : {len(y_true)}")
        print(f"ROC-AUC score        : {auc:.4f}")
        print(f"Log Loss             : {loss:.4f}\n")
        print(classification_report(y_true, y_pred, target_names=['Clase 0 (Normal)', 'Clase 1 (Alerta)'], digits=4))

        return {"roc_auc": auc, "log_loss": loss}


if __name__ == "__main__":
    np.random.seed(42)

    # Simulación de matrices de salida provenientes de Paso 2 y Paso 3
    X_tab_train = np.random.randn(700, 5)
    X_text_train = np.random.randn(700, 16)
    noise_train = np.random.randn(700) * 1.2
    y_train = ((0.8 * X_tab_train[:, 0] - 0.5 * X_tab_train[:, 1] + 1.1 * X_text_train[:, 2] + noise_train) > 0).astype(int)

    X_tab_val = np.random.randn(150, 5)
    X_text_val = np.random.randn(150, 16)
    noise_val = np.random.randn(150) * 1.2
    y_val = ((0.8 * X_tab_val[:, 0] - 0.5 * X_tab_val[:, 1] + 1.1 * X_text_val[:, 2] + noise_val) > 0).astype(int)

    # Pipeline
    clf = ITACAHybridClassifier(C=0.5)
    clf.fit(X_tab_train, X_text_train, y_train)
    metrics = clf.evaluate(X_tab_val, X_text_val, y_val)
