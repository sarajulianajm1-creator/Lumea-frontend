# Estado de la misión del rediseño

Rama `rediseno` (sale de `gamificacion-100`). Misión: `docs/tickets/MISION-rediseno.md`. Se actualiza al cerrar cada fase.

El código del rediseño es de la IA; el plan, las decisiones, los textos y la revisión son de Isabella.

## R0 · Plan: LISTA (7 oct 2026)

**Qué quedó listo**
- Se creó el worktree `.claude/worktrees/rediseno` sobre la rama `rediseno` (no existía) y se trajo la misión actualizada con `git merge --ff-only gamificacion-100`.
- Se leyó todo lo que pide R0, más `docs/rediseno/inicio-nuevo.md` y su imagen.
- Capturas «antes» de las seis pantallas privadas a 1280 y a 390 px en `pruebas/capturas/antes/` (ignorada por git). Se tomaron con el backend simulado de `pruebas/conftest.py`, con la cuenta de prueba.
- Plan aprobado por Isabella el 7 de oct, con respuesta a las 9 dudas (sección «Respuestas de Isabella al plan R0» de la misión).

**Línea base antes de tocar nada:** 222 pruebas pasan, 1 `xfail` (el borrador `inicio.html`) y **1 falla que ya existía**: `test_avatar.py::test_un_solo_h1_y_la_navegacion_marca_avatar`. Hay dos `nav` con `aria-current` (el lateral de Sara y la barra del celular) y la prueba espera uno. R1 la arregla al pasar a un solo `.nav-app`.

**Decisiones tomadas en R0 (todas de Isabella)**
- Estado neutro: casi blanco (h 85, croma ≤ 0,006); el botón principal va en aguacate.
- Sellos de la Res. 810: se exceptúan de la prueba de mayúsculas, el octágono crece hasta que su texto mida 12,8 px o más y llevan un nombre accesible en minúsculas.
- «Cerrar sesión» en celular: botón de texto al final de Avatar, siempre visible.
- Ánimo: sin flecha de volver, sin la píldora «+5 XP para todos los ánimos» y sin «(+5 XP)» en el botón.
- «Foto directa» queda como botón de texto dentro de «Tu día».
- Bootstrap: se quita de las pantallas privadas; si hay un componente JavaScript de Bootstrap, se cambia por `<dialog>` o `[hidden]`.
- Paleta y set de caras se guardan en el navegador, no en la cuenta (límite conocido; va a `docs/defensa/`).
- `--r-panel` se queda en 28 px; no se cambia `tokens.css` sin preguntar.

## R1 · Cimientos: un solo armazón: LISTA (7 oct 2026)

**Qué quedó listo**
- **Un solo armazón en las seis pantallas privadas** (Inicio, Mis registros, Registrar, Progreso, Avatar y Ánimo): `.app` + un único `<nav class="nav-app">`. En el computador es una barra lateral de 248 px (logo, cinco destinos y, abajo, nombre, nivel y «Cerrar sesión»); en el celular (≤ 720 px) el mismo `<nav>` es la barra inferior con Registrar al centro, relleno. Ya no hay un menú de celular aparte.
- `herramientas/menu_privado.py` se reescribió: solo regenera lo que hay entre las marcas `menu-privado:nav` de cada página (ya no arma el armazón). Se corre con `python3 herramientas/menu_privado.py`.
- Las seis páginas **ya no cargan** `style.css`, `pantallas-sara.css` ni `puente-sara.css`, ni las fuentes de Google (la fuente única es Bricolage Grotesque, local). Cargan `tokens.css`, `paletas.css`, `componentes.css` y el nuevo **`estilos/app.css`**.
- **Bootstrap:** el CSS ya no está en Avatar. Sigue en Inicio, Ánimo, Progreso, Registrar y Mis registros **solo por sus utilidades de grilla** (`d-flex`, `row`, `gap-*`…): su aspecto se reemplaza en `app.css` con tokens (secciones «PROVISIONAL»). Se borra pantalla por pantalla en R2, R3, R5 y R6. No hay ningún componente JavaScript de Bootstrap en las pantallas privadas (había un `bootstrap.bundle.min.js` sin uso en Mis registros: se quitó). Bootstrap Icons se queda.
- **Radios:** solo `--r-control`, `--r-tarjeta`, `--r-panel` y `--r-pildora` (o 50 % en círculos), medido por prueba. **Sombras:** una sola (`--s-2`), para la barra inferior y los avisos; las tarjetas se separan con un borde (`componentes.css`: `.tarjeta`, `.panel` y `.etiqueta`). No se tocó `tokens.css`.
- **Fondo y ancho:** el fondo es del `<html>` y cubre toda la altura; el contenido tiene `--ancho-contenido` como máximo. Se arregló además un desborde horizontal en el celular (la grilla del armazón y de `.contenido` usan `minmax(0, 1fr)`).
- **Quitado:** la hora en Inicio, la flecha de volver en Progreso **y en Ánimo**, el 🌿 y «LUMEA» en mayúsculas (el pie de Mis registros también usaba «LUMEA»: ahora es el logo).
- **Sello de advertencia (Res. 810):** el octágono mide 148 px para que su texto llegue a 12,8 px; es lo único con `text-transform: uppercase` (la prueba lo exceptúa). `.sello` y `.sello-mini` (Mis registros) comparten la misma regla. El nombre accesible en minúsculas (`role="img"` + `aria-label`) se hizo en la cámara (R5) y en Mis registros (R6).
- **Foco:** `componentes.css` usa `--c-foco` (el que mide `generar_paletas.py`) y ya no fuerza un radio al enfocar (deformaba círculos y píldoras).
- **«Cerrar sesión» en el celular:** botón de texto al final de Avatar, visible **solo ≤ 720 px** (en el computador ya está en el menú; mostrarlo dos veces en la misma pantalla era redundante). Si prefieres que se vea siempre, es borrar la regla `.salir-celular` de `app.css`.
- **Logo:** una sola imagen, `<img class="marca" src="img/logo.svg" alt="Lumea">`. `img/logo.svg` es un marcador que dice «Lumea» en texto (se adapta al modo oscuro del sistema, no a `data-modo`). **Cuando llegue el logo de Isabella en PNG:** copiarlo a `img/` y cambiar la constante `LOGO` de `herramientas/menu_privado.py`, correr la herramienta y reemplazar la misma ruta en el `<img class="marca">` del pie de `mis-registros.html` (y, en R7, en las páginas públicas).
- **Marcado para la prueba:** la acción principal de cada pantalla lleva `data-accion-principal` (hoy «Cámara en vivo» en Inicio, «Tomar foto» en Registrar y «Guardar mi ánimo» en Ánimo; R2 la cambia a «Registrar comida»).

