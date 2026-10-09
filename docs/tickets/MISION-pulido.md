# Misión: pulido final de Lumea (avatar voxel, Registrar, Inicio, Mis registros, escritorio)

**Para:** Claude Code, en el worktree `.claude/worktrees/rediseno` (rama `rediseno`). Es la única sesión en esta carpeta.

**Hoy es el día de la entrega:** viernes 9 de octubre, 11:59 p. m.
- **A las 12:00 m. (mediodía, hora de Bogotá; mírala con `date`) se congela el código:** terminas el commit en curso, corres las pruebas y dejas el ESTADO al día. Después de esa hora, solo arreglos que Isabella pida. A la 1:00 p. m. las ramas tienen que estar unidas en `main`.
- **Tienes unas dos horas y media.** No alcanza para todo, así que este es el recorte, en orden: P1 y P2 completas. De P3, el compañero que saluda y el dato del día (la semana, solo si sobra tiempo). De P4, las tarjetas por día y la forma decorativa. De P5, solo los 3 problemas más visibles. De P6, solo la transición entre pantallas y la respuesta al toque. A las 11:40 empiezas el cierre (P7), vayas donde vayas.
- A Isabella le queda poco uso de Claude. Las fases van de la más importante a la menos importante: trabájalas en ese orden. Un commit por idea y el ESTADO al día al cerrar cada fase, para que lo hecho quede usable si el uso se acaba.

## Antes de empezar

- **Estado de git.** `git status` debe mostrar `api.js`, este archivo, `docs/aprende/`, `docs/rediseno/voxel-etapas.png` y `vendor/dicebear/`. Si hay otras cosas, para y pregunta.
- **Commits iniciales:**
  1. este archivo y `docs/aprende/tipografia-y-color.md`;
  2. solo `api.js`: «Demo en el celular: la API usa el nombre del equipo (location.hostname)».

  `vendor/dicebear/` va en P2, con el código que lo usa.
- **Lee:** el ESTADO (sección «Camino del cuidado»), `docs/rediseno/inicio-nuevo.md`, `vendor/dicebear/README.md`, `docs/rediseno/voxel-etapas.png` y, del backend, `~/Python_proyects/Lumea/MISION_PULIDO_BACKEND.md` (el contrato del avatar está ahí, en B3).
- **Prohibido:** `git add -A`, `git commit -a` y el push.
- **Textos de Isabella.** No toques sus textos (`conocenos.html`, `index.html`, `crear-cuenta.html`) más allá de lo que pide esta misión.

### Isabella trabaja hoy en paralelo

Isabella va a cambiar la tipografía y los colores con su guía (`docs/aprende/tipografia-y-color.md`). Sus archivos son **`estilos/tokens.css`, `estilos/paletas.css` y `estilos/fuentes/`**:
- No los edites en esta misión. Si necesitas un token nuevo, defínelo en el CSS del componente o pregúntale.
- Nunca pases esos archivos a tus commits; si `git status` los muestra cambiados, son de ella.
- Si una prueba de contraste falla por un cambio suyo en `paletas.css`, no lo arregles tú: anótalo en el ESTADO y avísale con el valor y el contraste que falta.

## P0 · Plan (modo plan, corto: no más de 20 líneas, sin capturas)

Muéstrale a Isabella:

1. El orden en que vas a trabajar y los archivos que vas a tocar.
2. El Avatar nuevo (P2) en ASCII, solo para computador.
3. **Las decisiones pendientes**, con tu recomendación:
   - a. ¿Ánimo conserva la cara grande del compañero?
   - b. ¿En Avatar se mueve la persona y el compañero queda quieto? (recomendado: sí).
   - c. ¿Se quedan los textos extra «Llegaste a la etapa máxima», «Te falta 1 semilla» y «Compañero nuevo:»?
   - d. ¿Qué forma y qué color lleva cada bloque decorado (P4)?

Espera la aprobación. Isabella dirige el diseño: si elige otra cosa, sigue su elección.

## P1 · Arreglos que no pueden faltar

### Enchufes de tipografía para Isabella (primero, en un commit pequeño)

