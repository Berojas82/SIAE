"""
División de variables tabulares, texto libre y etiquetas.
"""
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from ..utils.constants import NUMERICAL_COLS, CATEGORICAL_COLS, TEXT_COL, TARGET_COL

class DataSplitter:
    """Separa el DataFrame en rama tabular, rama de texto y etiqueta target."""

    def __init__(
        self,
        numerical_cols=NUMERICAL_COLS,
        categorical_cols=CATEGORICAL_COLS,
        text_col=TEXT_COL,
        target_col=TARGET_COL
    ):
        self.numerical_cols = numerical_cols
        self.categorical_cols = categorical_cols
        self.tabular_cols = numerical_cols + categorical_cols
        self.text_col = text_col
        self.target_col = target_col

    def split_features_and_target(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, Optional[pd.Series]]:
        """
        Retorna:
        - X_tabular: DataFrame con variables numéricas y categóricas
        - X_text: Series con las respuestas de texto
        - y: Series con la variable objetivo
        """
        X_tabular = df[self.tabular_cols].copy()
        X_text = df[self.text_col].copy() if self.text_col in df.columns else pd.Series([""] * len(df))
        y = df[self.target_col].copy() if self.target_col in df.columns else None

        return X_tabular, X_text, y
