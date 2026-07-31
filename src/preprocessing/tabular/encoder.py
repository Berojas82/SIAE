"""
Codificación One-Hot para variables categóricas.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from typing import List, cast

class CategoricalEncoder:
    def __init__(self, cat_cols: List[str]):
        self.cat_cols = cat_cols
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        self.is_fitted = False
        self.feature_names_ = []

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        encoded = cast(np.ndarray, self.encoder.fit_transform(df[self.cat_cols]))
        self.feature_names_ = list(self.encoder.get_feature_names_out(self.cat_cols))
        self.is_fitted = True
        return encoded

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("El codificador categórico debe ser ajustado (fit) antes de transformar.")
        return cast(np.ndarray, self.encoder.transform(df[self.cat_cols]))