Para que Isabella pueda elegir la letra de los títulos y de las cifras sin tocar componentes:
- Los títulos (`h1`, `h2`, `h3` y las clases de título) usan `font-family: var(--f-titulos, var(--f-familia))`.
- Una clase `.cifra` va en los números que importan: las calorías, los gramos, las semillas, la etapa y la racha. Lleva `font-family: var(--f-cifras, var(--f-familia))` y `font-variant-numeric: tabular-nums lining-nums`.
- No definas `--f-titulos` ni `--f-cifras`: Isabella los define en `tokens.css`. Sin ellos, todo se ve como hoy.

### Registrar: el botón de play encima de «La cámara está apagada»

- **Causa.** Safari dibuja su botón de reproducir sobre un `<video autoplay>` que no tiene imagen.
- **Arreglo:**
  - `#webcam` lleva `hidden` mientras no haya cámara, y lo pierde solo cuando el video empieza a mostrarse (`playing`).
  - Al apagar la cámara se detienen las pistas, `srcObject = null` y el video vuelve a `hidden`.
  - Como respaldo en CSS: `.camera-video-stream::-webkit-media-controls-start-playback-button { display: none !important; -webkit-appearance: none; }`.
- **Prueba.** Con la cámara apagada, el video está oculto y el aviso «La cámara está apagada» se ve completo. Deja en el ESTADO que Isabella lo compruebe en Safari.

### Avatar: la vitrina tapa la lista de compañeros

- **Causa.** `.avatar-companeros` cae debajo de la vitrina `sticky`, en la columna 1.
- **Arreglo.** El layout nuevo de P2 no puede repetir el problema: nada debe quedar debajo de un `sticky` en su misma columna.
- **Comprobación.** Capturas después de hacer scroll, en 1280 y en 1440 px.

### Crear cuenta (decisiones de Isabella del 8 de octubre)

- **Peso y altura salen.** Se quitan los dos campos con su etiqueta, su ayuda y su validación, y salen del payload.
- **Edad mínima: 11 años** (`min="11"`). Mensaje provisional: «Lumea es para personas de 11 años en adelante.».
- **Casilla para menores de 18.** Si la edad es menor de 18, aparece una casilla obligatoria con el texto literal de Isabella: «Mi madre, padre o acudiente sabe que uso Lumea».
  - Se envía `acudiente_sabe: true`.
  - Con 18 años o más, la casilla no se ve y no se envía.
  - Accesibilidad: `<label>`, `required` solo cuando se muestra, y el error conectado con `aria-describedby`.
- **Textos relacionados.** Busca «peso», «altura», «14 años» e «IMC» en todo el frontend. No cambies esos textos: anótalos en el ESTADO para Isabella.
- **Pruebas:**
  - el payload ya no lleva peso ni altura;
  - con 10 años no se envía;
  - con 15 años, sin la casilla no se envía y con ella sí;
  - con 20 años la casilla no aparece.

## P2 · La persona (DiceBear voxel-art) y el armario por etapas

**Decisión de Isabella (9 de octubre).** El avatar de Laura no llega a tiempo, y el armario de hoy no cambia nada de lo que se ve. Por eso:
- la persona ahora es un avatar **voxel-art** de DiceBear 10.x;
- **cada etapa desbloquea una prenda o un accesorio nuevo**, que sí cambia a la persona.

### Todo DiceBear se dibuja en el navegador, sin pedirle nada a DiceBear

- **Los archivos.** `vendor/dicebear/` trae `@dicebear/core` 10.7.0 (MIT) y los estilos voxel-art y gaze (CC0). Ya están verificados en Chromium: 0 peticiones externas. Lee su README.
- **`persona.js`** (módulo nuevo):
  - Exporta `dibujarPersona(persona, { animada })`, que devuelve el SVG.
  - Carga `voxel-art.json` una sola vez.
  - Las opciones son los `rasgos` más los `parametros` de lo que la persona tiene puesto.
  - La semilla es fija (`'lumea'`): **nunca el correo**.
  - El fondo es transparente (`backgroundColor: ['ffffff00']`).
  - Ningún rasgo visible queda al azar: `topProbability`, `glassesProbability`, `beardProbability` y `cheeksProbability` valen 100 o 0 según lo elegido, y los colores de pantalón y zapatos son fijos.
  - Desde un script clásico se usa con `import()`.
- **`companero.js`** también dibuja en el navegador, con `gaze.json`:
  - toma las opciones de los parámetros de la URL que ya manda el backend (`new URL(url).searchParams`, cada valor en lista);
  - les agrega `animationVariant` cuando la cara va animada;
  - no se le pide nada a `api.dicebear.com`.
