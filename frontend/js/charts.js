/* ============================================================
   SIAE / ITACA – Gráficas comparativas por sector
   SVG generado a mano: sin dependencias externas, funciona
   offline dentro del contenedor nginx.
   ============================================================ */

/* Color de cada nivel de madurez (coherente con .level-badge del CSS) */
const COLORES_NIVEL = {
    'Inicial':       '#ED202D',
    'En Desarrollo': '#FFD600',
    'Definido':      '#23C2E8',
    'Optimizado':    '#10b981'
};

/* Color de texto legible sobre cada color de nivel */
const TEXTO_SOBRE_NIVEL = {
    'Inicial':       '#FFFFFF',
    'En Desarrollo': '#1A1B1C',
    'Definido':      '#1A1B1C',
    'Optimizado':    '#FFFFFF'
};

const COLOR_PROMEDIO = 'rgba(241, 240, 239, 0.35)';

/** Escapa texto que se inserta en el SVG. */
function esc(texto) {
    return String(texto)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

/** Construye la leyenda HTML compartida por las gráficas. */
function construirLeyenda(items) {
    const entradas = items.map(({ etiqueta, color }) => `
        <span class="chart-legend-item">
            <span class="chart-legend-swatch" style="background:${esc(color)}"></span>
            ${esc(etiqueta)}
        </span>
    `).join('');
    return `<div class="chart-legend">${entradas}</div>`;
}

/**
 * Gráfica 1 — Barras apiladas al 100%: distribución de niveles de madurez
 * por sector. Resalta el sector de la empresa evaluada si se indica.
 *
 * @param {string} contenedorId  Id del contenedor destino
 * @param {object} stats         Respuesta de /stats/sectores
 * @param {string|null} sectorDestacado Sector a resaltar
 */
function renderDistribucionSectores(contenedorId, stats, sectorDestacado = null) {
    const cont = document.getElementById(contenedorId);
    if (!cont) return;

    const sectores = stats.sectores || [];
    const clases   = stats.clases || [];

    if (!sectores.length) {
        cont.innerHTML = '<p class="chart-empty">No hay datos de referencia disponibles.</p>';
        return;
    }

    /* Geometría */
    const W        = 640;
    const barX     = 128;
    const rightPad = 54;
    const barW     = W - barX - rightPad;
    const rowH     = 30;
    const gap      = 14;
    const H        = sectores.length * (rowH + gap) - gap;

    let defs  = '';
    let filas = '';

    sectores.forEach((sector, i) => {
        const y   = i * (rowH + gap);
        const pct = (stats.distribucion_pct || {})[sector] || {};
        const tot = (stats.total_por_sector || {})[sector] || 0;
        const esDestacado = sector === sectorDestacado;

        const clipId = `clip-${contenedorId}-${i}`;
        defs += `<clipPath id="${clipId}"><rect x="${barX}" y="${y}" width="${barW}" height="${rowH}" rx="6"/></clipPath>`;

        /* Fondo de resalte para el sector de la empresa evaluada */
        if (esDestacado) {
            filas += `<rect x="0" y="${y - 5}" width="${W}" height="${rowH + 10}"
                        rx="8" fill="rgba(35,194,232,0.10)" stroke="rgba(35,194,232,0.45)"/>`;
        }

        /* Etiqueta del sector */
        filas += `<text x="${barX - 14}" y="${y + rowH / 2}" text-anchor="end"
                    dominant-baseline="central" class="chart-label${esDestacado ? ' is-highlight' : ''}">
                    ${esc(sector)}</text>`;

        /* Segmentos apilados */
        let x = barX;
        let segmentos = '';
        clases.forEach((clase) => {
            const valor = Number(pct[clase] || 0);
            const w = valor / 100 * barW;
            if (w <= 0) return;

            segmentos += `<rect x="${x}" y="${y}" width="${w}" height="${rowH}"
                            fill="${COLORES_NIVEL[clase] || '#888'}">
                            <title>${esc(sector)} · ${esc(clase)}: ${valor}%</title>
                          </rect>`;

            if (w > 36) {
                segmentos += `<text x="${x + w / 2}" y="${y + rowH / 2}"
                                text-anchor="middle" dominant-baseline="central"
                                class="chart-seg-label" fill="${TEXTO_SOBRE_NIVEL[clase] || '#fff'}">
                                ${Math.round(valor)}%</text>`;
            }
            x += w;
        });

        filas += `<g clip-path="url(#${clipId})">${segmentos}</g>`;

        /* Total de empresas del sector */
        filas += `<text x="${W - 6}" y="${y + rowH / 2}" text-anchor="end"
                    dominant-baseline="central" class="chart-total">n=${tot}</text>`;
    });

    const leyenda = construirLeyenda(
        clases.map(c => ({ etiqueta: c, color: COLORES_NIVEL[c] || '#888' }))
    );

    cont.innerHTML = leyenda + `
        <svg viewBox="0 0 ${W} ${H}" class="chart-svg" role="img"
             aria-label="Distribución porcentual de niveles de madurez digital por sector económico">
            <defs>${defs}</defs>
            ${filas}
        </svg>`;
}

/**
 * Gráfica 2 — Barras agrupadas: compara la distribución del sector
 * seleccionado contra el promedio de todos los sectores.
 *
 * @param {string} contenedorId Id del contenedor destino
 * @param {object} stats        Respuesta de /stats/sectores
 * @param {string} sector       Sector a comparar
 * @param {string|null} nivelPredicho Nivel de la empresa, para marcarlo
 */
function renderComparativaSector(contenedorId, stats, sector, nivelPredicho = null) {
    const cont = document.getElementById(contenedorId);
    if (!cont) return;

    const clases = stats.clases || [];
    const pctSector = (stats.distribucion_pct || {})[sector];

    if (!sector) {
        cont.innerHTML = '<p class="chart-empty">Seleccione un sector para ver la comparativa.</p>';
        return;
    }

    if (!pctSector) {
        cont.innerHTML = `<p class="chart-empty">No hay datos de referencia para el sector
            &quot;${esc(sector)}&quot; en la muestra actual.</p>`;
        return;
    }

    /* Distribución global: se recalcula sobre los conteos absolutos */
    const totalGlobal = Object.values(stats.total_por_sector || {})
        .reduce((a, b) => a + b, 0);
    const pctGlobal = {};
    clases.forEach((clase) => {
        const suma = Object.values(stats.distribucion || {})
            .reduce((acc, d) => acc + Number(d[clase] || 0), 0);
        pctGlobal[clase] = totalGlobal ? (suma / totalGlobal * 100) : 0;
    });

    /* Geometría */
    const W = 640, H = 250;
    const padL = 42, padR = 12, padT = 14, padB = 46;
    const plotW = W - padL - padR;
    const plotH = H - padT - padB;

    const maxVal = Math.max(
        ...clases.map(c => Math.max(Number(pctSector[c] || 0), pctGlobal[c]))
    );
    const yMax = Math.max(10, Math.ceil(maxVal / 10) * 10);
    const escalaY = (v) => plotH - (v / yMax) * plotH;

    /* Rejilla y eje Y */
    let grid = '';
    for (let i = 0; i <= 4; i++) {
        const v = yMax * i / 4;
        const y = padT + escalaY(v);
        grid += `<line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}"
                   stroke="rgba(241,240,239,0.10)" stroke-width="1"/>`;
        grid += `<text x="${padL - 8}" y="${y}" text-anchor="end"
                   dominant-baseline="central" class="chart-axis">${Math.round(v)}%</text>`;
    }

    /* Barras agrupadas */
    const grupoW = plotW / clases.length;
    const barraW = Math.min(38, grupoW / 3);
    let barras = '';

    clases.forEach((clase, i) => {
        const cx = padL + grupoW * i + grupoW / 2;
        const vSector = Number(pctSector[clase] || 0);
        const vGlobal = pctGlobal[clase];

        const xS = cx - barraW - 3;
        const xG = cx + 3;
        const yS = padT + escalaY(vSector);
        const yG = padT + escalaY(vGlobal);

        const esNivelPredicho = clase === nivelPredicho;

        if (esNivelPredicho) {
            barras += `<rect x="${cx - grupoW / 2 + 4}" y="${padT - 4}"
                         width="${grupoW - 8}" height="${plotH + 8}"
                         rx="6" fill="rgba(35,194,232,0.08)"/>`;
        }

        barras += `<rect x="${xS}" y="${yS}" width="${barraW}" height="${padT + plotH - yS}"
                     rx="4" fill="${COLORES_NIVEL[clase] || '#888'}">
                     <title>${esc(sector)} · ${esc(clase)}: ${vSector.toFixed(1)}%</title>
                   </rect>`;
        barras += `<rect x="${xG}" y="${yG}" width="${barraW}" height="${padT + plotH - yG}"
                     rx="4" fill="${COLOR_PROMEDIO}">
                     <title>Promedio general · ${esc(clase)}: ${vGlobal.toFixed(1)}%</title>
                   </rect>`;

        /* Etiqueta del nivel */
        barras += `<text x="${cx}" y="${padT + plotH + 18}" text-anchor="middle"
                     class="chart-axis${esNivelPredicho ? ' is-highlight' : ''}">
                     ${esc(clase)}</text>`;

        if (esNivelPredicho) {
            barras += `<text x="${cx}" y="${padT + plotH + 34}" text-anchor="middle"
                         class="chart-marker">▲ su empresa</text>`;
        }
    });

    /* La barra del sector se colorea por nivel, de ahí el degradado en la leyenda */
    const degradadoNiveles = 'linear-gradient(90deg,' + clases.map((c, i) => {
        const desde = (i / clases.length * 100).toFixed(0);
        const hasta = ((i + 1) / clases.length * 100).toFixed(0);
        return `${COLORES_NIVEL[c] || '#888'} ${desde}% ${hasta}%`;
    }).join(',') + ')';

    const leyenda = construirLeyenda([
        { etiqueta: sector, color: degradadoNiveles },
        { etiqueta: 'Promedio general', color: COLOR_PROMEDIO }
    ]);

    cont.innerHTML = leyenda + `
        <svg viewBox="0 0 ${W} ${H}" class="chart-svg" role="img"
             aria-label="Comparación de la distribución de madurez del sector ${esc(sector)} frente al promedio general">
            ${grid}
            ${barras}
            <line x1="${padL}" y1="${padT + plotH}" x2="${W - padR}" y2="${padT + plotH}"
                  stroke="rgba(241,240,239,0.25)" stroke-width="1"/>
        </svg>`;
}
