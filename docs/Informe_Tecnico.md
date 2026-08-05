# Informe Técnico — Proyecto ITACA
## Sistema Inteligente de Autodiagnóstico Empresarial (SIAE)

**Versión:** 2.0.0 · **Fecha:** Agosto de 2026
**Stack:** TensorFlow/Keras · SentenceTransformers · FastAPI · Docker

---

## 1. Descripción y Justificación del Problema

### 1.1 Contexto de negocio

Ítaca acompaña a pequeñas y medianas empresas en su proceso de transformación
digital. El primer paso de ese acompañamiento — diagnosticar el nivel de madurez
digital de cada empresa — se realizaba de forma manual: un consultor entrevistaba
a la organización, revisaba sus procesos y emitía un dictamen. Este enfoque
presenta tres limitaciones estratégicas:

1. **Escalabilidad:** el diagnóstico manual toma horas por empresa; la demanda
   supera la capacidad del equipo consultor.
2. **Consistencia:** dos consultores pueden emitir dictámenes distintos ante
   evidencia similar, introduciendo subjetividad.
3. **Costo de entrada:** para una microempresa, el costo de una consultoría
   inicial puede ser disuasorio, dejando fuera al segmento que más la necesita.

### 1.2 ¿Por qué IA/Deep Learning y no métodos tradicionales?

La evidencia disponible para el diagnóstico es **inherentemente multimodal**:
combina variables estructuradas (sector, tamaño, presupuesto tecnológico) con
**texto libre** donde la empresa describe sus procesos. Un sistema de reglas o
un modelo tabular clásico (árboles, regresión logística) puede tratar las
variables estructuradas, pero no puede interpretar frases como *"el trabajo es
muy empírico, dependemos de registros en papel"* — que es precisamente donde
reside la señal más rica del diagnóstico.

El aprendizaje profundo permite:

- **Fusionar ambas modalidades** en una única red con dos ramas de entrada.
- **Aprovechar transfer learning** en la rama de texto: representaciones
  semánticas preentrenadas en corpus masivos multilingües, sin necesidad de
  entrenar un modelo de lenguaje desde cero.
- **Escalar a coste marginal cercano a cero**: una vez entrenado, cada
  diagnóstico adicional cuesta ~0,3 segundos de cómputo.

---

## 2. Diseño Técnico y Metodología

### 2.1 Arquitectura multi-input

El modelo (`src/models/hybrid_model.py`) es una red Keras funcional con dos
ramas de entrada que se fusionan antes de la capa de clasificación:

```
tabular_input (9)          text_input (384)
      │                          │
 Dense + BatchNorm          Dense + BatchNorm
      │                          │
      └────── Concatenate ───────┘
                   │
             Dense (fusión)
                   │
           Softmax (4 clases)
```

- **Rama tabular:** recibe 9 features producidas por el preprocesador
  (codificación one-hot de `sector` y `tamano_empresa`, escalado de
  `presupuesto_anual_tecnología`).
- **Rama de texto:** recibe el embedding de 384 dimensiones de la respuesta
  textual de la empresa.
- **Fusión:** concatenación seguida de capas densas y una salida softmax sobre
  las 4 clases de madurez: *Inicial*, *En Desarrollo*, *Definido*, *Optimizado*.

### 2.2 Justificación de TensorFlow/Keras

- La **API funcional de Keras** expresa arquitecturas multi-input de forma
  declarativa y legible, lo que facilita el mantenimiento por un equipo mixto.
- El formato de serialización **`.keras`** empaqueta arquitectura y pesos en un
  único artefacto portable, cargado en producción por la API.
- El ecosistema TensorFlow ofrece ejecución **CPU-only** eficiente
  (`tensorflow-cpu`), relevante porque el despliegue objetivo (Docker en
  infraestructura de PyME) no dispone de GPU.

### 2.3 Estrategia de Transfer Learning

Entrenar un modelo de lenguaje desde cero requeriría millones de documentos y
recursos de cómputo fuera del alcance del proyecto. En su lugar, la rama de
texto usa **SentenceTransformers** con el modelo preentrenado
**`paraphrase-multilingual-MiniLM-L12-v2`**:

- **Multilingüe** (50+ idiomas, incluido el español), esencial para el corpus.
- **Ligero** (~120 MB), apto para contenedores sin GPU.
- Produce embeddings de **384 dimensiones** que capturan similitud semántica:
  frases como "no documentamos nada" y "todo es empírico" quedan próximas en el
  espacio vectorial aunque no compartan vocabulario.

El transformer actúa como extractor de características congelado: no se
reentrena, solo se entrenan las capas densas posteriores. Esto reduce el tiempo
de entrenamiento completo a menos de 2 minutos en CPU.

### 2.4 Pipeline de entrenamiento

