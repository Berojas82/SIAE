"""
Modelos Pydantic para los esquemas de petición y respuesta HTTP.
"""
from pydantic import BaseModel, Field
from typing import Dict, List

class PredictionRequest(BaseModel):
    sector: str = Field(
        ...,
        description="Sector económico de la empresa (Ej: Tecnología, Manufactura, Servicios, Retail)",
        json_schema_extra={"example": "Tecnología"}
    )
    tamano_empresa: str = Field(
        ...,
        description="Tamaño de la empresa (Ej: Micro, Pequeña, Mediana, Grande)",
        json_schema_extra={"example": "Micro"}
    )
    porcentaje_procesos_documentados: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Porcentaje de procesos documentados (0.0 a 1.0)",
        json_schema_extra={"example": 0.25}
    )
    presupuesto_anual_tecnología: float = Field(
        ...,
        ge=0.0,
        description="Presupuesto anual asignado a tecnología en USD",
        json_schema_extra={"example": 15000.0}
    )
    respuesta_texto: str = Field(
        ...,
        description="Descripción cualitativa del estado de la empresa",
        json_schema_extra={"example": "El trabajo es muy empírico, no hay documentación de lo que hacemos."}
    )

class PredictionResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "SUCCESS"})
    nivel_madurez: str = Field(..., json_schema_extra={"example": "Inicial"})
    confidence_score: float = Field(..., json_schema_extra={"example": 0.8542})
    probabilities: Dict[str, float] = Field(
        ...,
        json_schema_extra={
            "example": {
                "Inicial": 0.8542,
                "En Desarrollo": 0.1023,
                "Definido": 0.0315,
                "Optimizado": 0.0120
            }
        }
    )
    recomendacion_principal: str = Field(
        ...,
        json_schema_extra={
            "example": "Mapear flujos de trabajo de desarrollo y usar repositorios de código centralizados."
        }
    )
