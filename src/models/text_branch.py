"""
Rama de red neuronal densa para procesar embeddings de texto (384-d).
"""
from typing import Tuple, Any
import tensorflow as tf
from tensorflow.keras import layers, regularizers  # type: ignore
from .config import TEXT_EMBEDDING_DIM, TEXT_DENSE_UNITS_1, TEXT_DENSE_UNITS_2, DROPOUT_RATE

def build_text_branch(input_dim: int = TEXT_EMBEDDING_DIM) -> Tuple[Any, Any]:
    input_layer = layers.Input(shape=(input_dim,), name="text_input")
    x = layers.Dense(TEXT_DENSE_UNITS_1, activation="relu", kernel_regularizer=regularizers.l2(1e-4), name="text_dense_1")(input_layer)
    x = layers.BatchNormalization(name="text_bn_1")(x)
    x = layers.Dropout(DROPOUT_RATE, name="text_dropout_1")(x)
    x = layers.Dense(TEXT_DENSE_UNITS_2, activation="relu", kernel_regularizer=regularizers.l2(1e-4), name="text_dense_2")(x)
    x = layers.BatchNormalization(name="text_bn_2")(x)
    return input_layer, x