`scripts/train.py` ejecuta el flujo end-to-end de forma reproducible:

1. Carga y partición estratificada 70/15/15 (train/val/test).
2. Ajuste del preprocesador tabular **solo con train** (sin fuga de escalado).
3. Limpieza NLP (minúsculas, stopwords) y codificación con el transformer.
4. Entrenamiento (30 épocas, batch 32, pesos de clase balanceados).
5. Evaluación sobre test + **auditoría de equidad por sector**.
6. Exportación de artefactos: `model.keras`, `tabular_preprocessor.joblib`,
   `label_encoder.joblib`, `metadata.json`, `metrics_report.json`.

---

## 3. Especificación de Datos

| Aspecto | Detalle |
|---|---|
| Volumen | 3.000 registros |
| Formato | CSV (UTF-8), 8 columnas |
| Variables tabulares | `sector` (4 categorías), `tamano_empresa` (4), `porcentaje_procesos_documentados` (numérica), `presupuesto_anual_tecnología` (numérica) |
| Variable textual | `respuesta_texto` (descripción libre de procesos) |
| Etiqueta | `nivel_madurez` (4 clases) |
| Distribución de clases | Inicial 26%, En Desarrollo 31%, Definido 30%, Optimizado 12% (desbalance moderado, tratado con pesos de clase) |

### 3.1 Calidad y limitaciones detectadas

El análisis exploratorio (`notebooks/01_EDA.ipynb`) y los scripts de auditoría
revelaron dos problemas de calidad **críticos**, documentados en la sección 5:

1. **Fuga determinista en variable numérica:** `porcentaje_procesos_documentados`
   determina la etiqueta con exactitud del 100% mediante umbrales fijos
   (verificable con `scripts/diagnostico_fuga.py`). **Acción:** la variable fue
   excluida del entrenamiento (`src/utils/constants.py`).
2. **Corpus textual sintético de baja variedad:** las 3.000 filas contienen solo
   **32 textos únicos** (exactamente 8 por clase), y ningún texto aparece en más
   de una clase. La relación texto→etiqueta es por tanto una tabla de búsqueda.

### 3.2 Plan de preprocesamiento

- **Tabular:** imputación, codificación one-hot de categóricas y escalado de
  numéricas, encapsulado en un `TabularPreprocessor` serializable que garantiza
  transformaciones idénticas en entrenamiento y producción.
- **Texto:** normalización a minúsculas, eliminación de stopwords en español y
  codificación con SentenceTransformer.
- **Particiones:** estratificadas por etiqueta para preservar la distribución de
  clases en train/val/test.

---

## 4. Análisis Ético y de Responsabilidad

### 4.1 Anonimización y PII

- El dataset de trabajo es **sintético**: no contiene datos de empresas reales,
  por lo que el riesgo de exposición de PII en esta fase es nulo.
- El diseño del pipeline anticipa el paso a datos reales: el identificador
  (`id_diagnostico`) es un código opaco sin relación con la identidad; no se
  recogen nombres, NIT/RUC, direcciones ni contactos; y el texto libre será
  sometido a un filtro de detección de entidades nombradas (NER) antes de
  almacenarse, para eliminar menciones accidentales de personas u
  organizaciones.
- Los artefactos serializados no contienen registros del dataset: el modelo
  almacena únicamente pesos agregados y el preprocesador, estadísticos de
  ajuste.

### 4.2 Auditoría de equidad (Fairness)

La equidad entre sectores industriales es un requisito de diseño, no una
comprobación posterior. El componente `ITACAModelEvaluator`
(`src/evaluation/itaca_model_evaluator.py`) ejecuta en **cada entrenamiento**:

- Cálculo de **F1 por sector** (Manufactura, Retail, Servicios, Tecnología).
- Verificación de que la **diferencia máxima de F1 entre sectores ≤ 5%**
  (umbral `max_fairness_delta = 0.05`).
- El resultado queda registrado en `artifacts/metrics_report.json`
  (`fairness_audit`), con veredicto explícito `fairness_passed`.

En la ejecución actual: F1 = 1.0 en los cuatro sectores, delta = 0.0,
`fairness_passed = true`. **Lectura crítica:** dado el problema de memorización
descrito en la sección 5, este resultado confirma que *el mecanismo de
auditoría funciona*, pero no constituye aún evidencia de equidad en condiciones
reales; deberá re-ejecutarse cuando exista un corpus con variedad textual
genuina.

### 4.3 Estrategias de explicabilidad (XAI)

- **Estudios de ablación** (`scripts/ablacion_solo_texto.py`): entrena una
  variante solo-texto para aislar la contribución de cada modalidad al
  diagnóstico.
