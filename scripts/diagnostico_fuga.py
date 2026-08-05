import sys
import pandas as pd
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

train = pd.read_csv(repo_root / "data" / "splits" / "train.csv")
test = pd.read_csv(repo_root / "data" / "splits" / "test.csv")
COL = "porcentaje_procesos_documentados"

# Un árbol trivial con UNA sola variable de entrada
arbol = DecisionTreeClassifier(max_depth=4, random_state=42)
arbol.fit(train[[COL]], train["nivel_madurez"])
acc = accuracy_score(test["nivel_madurez"], arbol.predict(test[[COL]]))

print(f"Accuracy usando SOLO '{COL}': {acc:.4f}")
if acc == 1.0:
    print("Si este numero es 1.0, la etiqueta es una funcion determinista de esa columna:")
    print("El modelo hibrido no aprende del texto, solo copia el umbral de la variable numerica.")
