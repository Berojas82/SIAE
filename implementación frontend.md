# Plan de Acción: Mejora de Interfaz Gráfica SIAE (ITACA)

## Descripción General

El frontend actual de **ITACA** (Sistema Inteligente de Autodiagnóstico Empresarial) tiene una base glassmorphism funcional, pero presenta varios problemas críticos que se deben corregir:

1. **Variables CSS inconsistentes**: Se referencian variables inexistentes (`--bg-dark`, `--card-bg`, `--border-color`, `--text-muted`, `--primary`, `--accent`) que nunca fueron definidas en `:root`, lo que rompe el diseño visualmente.
2. **Paleta corporativa no aplicada**: Los colores definidos por la institución (`#ED202D`, `#23C2E8`, `#353638`, `#FFD600`, `#F1F0EF`) no están siendo utilizados de forma coherente.
3. **Modo oscuro sin fondo definido**: El `body` referencia `var(--bg-dark)` que no existe → fondo completamente transparente/blanco en los navegadores.
4. **Lógica JS incompleta**: `cargarCasoDemo` y `procesarRespuestaAPI` están definidas en dos ámbitos distintos y hay referencias a IDs inexistentes (`nivelMadurez`, `recomendacion`).
5. **Diseño poco diferenciado**: El header no expresa la identidad de la Corporación Iberoamericana; los botones demo carecen de estilo corporativo.
6. **Sin feedback visual en loading**: El spinner existe en HTML pero no tiene animación CSS definida.
7. **Nota ética con inline styles**: Mezcla de estilos inline que dificultan el mantenimiento.

---

## Decisiones de Diseño

> [!IMPORTANT]
> El nuevo diseño adoptará un **modo oscuro elegante** usando `--dark-anthracite (#353638)` como fondo base, con acentos en `--primary-red (#ED202D)` para acciones principales y `--accent-cyan (#23C2E8)` para elementos interactivos de IA. El fondo `--light-gray (#F1F0EF)` se usará para componentes de contraste (badges, inputs).

> [!NOTE]
> La paleta completa que se respetará estrictamente:
> - 🔴 **Primary** `#ED202D` → botón principal, alertas de error, borde activo
> - 🔵 **Secondary** `#23C2E8` → badges de IA, barras de probabilidad activas, enlaces
> - ⚫ **Text** `#353638` → fondo del body y cards oscuros
> - 🟡 **Accent** `#FFD600` → alertas de baja confianza, highlights de recomendación
> - ⚪ **Surface** `#F1F0EF` → fondo de inputs, superficies claras, texto en fondos oscuros

---

## Cambios Propuestos

### 1. Sistema de Tokens CSS

#### [MODIFY] [styles.css](file:///c:/Users/beroj/OneDrive%20-%20Corporacion%20Universitaria%20Iberoamericana/SIAE/frontend/css/styles.css)

Reescribir completamente el `:root` para:
- Definir **todas** las variables corporativas con alias semánticos
- Eliminar referencias a variables inexistentes
- Añadir tokens de sombra, gradientes y transiciones coherentes

**Nuevas variables a definir:**
```css
:root {
  /* Paleta Corporativa Oficial */
  --color-primary:   #ED202D;   /* Rojo ITACA - acciones principales */
  --color-secondary: #23C2E8;   /* Cian IA - elementos interactivos */
  --color-text:      #353638;   /* Antracita - fondos oscuros */
  --color-accent:    #FFD600;   /* Amarillo - alertas y recomendaciones */
  --color-surface:   #F1F0EF;   /* Gris claro - superficies, inputs */

  /* Tokens semánticos (derivados de la paleta) */
  --bg-body:         #1E1F20;        /* Fondo principal ligeramente más oscuro que antracita */
  --bg-card:         rgba(53,54,56,0.85);  /* Card glassmorphism */
  --bg-card-inner:   rgba(30,31,32,0.6);  /* Secciones internas */
  --border-color:    rgba(241,240,239,0.12);
  --border-active:   var(--color-primary);
  --text-main:       var(--color-surface);
  --text-muted:      rgba(241,240,239,0.55);
  --primary:         var(--color-primary);
  --accent:          var(--color-secondary);

  /* Sombras */
  --shadow-card:     0 20px 40px rgba(0,0,0,0.4);
  --shadow-glow-red: 0 0 20px rgba(237,32,45,0.3);
  --shadow-glow-cyan:0 0 20px rgba(35,194,232,0.3);
}
```