- **Prueba.** Con las peticiones de red de Playwright, comprueba que ninguna página pide `dicebear.com`.

### El contrato

Está en `MISION_PULIDO_BACKEND.md`, B3. Mientras el backend no esté listo, usa respuestas simuladas con esa forma.
- `GET /avatar` agrega:
  - `persona`, con `rasgos` y `puesto` (`ropa` y `accesorio`, cada uno con `id`, `nombre` y `parametros`);
  - en cada objeto, `parametros`, `nivel_requerido` y `desbloqueado`;
  - `rasgos_disponibles`, que trae los nombres en español.
- `POST /avatar/rasgos` recibe `{email, rasgos}`.
- `equiparObjeto` y `quitarObjeto` siguen como están.

### La pantalla de Avatar

- **La vitrina.**
  - La persona va grande (unos 260 px) y animada (`slow`), con el compañero pequeño a su lado y quieto.
  - Debajo, la etapa y lo que viene: «Te faltan 35 semillas para la etapa 5: Camisa de cuadros». Es un texto nuevo y va a la revisión de Isabella.
- **«Mi armario»** (la acción principal de la pantalla):
  - una cuadrícula de mosaicos;
  - cada mosaico muestra **a la persona con esa prenda puesta**, dibujada con sus propios rasgos;
  - los bloqueados se ven atenuados, con candado, «Etapa N» y `aria-disabled="true"`;
  - tocar uno desbloqueado se lo pone a la persona, y tocar el que tiene puesto se lo quita (la ropa vuelve a la camiseta lisa);
  - la persona de la vitrina cambia al instante: esa es la respuesta a la acción.
- **«Cómo me veo»: los rasgos son libres** y nunca se bloquean, porque la identidad no es un premio.
  - Son: tono de piel, peinado, color de pelo, ojos, boca, pecas o rubor, barba y color de la camiseta.
  - Los colores son muestras redondas. El peinado, los ojos y la boca son mosaicos pequeños dibujados en el navegador.
  - Los nombres salen de `rasgos_disponibles`.
  - Se usa un grupo de `radio` con su `label` por rasgo. Los tonos de piel se llaman «Tono 1» a «Tono 8», sin otros nombres.
  - La vista previa cambia al instante, y el botón secundario «Guardar cómo me veo» llama a `POST /avatar/rasgos`.
- **Lo demás.** Misiones, calcomanías, «Tu compañero» y «Mis colores» se conservan, en pestañas o debajo, sin tapar nada (P1).
- **Celebración.** Cuando una etapa desbloquea una prenda, la celebración muestra «Prenda nueva: Overol de jardín» con la persona puesta esa prenda.
- **Pruebas:**
  - el armario se dibuja desde el contrato;
  - los bloqueados no se pueden poner;
  - guardar los rasgos envía solo claves permitidas;
  - no hay peticiones externas.

## P3 · El Inicio nuevo

Isabella eligió tres cosas nuevas. Lo que ya existe se conserva: «Tu día» con el único botón principal, «¿Cómo llegas hoy?», la misión y la etapa.

### 1. El compañero que saluda

- **Dónde y cómo.** Va junto al `h1` «Hola, Ana»: grande (unos 140 px en computador y 96 en celular), animado (`slow`) y con la cara del ánimo de hoy. Si hoy no hay check-in, la cara `neutral`.
- **Lo único que se mueve en Inicio.** Los botones del check-in quedan quietos. Al guardar el ánimo, el compañero cambia a esa cara: esa es la respuesta a la acción.
- **La imagen es decorativa** (`alt=""`). Si no se puede dibujar, el saludo queda igual.

### 2. «¿Sabías que…?» del día

- **Qué muestra.** Una tarjeta con el dato curioso del día, el mismo para todas las personas, con el nombre del alimento como subtítulo.
- **Cómo se dibuja.** Reutiliza el bloque largo de K0.5 («Leer más» con `aria-expanded`). Va decorada con la técnica de P4. Si la petición falla, la tarjeta no se dibuja.
- **De dónde sale.** De `GET /dato-del-dia`, sin correo. Agrega `obtenerDatoDelDia()` a `api.js`.
- **Contrato:**
  ```json
  {"fecha": "2026-10-09", "alimento_codigo": "banano", "nombre": "Banano", "dato_curioso": "..."}
  ```
  Sin datos, la respuesta es un 404.

