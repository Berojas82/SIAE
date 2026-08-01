"""
Definición de endpoints HTTP para la API de ITACA.
"""
from fastapi import APIRouter, HTTPException, status
from .schemas import PredictionRequest, PredictionResponse
from .dependencies import container
from ..utils.logger import get_logger

logger = get_logger("APIEndpoints")

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Verifica el estado de disponibilidad del motor de inferencia API."""
    return {
        "status": "ONLINE",
        "artifacts_loaded": container.is_loaded
    }

@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
def predict(payload: PredictionRequest):
    """
    Endpoint principal para generar el autodiagnóstico de madurez digital
    a partir de datos tabulares de negocio y texto cualitativo.
    """
    try:
        res = container.predict_sample(
            sector=payload.sector,
            tamano_empresa=payload.tamano_empresa,
            porcentaje_procesos_documentados=payload.porcentaje_procesos_documentados,
            presupuesto_anual_tecnologia=payload.presupuesto_anual_tecnología,
            respuesta_texto=payload.respuesta_texto
        )
        return res
    except Exception as e:
        logger.exception("Fallo durante la inferencia")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al generar el diagnostico. Intente nuevamente."
        )
