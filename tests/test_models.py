import pytest
import numpy as np
from src.models.hybrid_model import HybridModel

def test_hybrid_model_architecture_and_forward_pass():
    tabular_dim = 6
    text_dim = 384
    num_classes = 4

    model = HybridModel(tabular_input_dim=tabular_dim, text_input_dim=text_dim, num_classes=num_classes)

    batch_size = 8
    dummy_tab = np.random.randn(batch_size, tabular_dim).astype(np.float32)
    dummy_text = np.random.randn(batch_size, text_dim).astype(np.float32)

    probs = model.predict(dummy_tab, dummy_text)

    assert probs.shape == (batch_size, num_classes)
    # Suma de probabilidades Softmax es 1.0 por cada muestra
    np.testing.assert_allclose(np.sum(probs, axis=1), 1.0, atol=1e-5)
