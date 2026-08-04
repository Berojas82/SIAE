import sys
import pandas as pd
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

def main():
    train_path = repo_root / "data" / "splits" / "train.csv"
    test_path = repo_root / "data" / "splits" / "test.csv"

    if not train_path.exists() or not test_path.exists():
        print("Los splits no existen aún. Generándolos ejecutando el data loader...")
        from src.data_loader.data_loader import DataLoader
        loader = DataLoader()
        loader.split_data(save_splits=True)

    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    
    col = "porcentaje_procesos_documentados"
    
    print("--- Agrupación de porcentaje_procesos_documentados por nivel_madurez ---")
    print(train.groupby("nivel_madurez")[col].agg(["min", "max", "count"]))
    
    arbol = DecisionTreeClassifier(max_depth=4, random_state=42)
    arbol.fit(train[[col]], train["nivel_madurez"])
    acc = accuracy_score(test["nivel_madurez"], arbol.predict(test[[col]]))
    
    print(f"\nAccuracy usando SOLO '{col}': {acc:.4f}")
    if acc == 1.0:
        print("¡FUGA CONFIRMADA! La etiqueta es una función determinista de esa sola columna.")
        print("El modelo híbrido no aprende del texto, solo memoriza el umbral.")

if __name__ == "__main__":
    main()
