"""
Codificador de texto utilizando SentenceTransformers para embeddings multilingües (384-d).
"""
import numpy as np
import pandas as pd
from typing import List, Union, cast
from sentence_transformers import SentenceTransformer

from ...utils.constants import TRANSFORMER_MODEL_NAME
from ...utils.logger import get_logger

logger = get_logger("TextEncoder")

class TextEncoder:
    """Transforma secuencias de texto libre en embeddings vectoriales densos de 384 dimensiones."""

    def __init__(self, model_name: str = TRANSFORMER_MODEL_NAME):
        self.model_name = model_name
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Cargando modelo SentenceTransformer: '{self.model_name}'...")
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: Union[List[str], pd.Series, np.ndarray], show_progress_bar: bool = False) -> np.ndarray:
        if isinstance(texts, (pd.Series, np.ndarray)):
            text_list: List[str] = [str(x) for x in texts.tolist()]
        elif isinstance(texts, list):
            text_list = [str(x) for x in texts]
        else:
            text_list = [str(texts)]

        logger.info(f"Generando embeddings para {len(text_list)} elementos de texto...")
        embeddings = cast(np.ndarray, self.model.encode(text_list, show_progress_bar=show_progress_bar, convert_to_numpy=True))
        return embeddings
