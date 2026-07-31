"""
Preprocesador tabular completo (escalado numérico + codificación categórica).
"""
import pandas as pd
import numpy as np
from typing import List

from .scaler import TabularScaler
from .encoder import CategoricalEncoder
from ...utils.constants import NUMERICAL_COLS, CATEGORICAL_COLS

class TabularPreprocessor:
    def __init__(self, num_cols: List[str] = NUMERICAL_COLS, cat_cols: List[str] = CATEGORICAL_COLS):
        self.num_cols = num_cols
        self.cat_cols = cat_cols
        self.scaler = TabularScaler(num_cols)
        self.encoder = CategoricalEncoder(cat_cols)
        self.is_fitted = False
        self.feature_names_ = []

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        num_arr = self.scaler.fit_transform(df)
        cat_arr = self.encoder.fit_transform(df)

        self.feature_names_ = self.num_cols + self.encoder.feature_names_
        self.is_fitted = True
        return np.hstack([num_arr, cat_arr])

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("El preprocesador tabular debe ser ajustado (fit) antes de transformar nuevos datos.")
        num_arr = self.scaler.transform(df)
        cat_arr = self.encoder.transform(df)
        return np.hstack([num_arr, cat_arr])
