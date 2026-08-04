<<<<<<< HEAD
// ============================================================
//  ITACA - App Frontend | Corporación Universitaria Iberoamericana
//  Scope: Funciones globales + lógica de formulario
// ============================================================

// Payloads precargados para la sustentación - scope GLOBAL
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

// Función global - accesible desde los onclick del HTML
=======
/* ============================================================
   SIAE / ITACA – Lógica del cliente web
   ============================================================ */

/* ── DATOS DE PRUEBA (scope global para acceso desde onclick HTML) ── */
const CASOS_DEMO = {
    inicial: {
        sector:                          "Manufactura",
        tamano_empresa:                  "Micro",
        porcentaje_procesos_documentados: 5,
        presupuesto_anual_tecnología:    3000000,
        respuesta_texto:
            "Todo lo anotamos en cuadernos y se nos pierde la información."
    },
    intermedio: {
        sector:                          "Comercio",
        tamano_empresa:                  "Pequeña",
        porcentaje_procesos_documentados: 35,
        presupuesto_anual_tecnología:    8000000,
        respuesta_texto:
            "Tenemos algunas herramientas digitales pero no están integradas."
    },
    optimizado: {
        sector:                          "Tecnología",
        tamano_empresa:                  "Grande",
        porcentaje_procesos_documentados: 92,
        presupuesto_anual_tecnología:    250000000,
        respuesta_texto:
            "Automatizamos el ciclo completo y medimos todo con tableros de control."
    }
};

/**
 * Carga un caso de demostración en el formulario.
 * Definida en scope global para que los botones onclick del HTML puedan accederla.
 * @param {string} nombreCaso - 'inicial' | 'intermedio' | 'optimizado'
 */
>>>>>>> a803204d3deb8f9f905ece8a7ba3342953caf5e4
function cargarCasoDemo(nombreCaso) {
    const c = CASOS_DEMO[nombreCaso];
    if (!c) return;

<<<<<<< HEAD
    document.getElementById('sector').value = c.sector;
    document.getElementById('tamano_empresa').value = c.tamano_empresa;
    document.getElementById('porcentaje_procesos_documentados').value = c.porcentaje_procesos_documentados;
    document.getElementById('presupuesto_anual_tecnología').value = c.presupuesto_anual_tecnología;
    document.getElementById('respuesta_texto').value = c.respuesta_texto;

    // Actualizar la etiqueta visual del rango
    const pctDisplay = document.getElementById('pctValue');
    if (pctDisplay) pctDisplay.textContent = `${c.porcentaje_procesos_documentados}%`;
}

// ============================================================
//  Lógica principal (DOM ready)
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    const form        = document.getElementById('diagnosisForm');
    const rangeInput  = document.getElementById('porcentaje_procesos_documentados');
    const pctValue    = document.getElementById('pctValue');
    const emptyState  = document.getElementById('emptyState');
=======
    document.getElementById('sector').value                          = c.sector;
    document.getElementById('tamano_empresa').value                  = c.tamano_empresa;
    document.getElementById('porcentaje_procesos_documentados').value = c.porcentaje_procesos_documentados;
    document.getElementById('presupuesto_anual_tecnología').value    = c.presupuesto_anual_tecnología;
    document.getElementById('respuesta_texto').value                 = c.respuesta_texto;

    // Sincronizar el badge del rango con el valor cargado
    const pctValue = document.getElementById('pctValue');
    if (pctValue) pctValue.textContent = `${c.porcentaje_procesos_documentados}%`;

    // Limpiar mensajes anteriores al cargar un demo
    ocultarMensajes();
}

