# 🚀 ITACA - Motor de Inferencia y Autodiagnóstico Multimodal (IA)

Este repositorio contiene la arquitectura end-to-end del **Proyecto ITACA**, diseñada para procesar datos tabulares y textuales (NLP) mediante un clasificador híbrido con auditoría de equidad (*Fairness*) por sector económico y despliegue en API REST.

---

## 📐 Arquitectura y Estructura del Proyecto

```text
.
├── src/
│   ├── data/                   # [PASO 1-3] Módulos de limpieza NLP y preprocesado tabular
│   │   ├── nlp_cleaner.py
│   │   └── tabular_preprocessor.py
│   ├── models/                 # [PASO 4-5] Modelo Híbrido y Evaluador de Equidad
│   │   ├── hybrid_model.py
│   │   └── train_and_evaluate.py
│   ├── inference/              # [PASO 6] Motor de inferencia en caliente
│   │   └── predict.py
│   ├── api/                    # Servidor REST API (FastAPI + Pydantic)
│   │   └── app.py
│   ├── utils/                  # Generación de gráficos e informes
│   │   └── plot_results.py
│   └── main.py                 # [PASO 7] Orquestador End-to-End
├── model_itaca.joblib          # Artefacto del modelo entrenado
├── metrics_report.json         # Reporte de métricas y auditoría de Fairness
├── analisis_desempeno_itaca.png# Gráfica de Matriz de Confusión y ROC
├── auditoria_fairness_itaca.png# Gráfica de equidad por sector económico
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Documentación técnica