**Pruebas:** `.venv/bin/pytest pruebas` → **297 pasan, 1 `xfail`** (el borrador `inicio.html`). Contraste (`-m capturas`, 5 paletas × claro/oscuro) sobre las seis pantallas: 0 errores.
- **Nueva:** `pruebas/test_rediseno.py` (74 casos, 6 pantallas × 1280 y 390 px): texto ≥ 12,8 px, radios, sin mayúsculas, fondo a toda la altura, menú y acción principal ≥ 44 × 44, un solo `nav`, sin estilos de Sara, logo, sin hora, sin flecha de volver, «Cerrar sesión» siempre a mano. Se comprobó que detectan (se inyectó un `<p>` de 10 px, radio 7 px y mayúsculas, y los tres fallaron).
- **Que ya fallaba y ahora pasa:** `test_avatar::test_un_solo_h1_y_la_navegacion_marca_avatar` (había dos `nav`).

**Pruebas que cambiaron en R1, y por qué** (ninguna se borró ni se debilitó)
- `test_navegacion.py::test_el_menu_del_celular_tiene_los_mismos_cinco_destinos`: ya no existe «Principal en celular»; ahora comprueba que el **mismo** `nav` (el único) queda pegado abajo con los cinco destinos y `aria-current`.
- `test_progreso.py::test_el_menu_lateral_…`: la zona de usuario del menú es «delgada» (nombre, nivel y «Cerrar sesión»), sin racha; renombrada a `…_muestra_nombre_y_nivel`. La racha se sigue probando en `test_muestra_el_nivel_y_la_racha`.
- `test_mis_registros.py::test_el_texto_del_servidor_nunca_es_html`: usa `text_content()` y no `inner_text()` para leer el sello, porque `inner_text` devuelve el texto en mayúsculas por el CSS del sello. Comprueba lo mismo (el texto del servidor no se convierte en HTML).

**Cosas que conviene saber**
- Las capturas `?piel=sara` de `test_capturas.py` ya no muestran el diseño de Sara en las pantallas privadas (esas páginas no cargan `puente-sara.css`): salen iguales que la piel de Lumea. Las páginas públicas siguen usando esa piel hasta R7.
- Las secciones «PROVISIONAL» de `app.css` (Inicio, check-in, Progreso, Registrar, Mis registros) son lo que mantiene presentable el marcado viejo mientras se rehace; no son el diseño final.
- Hay un fallo del hook `design-drift` en esta sesión (la ruta del plugin tiene espacios): no afecta al repositorio, solo imprime un error al escribir archivos.

## R2 · Inicio nuevo: LISTA (7 oct 2026)