### 3. Tu semana, en una franja

- **Qué muestra.** Los últimos 7 días, con hoy a la derecha. Cada día lleva su inicial, cuántas comidas registró la persona y la cara quieta de su ánimo: la última del día, o un punto vacío si no hubo check-in.
- **Datos.** Salen de `obtenerHistorial` y de `obtenerEstadosAnimo(email, 7)`.
- **Enlace.** La franja entera lleva a `progreso.html` («Ver mi progreso»).
- **Lector de pantalla.** Una lista, con días como «martes 6: 2 comidas, ánimo bien».
- **Sin juicio.** Ningún día va en rojo ni se marca como malo.

## P4 · Mis registros y la forma decorativa

### La técnica que eligió Isabella

Sale de una imagen de referencia: una tarjeta rosa pastel con un corazón grande, del mismo rosa pero más oscuro, recortado por el borde de la tarjeta.

- **El componente.** Crea `estilos/formas.css` con `.con-forma`:
  - la tarjeta lleva `position: relative`, `overflow: hidden`, `isolation: isolate` y `background: var(--forma-fondo)`;
  - un `::after` decorativo, con `background: var(--forma-color)`, la máscara `mask` / `-webkit-mask: var(--forma-imagen) center / contain no-repeat`, `width: var(--forma-tam, 9rem)` y `aspect-ratio: 1`;
  - el `::after` va abajo a la derecha y sale un poco del borde, girado `var(--forma-giro, -12deg)`, con `z-index: -1`.
- **Variantes por rol.** Usan los tokens que ya existen: el fondo es `--c-<rol>-suave` y la forma, `--c-<rol>-contenedor`. Los roles son `comida`, `marca`, `logro`, `emocion` y `mision`.
- **Las formas** (`img/formas/*.svg`) son originales, simples y de un solo trazado, y vienen del Cántico de las criaturas: sol, luna, estrella, gota, hoja y flor.
- **Sin dibujo.** Con `forced-colors: active`, la forma no se dibuja.
- **Contraste.** El texto cumple 4,5:1 sobre el fondo y sobre la forma, en las 5 paletas, en el estado neutro y en los dos modos.
- **Dónde va.** Va en pocos lugares, para que se note:
  - los bloques de consejo de Registrar;
  - los «¿Sabías que…?» (Registrar e Inicio);
  - la tarjeta «Hoy» de Mis registros.

  Sugerencia para P0: «Lo que aporta», comida y hoja; «Para completar tu plato», marca y flor; «A tener en cuenta», logro y gota (nunca color de alerta); «¿Sabías que…?», emoción y estrella.

### Mis registros: tarjetas por día

- **Orden.** Los registros se agrupan por día y van del más reciente al más viejo: «Hoy», «Ayer», «martes 6 de octubre».
- **Cada tarjeta lleva:**
  - una línea de resumen: «3 comidas» y los 6 grupos del plato del ICBF como 6 marcas pequeñas, llenas las de los grupos que aparecieron (es información, no una meta: sin «te faltan»);
  - una fila por registro: la hora, el nombre, un chip con su grupo, los sellos y, en segundo plano, las calorías (con `.cifra`).
- **Datos.** El backend agrega `grupo` a cada ítem de `/historial`. Si no viene, no se dibujan el chip ni las marcas.
- **Estado vacío.** Una invitación a registrar, con el botón «Registrar comida».

## P5 · El computador (Mac)

En el celular Lumea se ve mucho mejor que en el Mac. Arregla lo que mostraste en P0 con estas reglas:
- **Ancho.** El contenido tiene un ancho máximo (unos 1120 px) y queda centrado a la derecha del menú. Los párrafos no pasan de unos 70 caracteres.
- **Tarjetas y listas.** Ninguna tarjeta ocupa todo el ancho con una sola línea adentro. Las listas usan 2 o 3 columnas cuando caben.
- **Tamaños de prueba.** 1280×800, 1440×900 y 1728×1117.

## P6 · Movimiento con propósito

