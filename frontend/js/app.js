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

/* ── Alertas globales (usadas también por cargarCasoDemo) ─────── */
const avisoConfianza = document.getElementById('avisoConfianza');
const mensajeError   = document.getElementById('mensajeError');

function ocultarMensajes() {
    avisoConfianza.style.display = 'none';
    avisoConfianza.textContent   = '';
    mensajeError.style.display   = 'none';
    mensajeError.textContent     = '';
}

/* ── DASHBOARD COMPARATIVO ───────────────────────────────────── */

const API_BASE = 'http://localhost:8000';

let statsSectoriales = null;   // Respuesta cacheada de /stats/sectores
let sectorSeleccionado = null; // Sector elegido en el formulario
let nivelPredicho = null;      // Nivel devuelto por el último diagnóstico

/** Redibuja ambas gráficas con el estado actual de selección. */
function actualizarGraficas() {
    if (!statsSectoriales || !statsSectoriales.disponible) return;

    renderDistribucionSectores('chartDistribucion', statsSectoriales, sectorSeleccionado);
    renderComparativaSector('chartComparativa', statsSectoriales, sectorSeleccionado, nivelPredicho);

    const titulo = document.getElementById('chartComparativaTitle');
    if (titulo) {
        titulo.textContent = sectorSeleccionado
            ? `${sectorSeleccionado} frente al promedio general`
            : 'Su sector frente al promedio general';
    }
}

/** Registra el sector elegido y refresca el dashboard. */
function seleccionarSector(sector) {
    sectorSeleccionado = sector || null;
    actualizarGraficas();
}

/**
 * Carga un caso de demostración en el formulario.
 * Definida en scope global para que los botones onclick del HTML puedan accederla.
 * @param {string} nombreCaso - 'inicial' | 'intermedio' | 'optimizado'
 */
function cargarCasoDemo(nombreCaso) {
    const c = CASOS_DEMO[nombreCaso];
    if (!c) return;

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

    // El caso demo cambia el sector por asignación directa, que no dispara
    // el evento 'change' del <select>; hay que refrescar el dashboard a mano.
    nivelPredicho = null;
    seleccionarSector(c.sector);
}

/* ── LÓGICA PRINCIPAL (DOMContentLoaded) ─────────────────────── */
document.addEventListener('DOMContentLoaded', () => {

    /* Referencias DOM */
    const form            = document.getElementById('diagnosisForm');
    const rangeInput      = document.getElementById('porcentaje_procesos_documentados');
    const pctValue        = document.getElementById('pctValue');
    const emptyState      = document.getElementById('emptyState');
    const resultsContent  = document.getElementById('resultsContent');
    const levelBadge      = document.getElementById('levelBadge');
    const confidenceScore = document.getElementById('confidenceScore');
    const probBars        = document.getElementById('probBars');
    const recommendationText = document.getElementById('recommendationText');
    const submitBtn       = document.getElementById('submitBtn');

    const UMBRAL_CONFIANZA = 0.55; // Definido en las especificaciones del plan

    /* ── Helpers UI ────────────────────────────────────────────── */

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
    rangeInput.addEventListener('input', (e) => {
        pctValue.textContent = `${e.target.value}%`;
    });

    /* ── Dashboard: cargar referencia y reaccionar al sector ───── */
    document.getElementById('sector').addEventListener('change', (e) => {
        nivelPredicho = null;
        seleccionarSector(e.target.value);
    });

    (async function cargarStatsSectoriales() {
        const contDist = document.getElementById('chartDistribucion');
        try {
            const res = await fetch(`${API_BASE}/stats/sectores`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            statsSectoriales = await res.json();

            if (!statsSectoriales.disponible) {
                contDist.innerHTML =
                    '<p class="chart-empty">El dataset de referencia no está disponible en el servidor.</p>';
                return;
            }

            const desc = document.getElementById('dashboardDesc');
            if (desc) {
                desc.textContent =
                    `Distribución de la madurez digital en ${statsSectoriales.total_empresas} ` +
                    `empresas de referencia, agrupadas en ${statsSectoriales.sectores.length} sectores.`;
            }

            seleccionarSector(document.getElementById('sector').value || null);
        } catch (err) {
            contDist.innerHTML =
                '<p class="chart-empty">No se pudieron cargar los datos de referencia. ' +
                'Verifique que la API esté activa.</p>';
        }
    })();

    /* ── Envío del formulario ──────────────────────────────────── */
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        ocultarMensajes();

        const sector                           = document.getElementById('sector').value;
        const tamano_empresa                   = document.getElementById('tamano_empresa').value;
        const porcentaje_procesos_documentados = parseFloat(rangeInput.value) / 100.0;
        const presupuesto_anual_tecnología     = parseFloat(document.getElementById('presupuesto_anual_tecnología').value);
        const respuesta_texto                  = document.getElementById('respuesta_texto').value.trim();

        // Validación básica de campos requeridos
        if (!sector || !tamano_empresa || !respuesta_texto) {
            mostrarErrorUI('⚠️ Por favor complete todos los campos obligatorios antes de continuar.');
            return;
        }

        const payload = {
            sector,
            tamano_empresa,
            porcentaje_procesos_documentados,
            presupuesto_anual_tecnología,
            respuesta_texto
        };

        setLoadingState(true);

        try {
            const response = await fetch(`${API_BASE}/predict`, {
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

        /* Situar el diagnóstico dentro del dashboard comparativo */
        nivelPredicho = nivel_madurez;
        seleccionarSector(document.getElementById('sector').value);

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
