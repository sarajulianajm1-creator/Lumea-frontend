# Misión: rediseño del frontend (entrega del viernes 9 de octubre)

**Para:** Claude Code, en una sesión Local, en el worktree `.claude/worktrees/rediseno`, rama `rediseno`, que sale de `gamificacion-100`.

**Decisión de Isabella (7 de octubre de 2026).** Por falta de tiempo, delega el rediseño visual a Claude Code siguiendo el plan del documento «Rediseño». Ella escribe los textos, toma las decisiones y revisa el resultado. Regístralo así en `docs/bitacora-ia.md`: el código del rediseño es de la IA; el plan, las decisiones, los textos y la revisión son de Isabella.

**Trabajo en paralelo.** Isabella reescribe textos en `.claude/worktrees/gamificacion`, rama `gamificacion-100`. Las dos ramas se unen el viernes. Para que no choquen, cada archivo tiene un solo dueño (ver «Qué no se toca»).

## Decisiones de Isabella (7 de octubre)

- [x] **Ninguna paleta es predeterminada.** Cada persona elige la suya. Mientras no elija, Lumea se ve en un estado neutro (ver R4).
- [x] **Caras del check-in.**
  - Se usan las caras de DiceBear 10.x por la API. Depender de internet está aceptado.
  - Solo cambian los cinco botones del check-in, en Inicio y en Ánimo. La semana de ánimo, Progreso y Avatar siguen con la cara del avatar.
  - El estilo elegido es `gaze`. La alternativa `moods` queda lista para cambiarla con una palabra (ver R3).
- [x] **Logo.** Isabella lo entrega esta noche. Déjale un solo lugar donde ponerlo (ver R1).
- [x] **Navegación.** Sigue la navegación B: Inicio · Mis registros · Registrar · Progreso · Avatar. Ánimo se abre desde Inicio y desde Progreso.
- [x] **Cámara.** Se conserva `alimentos.html` con `lumea-camara.js`, con los estados «IA segura» e «IA duda». Solo cambia su aspecto.
- [ ] **Calorías en el resultado de la cámara.** Isabella todavía no decide. Hoy se muestran y así quedan, controladas por una sola constante (ver R5).

## Qué no se toca

- **Textos de Isabella.** Las páginas públicas son `index.html` (Bienvenida), `conocenos.html`, `guialumea.html`, `crear-cuenta.html`, `iniciar-sesion.html` y `terminos.html`.
  - En ellas solo editas el `<head>` (enlaces a CSS y scripts) y los archivos CSS.
  - La única excepción en el `<body>` son las líneas del logo del encabezado (`.logo-brand`).
  - Si una página pública necesita otro cambio en su `<body>`, anótalo en el ESTADO bajo «Para después de unir» y no lo hagas.
- **Archivos de Isabella:** `inicio.html`, `estilos/inicio.css` y `sesion-nav.js`.
- **Archivos de Sara:** no edites `style.css`. Solo dejas de cargarlo en las páginas privadas (ver R1).
- **Archivos generados:** `estilos/paletas.css` y `estilos/tokens.json` se cambian solo con `herramientas/generar_paletas.py`. El menú privado se cambia solo con `herramientas/menu_privado.py`.
- **Backend:** esta misión no lo toca.
- **Git:**
  - Nunca uses `git add -A` ni `git commit -a`. Agrega archivo por archivo.
  - Nunca hagas push ni unas a `main`.
  - `.env` y `fotos_prueba/` jamás entran al repositorio.

## Dirección (del documento «Rediseño»)

1. **Superficies tranquilas.** El color va en los momentos: un logro, una misión cumplida, el ánimo elegido. No va en las cajas. El color saturado ocupa áreas pequeñas sobre superficies calmadas (Schloss y Palmer, 2011).
2. **Una acción principal por pantalla.** Solo un botón relleno; el resto es secundario o de texto.
3. **Tres niveles de jerarquía por pantalla.**
   - El título de la pantalla usa `--t-2xl`; las secciones usan `--t-l` o `--t-xl`; el cuerpo usa `--t-m`.
   - El cuerpo, los botones y las instrucciones van a 16 px o más.
   - `--t-s` (14 px) es solo para texto secundario y `--t-xs` (12,8 px) solo para notas y fechas. Nada va por debajo de `--t-xs`.
