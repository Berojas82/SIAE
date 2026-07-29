import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split

def generate_synthetic_itaca_data(n_samples=3000, seed=42):
    """
    Genera un dataset sintético con el esquema del proyecto ITACA para pruebas.
    """
    np.random.seed(seed)

    sectores = ['Tecnología', 'Manufactura', 'Servicios', 'Comercio', 'Salud']
    tamanios = ['Micro', 'Pequeña', 'Mediana', 'Grande']
    niveles_madurez = ['Inicial', 'En Desarrollo', 'Definido', 'Optimizado']

    data = {
        'id_empresa': [f'EMP-{i:04d}' for i in range(1, n_samples + 1)],
        'sector': np.random.choice(sectores, size=n_samples, p=[0.25, 0.20, 0.30, 0.15, 0.10]),
        'tamano_empresa': np.random.choice(tamanios, size=n_samples, p=[0.40, 0.35, 0.15, 0.10]),
        'pct_procesos_documentados': np.random.uniform(5.0, 98.0, size=n_samples).round(2),
        'presupuesto_tech_usd': np.random.exponential(scale=15000, size=n_samples).round(2),
        'texto_respuestas': np.random.choice([
            "Nuestros procesos son manuales y dependemos de hojas de cálculo de Excel para todo.",
            "Tenemos algunas herramientas digitales pero no están integradas entre sí.",
            "Contamos con un ERP estructurado, documentación clara y KPIs automatizados.",
            "Usamos inteligencia artificial en varios procesos y optimizamos flujos continuamente."
        ], size=n_samples),
        'nivel_madurez': np.random.choice(niveles_madurez, size=n_samples, p=[0.35, 0.30, 0.20, 0.15])
    }

    df = pd.DataFrame(data)
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/itaca_dataset.csv', index=False)
    print(f" Dataset de prueba guardado en 'data/itaca_dataset.csv' con {n_samples} registros.")
    return df

def load_and_split_data(filepath='data/itaca_dataset.csv', target_col='nivel_madurez', test_size=0.15, val_size=0.15, seed=42):
    """
    Carga el dataset y realiza el split 70% Train / 15% Val / 15% Test con estratificación.
    """
    if not os.path.exists(filepath):
        print(f"⚠️ Archivo {filepath} no encontrado. Generando datos de prueba...")
        generate_synthetic_itaca_data()

    df = pd.read_csv(filepath)

    # Cálculo para mantener 70% Train, 15% Val, 15% Test
    # Primero se separa el conjunto de prueba (15%)
    train_val_df, test_df = train_test_split(
        df, test_size=test_size, random_state=seed, stratify=df[target_col]
    )

    # Del 85% restante, se calcula la proporción equivalente al 15% del total
    val_relative_size = val_size / (1.0 - test_size)
    train_df, val_df = train_test_split(
        train_val_df, test_size=val_relative_size, random_state=seed, stratify=train_val_df[target_col]
    )

    print(" Divisón de datos completada exitosamente:")
    print(f"   - Entrenamiento (Train): {len(train_df)} filas ({len(train_df)/len(df):.0%})")
    print(f"   - Validación (Val):       {len(val_df)} filas ({len(val_df)/len(df):.0%})")
    print(f"   - Prueba (Test):          {len(test_df)} filas ({len(test_df)/len(df):.0%})")

    return train_df, val_df, test_df

if __name__ == "__main__":
    load_and_split_data()

# Probar la función
train_df, val_df, test_df = load_and_split_data()

# Mostrar las primeras filas del conjunto de entrenamiento
train_df.head()