**Qué quedó listo** (`index-ingresado.html`, `indexx.js`, `lumea-ui.js`, `estilos/app.css`; el esquema sale de `docs/rediseno/inicio-nuevo.md` y la estructura semántica, de `inicio.html` de Isabella, que no se tocó)
- De arriba abajo: saludo (`h1` «Hola, Ana», la fecha en un `<time>` y el chip «Nivel 2»), el aviso de regreso (si el backend lo manda), **dos tarjetas** (Tu día y ¿Cómo llegas hoy?) y **dos franjas planas** (Misión de hoy y Nivel y racha, que enlaza a Progreso). Cada bloque es una `<section aria-labelledby>`.
- **De 13 cajas a 4 superficies, de 11 textos con «XP» a 3** («10 de 15 XP hoy», el chip «+10 XP» de la misión y «Te faltan 35 XP para el nivel 3»). Una prueba lo mide.
- **«Registrar comida» es el único botón relleno** (`data-accion-principal`). «Foto directa» queda como botón de texto dentro de «Tu día» (aprobado) y sigue pasando la foto a Registrar.
- **«Tu día»:** «1 de 3 comidas» y la barra de la meta de comidas (`lumea-bind-comidas-bar`, nueva en `lumea-ui.js`) más la nota de XP de hoy.
- **Check-in:** eliges una cara (`aria-pressed`) y la guardas con **«Guardar mi ánimo»** (secundario, sin «+5 XP»). Antes tocar una cara guardaba al instante. Si ya hiciste el check-in hoy, se ve «Hoy llegaste: Bien…», los otros cuatro quedan en reposo y el botón de guardar se esconde. Cada botón trae un hueco `data-cara-checkin` para la cara del set que elija la persona (R3); mientras no haya set solo se ve la palabra. En una tarjeta angosta las cinco opciones van 3 + 2; si caben, en una fila (`container query`).
- Se conservaron las clases `lumea-bind-*` y los ids que usan `lumea-ui.js` y las pruebas. Inicio **ya no carga el CSS de Bootstrap**.
- **Quitado de Inicio:** el atajo «Acceso directo a la cámara» con «+10 XP», la canasta de cuatro formas, «¿Sabías que?», el botón del avatar de arriba, la frase «Cada bocado y cada emoción cuentan en tu bienestar» (el esquema solo trae la fecha) y «Mejor racha» (sigue en Progreso). La cara del avatar de hoy ya no sale en Inicio.
- **Ánimo se abre desde Inicio** con un enlace de texto dentro del check-in, «Ver mi semana de ánimo» (la decisión de navegación lo exige y la franja de ánimo de la canasta, que antes lo enlazaba, ya no existe).

**Pruebas:** `.venv/bin/pytest pruebas` → **304 pasan, 1 `xfail`**. Contraste de Inicio en 5 paletas × claro/oscuro: 0 errores.

**Pruebas que cambiaron en R2, y por qué** (`test_index_ingresado.py`; ninguna se borró ni se debilitó)
- Las de la meta, las comidas, el nivel y la misión cambiaron de selector (`#shape-*`, `.card-racha-nivel` y `.progress-bar` pasaron a `.inicio__dia`, `.inicio__nivel` y `[role=progressbar]`); los textos esperados son los mismos («Meta cumplida: 20 XP hoy», «1 de 3», «Te faltan 35 XP para el nivel 3», «+10 XP»). La comida suma una comprobación de la barra (33 %).
- **Misiones listas «N de 3» (la forma de la canasta)** y **la cara de ánimo de hoy en la canasta**: ya no existen en el diseño nuevo. La primera se reemplazó por la prueba de la franja «Misión de hoy» (con tres cumplidas, el chip se esconde); la segunda, por la de «si ya hizo el check-in hoy».
- **Check-in:** «usa las caras del avatar» pasó a «cinco estados con su palabra y sin XP»; «guarda, celebra y queda registrado» ahora toca una cara y luego «Guardar mi ánimo»; nuevas: elegir no guarda, si guardar falla se puede reintentar, y el enlace a la semana de ánimo.
- **El rebote de la canasta con movimiento reducido:** se borró porque la canasta ya no existe (no hay nada que rebote). El movimiento de la cara elegida se prueba en R3 y R8.
- **Nuevas** (el diseño nuevo): cuatro superficies y un solo botón relleno, XP ≤ 3, secciones con título, jerarquía de tamaños, la fecha en `<time>` sin hora.

## R3 · Caras del check-in con DiceBear: LISTA (7 oct 2026)

**Qué quedó listo** (`caras-checkin.js`, `emociones.html`, `emociones.js`, `index-ingresado.html`, `estilos/app.css`)
- **`caras-checkin.js`** con un solo objeto `ESTILOS` que Isabella puede leer y editar (los sets `gaze` y `moods` de la misión, tal cual). API: `LumeaCaras.poner("gaze" | "moods" | null)`, `actual()`, `url()`, `imagen()` (la usará el selector de R4) y `dibujar()`.
- **Cada persona elige su set; ninguno es predeterminado.** La elección se guarda en `localStorage` con la clave `lumea-caras` (con `try/catch`, como `tema.js`) y emite `lumea:caras`. Sin elección, o con un valor desconocido, no hay imagen: queda la palabra, y el hueco no ocupa lugar.
- **El color del cuerpo** sale de `--c-emocion` de la paleta activa y las caras se vuelven a dibujar con `lumea:tema` (al cambiar de paleta o de modo).
- **Quietas por defecto** (`animationVariant=none`); solo la del botón con `aria-pressed="true"` va con `medium`. Un `MutationObserver` redibuja solo esa cara cuando cambia el botón elegido, así que el movimiento sigue a lo que la persona hace y nunca hay cinco caras moviéndose. La animación vive dentro del SVG y se apaga sola con `prefers-reduced-motion`.
- **Accesibilidad:** `alt=""`; la palabra visible es el nombre del botón; la selección es `aria-pressed`. Sin internet, la imagen se quita y queda la palabra; el botón funciona igual.
- **Las diez direcciones se verificaron en el navegador** (200, `image/svg+xml`, el color llega en la dirección) y se comprobó que `animationVariant=none` quita las animaciones del SVG y `medium` las trae con su `prefers-reduced-motion`.
- **Ánimo (`emociones.html`) se rehízo con el mismo componente de Inicio** (`.animo-caras` / `.animo-cara`) y dejó de cargar el CSS de Bootstrap (como no tiene fase propia, se terminó aquí). Sin la flecha (R1), sin la píldora «+5 XP para todos los ánimos», sin «+5 XP» en los botones ni «(+5 XP)» en «Guardar mi ánimo». La cara **grande** y la **semana** siguen con la cara del avatar (decisión de la misión).
- **Marcado:** los botones del check-in ya no usan `data-cara`; usan `data-cara-checkin` (así `lumea-ui.js` no les pinta la cara del avatar).
- **Privacidad y límite conocido** anotados en `docs/defensa/privacidad-y-limites-rediseno.md` (la dirección no lleva datos de la persona; la paleta y las caras se guardan en el navegador, no en la cuenta).
- **Créditos:** no había pantalla de créditos ni README; se creó un `README.md` corto con la sección «Créditos» («Caras del check-in: DiceBear (CC0)», más la fuente y los íconos). Si prefieres la pantalla de créditos, se mueve esa línea.

