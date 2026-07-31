"""
Escalado de variables numéricas utilizando StandardScaler.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import List, cast

class TabularScaler:
    def __init__(self, num_cols: List[str]):
        self.num_cols = num_cols
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        scaled = cast(np.ndarray, self.scaler.fit_transform(df[self.num_cols]))
        self.is_fitted = True
        return scaled

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("El escalador numérico debe ser ajustado (fit) antes de transformar.")
        return cast(np.ndarray, self.scaler.transform(df[self.num_cols]))
