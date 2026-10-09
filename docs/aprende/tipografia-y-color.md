# Aprende: tipografía, color y la forma decorativa en Lumea

**Para Isabella.** Hoy tus archivos son `estilos/tokens.css`, `estilos/paletas.css` y la carpeta `estilos/fuentes/`. Claude Code no los toca en esta misión, así que puedes trabajar al mismo tiempo que él.

## 1. Cómo está hecho hoy (lee esto primero)

- **Una sola familia de letra.** Es *Bricolage Grotesque*: está guardada en `estilos/fuentes/` (licencia OFL) y se usa por medio de `--f-familia` en `tokens.css`.
- **Una escala de tamaños** con razón fija de unos 1,25 (una «tercera mayor»): 16 → 20 → 25 → 31 → 49 px (`--t-m` a `--t-3xl`).
  - *Pregunta:* ¿qué ganas al usar una razón fija en lugar de elegir cada tamaño «a ojo»?
- **Tres pesos:** 400, 560 y 720 (`--t-peso-*`).
- **El color va por roles, no por colores sueltos.** Cada paleta de `paletas.css` define familias de roles: `comida`, `emocion`, `mision`, `logro`, `marca`… Cada rol tiene cuatro pasos:

  | Paso | Para qué sirve |
  |---|---|
  | `--c-comida` | el color fuerte (botones, barras, chips) |
  | `--c-comida-suave` | un fondo pastel |
  | `--c-comida-contenedor` | el mismo tono, un paso más oscuro |
  | `--c-comida-tinta` | el texto que va sobre lo suave |

  Los componentes usan los roles. Por eso, si cambias un valor aquí, cambia en toda la app.
- **Enchufes nuevos** (los agrega Claude Code en P1): `--f-titulos` (los títulos) y `--f-cifras` (los números que importan). Si no los defines, todo sigue con `--f-familia`.

## 2. Tipografía: tres decisiones

### Decisión 1: ¿una familia o dos?

La regla: **máximo dos, y que se distingan claramente.**

- **Opción A (la que yo probaría):**
  - Bricolage para los títulos, porque tiene personalidad.
  - *Atkinson Hyperlegible Next* para las cifras (y, si te gusta, para el cuerpo).
  - La razón tiene evidencia detrás: el Braille Institute diseñó Atkinson Hyperlegible (2019) para que los caracteres parecidos no se confundan (I, l y 1; 0 y O; B y 8), pensando en lectores con baja visión. La versión *Next* (2025) tiene más pesos.
  - En la información nutricional, confundir un 1 con un 7 importa.
- **Opción B:** Bricolage en todo, y solo cifras tabulares en los números.

*Pregunta:* Lumea, ¿habla como una amiga mayor, como una científica o como un juego? ¿Cuál de las dos opciones suena así?

### Decisión 2: la información nutricional no se ve plana si hay jerarquía, no si todo es más grande

- **Ya decidiste algo:** las calorías van en **una línea secundaria**.
  - *Pregunta:* si ahora las vuelves enormes, ¿qué mensaje le das a una persona de 12 años?
- **El orden de lectura que propongo:**
  1. el nombre del alimento (`--t-3xl`), que es el protagonista;
  2. los bloques de consejo (con la forma decorativa, sección 4);
  3. las calorías, con `.cifra` y en tamaño secundario.
- **Número grande y unidad pequeña:** «391» en peso fuerte y «kcal» en `--t-s` con `--c-tinta-suave`. El ojo lee primero el número sin esfuerzo, y la unidad no compite.
- **Cifras tabulares** (`tabular-nums`): todos los dígitos ocupan el mismo ancho. Así, en una lista los números quedan alineados. El enchufe `.cifra` ya lo trae.

### Decisión 3: medidas que no se negocian

- **Cuerpo de texto:** 16 px o más.
- **Líneas de 45 a 75 caracteres** (Bringhurst, *The Elements of Typographic Style*). Lumea ya usa `max-width: 65ch`.
- **Interlineado:** 1,5 en el cuerpo (WCAG 2.1, criterio 1.4.12) y entre 1,1 y 1,2 en los títulos.

### Paso a paso: cambiar la letra

1. **Elige** en Google Fonts. Prueba la letra con español de verdad: «¿Sabías que el ñame…? ¡Qué rico!» (tildes, eñe, ¿ y ¡).
2. **Descárgala en `.woff2`.** En `gwfh.mranftl.com` (google-webfonts-helper): busca la letra, marca el juego de caracteres *latin* y los pesos que necesitas, y descarga los archivos para navegadores modernos.
   - Copia el `.woff2` a `estilos/fuentes/`.
   - Copia también su licencia OFL como `OFL-<nombre>.txt`, igual que la de Bricolage.