**Pruebas:** `.venv/bin/pytest pruebas` → **349 pasan, 1 `xfail`**. Contraste de Inicio y Ánimo en 5 paletas × claro/oscuro: 0 errores.
- **Nueva:** `pruebas/test_caras_checkin.py` (45 casos) en Inicio y en Ánimo, con los tres estados (sin elección, `gaze` y `moods`): dirección sin datos personales, `alt=""`, `aria-pressed`, solo la elegida se anima, el color sigue a la paleta y al modo, el redibujo con `lumea:tema` y con `lumea:caras`, un valor guardado desconocido, `localStorage` que falla, sin internet, y que ningún botón dice «XP» ni tiene un color distinto por ánimo.
- **Cambiaron en `test_emociones.py`** (ninguna se borró ni se debilitó): `.btn-face-mood` / `.face-name-label` pasaron a `.animo-cara` / `.animo-cara__nombre`; «los cinco estados con la cara del avatar» pasó a «con su palabra y sin XP» (las caras de cada set van en la prueba nueva); «sin internet» ahora parte de un set elegido; el botón se llama «Guardar mi ánimo» (sin «(+5 XP)»). Nuevas: sin píldora, sin flecha y sin «+5»; las caras de los botones son las del set y la grande sigue siendo la del avatar.

**Para decidir**
- **La cara elegida** va sobre un fondo suave de «emoción» con borde del mismo rol y no sobre el color pleno: el cuerpo de la cara ya es `--c-emocion`, y sobre ese mismo color se perdía.
- **El texto de Ánimo «Todas las emociones dan el mismo XP: no se premia estar siempre bien.»** se dejó igual (es de Sara y dice una cosa importante), pero choca con la regla 4 (el XP solo en el nivel, las misiones y la celebración). En Inicio no está (el esquema trae otra nota). Dime si lo cambio.
- Falta que `tema.js` no tenga paleta predeterminada y que haya dónde elegir el set (R4): hasta entonces, para probarlo: `LumeaCaras.poner("gaze")` en la consola.

## R4 · Paleta y caras, sin predeterminados: LISTA (7 oct 2026)

**Qué quedó listo** (`herramientas/generar_paletas.py`, `estilos/paletas.css`, `estilos/tokens.json`, `docs/validacion-paletas.md`, `tema.js`, `selector-colores.js`, `index-ingresado.html`, `avatar.html`, `indexx.js`, `estilos/app.css`, `MARCA.md`)
- **Estado neutro.** `generar_paletas.py` tiene una paleta nueva, «neutro», que es la de `:root` (cuando no hay `data-paleta`). Superficies casi blancas (h 85, croma ≤ 0,006: el más alto es 0,0059) y texto sin tono; los **colores de rol son los de siempre** (los de Laguna), y el botón principal sigue en aguacate. Pasa los mismos 12 chequeos de contraste WCAG y de daltonismo que las demás. `paletas.css`, `tokens.json` y el informe se regeneraron con la herramienta (no se editaron a mano). Laguna ya no es la de `:root`: es una paleta más, igual que las otras cuatro.
- **Cuidado que ya está resuelto:** el bloque de `:root` tiene la misma especificidad que `[data-paleta="x"]`, así que **tiene que ir primero** en el CSS; si no, taparía a las paletas que quedaran antes. El generador lo pone primero y una prueba lo vigila. Las cinco paletas de siempre no cambiaron ni un color (se comparó contra el `tokens.json` anterior).
- **El estado neutro no se puede elegir:** no está en `LumeaTema.PALETAS` ni en el selector, y `ponerPaleta('neutro')` no hace nada. `tema.js` ya no cae en ninguna paleta; suma `paletaActual()` y `modoGuardado()`.
- **`selector-colores.js`:** un componente (lo llenan los contenedores `[data-selector-colores]`) con tres `radiogroup` de botones de radio de verdad (teclado, flechas y lector de pantalla sin código extra): **Colores** (cada opción es una tira con los cinco colores de rol de su paleta y su nombre; la tira usa el `data-paleta` de la opción, y `data-modo` el modo de ahora), **Modo** (Claro, Oscuro, Como mi dispositivo) y **Caras** (Miradas y Gestos, con sus cinco caras quietas en el color de emoción de la paleta activa). **Al elegir se aplica y se guarda al instante** (`LumeaTema.ponerPaleta` / `ponerModo`, `LumeaCaras.poner`), y los botones del check-in cambian en el mismo momento.
- **Inicio:** arriba aparece la tarjeta «Elige tus colores y tus caras» mientras **falte la paleta o el set de caras**. No es un diálogo (no impide registrar una comida) y no cuenta como superficie ni como botón relleno. **«Listo»** la cierra y no vuelve a aparecer (se recuerda en el navegador: `lumea-colores-listo`); **«Ahora no»** la esconde solo durante esta sesión. Una vez abierta se queda abierta aunque elijas las dos cosas, hasta que la cierres. El foco pasa a «Registrar comida».
- **Avatar:** sección «Mis colores y caras» con el mismo selector, sin «Listo» ni «Ahora no», para cambiarlos cuando sea.
- **Páginas públicas:** se ven en el estado neutro o en la paleta que ese navegador ya tenga guardada (`tema.js` la aplica); no se tocó ninguna. **Crear cuenta** no tiene ningún paso nuevo (hay una prueba).
- **`MARCA.md`** ya no dice «Laguna Verde (predeterminada)»: dice que ninguna lo es y describe el estado neutro.

