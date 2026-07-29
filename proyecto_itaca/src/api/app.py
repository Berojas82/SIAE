import sys
import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import numpy as np

# Inclusión del directorio raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.inference.predict import ITACAPredictor

# Inicialización del Framework FastAPI
app = FastAPI(
    title="ITACA Hybrid AI Inference Engine",
    description="API REST para el autodiagnóstico empresarial multimodal (Tabular + NLP)",
    version="1.0.0"
)

# Carga del motor de inferencia
PREDICTOR = None

@app.on_event("startup")
def load_artifacts():
    global PREDICTOR
    try:
        PREDICTOR = ITACAPredictor(model_path="model_itaca.joblib")
        print("✅ Artefactos del modelo cargados en memoria exitosamente.")
    except Exception as e:
        print(f"❌ Error al cargar los artefactos: {str(e)}")


# Esquemas de Entrada y Salida (Pydantic Contracts)
class InferenceRequest(BaseModel):
    tabular_features: List[float] = Field(..., example=[0.45, -1.2, 0.88, 0.12, -0.05], description="Vector tabular estandarizado (d=5)")
    text_embedding: List[float] = Field(..., example=[0.1]*16, description="Embedding de texto proveniente del módulo NLP (d=16)")

class InferenceResponse(BaseModel):
    status: str
    prediction: int
    label: str
    confidence_score: float
    threshold_used: float


# Endpoints HTTP
@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Estado de disponibilidad del servicio API."""
    return {"status": "ONLINE", "model_loaded": PREDICTOR is not None}

@app.post("/predict", response_model=InferenceResponse, status_code=status.HTTP_200_OK)
def predict_endpoint(payload: InferenceRequest):
    """Genera la predicción de diagnóstico empresarial a partir de vectores tabulares y de texto."""
    if PREDICTOR is None:
        raise HTTPException(status_code=500, detail="El modelo de inferencia no está cargado.")

    if len(payload.tabular_features) != 5:
        raise HTTPException(status_code=400, detail="El vector tabular debe contener exactamente 5 dimensiones.")

    if len(payload.text_embedding) != 16:
        raise HTTPException(status_code=400, detail="El vector de embedding de texto debe contener exactamente 16 dimensiones.")

    try:
        X_tab = np.array(payload.tabular_features).reshape(1, -1)
        X_text = np.array(payload.text_embedding).reshape(1, -1)

        response = PREDICTOR.predict_single(X_tab, X_text)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la inferencia: {str(e)}")
