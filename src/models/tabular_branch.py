"""
Rama de red neuronal densa para procesar datos tabulares.
"""
from typing import Tuple, Any
import tensorflow as tf
from tensorflow.keras import layers  # type: ignore
from .config import TABULAR_DENSE_UNITS_1, TABULAR_DENSE_UNITS_2, DROPOUT_RATE

def build_tabular_branch(input_dim: int) -> Tuple[Any, Any]:
    input_layer = layers.Input(shape=(input_dim,), name="tabular_input")
    x = layers.Dense(TABULAR_DENSE_UNITS_1, activation="relu", name="tabular_dense_1")(input_layer)
    x = layers.BatchNormalization(name="tabular_bn_1")(x)
    x = layers.Dropout(DROPOUT_RATE, name="tabular_dropout_1")(x)
    x = layers.Dense(TABULAR_DENSE_UNITS_2, activation="relu", name="tabular_dense_2")(x)
    x = layers.BatchNormalization(name="tabular_bn_2")(x)
    return input_layer, x
