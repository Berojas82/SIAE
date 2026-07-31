"""
Módulo de modelos de aprendizaje profundo para ITACA Project.
"""
from .hybrid_model import HybridModel
from .config import TEXT_EMBEDDING_DIM, NUM_CLASSES

__all__ = ["HybridModel", "TEXT_EMBEDDING_DIM", "NUM_CLASSES"]