3. **Declárala.** En `tokens.css`, copia el bloque `@font-face` de Bricolage y cambia el nombre de la letra y el archivo. Deja `font-display: swap`.
4. **Usa los enchufes,** dentro de `:root` en `tokens.css`:
   ```css
   --f-titulos: "Bricolage Grotesque", system-ui, sans-serif;
   --f-cifras: "Atkinson Hyperlegible Next", system-ui, sans-serif;
   ```
5. **Mírala en Safari.** Vacía las cachés con Opción + Cmd + E y recarga con Cmd + R. Revisa `sistema-diseno.html`, el resultado de Registrar y Progreso, en el computador y en tamaño de celular.
6. **Haz commit solo de lo tuyo:**
   ```
   git add estilos/tokens.css estilos/fuentes/<archivo>.woff2 estilos/fuentes/OFL-<nombre>.txt
   git commit -m "Tipografía: <lo que cambiaste y por qué>"
   ```
   Nunca uses `git add -A`.

## 3. Color

- **60-30-10:**
  - 60 % son superficies tranquilas (blanco y casi neutro);
  - 30 % son apoyos (bordes y fondos suaves);
  - 10 % es el acento (el botón principal, las barras, los chips).

  Es la Dirección 1 de Lumea: el color se nota porque es escaso.
- **El contraste mínimo** (WCAG 2.1):

  | Qué | Mínimo | Criterio |
  |---|---|---|
  | Texto normal | **4,5:1** | 1.4.3 |
  | Texto grande (24 px o más, o 18,66 px en negrita) | **3:1** | 1.4.3 |
  | Bordes de botones, íconos y gráficos | **3:1** | 1.4.11 |

- **Cómo comprobarlo:**
  - antes de guardar, con el WebAIM Contrast Checker;
  - después, con `pytest pruebas -m capturas`, que revisa las 5 paletas, el estado neutro y los dos modos.
- **Cómo cambiar un color.** En `paletas.css`, cada paleta tiene un bloque claro (`[data-paleta="laguna"]`) y un bloque oscuro (`…[data-modo="oscuro"]`). Cambia los dos.
- *Pregunta:* si subes mucho la saturación de `--c-comida-suave`, ¿la forma decorativa (que usa `--c-comida-contenedor`) se sigue viendo como «el mismo color, un poco más oscuro»?

## 4. La forma decorativa (la técnica de tu imagen)

**Por qué funciona:**
- **Mismo tono, un paso más oscuro.** La forma contrasta poco con el fondo, así que decora sin competir con el texto. El texto sí conserva su contraste alto.
- **Recortada por el borde.** El ojo completa lo que falta (es el principio de continuidad de la Gestalt). La tarjeta se siente con movimiento y profundidad sin ninguna animación.
- **Una sola forma, grande, por tarjeta.** Un adorno con un solo foco. Con formas distintas en cada tarjeta (sol, luna, estrella, gota, hoja y flor, del Cántico de las criaturas), las tarjetas parecen una familia.

**El CSS, línea por línea** (Claude Code lo crea en `estilos/formas.css`):

```css
.con-forma {
  position: relative;      /* la forma se ubica respecto a la tarjeta */
  overflow: hidden;        /* el borde de la tarjeta recorta la forma */
  isolation: isolate;      /* la forma queda detrás del texto, pero encima del fondo */
  background: var(--forma-fondo);
}
.con-forma::after {
  content: "";
  position: absolute;
  right: -1.5rem;
  bottom: -2rem;                       /* se sale un poco: así se recorta */
  width: var(--forma-tam, 9rem);
  aspect-ratio: 1;
  background: var(--forma-color);
  -webkit-mask: var(--forma-imagen) center / contain no-repeat;
          mask: var(--forma-imagen) center / contain no-repeat;
  rotate: var(--forma-giro, -12deg);
  z-index: -1;
  pointer-events: none;
}
```

**La clave es `mask`.** El SVG funciona como un esténcil: donde el dibujo es opaco, se ve el color de `background`. Por eso un mismo SVG sirve con el color de cualquier paleta.

**Ejercicio** (cuando Claude Code lo entregue):
1. Abre el inspector web de Safari (Desarrollo → Mostrar inspector web).
2. Elige una tarjeta y cambia en vivo `--forma-tam`, `--forma-giro`, `right` y `bottom` hasta encontrar la composición que más te guste.
3. Anota los valores y ponlos tú en `formas.css` después de la entrega (hoy no hay tiempo).

## 5. Antes de las 12:00 m.

- [ ] Elegí la letra y respondí la pregunta de la voz de Lumea.
- [ ] Definí `--f-titulos` y `--f-cifras` y revisé 3 pantallas en Safari.
- [ ] Si cambié colores, corrí `pytest pruebas -m capturas` y salió en 0 errores.
- [ ] Hice commit solo de mis archivos.