**Pruebas:** `.venv/bin/pytest pruebas` → **418 pasan, 1 `xfail`**. `.venv/bin/pytest pruebas -m capturas` → 234 casos (ahora con el **estado neutro** además de las 5 paletas × claro/oscuro) con **0 errores de contraste en todas las páginas**.
- **Nuevas:** `pruebas/test_paletas.py` (32: el neutro pasa contraste y daltonismo como Laguna, sin tono, conserva los colores de rol y la marca, va primero en el CSS, y los archivos generados están al día con el script; en el navegador, sin paleta guardada se ve el neutro y no Laguna —en claro y oscuro, en Inicio, Progreso y la Bienvenida—, elegir aplica la suya, el neutro no se puede elegir, los nombres viejos siguen funcionando) y `pruebas/test_selector_colores.py` (37: cuándo aparece la tarjeta, que no es un diálogo, Listo y Ahora no, los tres grupos, las tiras con los colores de cada paleta en claro y oscuro, elegir aplica y guarda, las caras toman el color de la paleta, sin internet, teclado y foco, la sección de Avatar y que Crear cuenta no cambió).
- **Cambiaron** (ninguna se borró ni se debilitó): `test_index_ingresado.py`: «cuatro superficies» y «cada bloque es una sección» ahora excluyen la tarjeta de colores (la misión dice «sin contar la tarjeta»); `test_capturas.py` suma el estado neutro (sin paleta guardada).

**Para decidir**
- **«Listo» se recuerda.** La misión dice «Listo cierra la tarjeta» y «mientras falte la paleta o el set»; sin recordar «Listo», alguien que prefiere las caras solo con palabra vería la tarjeta en cada visita. Si prefieres que reaparezca mientras falte algo, se quita una línea de `indexx.js`.
- **No hay una opción «solo la palabra»** en las caras (la misión no la pide): para volver a no tener caras hay que borrar la elección (`LumeaCaras.poner(null)`). Dime si la quieres como tercera opción.
- **Los tonos de las tarjetas elegidas** (fondo `--c-marca-suave` y borde `--c-marca-tinta`) toman el color de marca de la paleta: en Carnaval se ven verde lima, como el botón principal de esa paleta.

## R5 · Registrar: LISTA (7 oct 2026)