- **Diagnóstico de fuga** (`scripts/diagnostico_fuga.py`): verifica con un árbol
  de decisión trivial si alguna variable individual determina la etiqueta —
  técnica que detectó la fuga documentada.
- **Transparencia de la incertidumbre:** la API devuelve la distribución
  completa de probabilidades, y el frontend muestra una **alerta de baja
  confianza** cuando `confidence_score < 0.55`, recomendando revisión humana.
- **Trabajo futuro:** importancia por permutación sobre las features tabulares
  y análisis de similitud de embeddings para explicar qué frases del texto
  acercan a la empresa a cada nivel de madurez.

### 4.4 Alcance del sistema

El sistema se presenta explícitamente como **orientativo**: la interfaz muestra
de forma permanente la nota *"Este diagnóstico es orientativo y no reemplaza
una consultoría profesional"*, y los casos de baja confianza se derivan a
revisión humana. El modelo recomienda; no decide.

---

## 5. Resultados y Conclusiones

### 5.1 Métricas formales frente a metas

| Meta | Objetivo | Resultado formal | ¿Cumple? |
|---|---|---|---|
| Accuracy | ≥ 85% | 100% | Sí* |
| F1-macro | ≥ 0.80 | 1.00 | Sí* |
| Equidad (Δ F1 sectores) | ≤ 5% | 0.0% | Sí* |
| Latencia (inferencia caliente) | < 3 s | 0.30–0.32 s | Sí |
| Despliegue reproducible | end-to-end | Docker Compose funcional | Sí |

\* Con la salvedad crítica que se detalla a continuación.

### 5.2 Análisis crítico: por qué las métricas perfectas son una señal de alerta

Un accuracy de 1.0 en un problema real de clasificación multimodal es
estadísticamente implausible. El equipo trató este resultado como un síntoma a
investigar, no como un éxito, y la investigación produjo los dos hallazgos
centrales del proyecto:

**Hallazgo 1 — Fuga en variable numérica (corregida).**
`porcentaje_procesos_documentados` determina la etiqueta de forma exacta: un
árbol de decisión de profundidad 4 entrenado *solo* con esa columna alcanza
accuracy 1.0. La variable fue excluida del entrenamiento. Este es el
comportamiento esperado de un dataset sintético generado por reglas.

**Hallazgo 2 — Memorización del corpus textual (estructural).**
Tras excluir la variable con fuga, el accuracy se mantuvo en 1.0. La causa: el
corpus contiene únicamente **32 textos únicos para 3.000 filas** (8 por clase),
cada texto pertenece exactamente a una clase, y el **100% de los textos de test
aparecen literalmente en train**. El modelo no aprende a interpretar lenguaje:
memoriza 32 cadenas. Las métricas, por tanto, miden capacidad de memorización,
no de generalización.

**Implicación metodológica:** para obtener una métrica honesta de
generalización se requiere (a) una partición agrupada por texto
(`GroupShuffleSplit`), evaluando solo sobre textos nunca vistos, y — de forma
más fundamental — (b) un corpus con variedad textual real. Con 32 textos
únicos, incluso la partición agrupada dejaría una muestra de evaluación
estadísticamente insuficiente. **La recolección de respuestas textuales reales
es el paso crítico previo a cualquier afirmación de desempeño.**

### 5.3 Nivel de madurez tecnológica (TRL)

| Dimensión | Evidencia |
|---|---|
| Pipeline completo y reproducible | `train.py` regenera los 5 artefactos en una corrida |
| Integración de sistema | API + frontend + healthchecks orquestados con Docker Compose |
| Validación en entorno relevante | Demo end-to-end funcional con latencia verificada |
| Validación con datos reales | **Pendiente** (dataset sintético) |

El sistema alcanza **TRL 5–6**: prototipo integrado y validado en un entorno
relevante (contenedores, API real, cliente web). La transición a TRL 7
(demostración en entorno operativo) queda condicionada a la validación con
datos de empresas reales.

### 5.4 Conclusiones

1. **La ingeniería del sistema está completa y es sólida:** pipeline
   reproducible, artefactos versionados, API con manejo seguro de errores,
   auditoría de equidad automatizada, frontend con dashboard comparativo y
   despliegue contenedorizado con healthchecks.
2. **El hallazgo más valioso del proyecto es metodológico:** la detección y
   documentación de dos fugas de datos encadenadas demuestra madurez en
   auditoría de ML — una competencia más escasa y valiosa que reportar métricas
   altas sin escrutinio.
3. **El camino a producción está claramente definido:** recolectar corpus
   textual real, re-particionar por grupos, re-entrenar y re-auditar equidad.
   La arquitectura no requiere cambios para ese paso; solo los datos.

---

*Documento generado como parte de la entrega del proyecto ITACA — SIAE,
Corporación Universitaria Iberoamericana.*
