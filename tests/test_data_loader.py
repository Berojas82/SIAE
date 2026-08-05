import pytest
import pandas as pd
from pathlib import Path
from src.data_loader.data_loader import DataLoader
from src.data_loader.data_splitter import DataSplitter
from src.utils.constants import PROCESSED_DATA_PATH

def test_data_loader_split():
    if not PROCESSED_DATA_PATH.exists():
        pytest.skip("Dataset limpio no disponible en data/processed/cleaned_data.csv")

    loader = DataLoader()
    train_df, val_df, test_df = loader.split_data(save_splits=False)

    total_len = len(train_df) + len(val_df) + len(test_df)
    assert len(train_df) > 0
    assert len(val_df) > 0
    assert len(test_df) > 0

    # Proporción aproximada 80/10/10
    assert abs((len(train_df) / total_len) - 0.80) < 0.02
    assert abs((len(val_df) / total_len) - 0.10) < 0.02
    assert abs((len(test_df) / total_len) - 0.10) < 0.02

def test_data_splitter():
    df = pd.DataFrame({
        "porcentaje_procesos_documentados": [0.1, 0.5],
        "presupuesto_anual_tecnología": [1000.0, 50000.0],
        "sector": ["Tecnología", "Manufactura"],
        "tamano_empresa": ["Micro", "Grande"],
        "respuesta_texto": ["Texto 1", "Texto 2"],
        "nivel_madurez": ["Inicial", "Definido"]
    })

    splitter = DataSplitter()
    X_tab, X_text, y = splitter.split_features_and_target(df)

    assert X_tab.shape == (2, 3)
    assert len(X_text) == 2
    assert len(y) == 2
    assert "sector" in X_tab.columns
    assert "presupuesto_anual_tecnología" in X_tab.columns
