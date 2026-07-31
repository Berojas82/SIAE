"""
Gestión de artefactos en memoria e inyección de dependencias para FastAPI.
"""
import joblib
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional

from ..models.hybrid_model import HybridModel
from ..preprocessing.text.nlp_cleaner import NLPCleaner
from ..preprocessing.text.text_encoder import TextEncoder
from ..preprocessing.tabular.tabular_preprocessor import TabularPreprocessor
from ..utils.constants import (
    MODEL_KERAS_PATH,
    TABULAR_PREPROCESSOR_PATH,
    LABEL_ENCODER_PATH,
    CLASSES
)
from ..utils.logger import get_logger

logger = get_logger("APIDependencies")

# Recomendaciones por nivel de madurez y sector (Reglas de negocio)
RECOMENDACIONES_DEFAULT = {
    "Inicial": {
        "Tecnología": "Mapear flujos de trabajo de desarrollo y usar repositorios de código centralizados.",
        "Manufactura": "Estandarizar el registro diario de mermas e inventario en plantillas compartidas.",
        "Retail": "Implementar un sistema POS básico para abandonar el registro manual de ventas.",
        "Servicios": "Digitalizar la base de datos de clientes y centralizar la agenda de servicios.",
        "Default": "Estandarizar los procesos operativos básicos e iniciar registro digital."
    },
    "En Desarrollo": {
        "Tecnología": "Integrar herramientas de tickets con repositorios y documentar APIs.",
        "Manufactura": "Implementar un sistema MRP básico para la planificación de materiales.",
        "Retail": "Centralizar el inventario de todas las sucursales en un único sistema digital.",
        "Servicios": "Implementar un CRM para el seguimiento estructurado de ventas y clientes.",
        "Default": "Documentar procesos clave e integrar herramientas informáticas parciales."
    },
    "Definido": {
        "Tecnología": "Implementar CI/CD y pruebas automatizadas para garantizar calidad en entregas.",
        "Manufactura": "Conectar los datos de producción en planta con el ERP financiero de la empresa.",
        "Retail": "Integrar el ERP de inventarios con el CRM para campañas de fidelización.",
        "Servicios": "Automatizar la generación de reportes y medir satisfacción de clientes (NPS).",
        "Default": "Establecer métricas continuas y conectar sistemas clave con ERP/CRM."
    },
    "Optimizado": {
        "Tecnología": "Aplicar MLOps y analítica predictiva para optimizar el ciclo de vida del software.",
        "Manufactura": "Adoptar sensores IoT en maquinaria para mantenimiento predictivo.",
        "Retail": "Implementar modelos de predicción de demanda basados en inteligencia artificial.",
        "Servicios": "Utilizar analítica avanzada para hiper-personalización y recomendaciones.",
        "Default": "Aprovechar Inteligencia Artificial e Analítica Avanzada para optimización continua."
    }
}

class ModelContainer:
    """Contenedor de modelo y preprocesadores en memoria."""

    def __init__(self):
        self.model: Optional[HybridModel] = None
        self.tabular_preprocessor: Optional[TabularPreprocessor] = None
        self.label_encoder: Any = None
        self.nlp_cleaner = NLPCleaner(remove_stopwords=True)
        self.text_encoder = TextEncoder()
        self.is_loaded = False

    def load_artifacts(
        self,
        model_path: Path = MODEL_KERAS_PATH,
        preprocessor_path: Path = TABULAR_PREPROCESSOR_PATH,
        label_encoder_path: Path = LABEL_ENCODER_PATH
    ):
        try:
            logger.info("Cargando artefactos en memoria...")
            if model_path.exists():
                self.model = HybridModel.load(str(model_path))
            else:
                logger.warning(f"No se encontró el modelo Keras en {model_path}")

            if preprocessor_path.exists():
                self.tabular_preprocessor = joblib.load(preprocessor_path)
            else:
                logger.warning(f"No se encontró el preprocesador tabular en {preprocessor_path}")

            if label_encoder_path.exists():
                self.label_encoder = joblib.load(label_encoder_path)
            else:
                self.label_encoder = None

            self.is_loaded = self.model is not None and self.tabular_preprocessor is not None
            if self.is_loaded:
                logger.info("✅ Todos los artefactos fueron cargados exitosamente.")
            else:
                logger.warning("⚠️ Los artefactos no están completos. La API funcionará en modo degradado/mock.")
        except Exception as e:
            logger.error(f"Error al cargar artefactos: {str(e)}")
            self.is_loaded = False

    def predict_sample(
        self,
        sector: str,
        tamano_empresa: str,
        porcentaje_procesos_documentados: float,
        presupuesto_anual_tecnologia: float,
        respuesta_texto: str
    ) -> Dict[str, Any]:
        if not self.is_loaded or self.tabular_preprocessor is None or self.model is None:
            # Fallback seguro para pruebas si no hay artefactos serializados
            return {
                "status": "MOCK_RESPONSE",
                "nivel_madurez": "Inicial",
                "confidence_score": 0.75,
                "probabilities": {"Inicial": 0.75, "En Desarrollo": 0.15, "Definido": 0.07, "Optimizado": 0.03},
                "recomendacion_principal": RECOMENDACIONES_DEFAULT["Inicial"].get(sector, RECOMENDACIONES_DEFAULT["Inicial"]["Default"])
            }

        # 1. Preprocesar variables tabulares
        input_df = pd.DataFrame([{
            "sector": sector,
            "tamano_empresa": tamano_empresa,
            "porcentaje_procesos_documentados": porcentaje_procesos_documentados,
            "presupuesto_anual_tecnología": presupuesto_anual_tecnologia
        }])
        X_tab = self.tabular_preprocessor.transform(input_df)

        # 2. Preprocesar texto
        cleaned_text = self.nlp_cleaner.clean_text(respuesta_texto)
        X_text = self.text_encoder.encode([cleaned_text])

        # 3. Predicción
        probs = self.model.predict(X_tab, X_text)[0]
        pred_idx = int(np.argmax(probs))

        if self.label_encoder is not None and hasattr(self.label_encoder, "classes_"):
            classes_list = list(self.label_encoder.classes_)
            nivel_madurez = classes_list[pred_idx]
        else:
            classes_list = CLASSES
            nivel_madurez = classes_list[pred_idx]

        probs_dict = {classes_list[i]: float(round(probs[i], 4)) for i in range(len(classes_list))}

        # 4. Obtención de recomendación
        rec_map = RECOMENDACIONES_DEFAULT.get(nivel_madurez, {})
        recomendacion = rec_map.get(sector, rec_map.get("Default", "Estandarizar procesos clave."))

        return {
            "status": "SUCCESS",
            "nivel_madurez": nivel_madurez,
            "confidence_score": float(round(probs[pred_idx], 4)),
            "probabilities": probs_dict,
            "recomendacion_principal": recomendacion
        }

container = ModelContainer()
