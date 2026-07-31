"""
Limpieza de texto en español para el proyecto ITACA.
"""
import re
import pandas as pd

class NLPCleaner:
    """Clase para la limpieza y normalización de texto libre en español."""

    def __init__(self, remove_stopwords: bool = True):
        self.remove_stopwords = remove_stopwords
        self.stopwords = self._get_spanish_stopwords()

    def _get_spanish_stopwords(self) -> set:
        return {
            'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para',
            'con', 'no', 'una', 'su', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o',
            'este', 'sí', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre', 'también',
            'me', 'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 'todos',
            'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto',
            'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'otro', 'otras', 'otra', 'él', 'tanto',
            'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos', 'cual', 'poco', 'ella', 'estar',
            'estas', 'algunas', 'algo', 'nosotros', 'mi', 'mis', 'tu', 'tus', 'nuestros', 'nuestras'
        }

    def clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""

        text = text.lower()
        text = re.sub(r'[^a-záéíóúñ\s]', '', text)
        words = text.split()

        if self.remove_stopwords:
            words = [w for w in words if w not in self.stopwords and len(w) > 1]

        return " ".join(words)

    def clean_series(self, series: pd.Series) -> pd.Series:
        return series.apply(self.clean_text)
