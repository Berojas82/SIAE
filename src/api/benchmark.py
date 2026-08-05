"""
Agregación de estadísticas sectoriales para el dashboard comparativo.

Los datos provienen del dataset procesado y se calculan una única vez al
primer acceso, ya que constituyen una referencia estática de la muestra.
"""
from typing import Any, Dict, List, Optional

import pandas as pd

from ..utils.constants import CLASSES, PROCESSED_DATA_PATH, TARGET_COL
from ..utils.logger import get_logger

logger = get_logger("SectorBenchmark")

PRESUPUESTO_COL = "presupuesto_anual_tecnología"

# Caché en memoria: el dataset de referencia no cambia en tiempo de ejecución.
_stats_cache: Optional[Dict[str, Any]] = None


def _stats_vacias() -> Dict[str, Any]:
    """Respuesta degradada cuando el dataset de referencia no está disponible."""
    return {
        "disponible": False,
        "total_empresas": 0,
        "sectores": [],
        "clases": list(CLASSES),
        "distribucion": {},
        "distribucion_pct": {},
        "presupuesto_mediano": {},
        "total_por_sector": {},
    }


def calcular_stats_sectoriales() -> Dict[str, Any]:
    """
    Agrega el dataset procesado por sector y nivel de madurez.

    Devuelve conteos absolutos, porcentajes normalizados por sector y la
    mediana de presupuesto tecnológico de cada sector.
    """
    if not PROCESSED_DATA_PATH.exists():
        logger.warning(f"No se encontró el dataset de referencia en {PROCESSED_DATA_PATH}")
        return _stats_vacias()

    df = pd.read_csv(PROCESSED_DATA_PATH, encoding="utf-8")

    columnas_requeridas = {"sector", TARGET_COL}
    faltantes = columnas_requeridas - set(df.columns)
    if faltantes:
        logger.warning(f"El dataset de referencia no contiene las columnas: {faltantes}")
        return _stats_vacias()

    sectores: List[str] = sorted(df["sector"].dropna().unique().tolist())

    # Tabla de contingencia sector × nivel, reindexada al orden canónico de clases
    tabla = pd.crosstab(df["sector"], df[TARGET_COL])
    tabla = tabla.reindex(columns=CLASSES, fill_value=0)

    distribucion: Dict[str, Dict[str, int]] = {}
    distribucion_pct: Dict[str, Dict[str, float]] = {}
    total_por_sector: Dict[str, int] = {}

    for sector in sectores:
        fila = tabla.loc[sector]
        total = int(fila.sum())
        total_por_sector[sector] = total
        distribucion[sector] = {clase: int(fila[clase]) for clase in CLASSES}
        distribucion_pct[sector] = {
            clase: round(float(fila[clase]) / total * 100, 2) if total else 0.0
            for clase in CLASSES
        }

    presupuesto_mediano: Dict[str, float] = {}
    if PRESUPUESTO_COL in df.columns:
        medianas = df.groupby("sector")[PRESUPUESTO_COL].median()
        presupuesto_mediano = {
            sector: round(float(medianas.get(sector, 0.0)), 2) for sector in sectores
        }

    logger.info(f"Estadísticas sectoriales calculadas sobre {len(df)} registros.")

    return {
        "disponible": True,
        "total_empresas": int(len(df)),
        "sectores": sectores,
        "clases": list(CLASSES),
        "distribucion": distribucion,
        "distribucion_pct": distribucion_pct,
        "presupuesto_mediano": presupuesto_mediano,
        "total_por_sector": total_por_sector,
    }


def get_sector_stats() -> Dict[str, Any]:
    """Devuelve las estadísticas sectoriales, calculándolas solo la primera vez."""
    global _stats_cache
    if _stats_cache is None:
        _stats_cache = calcular_stats_sectoriales()
    return _stats_cache