/* ── LÓGICA PRINCIPAL (DOMContentLoaded) ─────────────────────── */
document.addEventListener('DOMContentLoaded', () => {

    /* Referencias DOM */
    const form           = document.getElementById('diagnosisForm');
    const rangeInput     = document.getElementById('porcentaje_procesos_documentados');
    const pctValue       = document.getElementById('pctValue');
    const emptyState     = document.getElementById('emptyState');
>>>>>>> a803204d3deb8f9f905ece8a7ba3342953caf5e4
    const resultsContent = document.getElementById('resultsContent');
    const levelBadge     = document.getElementById('levelBadge');
    const confidenceScore= document.getElementById('confidenceScore');
    const probBars       = document.getElementById('probBars');
    const recommendationText = document.getElementById('recommendationText');
    const submitBtn      = document.getElementById('submitBtn');
<<<<<<< HEAD

    const UMBRAL_CONFIANZA = 0.55;

    // ── Actualizar valor del rango en tiempo real ──
=======
    const avisoConfianza = document.getElementById('avisoConfianza');
    const mensajeError   = document.getElementById('mensajeError');

    const UMBRAL_CONFIANZA = 0.55; // Definido en las especificaciones del plan

    /* ── Helpers UI ────────────────────────────────────────────── */

    function ocultarMensajes() {
        avisoConfianza.style.display = 'none';
        avisoConfianza.textContent   = '';
        mensajeError.style.display   = 'none';
        mensajeError.textContent     = '';
    }

    function mostrarErrorUI(mensaje) {
        mensajeError.textContent     = mensaje;
        mensajeError.style.display   = 'block';
        mensajeError.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function setLoadingState(isLoading) {
        const btnText = submitBtn.querySelector('.btn-text');
        const spinner = submitBtn.querySelector('.spinner');

        submitBtn.disabled = isLoading;
        btnText.textContent = isLoading ? 'Procesando en IA...' : '⚡ Generar Diagnóstico IA';
        spinner.classList.toggle('hidden', !isLoading);
    }

    /* ── Sincronizar badge de rango ────────────────────────────── */
>>>>>>> a803204d3deb8f9f905ece8a7ba3342953caf5e4
    rangeInput.addEventListener('input', (e) => {
        pctValue.textContent = `${e.target.value}%`;
    });

<<<<<<< HEAD
    // ── Mostrar error inline (sin alert() nativo) ──
    function mostrarErrorUI(mensaje) {
        const contenedorError = document.getElementById('mensajeError');
        contenedorError.textContent = mensaje;
        contenedorError.style.display = 'block';
    }

    function ocultarError() {
        const contenedorError = document.getElementById('mensajeError');
        contenedorError.style.display = 'none';
        contenedorError.textContent = '';
    }

    // ── Spinner toggle ──
    function setLoading(isLoading) {
        const spinner = submitBtn.querySelector('.spinner');
        const btnText = submitBtn.querySelector('.btn-text');
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.textContent = 'Procesando en IA...';
            spinner.classList.remove('hidden');
        } else {
            submitBtn.disabled = false;
            btnText.textContent = '⚡ Generar Diagnóstico IA';
            spinner.classList.add('hidden');
        }
    }

    // ── Renderizar resultados ──
    function renderResults(data) {
        emptyState.classList.add('hidden');
        resultsContent.classList.remove('hidden');

        const { nivel_madurez, confidence_score, probabilities, recomendacion_principal } = data;

        // Badge de nivel con clase de color dinámica
        levelBadge.textContent = nivel_madurez;
        levelBadge.className = 'level-badge'; // reset
        const nivelSlug = nivel_madurez.toLowerCase().replace(/\s+/g, '-');
        levelBadge.classList.add(`nivel-${nivelSlug}`);

        // Puntaje de confianza
        confidenceScore.textContent = `Confianza del modelo: ${(confidence_score * 100).toFixed(1)}%`;

        // Aviso por baja confianza
        const aviso = document.getElementById('avisoConfianza');
        if (confidence_score < UMBRAL_CONFIANZA) {
            aviso.textContent = "⚠️ Diagnóstico preliminar: Se sugiere revisión manual por un consultor humano debido a baja certeza del modelo.";
            aviso.style.display = 'block';
        } else {
            aviso.style.display = 'none';
        }

        // Recomendación
        recommendationText.textContent = recomendacion_principal;

        // Barras de probabilidad
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
                    <div class="bar-fill" style="width: 0%"></div>
                </div>
            `;
            probBars.appendChild(probItem);
            // Animación diferida para que el CSS transition funcione
            requestAnimationFrame(() => {
                const barFill = probItem.querySelector('.bar-fill');
                if (barFill) barFill.style.width = `${pct}%`;
            });
        });
    }

    // ── Submit del formulario ──
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        ocultarError();
=======
    /* ── Envío del formulario ──────────────────────────────────── */
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        ocultarMensajes();

        const sector                        = document.getElementById('sector').value;
        const tamano_empresa                = document.getElementById('tamano_empresa').value;
        const porcentaje_procesos_documentados = parseFloat(rangeInput.value) / 100.0;
        const presupuesto_anual_tecnología  = parseFloat(document.getElementById('presupuesto_anual_tecnología').value);
        const respuesta_texto               = document.getElementById('respuesta_texto').value.trim();

        // Validación básica de campos requeridos
        if (!sector || !tamano_empresa || !respuesta_texto) {
            mostrarErrorUI('⚠️ Por favor complete todos los campos obligatorios antes de continuar.');
            return;
        }
>>>>>>> a803204d3deb8f9f905ece8a7ba3342953caf5e4

        const payload = {
            sector:                            document.getElementById('sector').value,
            tamano_empresa:                    document.getElementById('tamano_empresa').value,
            porcentaje_procesos_documentados:  parseFloat(rangeInput.value) / 100.0,
            presupuesto_anual_tecnología:      parseFloat(document.getElementById('presupuesto_anual_tecnología').value),
            respuesta_texto:                   document.getElementById('respuesta_texto').value
        };

<<<<<<< HEAD
        setLoading(true);
=======
        setLoadingState(true);
>>>>>>> a803204d3deb8f9f905ece8a7ba3342953caf5e4

        try {
            const response = await fetch('http://localhost:8000/predict', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `Error del servidor (HTTP ${response.status})`);
            }

            const data = await response.json();
            renderResults(data);

        } catch (error) {
<<<<<<< HEAD
            mostrarErrorUI(`⚠️ No se pudo obtener la predicción: ${error.message}. Asegúrese de que la API esté corriendo con 'python scripts/serve.py'`);
        } finally {
            setLoading(false);
        }
    });
});
=======
            mostrarErrorUI(
                `⚠️ No se pudo obtener la predicción: ${error.message}. ` +
                `Asegúrese de que la API esté activa ('python scripts/serve.py').`
            );
        } finally {
            setLoadingState(false);
        }
    });

    /* ── Renderizar resultados ─────────────────────────────────── */
    function renderResults(data) {
        const { nivel_madurez, confidence_score, probabilities, recomendacion_principal } = data;

        /* Mostrar sección de resultados */
        emptyState.classList.add('hidden');
        resultsContent.classList.remove('hidden');
        resultsContent.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        /* Nivel de madurez */
        levelBadge.textContent           = nivel_madurez;
        levelBadge.dataset.level         = nivel_madurez;  // Para el CSS data-level dinámico
        confidenceScore.textContent      = `Confianza del modelo: ${(confidence_score * 100).toFixed(1)}%`;
        recommendationText.textContent   = recomendacion_principal;

        /* Alerta por baja confianza */
        if (confidence_score < UMBRAL_CONFIANZA) {
            avisoConfianza.textContent  =
                '⚠️ Diagnóstico preliminar: Se sugiere revisión manual por un consultor humano debido a baja certeza del modelo.';
            avisoConfianza.style.display = 'block';
        }

        /* Barras de probabilidad */
        probBars.innerHTML = '';
        if (probabilities && typeof probabilities === 'object') {
            Object.entries(probabilities).forEach(([cls, prob]) => {
                const pct     = (prob * 100).toFixed(1);
                const probItem = document.createElement('div');
                probItem.className = 'prob-item';
                probItem.innerHTML = `
                    <div class="prob-label">
                        <span>${cls}</span>
                        <span>${pct}%</span>
                    </div>
                    <div class="bar-bg">
                        <div class="bar-fill" style="width: 0%"></div>
                    </div>
                `;
                probBars.appendChild(probItem);

                /* Animar la barra con requestAnimationFrame para activar la transición CSS */
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        probItem.querySelector('.bar-fill').style.width = `${pct}%`;
                    });
                });
            });
        }
    }

}); // fin DOMContentLoaded
>>>>>>> a803204d3deb8f9f905ece8a7ba3342953caf5e4
