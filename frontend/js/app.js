document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('diagnosisForm');
    const rangeInput = document.getElementById('porcentaje_procesos_documentados');
    const pctValue = document.getElementById('pctValue');
    const emptyState = document.getElementById('emptyState');
    const resultsContent = document.getElementById('resultsContent');

    const levelBadge = document.getElementById('levelBadge');
    const confidenceScore = document.getElementById('confidenceScore');
    const probBars = document.getElementById('probBars');
    const recommendationText = document.getElementById('recommendationText');
    const submitBtn = document.getElementById('submitBtn');

    // Payloads precargados para la sustentación
    const CASOS_DEMO = {
        inicial: {
            sector: "Manufactura",
            tamano_empresa: "Micro",
            porcentaje_procesos_documentados: 5,
            presupuesto_anual_tecnología: 3000000,
            respuesta_texto: "Todo lo anotamos en cuadernos y se nos pierde la información."
        },
        intermedio: {
            sector: "Comercio",
            tamano_empresa: "Pequeña",
            porcentaje_procesos_documentados: 35,
            presupuesto_anual_tecnología: 8000000,
            respuesta_texto: "Tenemos algunas herramientas digitales pero no están integradas."
        },
        optimizado: {
            sector: "Tecnología",
            tamano_empresa: "Grande",
            porcentaje_procesos_documentados: 92,
            presupuesto_anual_tecnología: 250000000,
            respuesta_texto: "Automatizamos el ciclo completo y medimos todo con tableros de control."
        }
    };

    function cargarCasoDemo(nombreCaso) {
        const c = CASOS_DEMO[nombreCaso];
        if (!c) return;

        document.getElementById('sector').value = c.sector;
        document.getElementById('tamano_empresa').value = c.tamano_empresa;
        document.getElementById('porcentaje_procesos_documentados').value = c.porcentaje_procesos_documentados;
        document.getElementById('presupuesto_anual_tecnología').value = c.presupuesto_anual_tecnología;
        document.getElementById('respuesta_texto').value = c.respuesta_texto;
    }

    const UMBRAL_CONFIANZA = 0.55; // Definido en las especificaciones del plan

    function procesarRespuestaAPI(data) {
        const { nivel_madurez, confidence_score, recomendacion_principal } = data;

        // Actualizar métricas visuales
        document.getElementById('nivelMadurez').textContent = nivel_madurez;
        document.getElementById('confidenceScore').textContent = `Confianza IA: ${(confidence_score * 100).toFixed(1)}%`;

        // Control de aviso por baja confianza
        const aviso = document.getElementById('avisoConfianza');
        if (confidence_score < UMBRAL_CONFIANZA) {
            aviso.textContent = "⚠️ Diagnóstico preliminar: Se sugiere revisión manual por un consultor humano debido a baja certeza del modelo.";
            aviso.style.display = 'block';
            aviso.style.backgroundColor = 'var(--warning-yellow)';
        } else {
            aviso.style.display = 'none';
        }

        document.getElementById('recomendacion').textContent = recomendacion_principal;
    }

    // Reemplazo de alert() nativo por mensaje en interfaz
    function mostrarErrorUI(mensaje) {
        const contenedorError = document.getElementById('mensajeError');
        contenedorError.textContent = mensaje;
        contenedorError.style.display = 'block';
        contenedorError.style.color = 'var(--primary-red)';
    }


    // Actualizar valor de rango
    rangeInput.addEventListener('input', (e) => {
        pctValue.textContent = `${e.target.value}%`;
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const sector = document.getElementById('sector').value;
        const tamano_empresa = document.getElementById('tamano_empresa').value;
        const porcentaje_procesos_documentados = parseFloat(rangeInput.value) / 100.0;
        const presupuesto_anual_tecnología = parseFloat(document.getElementById('presupuesto_anual_tecnología').value);
        const respuesta_texto = document.getElementById('respuesta_texto').value;

        const payload = {
            sector,
            tamano_empresa,
            porcentaje_procesos_documentados,
            presupuesto_anual_tecnología,
            respuesta_texto
        };

        // Estado de Carga
        submitBtn.disabled = true;
        submitBtn.querySelector('.btn-text').textContent = 'Procesando en IA...';

        try {
            const response = await fetch('http://localhost:8000/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Error en el servidor API');
            }

            const data = await response.json();
            renderResults(data);
        } catch (error) {
            alert(`⚠️ No se pudo obtener la predicción: ${error.message}\nAsegúrese de que la API esté corriendo con 'python scripts/serve.py'`);
        } finally {
            submitBtn.disabled = false;
            submitBtn.querySelector('.btn-text').textContent = '⚡ Generar Diagnóstico IA';
        }
    });

    function renderResults(data) {
        emptyState.classList.add('hidden');
        resultsContent.classList.remove('hidden');

        const { nivel_madurez, confidence_score, probabilities, recomendacion_principal } = data;

        levelBadge.textContent = nivel_madurez;
        confidenceScore.textContent = `Confianza del modelo: ${(confidence_score * 100).toFixed(1)}%`;
        recommendationText.textContent = recomendacion_principal;

        // Renderizar barras de probabilidad
        probBars.innerHTML = '';
        Object.entries(probabilities).forEach(([cls, prob]) => {
            const pct = (prob * 100).toFixed(1);
            const probItem = document.createElement('div');
            probItem.className = 'prob-item';
            probItem.innerHTML = `
                <div class="prob-label">
                    <span>${cls}</span>
                    <span>${pct}%</span>
                </div>
                <div class="bar-bg">
                    <div class="bar-fill" style="width: ${pct}%"></div>
                </div>
            `;
            probBars.appendChild(probItem);
        });
    }
});