4. **La gamificación acompaña, no grita.** El XP aparece solo en el nivel, en las misiones y en la celebración. Ningún botón de ánimo dice «+5 XP».
5. **Movimiento con propósito.**
   - Hay una entrada por pantalla, la celebración y las respuestas a lo que la persona hace. Nada más se mueve.
   - Todo dura 420 ms o menos (`--m-lento`).
   - Con `prefers-reduced-motion` nada se mueve: las cosas solo aparecen.
6. **Nada promete lo que Lumea no hace.** Lumea no detecta ingredientes ni registra agua, ejercicio o sueño.

Además siguen vigentes las reglas de `MARCA.md`:
- Nada en MAYÚSCULAS sostenidas, ni por CSS ni escrito.
- Ningún emoji como ícono. Todos los íconos son de Bootstrap Icons.
- Maracuyá y mango nunca se usan como color de texto (usa `--c-ROL-tinta`).
- Los textos se escriben con `textContent`, el foco siempre se ve y todo se puede usar con teclado.

## Fases

Van en este orden. Cada fase termina con `pytest pruebas` en verde, sus commits y el ESTADO al día. **Si el uso se acaba:** el mínimo para el viernes es R1–R4. R9 se hace siempre al final, aunque falten R6–R8.

### R0 · Plan (modo plan)

1. Lee estos archivos:
   - Documentación: `CLAUDE.md`, `MARCA.md`, este archivo y `docs/tickets/ESTADO-gamificacion.md` (las decisiones 1 a 25 siguen vigentes).
   - Estilos: `estilos/tokens.css`, `estilos/componentes.css`.
   - Herramientas: `herramientas/generar_paletas.py`, `herramientas/menu_privado.py`.
   - Pantallas y lógica: `index-ingresado.html`, `indexx.js`, `lumea-ui.js`, `emociones.html`, `emociones.js`, `alimentos.html`, `progreso.html`, `avatar.html`, `mis-registros.html` y `tema.js`.
2. Toma capturas «antes» de las seis pantallas privadas a 1280 y a 390 px en `pruebas/capturas/antes/`. Esa carpeta está ignorada por git.
3. Muestra un plan de una pantalla con estas tres cosas:
   - qué archivos creas o cambias en cada fase;
   - qué pruebas cambiarán y por qué;
   - qué dudas tienes.
4. Espera la aprobación de Isabella.

### R1 · Cimientos: un solo armazón para las seis pantallas privadas

Las seis pantallas son Inicio (`index-ingresado.html`), Mis registros, Registrar (`alimentos.html`), Progreso, Avatar y Ánimo (`emociones.html`).

- **Armazón.**
  - Todas usan `.app` y `.nav-app` de `componentes.css`.
  - En el computador, una barra lateral de 248 px con el logo arriba, los cinco destinos y abajo una zona de usuario delgada: nombre, nivel y «Cerrar sesión».
  - En el celular (≤ 720 px), una barra inferior con Registrar al centro.
  - El menú se cambia en la plantilla de `herramientas/menu_privado.py` y se vuelve a correr la herramienta.
- **Deja de cargar** `style.css`, `pantallas-sara.css` y `puente-sara.css` en esas seis páginas.
  - Lo que todavía haga falta de ahí se reescribe con tokens en `estilos/app.css`, que es nuevo y solo para pantallas privadas.
  - Bootstrap Icons se queda. El CSS de Bootstrap se queda solo si una pantalla todavía lo necesita para su grilla; el aspecto ya no sale de Bootstrap (nada de `btn-success` ni colores de Bootstrap).
- **Fondo y ancho.**
  - El fondo cubre toda la altura (hoy se corta abajo).
  - El contenido tiene un ancho máximo (`--ancho-contenido`) y márgenes con `--e-*`.
- **Radios por jerarquía.**
  - Solo existen `--r-control` (botones y campos), `--r-tarjeta` (tarjetas), `--r-panel` (hojas y diálogos) y `--r-pildora` (chips).
  - Hoy hay seis radios distintos (8, 16, 20, 22, 24 y 800).
- **Sombras.**
  - Una sola elevación, y solo para lo que flota: un diálogo o la barra inferior.
  - Las tarjetas se separan con un borde o con un cambio de superficie.
- **Quitar:**
  - la hora en Inicio;
  - la flecha de volver en Progreso (para eso está el menú);
  - el 🌿 y «LUMEA» en mayúsculas.