**Qué quedó listo** (`alimentos.html`, `estilos/app.css`, `lumea-camara.js`; `componentes.css` ya traía la etiqueta, el visor y las opciones)
- **Una sola acción principal:** «Tomar foto» es el único botón relleno (antes había cinco iguales). «Encender cámara» es secundario; «Subir foto», «Otra foto» y «Apagar» son botones de texto. Todos los íconos son de Bootstrap Icons (se quitaron los SVG a mano). Ya no carga el CSS de Bootstrap.
- **Dos columnas en el computador** (la cámara y «Lo que reconoció Lumea» lado a lado) y una en el celular. El `h1` «Registrar comida» ahora se ve (antes estaba escondido). Los títulos «1. MUÉSTRALE TU PLATO» y «2. LO QUE VE LA IA» pasaron a «Muéstrale tu plato» y «Lo que reconoció Lumea»; los criterios Sellos, Energía y Precisión ya no están en tarjetas ni en mayúsculas.
- **Resultado** (la etiqueta de plaza de `componentes.css`): el nombre del alimento en `--t-3xl`, la certeza **en palabras y número** («La IA está segura: 94 %» / «La IA no está segura: 65 %», al tamaño del cuerpo: antes 10 px), las calorías en una línea, los sellos, las opciones para confirmar, el mensaje, el dato curioso y los logros. **«IA duda»** usa el contenedor del rol duda (el mango no se usa como texto); «IA segura», la etiqueta normal. Antes de la primera foto solo se ve la invitación a tomarla.
- **Calorías:** `const MOSTRAR_CALORIAS = true;` arriba de `lumea-camara.js`, con el comentario «Decisión de Isabella, 7 oct 2026: se muestran». En `true`, una sola línea secundaria («Calorías aproximadas: 120 kcal por 100 g»), sin color de alerta; en `false`, no se dibujan.
- **Sellos (Res. 810):** siguen en negro, ahora con el octágono de 148 px que deja su texto en 12,8 px, y con nombre accesible en minúsculas (`role="img"` + `aria-label="Exceso en azúcares"`). Van dentro de un `.sellos`, que en modo oscuro les pone la placa clara alrededor (el negro solo no se ve: 1.1–1.5:1).
- **Lo que tocó `lumea-camara.js`** (la lógica de la cámara y del backend no cambió): la constante de las calorías, el atributo `data-estado="segura"|"duda"` en el contenedor del resultado (para que el CSS lo pinte), el texto de la certeza, los sellos con su `aria-label` dentro de `.sellos`, y la clase de los botones de opciones (`opciones__boton`). El contrato de ids del encabezado sumó `resultado`.
- Se quitó de `app.css` todo lo provisional de Registrar y los `lumea-btn-*` de Sara.

**Pruebas:** `.venv/bin/pytest pruebas` → **435 pasan, 1 `xfail`**. Contraste: 0 errores en Registrar vacío (5 paletas + neutro × claro/oscuro) y **también con resultado «segura» (con sellos) y «duda»** en las 12 combinaciones (prueba nueva en `test_capturas.py`).
- **Cambió en `test_camara.py`:** `test_ia_segura_muestra_logros` esperaba «94% seguridad» y ahora «La IA está segura: 94 %» (el texto de la certeza es otro). Nada más se tocó.
- **Nuevas (14):** antes de la foto solo hay la invitación; «Tomar foto» es la única acción principal; los íconos son de Bootstrap Icons; el nombre en `--t-3xl` y la certeza en 16 px; «IA duda» en el contenedor del rol duda sin texto en mango; las calorías en una línea secundaria; el interruptor `MOSTRAR_CALORIAS` está arriba con su comentario y en `false` no se dibuja; sin dato de calorías no se dibuja la línea; los sellos (nombre accesible, texto ≥ 12,8 px, cabe en el octágono, siempre negro, mayúsculas oficiales, placa en oscuro); nada en mayúsculas salvo el sello; todo el texto ≥ 12,8 px; sin desborde en 375 y 1280 px; lado a lado en computador y apilado en celular.

**Para decidir**
- **Calorías «por 100 g».** La misión da el ejemplo «Calorías aproximadas: 60 kcal». El catálogo trae las kcal **por cada 100 g** (el banano trae 89), así que decir solo «60 kcal» sería prometer algo que Lumea no sabe (una porción). Puse «… kcal por 100 g». Si prefieres otra frase, es una línea de `lumea-camara.js`.
- **Mientras «IA duda» no se muestran las calorías ni los sellos** (son de una suposición que la persona todavía no confirmó). Al confirmar, aparecen con la comida elegida. Antes se mostraba la energía de la suposición.
- **El mensaje de «IA duda»** («La IA no está segura. Toca el que es para guardarlo en tu historial.») no cambió.

## R6 · Avatar, Progreso y Mis registros, en armonía: LISTA (7 oct 2026)

**Qué quedó listo** (`avatar.html`, `avatar.js`, `estilos/avatar.css`, `progreso.html`, `mis-registros.html`, `estilos/app.css`)
- **Avatar.** Sin el gran fondo rosado: la vitrina es una tarjeta con borde sobre una superficie tranquila y la figura va sobre el fondo de la página; las misiones también son tarjetas con borde (antes cada una era una caja lila de «misión»: el color quedó en el chip «+10 XP» y en la calcomanía). **Dos columnas desde 992 px** (avatar y nivel a la izquierda, pestañas a la derecha) y una sola debajo (antes el corte era 840 px). La sección «Mis colores y caras» (R4) y «Cerrar sesión» del celular (R1) siguen debajo.
- **Progreso.** **Cinco superficies:** el nivel, la racha, las comidas de la semana, el ánimo de la semana y el enlace al álbum (una franja plana, no una tarjeta). Se quitó el botón «Ver mi avatar» de arriba (el menú ya lleva a Avatar) y la flecha de volver (R1). El mensaje de regreso va arriba, como en Inicio. La racha actual y la mejor ahora viven en una sola superficie (antes eran dos cajitas dentro de la del nivel). Sin Bootstrap; ningún botón relleno (el enlace al check-in es secundario).
- **Mis registros.** **Una lista de filas, no de tarjetas:** nombre y fecha a la izquierda, calorías y certeza a la derecha, y los sellos debajo; se separan con una línea. Sin Bootstrap (el «cargando» es una línea de texto, no un spinner; el error es un `role="alert"`). El título pasó de «Mis Registros» a «Mis registros», como el menú. El pie sigue llevando a las páginas públicas (ahora con el logo, no con «LUMEA»).
- **Sellos de advertencia en Mis registros:** nombre accesible en minúsculas (`role="img"` + `aria-label`) y dentro de un `.sellos`, que en modo oscuro les pone la placa clara alrededor.
- **Algo que arreglé de paso (venía desde R1):** al dejar de cargar `puente-sara.css` se perdió la «placa» de los sellos en modo oscuro; en realidad nunca funcionó (un `drop-shadow` puesto sobre un elemento con `clip-path` queda recortado). Ahora el filtro va en la envoltura `.sellos`, que no se recorta, en la cámara (R5) y en esta lista. Una prueba lo comprueba en las dos.
- `app.css` ya **no tiene nada provisional ni de Bootstrap**; el CSS de Bootstrap ya no se carga en ninguna pantalla privada (Bootstrap Icons sí).

