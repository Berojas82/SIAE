import pytest
import pandas as pd
import numpy as np
from src.preprocessing.text.nlp_cleaner import NLPCleaner
from src.preprocessing.tabular.tabular_preprocessor import TabularPreprocessor

def test_nlp_cleaner():
    cleaner = NLPCleaner(remove_stopwords=True)
    raw_text = "¡Hola! El trabajo es MUY empírico y no hay documentación en 2026."
    cleaned = cleaner.clean_text(raw_text)

    assert isinstance(cleaned, str)
    assert "2026" not in cleaned
    assert "¡" not in cleaned
    assert "el" not in cleaned  # Stopword eliminada

def test_tabular_preprocessor():
    df_train = pd.DataFrame({
        "porcentaje_procesos_documentados": [0.05, 0.81, 0.27],
        "presupuesto_anual_tecnología": [3000000.0, 261000000.0, 47000000.0],
        "sector": ["Tecnología", "Tecnología", "Manufactura"],
        "tamano_empresa": ["Micro", "Grande", "Pequeña"]
    })

    df_test = pd.DataFrame({
        "porcentaje_procesos_documentados": [0.10, 0.50],
        "presupuesto_anual_tecnología": [10000000.0, 50000000.0],
        "sector": ["Servicios", "Tecnología"],  # Categoría nueva ("Servicios")
        "tamano_empresa": ["Micro", "Mediana"]
    })

    prep = TabularPreprocessor(
        num_cols=["porcentaje_procesos_documentados", "presupuesto_anual_tecnología"],
        cat_cols=["sector", "tamano_empresa"]
    )

    X_train = prep.fit_transform(df_train)
    X_test = prep.transform(df_test)

    assert X_train.shape[0] == 3
    assert X_test.shape[0] == 2
    assert X_train.shape[1] == X_test.shape[1]  # Mismo número de columnas post OneHotEncoding
