import re
import pandas as pd

class NLPCleaner:
    """
    Clase para el preprocesamiento y limpieza de texto en español
    diseñada para el proyecto de autodiagnóstico de ITACA.
    """
    def __init__(self, remove_stopwords=True):
        self.remove_stopwords = remove_stopwords
        self.stopwords = self._get_spanish_stopwords()

    def _get_spanish_stopwords(self):
        """
        Lista de stopwords comunes en español para eliminar palabras vacías.
        """
        return set([
            'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para',
            'con', 'no', 'una', 'su', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o',
            'este', 'sí', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre', 'también',
            'me', 'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 'todos',
            'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto',
            'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'otro', 'otras', 'otra', 'él', 'tanto',
            'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos', 'cual', 'poco', 'ella', 'estar',
            'estas', 'algunas', 'algo', 'nosotros', 'mi', 'mis', 'tu', 'tus', 'nuestros', 'nuestras'
        ])

    def clean_text(self, text: str) -> str:
        """
        Limpia una cadena de texto individual:
        1. Convierte a minúsculas.
        2. Conserva solo caracteres alfabéticos en español (incluyendo acentos y ñ).
        3. Tokeniza y elimina stopwords.
        """
        if not isinstance(text, str):
            return ""

        # 1. Convertir a minúsculas
        text = text.lower()

        # 2. Conservar solo letras en español y espacios
        text = re.sub(r'[^a-záéíóúñ\s]', '', text)

        # 3. Tokenizar por espacios
        words = text.split()

        # 4. Filtrar stopwords y palabras de una sola letra
        if self.remove_stopwords:
            words = [w for w in words if w not in self.stopwords and len(w) > 1]

        # 5. Unir palabras limpias
        return " ".join(words)

    def clean_series(self, series: pd.Series) -> pd.Series:
        """
        Aplica la limpieza a toda una columna (Pandas Series).
        """
        return series.apply(self.clean_text)

if __name__ == "__main__":
    cleaner = NLPCleaner()
    sample = "¡Hola! Nuestros procesos son manuales y dependemos de Excel al 100%."
    print("Texto original:", sample)
    print("Texto limpio:  ", cleaner.clean_text(sample))
# 1. Cargar conjuntos de datos
train_df, val_df, test_df = load_and_split_data()

# 2. Instanciar el limpiador NLP
cleaner = NLPCleaner(remove_stopwords=True)

# 3. Aplicar la limpieza a la columna de texto de entrenamiento
train_df['texto_limpio'] = cleaner.clean_series(train_df['texto_respuestas'])

# 4. Mostrar comparativa entre el texto original y el texto limpio
print("\n---  PRUEBA DE VALIDACIÓN DE LIMPIEZA NLP ---")
comparativa = train_df[['texto_respuestas', 'texto_limpio']].drop_duplicates().head(4)

for idx, row in comparativa.iterrows():
    print(f"\n[Original]: {row['texto_respuestas']}")
    print(f"[Limpio]  : {row['texto_limpio']}")