- **Lugar del logo.**
  - `<img class="marca" src="img/logo.svg" alt="Lumea">` en la barra lateral y en el encabezado de las páginas públicas.
  - Mientras llega el de Isabella, `img/logo.svg` es un marcador simple que dice «Lumea» en texto.
  - Si su logo llega en PNG, cambiar la ruta debe ser un solo reemplazo. Anota cómo en el ESTADO.
- **Prueba nueva `pruebas/test_rediseno.py`**, con Playwright, sobre las seis pantallas privadas a 1280 y a 390 px. Debe comprobar:
  - ningún texto visible por debajo de 12,8 px;
  - todo `border-radius` calculado pertenece a los cuatro tokens (o es 50 % para círculos);
  - ningún `text-transform: uppercase` calculado;
  - el fondo de la página cubre el alto de la ventana;
  - los enlaces del menú y la acción principal miden al menos 44 × 44 px.

### R2 · Inicio nuevo (`index-ingresado.html` + `indexx.js`)

Sigue el esquema de la sección «El Inicio nuevo» del documento.

**Cambio de base respecto del documento.** El documento proponía construir el Inicio sobre `inicio.html`, pero ese archivo es el ejercicio de Isabella (estático, a medio hacer). Se construye sobre `index-ingresado.html`, que ya está conectado al backend y a las pruebas.
- La estructura semántica sale de su `inicio.html`:
  - el `h1` con el saludo;
  - cada bloque como `section` con `aria-labelledby`;
  - el check-in con botones `aria-pressed`.
- Úsala como modelo y menciónala en el mensaje del commit.
- No edites `inicio.html`: es su ejercicio.

De arriba abajo:

1. **Saludo** (`h1`) y, si el backend lo manda, el aviso cálido de `mensaje_regreso`.
2. **Tarjeta «Tu día».**
   - Muestra las comidas de hoy y la barra de la meta de comidas.
   - Tiene el único botón relleno de la pantalla: «Registrar comida».
3. **Tarjeta «¿Cómo llegas hoy?».**
   - Tiene las cinco caras (R3) y el botón secundario «Guardar mi ánimo».
   - Si ya hizo el check-in hoy, se comporta como hoy.
4. **Fila plana «Misión de hoy»:** la próxima misión, con su +10 XP.
5. **Fila plana «Nivel y racha»:** enlaza a Progreso.

Además:
- Pasa de 13 cajas a cuatro superficies como máximo, sin contar el aviso de regreso ni la tarjeta de colores de R4. Pasa también de 11 textos con «XP» a tres como máximo.
- Conserva las clases `lumea-bind-*` para que `lumea-ui.js` y sus pruebas sigan funcionando.

### R3 · Caras del check-in con DiceBear (Inicio y Ánimo)

**Configuración.** Crea `caras-checkin.js` con un solo objeto de configuración que Isabella pueda leer y editar:

```js
// Estilo de las caras del check-in. Isabella eligió "gaze"; "moods" también tiene boca.
// Para cambiarlo basta con cambiar esta palabra.
const ESTILO = "gaze";

const ESTILOS = {
  gaze: {
    base: "https://api.dicebear.com/10.x/gaze/svg",
    fijos: { seed: "lumea-animo", shapeVariant: "circle" },
    color: "bodyColor",
    caras: {
      muy_mal: { eyesVariant: "bars" },
      mal: { eyesVariant: "small" },
      neutral: { eyesVariant: "dots" },
      bien: { eyesVariant: "happy" },
      muy_bien: { eyesVariant: "grin" },
    },
  },
  moods: {
    base: "https://api.dicebear.com/10.x/moods/svg",
    fijos: { seed: "lumea-animo", faceVariant: "circle", cheeksProbability: 0, backgroundColor: "ffffff00" },
    color: "faceColor",
    caras: {
      muy_mal: { eyesVariant: "lookDown", mouthVariant: "frown" },
      mal: { eyesVariant: "pupils", mouthVariant: "wavy" },
      neutral: { eyesVariant: "pupils", mouthVariant: "line" },
      bien: { eyesVariant: "pupils", mouthVariant: "smile" },
      muy_bien: { eyesVariant: "happy", mouthVariant: "laugh" },
    },
  },
};
```

