"""
Definición de endpoints HTTP para la API de ITACA.
"""
from fastapi import APIRouter, HTTPException, status
from .schemas import PredictionRequest, PredictionResponse, SectorStatsResponse
from .dependencies import container
from .benchmark import get_sector_stats
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

@router.get("/stats/sectores", response_model=SectorStatsResponse, status_code=status.HTTP_200_OK)
def sector_stats():
    """
    Estadísticas agregadas del dataset de referencia, usadas por el dashboard
    para comparar el diagnóstico de una empresa contra su sector.
    """
    try:
        return get_sector_stats()
    except Exception:
        logger.exception("Fallo al calcular las estadísticas sectoriales")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener las estadisticas sectoriales."
        )

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