- **Entre pantallas.** `@view-transition { navigation: auto; }` dentro de `@media (prefers-reduced-motion: no-preference)`, con un fundido corto. El menú y el logo llevan `view-transition-name`.
- **Al tocar.** Botones, opciones y mosaicos responden en menos de 0,1 s.
- **Barras.** Se llenan una vez al cargar.
- **Nada más se mueve.** Con `prefers-reduced-motion: reduce`, nada se mueve, ni la persona ni el compañero.
- **Tokens.** Usa los de movimiento que ya existen.

## P7 · Cierre (empieza a las 11:40 y termina antes de las 12:00 m.)

- **Pruebas.** `pytest pruebas` en verde, y `pytest pruebas -m capturas` con 0 errores de contraste (también en 1440×900).
- **Bitácora.** Una fila por fase en `docs/bitacora-ia.md`.
- **ESTADO.** Una sección «Pulido final» con:
  - lo que se hizo y lo que quedó pendiente;
  - «Textos nuevos para que Isabella revise»;
  - la lista de P1 (peso, altura, 14 años e IMC);
  - lo que hay que mirar en Safari.
- **`docs/defensa/`.** Dos preguntas nuevas, sin respuesta. Por ejemplo: «¿Por qué los rasgos no se bloquean y la ropa sí?» o «¿Por qué Lumea no le pide nada a DiceBear?».

## P8 · Unir y README (de 12:00 m. a 1:00 p. m.)

**Lo que ya se sabe.** Hoy `rediseno` ya contiene `main` y los 3 commits de Laura que estaban en `origin/main` (b5ae62e, 902a653 y b89dc7d) según el último `fetch`, que fue del 3 de octubre. Por eso unir debería ser un avance rápido (*fast-forward*), sin conflictos.

1. **Estado limpio.** `git status` limpio. Si quedan cambios de Isabella en `tokens.css`, `paletas.css` o `fuentes/`, pídele que haga su commit.
2. **`git fetch origin`** y luego `git log --oneline rediseno..origin/main`.
   - Si sale vacío, sigue.
   - Si hay commits nuevos de Sara o de Laura, **para**. Muéstrale a Isabella quién los hizo y qué archivos tocan, y propón cómo unirlos sin perder su trabajo. **Nunca** uses `-s ours` ni descartes trabajo de una compañera sin que Isabella lo decida.
3. **`README.md`, al día.** Una pantalla por sección:
   - **Qué es Lumea.** Déjalo marcado «[Isabella: revisa este párrafo]».
   - **Cómo correrla.** El backend en el puerto 5002 con MySQL, el frontend con `python3 -m http.server 8001`, Safari y la cuenta demo.
   - **Las pantallas.**
   - **Decisiones de diseño:** las paletas, la accesibilidad y el movimiento.
   - **Ética y privacidad:**
     - Lumea no pide peso ni altura;
     - la edad mínima es 11 años, con aviso al acudiente;
     - DiceBear se dibuja dentro de Lumea;
     - lo que pasa con las fotos (verifícalo en el código; no lo supongas).
   - **Créditos del equipo:** sale de `git shortlog -sn` y de los ESTADO (Sara, Laura e Isabella). Marca «[Isabella: confirma los roles]».
   - **Uso de IA:** enlace a `docs/bitacora-ia.md`.
   - **Licencias:** DiceBear core (MIT), voxel-art y gaze (CC0), Bricolage Grotesque (OFL), Bootstrap y Bootstrap Icons (MIT), y cualquier letra nueva que agregue Isabella.
4. **Pruebas en verde** y un commit.
5. **Subir, solo cuando Isabella lo apruebe en el chat:**
   ```
   git push origin rediseno
   git push origin rediseno:main
   git branch -f main rediseno
   ```
   `main` no está abierta en ninguna carpeta, así que `git branch -f` es seguro y no hace falta tocar `~/Lumea-frontend`.
   - Si GitHub rechaza el push por permisos (el repositorio es de Sara), dile a Isabella exactamente qué falta. No intentes otra cosa.
6. **Comprueba en GitHub** que `main` muestra el README nuevo.

## Cómo trabajar

- Un commit por idea, en español, con `Co-Authored-By: Claude …`.
- Los textos nuevos de interfaz son provisionales: van a la lista de revisión de Isabella.
- Si el uso se acaba, termina el commit en curso y deja el ESTADO al día. Se sigue con `claude --continue`.
- Si algo no está aquí, pregunta.
