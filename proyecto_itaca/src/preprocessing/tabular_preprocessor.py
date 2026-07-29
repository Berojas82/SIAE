import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ==========================================
# 1. IMPLEMENTACIÓN DEL MÓDULO (tabular_preprocessor.py)
# ==========================================

class TabularPreprocessor:
    """Módulo de preprocesamiento tabular para la arquitectura ITACA.

    Aplica StandardScaler a columnas numéricas y OneHotEncoder a categóricas,
    garantizando cero filtración de datos entre sets.
    """
    def __init__(self, num_cols, cat_cols):
        self.num_cols = num_cols
        self.cat_cols = cat_cols
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), self.num_cols),
                ('cat', OneHotEncoder(sparse_output=False, handle_unknown='ignore'), self.cat_cols)
            ]
        )
        self.is_fitted = False
        self.feature_names_ = []

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajusta el escalador/codificador con datos de train y retorna el DataFrame transformado."""
        transformed_array = self.preprocessor.fit_transform(df)

        # Extracción dinámica de nombres de columnas post-transformación
        cat_encoder = self.preprocessor.named_transformers_['cat']
        encoded_cat_cols = list(cat_encoder.get_feature_names_out(self.cat_cols))
        self.feature_names_ = self.num_cols + encoded_cat_cols
        self.is_fitted = True

        return pd.DataFrame(transformed_array, columns=self.feature_names_, index=df.index)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica las transformaciones aprendidas en train sobre val o test."""
        if not self.is_fitted:
            raise RuntimeError("❌ El preprocesador debe ser ajustado (fit) antes de transformar nuevos datos.")

        transformed_array = self.preprocessor.transform(df)
        return pd.DataFrame(transformed_array, columns=self.feature_names_, index=df.index)

# ==========================================
# 2. BATERÍA DE VALIDACIÓN DEL PASO 3
# ==========================================

def ejecutar_validacion_paso_3():
    print("=" * 70)
    print("🧪 INICIANDO VALIDACIÓN DEL PASO 3: PREPROCESAMIENTO TABULAR")
    print("=" * 70)

    # 1. Generación de datos de prueba simulados
    np.random.seed(42)
    train_data = pd.DataFrame({
        'edad': [25, 40, 35, 50, 28, 60, 22, 45, 31, 55],
        'score_evaluacion': [85.5, 62.0, 78.0, 90.5, 71.0, 55.0, 88.0, 68.5, 95.0, 60.0],
        'nivel_experiencia': ['Principiante', 'Avanzado', 'Intermedio', 'Avanzado', 'Principiante',
                              'Intermedio', 'Principiante', 'Intermedio', 'Avanzado', 'Principiante']
    })

    val_data = pd.DataFrame({
        'edad': [30, 48],
        'score_evaluacion': [80.0, 65.0],
        'nivel_experiencia': ['Intermedio', 'Categoria_Nueva_Rara']  # Categoría no vista en train
    })

    num_cols = ['edad', 'score_evaluacion']
    cat_cols = ['nivel_experiencia']

    print("\n📌 [DATOS ENTRADA TRAIN - MUESTRA 3 FILAS]:")
    print(train_data.head(3).to_string(index=False))

    # 2. Inicialización y Fit-Transform en Train
    preprocessor = TabularPreprocessor(num_cols=num_cols, cat_cols=cat_cols)
    df_train_proc = preprocessor.fit_transform(train_data)

    print("\n✅ [RESULTADO TRANSFORMACIÓN TRAIN]:")
    print(df_train_proc.head(3).round(4).to_string(index=False))

    # 3. Verificación Estadística
    means = df_train_proc[num_cols].mean().round(4)
    vars_ = df_train_proc[num_cols].var(ddof=0).round(4)
    print(f"\n📊 [ESTADÍSTICAS NUMÉRICAS POST-ESCALADO (TRAIN)]:")
    print(f"   • Medias esperadas (0.0): {means.to_dict()}")
    print(f"   • Varianzas esperadas (1.0): {vars_.to_dict()}")

    # 4. Transformación en Validación (Detección de Data Leakage y Categorías Desconocidas)
    df_val_proc = preprocessor.transform(val_data)
    print("\n✅ [RESULTADO TRANSFORMACIÓN VAL (Inclusión de categoría no vista)]: ")
    print(df_val_proc.round(4).to_string(index=False))

    # 5. Asertiones formales
    assert abs(means.sum()) < 1e-4, "Error: La media no es 0"
    assert abs(vars_.sum() - len(num_cols)) < 1e-4, "Error: La varianza poblacional no es 1"
    assert df_train_proc.shape[1] == 5, f"Dimensión incorrecta: {df_train_proc.shape[1]} columnas"
    assert df_val_proc.shape[1] == df_train_proc.shape[1], "Disparidad de columnas entre train y val"

    print("\n" + "=" * 70)
    print("🎉 ¡PASO 3 VALIDADO Y APTO PARA INTEGRACIÓN AL MODELO!")
    print("=" * 70)

# Ejecutar la validación
ejecutar_validacion_paso_3()