**Datos verificados el 7 de octubre** con `@dicebear/core` 10.7.0 y `@dicebear/styles` 10.6.0:
- Los parámetros se llaman `<componente>Variant` y `<color>Color`, y el color va en hexadecimal sin `#`.
- `gaze` solo tiene ojos: sus componentes son shape, spacing, eyes y animation. `moods` tiene ojos y boca.
- Los dos estilos son CC0.
- La animación de los dos vive dentro del SVG, bajo `@media (prefers-reduced-motion: no-preference)`.
- La referencia visual está en `docs/rediseno/caras-gaze-vs-moods.png`.
- Antes de cerrar la fase, verifica en el navegador que las diez URL cargan.

**Comportamiento.**
- **Color:** el color del cuerpo sale de `--c-emocion` de la paleta activa, leído con `getComputedStyle`. Las caras se vuelven a dibujar con el evento `lumea:tema`.
- **Quietas por defecto:** en los botones van con `animationVariant=none`.
  - Solo la cara elegida se anima (`animationVariant=medium`): el movimiento responde a la acción y nunca hay cinco caras moviéndose a la vez.
- **Accesibilidad:**
  - La imagen lleva `alt=""` y la palabra («Muy mal» … «Muy bien») va siempre escrita y visible.
  - Esa palabra es el nombre accesible del botón. La selección se marca con `aria-pressed`.
- **Sin internet:** si la imagen falla, se oculta y queda la palabra. El botón funciona igual.
- **Marcado:** los botones dejan `data-cara` y usan `data-cara-checkin`. Así la semana de ánimo y el avatar siguen igual en `lumea-ui.js`.
- **Ningún ánimo es mejor que otro:**
  - no hay rojo ni verde por ánimo;
  - ningún botón muestra «+XP»;
  - ningún texto juzga lo que se marcó.
- **Privacidad:** la URL no lleva ningún dato de la persona: la semilla es fija. Anótalo en `docs/defensa/`, porque es una buena respuesta para el jurado.
- **Créditos:** agrega en la pantalla de créditos o en el README «Caras del check-in: DiceBear (CC0)».

### R4 · Paleta sin predeterminada

- **Estado neutro.**
  - Hoy `:root` sin `data-paleta` cae en Laguna (verde). Cambia `generar_paletas.py` para que ese caso sea un estado neutro:
    - superficies y texto sin tono, ni verde ni azul;
    - los colores de rol se conservan, porque llevan significado;
    - pasa las mismas pruebas de contraste y daltonismo que hace el generador.
  - El estado neutro no aparece en el selector. Regenera `paletas.css` y `tokens.json` con la herramienta.
- **Selector en Inicio.**
  - Mientras no haya paleta guardada, Inicio muestra arriba una tarjeta «Elige tus colores».
  - Las cinco paletas van como un `radiogroup`. Cada opción es una tira con sus colores de rol y su nombre: Laguna, Neblina, Carnaval, Colibrí, Cosecha.
  - También se elige Claro, Oscuro o Como mi dispositivo.
  - Al elegir, se aplica y se guarda al instante con `LumeaTema.ponerPaleta` y `ponerModo`. El botón «Listo» cierra la tarjeta.
  - «Ahora no» la esconde solo durante esta sesión.
  - No es un diálogo modal: no impide registrar una comida.
- **Selector en Avatar.** El mismo componente va en una sección «Mis colores», para cambiar la paleta cuando sea.
- **Páginas públicas:** se ven en el estado neutro, o en la paleta que ese navegador ya tenga guardada (`tema.js` ya la aplica).
- **Crear cuenta:** no le agregues ningún paso. Ese archivo es de Isabella.

### R5 · Registrar (`alimentos.html`)

La lógica de `lumea-camara.js` no cambia: solo cambia el aspecto.

- **Una acción principal:** «Tomar foto» es el único botón relleno. Hoy hay cinco botones iguales.
- **Resultado.**
  - El título es «Lo que reconoció Lumea» (no «Detectamos…»).
  - El nombre del alimento va en `--t-3xl` y la certeza en palabras y número.
  - «IA duda» usa el contenedor del rol duda; el mango nunca va como texto.
  - Los sellos de advertencia siguen en negro.
- **Texto:** los criterios hoy están a 10 px y pasan al tamaño del cuerpo. Los tres títulos en mayúsculas pasan a minúsculas normales.
- **Calorías.**
  - Pon `const MOSTRAR_CALORIAS = true;` arriba de `lumea-camara.js`, con un comentario que diga que lo decide Isabella.
  - En `true`, las calorías van en una sola línea secundaria: «Calorías aproximadas: 60 kcal», sin color de alerta ni juicio.
  - En `false`, no se dibujan.
- **Celebración:** sigue llamándose igual.