**Pruebas:** `.venv/bin/pytest pruebas` → **452 pasan, 1 `xfail`**. Contraste de Progreso, Avatar (las tres pestañas) y Mis registros en 5 paletas + neutro × claro/oscuro: 0 errores.
- **Se reescribió `test_mis_registros.py`** (conserva las pruebas de seguridad, sellos, vacío, error y sesión): la primera comparaba el HTML exacto de la tarjeta con la plantilla vieja y, al pasar a filas, no tiene sentido. Se reemplazó por una que comprueba que **cada fila muestra los mismos datos que la tarjeta de antes** (nombre, fecha, kcal y certeza de los tres registros) y que es una `<li>` sin sombra. `test_el_texto_del_servidor_nunca_es_html` sigue comprobando lo mismo. Nuevas: íconos de Bootstrap Icons, sellos con nombre accesible y placa en oscuro, sin sesión, mismo armazón y escala, y el pie.
- **`test_progreso.py`:** `.nivel-badge` y `.progress-bar` pasaron a `.lumea-bind-nivel` y `[role=progressbar]` (el marcado cambió; los textos esperados son los mismos). Nuevas: cinco superficies, sin flecha ni botón del avatar, sin Bootstrap ni clases suyas, jerarquía de tamaños, la racha en una superficie, sin botón relleno, y en celular cabe y apila.
- **`test_avatar.py`** (nuevas, ninguna existente cambió): la vitrina y las misiones sobre superficie tranquila, dos columnas desde 992 px (se mide en 1280, 992, 991 y 390), sin Bootstrap.

**Para decidir**
- **El botón «Ver mi avatar» de Progreso se quitó** (el menú ya lleva a Avatar). Si lo quieres de vuelta, es un enlace de texto en el encabezado.
- En la franja del ánimo de Progreso, la insignia «Es tuyo y no se compara con nadie» pasó a ser parte de la nota (mismo mensaje, sin la píldora).

## R7 · Páginas públicas, solo con CSS: LISTA (7 oct 2026)

**Qué quedó listo** (`estilos/publico.css`, y el `<head>` y el logo de las seis páginas: `index.html`, `conocenos.html`, `guialumea.html`, `crear-cuenta.html`, `iniciar-sesion.html` y `terminos.html`)
- **`estilos/publico.css`**, cargado después de `style.css` (y de `puente-sara.css`, que ya les pasó los colores a los tokens) en las seis páginas. Hace esto:
  - **Colores:** los verdes de Sara que quedaban pasan a tokens (el verde oscuro de `text-success-emphasis` era el último que no seguía la paleta); las páginas se ven en el **estado neutro** o en la paleta que ese navegador ya tenga guardada. Se midió: ningún color verdoso que no sea un token.
  - **Tipografía:** Bricolage Grotesque en todo el texto y la **escala de tipos** de `tokens.css` (los títulos de página en `--t-3xl` en pantallas anchas y `--t-2xl` en celular, las secciones en `--t-xl`, el cuerpo en `--t-m`, lo secundario en `--t-s`); ningún texto por debajo de 12,8 px.
  - **Radios:** los cuatro de siempre (los botones —también los «pastilla» de Sara— pasan a `--r-control`; las insignias, a `--r-pildora`; las tarjetas, a `--r-tarjeta`). Se logra redefiniendo las variables `--bs-border-radius-*` de Bootstrap y corrigiendo las clases propias de Sara.
  - **Sin mayúsculas** por CSS (el `text-uppercase` de las insignias), y **sin sombras**: las tarjetas y avisos se separan con un borde.
- **`<head>`:** se quitaron las fuentes de Google (la fuente única es local) y se agregó `publico.css`. **Logo:** las líneas de `.logo-brand` pasaron de `<span>🌿</span> LUMEA` a `<img class="marca" src="img/logo.svg" alt="Lumea">` (la misma imagen y el mismo lugar para cambiarla que el menú privado). **No se cambió ningún texto ni ninguna otra parte del `<body>`:** se comprobó, comparando el texto de cada página con el del commit anterior (idéntico en las seis, salvo el enlace del logo).
- **Crear cuenta** no tiene ningún paso nuevo (una prueba lo vigila: ni el selector de colores ni `caras-checkin.js`).

