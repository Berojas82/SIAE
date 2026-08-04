"""
Modelo Híbrido Multimodal (Texto + Tabular) en TensorFlow / Keras (Functional API).
"""
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, regularizers  # type: ignore
from typing import Tuple, Dict, Any, Optional

from .text_branch import build_text_branch
from .tabular_branch import build_tabular_branch
from .config import (
    TEXT_EMBEDDING_DIM,
    NUM_CLASSES,
    COMBINED_DENSE_UNITS,
    DROPOUT_RATE,
    LEARNING_RATE,
    BATCH_SIZE,
    EPOCHS
)
from ..utils.logger import get_logger

logger = get_logger("HybridModel")

class HybridModel:
    """Modelo híbrido multimodal en TensorFlow / Keras Functional API."""

    def __init__(self, tabular_input_dim: int, text_input_dim: int = TEXT_EMBEDDING_DIM, num_classes: int = NUM_CLASSES):
        self.tabular_input_dim = tabular_input_dim
        self.text_input_dim = text_input_dim
        self.num_classes = num_classes
        self.model = self._build_model()

    def _build_model(self) -> Any:
        # Rama 1: Texto
        text_in, text_out = build_text_branch(self.text_input_dim)

        # Rama 2: Tabular
        tab_in, tab_out = build_tabular_branch(self.tabular_input_dim)

        # Concatenación
        combined = layers.Concatenate(name="fusion_concatenate")([text_out, tab_out])
        x = layers.Dense(COMBINED_DENSE_UNITS, activation="relu", kernel_regularizer=regularizers.l2(1e-4), name="fusion_dense")(combined)
        x = layers.Dropout(DROPOUT_RATE, name="fusion_dropout")(x)

        # Capa de salida (4 clases Softmax: nivel_madurez)
        outputs = layers.Dense(self.num_classes, activation="softmax", name="classification_output")(x)

        model = models.Model(inputs=[tab_in, text_in], outputs=outputs, name="ITACA_Hybrid_Model")

        optimizer = tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE)
        model.compile(
            optimizer=optimizer,
            loss="categorical_crossentropy",
            metrics=["accuracy"]
        )
        return model

    def train(
        self,
        X_tabular_train: np.ndarray,
        X_text_train: np.ndarray,
        y_train: np.ndarray,
        X_tabular_val: Optional[np.ndarray] = None,
        X_text_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        epochs: int = EPOCHS,
        batch_size: int = BATCH_SIZE
    ) -> Any:
        logger.info(f"Entrenando HybridModel por {epochs} épocas (Batch size: {batch_size})...")

        validation_data: Any = None
        if X_tabular_val is not None and X_text_val is not None and y_val is not None:
            validation_data = ({"tabular_input": X_tabular_val, "text_input": X_text_val}, y_val)

        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor="val_loss" if validation_data else "loss",
            patience=5,
            restore_best_weights=True
        )

        history = self.model.fit(
            x={"tabular_input": X_tabular_train, "text_input": X_text_train},
            y=y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping],
            verbose=1
        )
        return history

    def predict(self, X_tabular: np.ndarray, X_text: np.ndarray) -> np.ndarray:
        return self.model.predict([X_tabular, X_text], verbose=0)

    def predict_classes(self, X_tabular: np.ndarray, X_text: np.ndarray) -> np.ndarray:
        probs = self.predict(X_tabular, X_text)
        return np.argmax(probs, axis=1)

    def save(self, filepath: str):
        self.model.save(filepath)
        logger.info(f"Modelo híbrido guardado en: {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "HybridModel":
        logger.info(f"Cargando modelo híbrido desde: {filepath}")
        keras_model = models.load_model(filepath)
        instance = cls.__new__(cls)
        instance.model = keras_model
        return instance