### R6 · Avatar, Progreso y Mis registros, en armonía

- **Avatar.**
  - Sin el gran fondo rosado: el avatar va sobre una superficie tranquila.
  - Dos columnas desde 992 px (avatar y nivel a la izquierda; las pestañas a la derecha) y una sola en el celular.
- **Progreso.**
  - Como máximo cinco superficies: nivel, racha, comidas de la semana, ánimo de la semana y el enlace al álbum.
  - No tiene flecha de volver.
- **Mis registros:** el mismo armazón y la misma escala. Las tarjetas pasan a filas de lista.

### R7 · Páginas públicas, solo con CSS

- Crea `estilos/publico.css` y cárgalo después de `style.css` en el `<head>` de las seis páginas públicas. Debe hacer esto:
  - reemplazar los verdes de Sara por tokens, en estado neutro o con la paleta guardada;
  - usar Bricolage Grotesque, la escala de tipos y los radios;
  - quitar las mayúsculas.
- Pon el logo en el encabezado (las líneas de `.logo-brand`).
- No cambies ningún texto. Si un texto rompe el diseño, anótalo para Isabella.

### R8 · Movimiento

- Una sola entrada por pantalla: el contenido principal aparece y sube un poco una vez, en 220 ms.
- La celebración queda como está.
- La cara elegida del check-in se anima (R3).
- Al cambiar de paleta, el fondo y el texto cambian de color en 220 ms. Esa transición va solo en esas dos propiedades, no en todos los elementos.
- La respuesta al pasar el cursor o al enfocar dura 120 ms.
- Nada más se mueve.

### R9 · Revisión y entrega

- **Pruebas:**
  - `pytest pruebas` en verde.
  - Toda prueba que cambie porque cambió el marcado queda en el ESTADO con su razón.
  - Nunca borres una prueba para que pase, ni debilites una de accesibilidad.
- **Contraste:** `pytest pruebas -m capturas` sobre las 5 paletas × 2 modos más el estado neutro, con 0 errores de contraste en las pantallas privadas.
- **Recorrido a mano** de cada pantalla privada:
  - con teclado, sin mouse;
  - el foco siempre visible;
  - a 200 % de zoom y a 320 px de ancho, sin barra horizontal (WCAG 1.4.10).
- **Capturas «después»** a 1280 y a 390 px en `pruebas/capturas/despues/`, de las seis pantallas privadas y de la Bienvenida. Isabella elige cuáles guarda para la defensa.
- **Documentación:**
  - una fila por fase en `docs/bitacora-ia.md`;
  - `docs/tickets/ESTADO-rediseno.md` al día;
  - `docs/defensa/preguntas-rediseno.md`: seis preguntas que un jurado podría hacer sobre este rediseño, cada una con el archivo donde está la respuesta. **Sin respuestas:** las escribe Isabella.

## Cómo trabajar

- **Una sesión por carpeta.**
  - Esta sesión vive en `.claude/worktrees/rediseno`.
  - Isabella trabaja sus textos en `.claude/worktrees/gamificacion`.
  - No abras otra sesión en ninguna de las dos.
- **Pruebas:** puedes reutilizar el entorno del otro worktree con `../gamificacion/.venv/bin/python -m pytest pruebas`, o crear tu propio `.venv` con `pruebas/requirements.txt`.
- **Para ver la demo:**
  - backend en el puerto 5002 con la cuenta `demo@lumea.co`;
  - esta carpeta con `python3 -m http.server 8001`. El puerto 8000 es el de la carpeta de Isabella, así se pueden comparar las dos.
- **Commits.**
  - Un commit por idea, en español, con `Co-Authored-By: Claude …`.
  - El código debe ser simple y comentado: Isabella tiene que poder explicarlo.
- **Textos nuevos.** Todo texto de interfaz que escribas («Elige tus colores», «Listo», «Ahora no», «Mis colores», «Lo que reconoció Lumea»…) va en una lista del ESTADO llamada «Textos nuevos para que Isabella revise». Ella decide la versión final.
- **Si el uso se acaba:** termina el commit en curso y deja el ESTADO al día. La siguiente sesión arranca con `claude --continue` en esta misma carpeta.
- **Si algo no está aquí ni en el documento,** pregunta. No inventes pantallas ni textos de marca.
- **No hagas push.** El viernes, Isabella une `gamificacion-100` (sus textos) dentro de `rediseno`, corre las pruebas y después pasa todo a `main`.