**Pruebas:** `.venv/bin/pytest pruebas` → **555 pasan, 1 `xfail`**, con **`pruebas/test_publico.py`** nuevo (103 casos, 6 páginas × 1280 y 390 px): `publico.css` va después de `style.css`; ya no piden fuentes a Google; el logo es una imagen sin 🌿 ni «LUMEA»; los radios son los cuatro tokens; nada en mayúsculas por CSS; todo el texto en Bricolage y en la escala de tipos (y ≥ 12,8 px); sin sombras; sin barra horizontal; los botones son controles y las insignias, píldoras; sin paleta guardada se ve el neutro y con una guardada, esa; Crear cuenta sin pasos nuevos.

**Para después de unir:** cinco cosas que no se hicieron porque tocan el `<body>` de una página de Isabella (el pie con emoji y «LUMEA», los emojis de Crear cuenta, «LUMEA» en mayúsculas dentro de los textos, estilos en línea y dos `innerHTML`): están en la sección «Para después de unir», más abajo.

## Textos nuevos para que Isabella revise

**Inicio (R2)**
- «Tu día» · «comidas» (en «1 de 3 comidas») · «Registrar comida»
- «Elige la cara que más se parece a tu día» (viene del esquema del documento) · «Guardar mi ánimo» · «Ver mi semana de ánimo»
- «Misión de hoy»
- Títulos que solo oye el lector de pantalla: «Nivel y racha» y «. Ver mi progreso» (al final de la franja del nivel)
- Racha dentro de la franja del nivel: «Te faltan 35 XP para el nivel 3. Racha: 3 días»
- Aviso si falla la foto directa: «No se pudo abrir la foto. Prueba con «Registrar comida».» (antes decía «Cámara en vivo»)

**Selector de colores y caras (R4)**
- Tarjeta de Inicio: «Elige tus colores y tus caras» · botones «Listo» y «Ahora no»
- Sección de Avatar: «Mis colores y caras»
- Títulos de los grupos: «Colores», «Modo», «Caras»
- Nombres de las paletas: Laguna, Neblina, Carnaval, Colibrí, Cosecha (los de `MARCA.md`; **siguen pendientes de votar** con estudiantes y familias)
- Modos: «Claro», «Oscuro», «Como mi dispositivo»
- Sets de caras (nombres provisionales de la misión): «Miradas» (`gaze`, solo ojos) y «Gestos» (`moods`, ojos y boca)

**Registrar (R5)**
- «Muéstrale tu plato» (antes «1. MUÉSTRALE TU PLATO») · «Lo que reconoció Lumea» (antes «2. LO QUE VE LA IA»)
- «Tomar foto» (antes «Tomar foto (espacio)»; la barra espaciadora sigue funcionando y el botón lo anuncia con `aria-keyshortcuts`)
- Invitación antes de la primera foto: «Toma una foto de tu plato o súbela y aquí verás lo que reconoció Lumea.»
- Certeza: «La IA está segura: 94 %» y «La IA no está segura: 65 %»
- Calorías: «Calorías aproximadas: 120 kcal por 100 g»
- Rótulo de los sellos: «Sellos de advertencia» (antes «Sellos»); nombres accesibles de cada sello: «Exceso en sodio», «Exceso en azúcares», «Exceso en grasas saturadas», «Exceso en grasas trans», «Contiene edulcorantes»

**Progreso y Mis registros (R6)**
- Progreso: título de sección «Racha» (nuevo) · nota del ánimo: «Las caras de tu avatar a lo largo de los días. Es tuyo y no se compara con nadie.» (antes: «Las caras de tu avatar reflejadas a lo largo de los días:» más la insignia «Es tuyo y no se compara con nadie»)
- Mis registros: título «Mis registros» (antes «Mis Registros»)

*(Se llena fase por fase.)*

## Para después de unir

(Cambios que necesitan tocar el `<body>` de una página pública o un archivo de Isabella; no se hicieron.)

1. **El pie de las seis páginas públicas** lleva `<span class="fw-bold hero-title">🌿 LUMEA</span>`: un emoji como ícono y «LUMEA» en mayúsculas, que `MARCA.md` prohíbe. Debería ser `<img class="marca" src="img/logo.svg" alt="Lumea">`, igual que el encabezado.
2. **`crear-cuenta.html`**: las cinco opciones de «Objetivo Principal» usan emojis como íconos (🥗 💧 🏃 🌙 🔍). Deberían ser Bootstrap Icons.
3. **«LUMEA» escrito en mayúsculas dentro de los textos** («Bienvenido a LUMEA», «Guía LUMEA», «¿Cómo utilizar LUMEA?»…): el menú y el logo dicen «Lumea». Decide cuál es la forma de la marca y se unifica.
4. **`style="font-size: …"` escritos en el HTML** (`terminos.html` en los `step-badge`, `conocenos.html` en dos párrafos): `publico.css` los lleva a la escala con `!important`. Cuando se unan los textos conviene quitar esos estilos del HTML.
5. (Ya anotado antes) `crear-cuenta.html`, función `mostrarAlerta`, escribe el mensaje con `innerHTML`; y `sesion-nav.js` escribe el correo con `innerHTML`.