---

### 2. Fondo y Decoración

#### [MODIFY] [styles.css](file:///c:/Users/beroj/OneDrive%20-%20Corporacion%20Universitaria%20Iberoamericana/SIAE/frontend/css/styles.css)

- **Body**: cambiar fondo a `var(--bg-body)` (#1E1F20)
- **`.background-decor`**: reemplazar el gradiente gris neutro por uno usando la paleta corporativa:
  ```css
  background: radial-gradient(ellipse at 30% 20%,
    rgba(237,32,45,0.15) 0%,
    rgba(35,194,232,0.1) 40%,
    transparent 70%);
  ```
- Añadir un segundo orbe decorativo cyan con `::after` o un segundo div para profundidad visual.

---

### 3. Header y Logo Badge

#### [MODIFY] [index.html](file:///c:/Users/beroj/OneDrive%20-%20Corporacion%20Universitaria%20Iberoamericana/SIAE/frontend/index.html)

- Actualizar el **logo-badge** con borde del color `--color-secondary` en lugar del violet (`rgba(139, 92, 246, 0.3)`)
- Añadir el sub-brand "Corporación Universitaria Iberoamericana" debajo del H1
- El `h1` pasará de gradiente blanco-slate a gradiente `#F1F0EF → #23C2E8` (de blanco corporativo a cyan IA)

#### [MODIFY] [styles.css](file:///c:/Users/beroj/OneDrive%20-%20Corporacion%20Universitaria%20Iberoamericana/SIAE/frontend/css/styles.css)

```css
h1 {
  background: linear-gradient(135deg, var(--color-surface) 0%, var(--color-secondary) 100%);
  /* reemplaza el gradiente white→slate actual */
}
.logo-badge {
  border-color: rgba(35,194,232,0.4); /* cyan en lugar de violet */
  background: rgba(35,194,232,0.08);
}
```

---

### 4. Cards y Formulario

#### [MODIFY] [styles.css](file:///c:/Users/beroj/OneDrive%20-%20Corporacion%20Universitaria%20Iberoamericana/SIAE/frontend/css/styles.css)

- `.card`: fondo → `var(--bg-card)`, sombra → `var(--shadow-card)`
- Inputs/selects/textarea: fondo → `var(--bg-card-inner)`, color texto → `var(--text-main)`, focus border → `var(--color-secondary)`
- `.badge` del rango: fondo → `rgba(35,194,232,0.2)`, color → `var(--color-secondary)`

---

### 5. Botones

#### [MODIFY] [styles.css](file:///c:/Users/beroj/OneDrive%20-%20Corporacion%20Universitaria%20Iberoamericana/SIAE/frontend/css/styles.css)

**Botón primario** (Generar Diagnóstico):
```css
.btn-primary {
  background: linear-gradient(135deg, var(--color-primary) 0%, #C41020 100%);
  box-shadow: var(--shadow-glow-red);
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 30px rgba(237,32,45,0.5);
}
```

**Botones demo** (Caso 1/2/3): Añadir estilo dedicado con borde cyan, fondo semitransparente y efecto hover con glow cyan.
```css
.btn-demo {
  border: 1px solid rgba(35,194,232,0.4);
  background: rgba(35,194,232,0.08);
  color: var(--color-secondary);
  /* + transición hover con glow */
}
```

---

### 6. Sección de Resultados

#### [MODIFY] [styles.css](file:///c:/Users/beroj/OneDrive%20-%20Corporacion%20Universitaria%20Iberoamericana/SIAE/frontend/css/styles.css)

- `.result-badge-container`: borde → `var(--border-color)`, fondo → `var(--bg-card-inner)`
- `.bar-fill`: degradado de rojo a cyan según valor (`--color-primary` → `--color-secondary`)
- `.recommendation-box`: reemplazar violet (`rgba(139,92,246,...)`) por amarillo corporativo:
  ```css
  .recommendation-box {
    background: rgba(255,214,0,0.08);
    border-color: rgba(255,214,0,0.35);
  }
  .recommendation-box h4 { color: var(--color-accent); }
  ```
- `.level-badge`: añadir color dinámico por nivel (Inicial → rojo, Intermedio → amarillo, Optimizado → cyan)

---

### 7. Spinner de Carga

#### [MODIFY] [styles.css](file:///c:/Users/beroj/OneDrive%20-%20Corporacion%20Universitaria%20Iberoamericana/SIAE/frontend/css/styles.css)

El elemento `.spinner` existe en el HTML pero no tiene CSS. Añadir:
```css
.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
  vertical-align: middle;
}
@keyframes spin { to { transform: rotate(360deg); } }
```

#### [MODIFY] [app.js](file:///c:/Users/beroj/OneDrive%20-%20Corporacion%20Universitaria%20Iberoamericana/SIAE/frontend/js/app.js)

Activar/desactivar el spinner al hacer submit:
```js
submitBtn.querySelector('.spinner').classList.toggle('hidden');
```

---

### 8. Correcciones de Bugs JS

#### [MODIFY] [app.js](file:///c:/Users/beroj/OneDrive%20-%20Corporacion%20Universitaria%20Iberoamericana/SIAE/frontend/js/app.js)

- **`cargarCasoDemo`**: Actualmente definida dentro del `DOMContentLoaded` pero llamada con `onclick` en el HTML (scope global). Mover al scope global o usar event listeners.
- **IDs incorrectos en `procesarRespuestaAPI`**: `nivelMadurez` → `levelBadge`, `recomendacion` → `recommendationText` (para que coincidan con el HTML real).
- **`alert()` nativo**: Reemplazar por `mostrarErrorUI()` que ya existe pero no se usa en el `catch`.
- **Ocultar error previo al nuevo submit**: Limpiar `mensajeError` al inicio de cada submit.

---

### 9. Nota Ética y Alerta de Confianza

#### [MODIFY] [index.html](file:///c:/Users/beroj/OneDrive%20-%20Corporacion%20Universitaria%20Iberoamericana/SIAE/frontend/index.html)

- Eliminar inline styles de `#avisoConfianza`, `#mensajeError`, `.nota-etica`
- Mover esos estilos a `styles.css` con las variables corporativas

#### [MODIFY] [styles.css](file:///c:/Users/beroj/OneDrive%20-%20Corporacion%20Universitaria%20Iberoamericana/SIAE/frontend/css/styles.css)

```css
.alert-box {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: rgba(255,214,0,0.15);
  border: 1px solid var(--color-accent);
  color: var(--color-accent);
}
.error-box {
  color: var(--color-primary);
  background: rgba(237,32,45,0.1);
  border: 1px solid rgba(237,32,45,0.3);
  border-radius: 8px;
  padding: 0.75rem 1rem;
}
.nota-etica {
  color: var(--text-muted);
  font-size: 0.82rem;
  text-align: center;
  margin-top: 1.5rem;
}
```

---

## Plan de Verificación

### Verificación Manual
1. Abrir `frontend/index.html` directamente en el navegador (o vía Docker `http://localhost:80`)
2. Confirmar que el **fondo oscuro** se renderiza correctamente (sin blanco)
3. Confirmar que todos los colores de la paleta corporativa son visibles
4. Probar los **botones demo** (Caso 1/2/3) y verificar que cargan datos
5. Hacer submit y verificar el **spinner** de carga + resultados con barras de probabilidad
6. Simular error de red y confirmar que aparece el mensaje inline (sin `alert()` nativo)

### Validación CSS
- Confirmar que **ninguna** variable CSS indefinida queda referenciada
- Verificar en DevTools > Computed Styles que todos los `var(--xxx)` resuelven a un valor real

### Responsive
- Verificar en viewport < 868px que el grid pasa a 1 columna correctamente

---

## Preguntas Abiertas

> [!IMPORTANT]
> **¿Deseas conservar el modo oscuro actual o prefieres una versión Light Mode** usando `--light-gray (#F1F0EF)` como fondo principal? El plan actual propone **dark mode** por defecto.

> [!NOTE]
> **¿El logo institucional de la Corporación Universitaria Iberoamericana debe aparecer en el header?** Si es así, comparte el archivo de imagen para integrarlo, o lo generaré con IA.

> [!NOTE]
> **¿Se deben añadir más sectores económicos al formulario?** Actualmente solo tiene: Tecnología, Manufactura, Retail, Servicios, Salud. La demo carga "Comercio" que no existe en la lista.
