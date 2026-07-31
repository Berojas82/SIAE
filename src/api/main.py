"""
Aplicación Principal FastAPI para el proyecto ITACA.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .endpoints import router as api_router
from .dependencies import container
from ..utils.logger import get_logger

logger = get_logger("FastAPIApp")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando API y cargando artefactos del modelo en memoria...")
    container.load_artifacts()
    yield
    logger.info("Cerrando servicio API ITACA.")

app = FastAPI(
    title="ITACA - Motor de Inferencia Multimodal",
    description="API REST de autodiagnóstico empresarial inteligente (Tabular + NLP con TensorFlow/Keras)",
    version="2.0.0",
    lifespan=lifespan
)

# Habilitar CORS para permitir llamadas desde el frontend web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
