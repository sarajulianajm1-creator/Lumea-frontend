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

## R8 · Movimiento: LISTA (7 oct 2026)

**Qué quedó listo** (`estilos/app.css` sección 9, `estilos/componentes.css`)
- **Una sola entrada por pantalla:** el `<main class="contenido">` de las seis pantallas aparece y sube 8 px (`--e-2`) **una vez, en 220 ms** (`--m-base`, curva `--m-salida`). Con `prefers-reduced-motion` no hay animación: el contenido solo aparece.
- **Cambio de paleta:** el fondo y el texto de la página (`html` y `body`) cambian de color en 220 ms. La transición va **solo en esas dos propiedades y solo en la página** (no hay ningún `transition: all`).
- **Responder a la persona:** pasar el cursor, enfocar o tocar dura 120 ms (`--m-rapido`) en botones, enlaces del menú, caras del check-in, opciones del selector y pestañas (ya era así; ahora una prueba lo comprueba).
- **La cara elegida del check-in se anima** (R3) y **la celebración queda como está** (no se tocó `celebracion.css`).
- **Lo que dejó de moverse** (todo era movimiento que nadie pidió):
  - La **transición automática entre páginas** (`@view-transition` en `componentes.css`): sumaría una segunda entrada.
  - La **barra de nivel que se llenaba con rebote** cada vez que se abría una pantalla: ahora aparece llena hasta donde va.
  - El **destello del esqueleto de carga** (se repetía sin parar, con una duración escrita a mano y un degradado): ahora es de un solo color y está quieto.
  - La entrada `etiqueta--entrando` / `@keyframes colgar` de la etiqueta de plaza (no la usaba nadie).
- Con movimiento reducido todas las duraciones valen 0 ms (`tokens.css`) y ninguna transición dura nada.

**Pruebas:** `.venv/bin/pytest pruebas` → **590 pasan, 1 `xfail`**. **Nueva:** `pruebas/test_movimiento.py` (35 casos): al abrir cada pantalla se mueve una sola cosa (se anota todo `animationstart` y todo `transitionrun` desde antes de que cargue cualquier script: solo «entrada» y ninguna transición de tamaño o lugar); la entrada es de 220 ms, una vez, sube 8 px y termina quieta; con movimiento reducido no se anima nada; ninguna transición ni animación pasa de 420 ms (se mide en cada elemento de cada pantalla); **ninguna hoja escribe una duración a mano** (todas salen de `tokens.css`); no queda `@view-transition`; el cursor y el foco responden en 120 ms; la transición del cambio de paleta es solo de fondo y texto (y con movimiento reducido es instantánea); el esqueleto está quieto; la barra de nivel no se llena sola. Ninguna prueba existente cambió.

**Para decidir**
- **El destello del esqueleto y la barra con rebote se quitaron** porque la regla es «nada más se mueve». Si quieres que la barra de nivel «se llene» al abrir Progreso o Avatar como un momento de logro, se vuelve a poner con una línea en `componentes.css`, pero sería una segunda animación por pantalla.
- `inicio.css` (el ejercicio de Isabella) todavía trae su propio `@view-transition`; no se toca. Solo lo carga `inicio.html`.

## R9 · Revisión y entrega: LISTA (7 oct 2026)

**Qué quedó listo**
- **Pruebas:** `.venv/bin/pytest pruebas` → **636 pasan, 1 `xfail`** (el borrador `inicio.html`; los 258 casos de contraste van aparte, con `-m capturas`). Ninguna prueba se borró ni se debilitó (la lista de las que cambiaron está abajo).
- **Contraste:** `pytest pruebas -m capturas` → **258 casos pasan** (las seis pantallas privadas —Avatar con sus tres pestañas— y las seis públicas, en las 5 paletas + el estado neutro × claro/oscuro, más Registrar con el resultado «IA segura» —con sellos— y «IA duda» en las 12 combinaciones). **0 errores de contraste en todas las pantallas del rediseño** (el resumen está en `pruebas/capturas/contraste.txt`, que git ignora). Lo único con contraste bajo es `?piel=sara` en las páginas públicas (el diseño original de Sara, que ya no es el de Lumea y que solo se conserva para comparar).
- **Recorrido de accesibilidad, hecho por una prueba nueva** (`pruebas/test_accesibilidad.py`, 46 casos) en vez de a mano, para que se repita cada vez:
  - **Teclado, sin mouse:** con Tab se recorre cada control de las seis pantallas a 1280 y a 320 px, sin trampa de teclado, cada parada es un control distinto, el foco siempre se ve (borde o anillo de 2 px como mínimo) y nunca queda fuera de la pantalla; lo primero que se alcanza es el menú, en su orden; Shift+Tab vuelve sin perderse.
  - **Zoom y reflujo (WCAG 1.4.10):** sin barra horizontal a 200 % de zoom (640 px de ancho) y a 320 px, en las seis pantallas; también Registrar con un resultado largo y tres sellos, Mis registros con nombres largos y la tarjeta de colores y caras.
  - **Flujos solo con teclado:** el check-in de Inicio (elegir una cara con Espacio, guardar con Enter), el menú, cerrar la tarjeta de colores (el foco pasa a la acción principal) y cerrar sesión.
  - **Nada solo con color:** la cara y la paleta elegidas se distinguen por `aria-pressed` o el radio marcado (lo oye el lector de pantalla) y por un borde más grueso.
  - Se comprobó que las pruebas detectan: se rompió a propósito el comportamiento que miden y fallaron; después se deshizo el cambio.
- **Capturas «después»** en `pruebas/capturas/despues/` (carpeta ignorada por git; **Isabella elige cuáles guarda para la defensa**): las seis pantallas privadas y la Bienvenida, en el estado neutro (como las ve una persona nueva), a 1280 y a 390 px (`<pantalla>__1280.png` y `__390.png`), más cuatro con paleta: Inicio en Colibrí oscuro, Progreso en Laguna, Avatar en Carnaval y Mis registros en Cosecha (`<pantalla>-<paleta>-<modo>__<ancho>.png`). Las capturas «antes» siguen en `pruebas/capturas/antes/`. El menú del celular sale a mitad de la captura de página completa porque es una barra pegada abajo.
- **Documentación:**
  - `docs/bitacora-ia.md`: una fila por fase (R0 a R9).
  - `docs/defensa/preguntas-rediseno.md`: **seis preguntas** que un jurado podría hacer (sin paleta predeterminada, DiceBear y la privacidad, `localStorage`, accesibilidad, gamificación sin juicio y movimiento reducido), cada una con el archivo donde está la respuesta y la prueba que la comprueba. **Sin respuestas:** las escribe Isabella.
  - `docs/defensa/privacidad-y-limites-rediseno.md`, `MARCA.md` y `README.md` (créditos de DiceBear) al día.

**Pruebas que cambiaron en todo el rediseño, y por qué** (ninguna se borró ni se debilitó una de accesibilidad)
- **R1:** `test_navegacion.py` (el menú del celular ahora es el mismo `nav`, el único), `test_progreso.py` (la zona de usuario del menú es delgada: nombre, nivel y «Cerrar sesión») y `test_mis_registros.py` (lee el sello con `text_content()` porque el CSS lo pone en mayúsculas). `test_avatar.py::test_un_solo_h1_…` ya fallaba (dos `nav`) y ahora pasa.
- **R2:** `test_index_ingresado.py` (selectores nuevos por el marcado nuevo —`.inicio__dia`, `.inicio__nivel`, `[role=progressbar]`—, con los mismos textos esperados; el check-in ahora elige una cara y luego «Guardar mi ánimo»; se borró la del rebote de la canasta porque la canasta ya no existe).
- **R3:** `test_emociones.py` (el marcado de Ánimo pasó a `.animo-cara`; mismas comprobaciones de guardado, celebración y errores).
- **R5:** `test_camara.py` (la certeza ahora dice «La IA está segura: 94 %»).
- **R6:** `test_progreso.py` (`.nivel-badge` y `.progress-bar` pasaron a `.lumea-bind-nivel` y `[role=progressbar]`) y `test_mis_registros.py` (reescrita para la lista de filas: `ul#listaRegistros > li.registro`, `#errorHistorial`; mismas comprobaciones de datos, errores, sesión y que el texto del servidor nunca es HTML).
- **R4:** `test_capturas.py` (suma el estado neutro y los resultados «segura» y «duda»). `test_avatar.py` solo sumó pruebas.
- **Nuevas:** `test_rediseno.py`, `test_caras_checkin.py`, `test_paletas.py`, `test_selector_colores.py`, `test_publico.py`, `test_movimiento.py` y `test_accesibilidad.py`.

**Para decidir** (todo lo que quedó abierto en las fases, en un solo lugar; cada punto dice qué se cambia si prefieres otra cosa)
1. **Cerrar sesión en el celular:** el botón de texto está solo al final de Avatar y solo ≤ 720 px (R1). Si lo quieres siempre, se borra la regla `.salir-celular` de `app.css`.
2. **Inicio:** el enlace «Ver mi semana de ánimo» y que no hay frase de bienvenida (R2).
3. **Ánimo:** el texto «Todas las emociones dan el mismo XP: no se premia estar siempre bien.» se dejó, pero choca con la regla de que el XP solo aparece en el nivel, las misiones y la celebración (R3). Y la cara elegida va sobre un fondo suave de «emoción» y no sobre el color pleno.
4. **Colores y caras:** «Listo» se recuerda (la tarjeta no vuelve); no hay opción «solo la palabra» para las caras; la tarjeta elegida toma el color de marca de la paleta (en Carnaval, verde lima) (R4).
5. **Registrar:** «por 100 g» en las calorías; sin calorías ni sellos mientras «IA duda»; `MOSTRAR_CALORIAS` arriba de `lumea-camara.js` si hay que apagarlas (R5).
6. **Progreso:** se quitó «Ver mi avatar»; la insignia «Es tuyo y no se compara con nadie» quedó dentro de la nota (R6).
7. **Movimiento:** se quitaron el destello del esqueleto de carga y el rebote de la barra de nivel; volverlos sería una segunda animación por pantalla (R8).
8. **Nombres** de las cinco paletas y de los dos sets de caras: siguen pendientes de votar (ver «Textos nuevos»).

**Para el viernes: unir y entregar** (lo hace Isabella; no se hizo push ni merge a `main`)
1. En `.claude/worktrees/rediseno`: `git merge gamificacion-100` (sus textos). Hay **conflictos probables** en `docs/bitacora-ia.md` (las dos ramas agregan filas: conservar las dos), en `docs/tickets/ESTADO-*.md` y en sus páginas públicas y de Inicio si las tocó; en un conflicto de `<body>` gana su texto y se conservan las líneas de `.logo-brand` (la imagen `img/logo.svg`).
2. Correr `.venv/bin/pytest pruebas` y mirar lo que falle: lo más probable son textos que ella cambió y que una prueba espera tal cual.
3. **Su logo:** copiarlo a `img/`, cambiar la constante `LOGO` de `herramientas/menu_privado.py`, correr la herramienta y reemplazar la misma ruta en el pie de `mis-registros.html` y en las líneas `.logo-brand` de las seis páginas públicas (`img/logo.svg` es un marcador que dice «Lumea» en texto).
4. Mirar la sección «Para después de unir» (cinco cosas del `<body>` de sus páginas públicas que no se tocaron).
5. Con las pruebas en verde, pasar `rediseno` a `main`.

## Camino del cuidado

Misión: `docs/tickets/MISION-camino.md` (rama `rediseno`). Isabella aprobó el plan K0 el 8 de oct de 2026. Fases, en orden: K0.5, K1, K2, K3, K4 y K5. Se actualiza al cerrar cada fase.

### K0.5 · Consejos en el resultado y páginas públicas: LISTA (8 oct 2026)

**Qué quedó listo** (cuatro commits, uno por idea, más el de la misión: `73415a1`, `76cfa9d`, `3073be0`, `ee52cbd`, `d5c2710`)

1. **Consejos en el resultado de Registrar** (`lumea-camara.js`, `alimentos.html`, `estilos/app.css`). Con `consejo` en la respuesta de `/predecir` o `/confirmar-alimento`, debajo del nombre, la certeza, las calorías y los sellos salen como máximo cuatro bloques cortos, en este orden: «Lo que aporta» (`aporta`); «Para completar tu plato» (`para_completar`) o, si no hay, «Una idea» (la `idea` del primer sello); «A tener en cuenta» (`a_tener_en_cuenta`) o, si no hay, el `dato` del primer sello; y «¿Sabías que…?» (el dato curioso de siempre). Los bloques vacíos no se dibujan; sin `consejo` (backend viejo) la pantalla queda como antes y el dato curioso no lleva título. Todo entra con `textContent`; sin color de alerta ni íconos. **Mientras «IA duda» no se aconseja** (igual que con las calorías y los sellos: es una suposición todavía sin confirmar); al confirmar el plato sí salen. Respuestas simuladas con consejo para banano (completo, sin «a tener en cuenta»), gaseosa (con sello de azúcares y los dos respaldos «Una idea» y «A tener en cuenta») y bandeja paisa (completo, dos sellos y un dato de 641 caracteres): `pruebas/respuestas/predecir_banano.json`, `predecir_gaseosa.json` y `predecir_bandeja_paisa.json`. **Los textos de esas tres respuestas son de ejemplo, escritos por la IA solo para las pruebas**; los reales son del backend.
2. **Registrar sigue a `ejemplo-camara.html`.** Qué se adoptó y qué no (donde choca, gana R5):

   | Pieza | `ejemplo-camara.html` | `alimentos.html` ahora | Decisión |
   |---|---|---|---|
   | Subtítulo bajo el `h1` | «Toma una foto de lo que vas a comer. Lumea te dice qué es y algo que vale la pena saber.» | Igual | **Adoptado** |
   | Visor vacío | «La cámara está apagada» + «Encender cámara» dentro del visor | Igual; el visor vacío se esconde con la cámara encendida o con una foto, y vuelve con «Otra foto» o «Apagar» | **Adoptado** (decisión de Isabella) |
   | Botón «Encender cámara» | Relleno | **Secundario** (y ya no está en el grupo de controles) | **R5:** «Tomar foto» es la única acción principal |
   | «Lumea cree que es» | Sobre el nombre | Sobre el nombre, con «…» al final, solo con la IA segura | **Adoptado** (decisión de Isabella). Con «IA duda» no sale: el nombre ya es la pregunta («¿Cuál de estos es?») |
   | Certeza | «Segura al 94 %» + medidor | «La IA está segura: 94 %» + el medidor al lado | **R5:** palabras y número; el medidor acompaña, no reemplaza (queda con `aria-hidden`) |
   | Calorías | «42 kcal por cada 100 ml», grande | Una línea secundaria: «Calorías aproximadas: N kcal por 100 g» | **R5** (decisión de Isabella del 7 de oct) |
   | «Sí, es esto +10 XP» / «No, es otra cosa» | Dos botones | Las opciones para confirmar de siempre; **ningún botón dice «XP»** | **R5:** nada de «+10 XP» en el botón de confirmar (una prueba lo vigila) |
   | «Tomar foto» y «Subir una foto» | Botones grandes | «Tomar foto» (relleno) y «Subir foto» de texto | **R5:** una sola acción principal |
   | Título de la tarjeta | No tiene | «Lo que reconoció Lumea» se queda; con respuesta pasa a ser solo para el lector de pantalla | R5 (estructura de encabezados) |
   | Íconos | Lucide con `<use>` | Bootstrap Icons | **R5** |

3. **El dato curioso largo** (500 a 860 caracteres): líneas de 65 caracteres como máximo y el interlineado del token (`--t-interlineado`, 1,5). Si pasa de cuatro líneas se corta y sale el botón de texto «Leer más» (`aria-expanded`, `aria-controls`; pasa a «Leer menos»), sin animación. Se vuelve a medir si cambia el ancho (solo se mira el ancho, para que cortar el texto no dispare otra medida) y con cada respuesta nueva.
4. **Páginas públicas: R7 + paleta, respetando el blanco** (solo `estilos/publico.css`; ningún HTML ni texto cambió: `git diff 6561468 -- conocenos.html index.html crear-cuenta.html` sale vacío).
   - **Blanco en modo claro:** el fondo de la página y el de las tarjetas, el menú y el pie son `#FFFFFF` en las 5 paletas y en el estado neutro. Vale con «Claro» guardado y con «Como mi dispositivo» cuando el sistema está en claro (`prefers-color-scheme`). Con «Oscuro», o con el sistema en oscuro y «Como mi dispositivo», siguen las superficies oscuras de la paleta. La paleta solo pone color en los acentos (botón principal, enlaces, íconos y chips).
   - **Las hojas, formas y destellos de Sara vuelven** al inicio (`.hero-section`) y a la tarjeta del inicio de sesión (y de Crear cuenta, que usa el mismo `.auth-container`), con su composición. `puente-sara.css` los había aplanado. `Lumen.png` trae un fondo crema y por eso no se puede teñir tal cual sin dejar de ser blanco: **`herramientas/hojas_mascara.py`** saca de ella una máscara (`img/hojas-mascara.png`, 137 KB: el alpha es lo que se aparta del crema) y el CSS la pinta de **un color plano** de la paleta, `--c-marca-tinta`, a baja opacidad (**0,22 en claro y 0,16 en oscuro**, variable `--publico-adorno`). No se mezclan colores: si en alguna paleta queda turbio, se baja esa opacidad. Se eligió `--c-marca-tinta` y no `--c-marca` porque en Carnaval `--c-marca` es casi negro y las hojas salían grises.
   - La piel de comparación de Sara (`?piel=sara`) no cambia. La tarjeta `.auth-card` conserva su composición, sin sombra (R7: borde, no sombra).

**Pruebas:** `.venv/bin/pytest pruebas` → **742 pasan, 1 `xfail`** (antes 636 + 1). `.venv/bin/pytest pruebas -m capturas` → **282 casos pasan** (258 de R9 + 24 del resultado con consejos), con **0 errores de contraste** en las pantallas privadas y, ahora, también en las seis públicas. **Contraste: 0 errores** en las seis públicas (ahora estrictas en `test_capturas.py`: 5 paletas + neutro × claro/oscuro), y en Registrar con consejos (dato largo cerrado y abierto) en las 12 combinaciones.
- **Nuevas:** `test_camara.py` +27 casos (consejos: orden y máximo cuatro, respaldos, vacíos, sin consejo, duda, HTML, sin alerta, 375 y 1280 px; el visor vacío con la cámara apagada, con foto y encendida; «Lumea cree que es…»; la certeza con el medidor; ningún botón con «XP»; el dato largo: corta, abre y cierra, 65 caracteres, interlineado, teclado y foco, 44 px, sin animación, reinicio, cambio de ancho). `test_publico.py` +79 (blanco en las 6 páginas × 6 paletas, «Como mi dispositivo» en claro y en oscuro, «Oscuro» con el sistema en claro, los acentos, los adornos y su opacidad, que no tapan nada, la máscara). Se comprobó que detectan: se rompió a propósito el CSS del blanco, la opacidad y el JS de los consejos, y fallaron; después se deshizo.
- **Cambiaron, y por qué** (ninguna se borró; ninguna de accesibilidad se debilitó):
  - `test_camara.py::test_los_iconos_son_de_bootstrap_icons_y_no_hay_svg_a_mano`: los cinco botones siguen con su ícono, pero «Encender cámara» pasó al visor vacío (ya no está en `.controles`) y el visor trae un sexto ícono: ahora cuenta `main .controles .bi, main .visor__vacio button .bi` (5) y los 6 de `aria-hidden`.
  - `test_paletas.py::test_sin_paleta_guardada_se_ve_el_estado_neutro_y_no_laguna[index.html, claro]` y `test_una_paleta_guardada_se_aplica_tambien_en_las_paginas_publicas` (5 casos): comprobaban que la página pública tiene el `--c-fondo` de la paleta; ahora ese fondo es `#FFFFFF` en claro (decisión de Isabella). Se conserva la intención: fondo y superficie deben ser `#FFFFFF`, y la paleta se comprueba por `--c-marca`, `--c-marca-suave`, `--c-marca-tinta`, `--c-tinta` y `--c-borde`.
  - `test_capturas.py`: las seis públicas pasan a `ESTRICTAS` (refuerzo) y `test_resultado_de_la_camara_sin_errores_de_contraste` suma los estados «consejos» y «consejos-abierto».

**Capturas** de lo que cambió (56, en `pruebas/capturas/despues-K0.5/`, carpeta que git ignora: **Isabella elige cuáles guarda**): Registrar (vacío, banano, gaseosa, bandeja paisa cerrada y con «Leer más» abierto, y con la IA en duda) a 1280 y 390 px, en claro y oscuro; las seis públicas en el estado neutro a 1280 y 390 px, claro y oscuro; e Inicio e Iniciar sesión con Carnaval y con Colibrí (claro y oscuro) a 1280 px.

**Para decidir**
1. **«Lumea cree que es…»** lleva «…» (la referencia no); y con «IA duda» no se muestra. Si prefieres otra frase para la duda, es un texto más.
2. **El subtítulo de Registrar** se adoptó de la referencia (no lo pedías de forma explícita): si no lo quieres, es borrar el `<p class="contenido__subtitulo">` de `alimentos.html`.
3. **La opacidad de los adornos** (0,22 y 0,16): es una variable (`--publico-adorno`) al final de `estilos/publico.css`.
4. **«Guardado en tu historial.»** (el mensaje) queda arriba de los consejos, no abajo. Si lo quieres después, se mueve en `alimentos.html`.
5. **En el computador, la tarjeta del resultado mide unos 310 px**, así que las líneas del dato curioso salen de unos 40 caracteres; el tope de 65 solo se nota en una columna (< 960 px). Para ver 65 a 1280 px habría que ensanchar la columna del resultado.
6. **«Leer más» pasa a «Leer menos»** (la misión pide solo «Leer más»): ambos son textos nuevos.
7. `herramientas/hojas_mascara.py` necesita Pillow y numpy, que no están en `pruebas/requirements.txt` (las pruebas no los usan: solo comprueban que el PNG existe, tiene alpha y es liviano).
8. **El backend todavía no manda `consejo`** (`MISION_CAMINO_BACKEND.md`, fase C0.5): por ahora solo se ve con respuestas simuladas. *(Actualizado en K3: la rama `gamificacion-100` ya lo manda; se vio con un banano real, ver K3.)*

### K1 · Semillas y etapas: LISTA (8 oct 2026)

**Qué quedó listo** (dos commits: `9f41f66` el vocabulario y `fa6a4f0` las respuestas simuladas y sus pruebas)

- **Lo que se lee dice «semillas» donde el contrato dice XP y «etapa» donde dice nivel**, en Inicio, Progreso, Avatar, Ánimo, Registrar (resultado y celebración), la barra de navegación y todos los `aria-label`. Las claves del contrato (`xp_total`, `nivel`, `xp_siguiente_nivel`, `nivel_requerido`…) y las variables **no cambian**. `formato.js` sigue siendo el único lugar de los textos compartidos y gana `semillas(n)` («1 semilla», «5 semillas»).
- **Respuestas simuladas al contrato real** de `gamificacion-100` (`Backend/docs/CONTRATO_GAMIFICACION.md`): `/progreso`, `/avatar` y `/avatares` traen `forma`, `color` y los compañeros de gaze 10.x con su URL quieta; `/predecir` trae `consejo` con sellos. `conftest.py` gana `url_companero()`, `companero()`, `companero_basico()` y `avatares_estado()`; `avatares.json` y `avatar_elegir.json` son nuevos, y las rutas `GET /avatares` y `POST /avatar` están simuladas. Los textos de misiones y calcomanías se copiaron **tal cual** de `gamificacion_config.py`, sin tocarlo.
- **`test_vocabulario.py`** (nuevo, 20 casos): ninguna pantalla privada dice «XP» ni «nivel» (texto visible y `aria-label`), los plurales, y los textos de etapa y de meta.

**Extras que no estaban en el plan** (anotados para que Isabella decida):
- «Llegaste a la etapa máxima» (el plan solo decía «Etapa máxima» para el `aria-label`; el texto del progreso antes decía «Llegaste al nivel máximo»).
- Singular correcto: «Te falta 1 semilla para la etapa 3» (con 1, «Te falta», no «Te faltan»).
- «Compañero nuevo:» en la celebración de la etapa (antes «Avatar nuevo:»): sale del vocabulario de los compañeros.
- `alimentos.html` ahora carga `formato.js` (lo usa `lumea-camara.js` para «+10 semillas»).
- Los textos con errores que siguen en el backend (`gamificacion_config.py`: «El camino continua», «Etapa: El Jardín»…) **no se corrigieron aquí**: los corrige la sesión del backend. Están copiados tal cual en `calcomanias.json`.
- `sistema-diseno.html` («Nivel 4», «320 de 500 XP», «el mismo XP») y `ejemplo-camara.html` («+10 XP» en el botón de la referencia) **no se tocaron**: son referencias, y cambiarlos bien es repasar el sistema de diseño entero.

### K2 · El compañero en Avatar: LISTA (8 oct 2026)

**Qué quedó listo** (un commit: `5c94710`; `avatar.html`, `avatar.js`, `estilos/avatar.css`, `companero.js` nuevo)

- **«Tu compañero»**: los seis (Sol, Luna, Río, Montaña, Orquídea, Colibrí) quietos, con su nombre y la etapa en que se abren, debajo de las pestañas. Usa la tarjeta y el foco del armario: los bloqueados llevan candado, «Etapa N», `aria-disabled="true"` y no hacen nada; se elige con `elegirAvatarDiceBear` (`POST /avatar`) y al elegir se vuelve a leer `GET /progreso` para traer las caras del compañero nuevo (el `POST` solo trae la de ojos neutros). El foco se queda en el botón. Si `/avatares` falla, la sección dice que no pudo cargar y lo demás funciona.
- **La figura grande:** con `imagen_lista` verdadero, la persona por capas y el compañero a su lado, más pequeño y **quieto**; si no, el compañero grande, con los ojos del ánimo de hoy y animado `slow`. Sin internet queda una silueta (que antes se quedaba **detrás** de la imagen y se veía por las partes transparentes de las formas de gaze).
- **`companero.js`** agrega `animationVariant` a la URL quieta del backend solo donde algo se anima, y **no lo pide si la persona tiene el movimiento reducido** (además de que el SVG de gaze ya respeta `prefers-reduced-motion` por dentro: se comprobó leyendo el SVG, con `animationVariant=medium` los fotogramas están dentro de `@media (prefers-reduced-motion: no-preference)`). Solo acepta direcciones http(s).
- **La acción principal de Avatar** sigue siendo ponerte algo del armario: los botones de los compañeros son secundarios.
- **Pruebas:** `test_avatar.py` +16 (seis compañeros, bloqueados, quietos y sin datos de la persona, elegir con ratón y teclado, 403 y 500, desbloqueo por etapa, el grande en `slow` y único que se mueve, movimiento reducido, persona + compañero, sin internet, sin `/avatares`, HTML en el nombre, 375 y 1280 px, la acción principal).

### K3 · El check-in con el compañero: LISTA (8 oct 2026)

**Qué quedó listo** (un commit: `4ee7d8e`)

- Los cinco botones del check-in (**Inicio y Ánimo**) muestran las caras de tu compañero (`avatar.urls_por_estado`), quietas; la del botón elegido (`aria-pressed`) se anima con `medium`, una a la vez, y una cara ya dibujada no se vuelve a cargar al elegir otra. Sin internet o sin compañero queda la palabra (el hueco no ocupa lugar). El nombre accesible es la palabra y la imagen lleva `alt=""`. Ya no se recortan en círculo (la forma del compañero es su silueta) y miden 56 px.
- **`caras-checkin.js` se eliminó.** Su trabajo era dibujar los sets «gaze» y «moods» con una semilla fija y el color de emoción de la paleta, y guardar la elección en `localStorage` (`lumea-caras`). Eso ya no existe: el compañero trae su forma y su color. Lo que sigue vivo (poner la imagen, quitarla si no carga, animar la elegida) pasó a `companero.js`, que además borra la clave `lumea-caras` que hubiera quedado.
- **`selector-colores.js` pierde el grupo «Caras»** y sus cinco caras de muestra. La tarjeta de Inicio pasa a **«Elige tus colores»** y se abre mientras falte la paleta (ya no el set de caras); la sección de Avatar, a **«Mis colores»**.
- **Probado una vez contra el backend real** (puerto 5002, rama `gamificacion-100`, con una cuenta de prueba): las cinco caras salen con los ojos `bars`, `small`, `dots`, `happy` y `grin`; la elegida lleva `animationVariant=medium`; guardar el ánimo celebra; `/avatares` trae los seis con sus etapas; elegir a Luna con `POST /avatar` funciona y la figura grande pasa a Luna (`animationVariant=slow`); y Registrar con un banano real muestra «Lo que aporta» y «A tener en cuenta» (el backend no mandó «Para completar tu plato») y la certeza «94 %». **Sin errores de consola ni peticiones fallidas**, en 1280 y 390 px. **La cuenta de prueba quedó en la base local:** correo `camino-k3@lumea.test` (créala de nuevo o bórrala con SQL cuando quieras; el backend no tiene ruta para borrar cuentas). Capturas en `pruebas/capturas/despues-K3-backend-real/`.

### K4 · La semana de ánimo y Progreso: LISTA (8 oct 2026)

**Qué quedó listo** (un commit, solo pruebas: `8117f61`)

`[data-cara]` y `dibujarSemanaAnimo` (`lumea-ui.js`) ya usaban `urls_por_estado`, así que Progreso y Ánimo muestran al compañero sin tocar código. Se revisó en pantalla con los seis compañeros (el triángulo de Montaña, el rombo de Orquídea, el huevo de Colibrí, la píldora de Río y el arco de Luna caben en el círculo de 40 px sin cortarse), quietos y sin errores de contraste. Dos pruebas lo cuidan: la semana lleva la cara de cada estado del compañero y ninguna pide animación; y en Ánimo, lo único que se mueve en toda la pantalla es la cara elegida.

### K5 · Pruebas, capturas y cierre: LISTA (8 oct 2026)

**Pruebas:** `.venv/bin/pytest pruebas` → **769 pasan, 1 `xfail`** (al cerrar K0.5 eran 742 + 1). `.venv/bin/pytest pruebas -m capturas` → **282 casos pasan, 0 errores de contraste**: las seis públicas y las pantallas privadas (Inicio, Ánimo, Progreso, Avatar con «Tu compañero», Registrar) en las 5 paletas + el neutro × claro/oscuro. Las imágenes de los compañeros no entran en el contraste (axe mira texto), pero el texto de sus tarjetas, de los botones del check-in y de la semana sí.
- **Nuevas:** `test_vocabulario.py` (20), `test_avatar.py` +16, `test_caras_checkin.py` y `test_selector_colores.py` reescritas, y +2 de K4 (la semana quieta en Progreso y en Ánimo).

**Pruebas que cambiaron, y por qué** (ninguna se borró para que pasara; ninguna de accesibilidad se debilitó):
- **K1** (`test_avatar.py`, `test_camara.py`, `test_celebracion.py`, `test_emociones.py`, `test_index_ingresado.py`, `test_progreso.py`, `test_rediseno.py`): esperaban «XP», «nivel», «Subiste al nivel», «Avatar nuevo» y las caras de DiceBear 9.x (`moods`, `twinkle`, `mouth=concerned`); ahora esperan el vocabulario nuevo y las URL de gaze 10.x (`grin`, `small`). `test_el_xp_aparece_tres_veces_como_maximo` pasó a llamarse `test_las_semillas_aparecen_tres_veces_como_maximo`.
- **K2** (`test_avatar.py`): las pruebas del armario contaban todas las `.prenda`; ahora miran solo `#armario-grupos` (la sección de compañeros usa la misma tarjeta). El `aria-label` de la figura pasó de «Tu avatar, tu ánimo de hoy: Bien» a «Tu compañero Sol, tu ánimo de hoy: Bien».
- **K3, `test_caras_checkin.py` y `test_selector_colores.py`**: pasan a probar el comportamiento nuevo (lo pedía la misión). **Se quitaron las pruebas de lo que dejó de existir:** `test_poner_guarda_la_eleccion_y_redibuja_con_lumea_caras`, `test_poner_ignora_un_set_que_no_existe`, `test_la_eleccion_dura_entre_paginas_porque_vive_en_el_navegador`, las de los sets «gaze» y «moods» y su color por paleta (`test_el_color_del_cuerpo_es_el_de_emocion_de_la_paleta_activa`, `test_al_cambiar_de_paleta_las_caras_se_dibujan_de_nuevo`, `test_al_cambiar_a_modo_oscuro_el_color_sigue_a_la_paleta`), y en el selector `test_elegir_el_set_de_caras_…`, `test_al_elegir_paleta_las_caras_toman_su_color_de_emocion`, `test_las_caras_de_muestra_son_cinco_por_set_y_van_quietas` y `test_sin_internet_en_el_selector_quedan_los_nombres`. Se **conservaron, adaptadas,** las que cuidaban una garantía que sigue valiendo: sin datos de la persona en la URL, alt vacío, `aria-pressed`, solo una cara animada, sin internet queda la palabra, `localStorage` bloqueado, ningún botón dice «XP» ni cambia de color por ánimo. `test_hay_tres_radiogroup…` pasó a dos grupos; `test_con_la_paleta_y_las_caras_ya_elegidas_no_aparece` pasó a solo la paleta.
- **K3, `test_emociones.py` y `test_index_ingresado.py`:** esperaban cero imágenes en los botones del check-in (sin set elegido) y ahora esperan cinco (las del compañero). `test_publico.py::test_crear_cuenta_no_tiene_ningun_paso_nuevo` busca `companero` en lugar de `caras-checkin`.

**Capturas** (carpetas que git ignora: **Isabella elige cuáles guarda**; las imágenes de los compañeros son las reales de DiceBear): `despues-K1` (Progreso, Inicio y la celebración de la etapa), `despues-K2` (Avatar con el compañero grande, con la persona y el compañero, en nivel alto y en el armario), `despues-K3` (Inicio y Ánimo con distintos compañeros y la cara elegida), `despues-K4` (la semana de ánimo en Progreso y en Ánimo) y `despues-K3-backend-real` (el recorrido contra el backend real). En 1280 y 390 px, claro y oscuro, el estado neutro y una paleta.

**Documentación:** una fila por fase en `docs/bitacora-ia.md`; dos preguntas nuevas, sin respuesta, en `docs/defensa/preguntas-camino.md`; y `docs/defensa/privacidad-y-limites-rediseno.md` y `preguntas-rediseno.md` al día (ya no hay set de caras ni `lumea-caras`).

**Para decidir**
1. **Privacidad: DiceBear puede ver el ánimo del momento.** Antes se decía que no sabía qué ánimo se elegía porque las cinco caras se piden siempre. Ahora la cara elegida se vuelve a pedir con `animationVariant=medium` y Avatar pide al compañero con los ojos del ánimo de hoy: DiceBear ve la IP, cuál de los seis compañeros (`seed=lumea-<id>`) y los ojos de esa petición, **sin nombre ni correo**. Está dicho con esas palabras en `privacidad-y-limites-rediseno.md`. Si quieres cerrarlo, el contrato ya sugiere descargar los SVG y servirlos desde Lumea (haría falta que `animationVariant` no dependiera de DiceBear).
2. **Ánimo repite al compañero:** la cara grande y el botón elegido son el mismo compañero. La misión no pide quitar la grande, así que se dejó; si sobra, es borrar `#cara-en-vivo-contenedor`.
3. **El compañero pequeño junto a la persona va quieto** (la misión solo dice `slow` para el grande). Es un cambio de una palabra en `avatar.js` si lo quieres animado.
4. **Los compañeros bloqueados se ven** (a 45 % de opacidad, con candado), no escondidos: la misión dice «los seis compañeros quietos». Si prefieres que sean una sorpresa, se cambia la imagen por el candado como en el armario.
5. **El compañero elegido** tiene el botón «Elegido» con `aria-disabled="true"` (se puede enfocar, no hace nada), no `aria-pressed`.
6. **`api.js` tiene un cambio sin commit que no es mío:** `API_BASE_URL` pasó de `"http://127.0.0.1:5002"` a `` `http://${location.hostname}:5002` `` (estaba entre comillas dobles, así que no interpolaba y rompía todas las llamadas; tú me pediste corregirlo con comillas invertidas). Queda **sin commit** para que lo revises; sirve para abrir el frontend desde otro dispositivo, y las pruebas siguen pasando porque sirven desde `127.0.0.1`.
7. Los textos nuevos de esta misión están abajo, en «Textos nuevos para que Isabella revise».

## Textos nuevos para que Isabella revise

**Inicio (R2)**
- «Tu día» · «comidas» (en «1 de 3 comidas») · «Registrar comida»
- «Elige la cara que más se parece a tu día» (viene del esquema del documento) · «Guardar mi ánimo» · «Ver mi semana de ánimo»
- «Misión de hoy»
- Títulos que solo oye el lector de pantalla: «Etapa y racha» (K1; antes «Nivel y racha») y «. Ver mi progreso» (al final de la franja de la etapa)
- Racha dentro de la franja de la etapa: «Te faltan 35 semillas para la etapa 3. Racha: 3 días» (K1; antes «…XP para el nivel 3»)
- Aviso si falla la foto directa: «No se pudo abrir la foto. Prueba con «Registrar comida».» (antes decía «Cámara en vivo»)

**Selector de colores (R4; sin caras desde K3)**
- Tarjeta de Inicio: **«Elige tus colores»** (K3; antes «…y tus caras») · botones «Listo» y «Ahora no»
- Sección de Avatar: **«Mis colores»** (K3; antes «Mis colores y caras»)
- Títulos de los grupos: «Colores», «Modo» (se quitó «Caras»)
- Nombres de las paletas: Laguna, Neblina, Carnaval, Colibrí, Cosecha (los de `MARCA.md`; **siguen pendientes de votar** con estudiantes y familias)
- Modos: «Claro», «Oscuro», «Como mi dispositivo»
- *(Los sets «Miradas» y «Gestos» ya no existen: el check-in usa las caras del compañero.)*

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

**Registrar · Camino del cuidado, K0.5**
- Títulos de los bloques de consejo: «Lo que aporta» · «Para completar tu plato» · «Una idea» · «A tener en cuenta» · «¿Sabías que…?»
- Botón del dato largo: «Leer más» · «Leer menos»
- Subtítulo (de `ejemplo-camara.html`): «Toma una foto de lo que vas a comer. Lumea te dice qué es y algo que vale la pena saber.»
- Sobre el nombre: «Lumea cree que es…»
- Visor vacío: «La cámara está apagada»
- Los textos de las tres respuestas simuladas (banano, gaseosa y bandeja paisa) son de ejemplo para las pruebas: no son textos de la app.

**Camino del cuidado, K1 · Semillas y etapas**
- «semillas» y «etapa» en todo lo visible: «10 de 15 semillas hoy» · «Meta cumplida: 20 semillas hoy» · «Te faltan 35 semillas para la etapa 3» · «Te falta 1 semilla para la etapa 3» · «Etapa 2» · «Etapa máxima» · «Llegaste a la etapa máxima» · «+10 semillas» · «Llegaste a la etapa 4» · «Se abre en la etapa 3» · «Cargando semillas…»
- Avatar: «Todavía no se abre: te falta 1 etapa» / «…te faltan 3 etapas» · «Lo que se abre al llegar a una etapa nueva es tuyo para siempre.»
- Ánimo: «Todas las emociones dan las mismas semillas: no se premia estar siempre bien.»
- Celebración de la etapa: «Compañero nuevo:» (antes «Avatar nuevo:»)
- Los `aria-label`: «Avance hacia la etapa 3» · «Avance hacia la siguiente etapa» · «Etapa máxima»

**Camino del cuidado, K2 · Tu compañero (Avatar)**
- Título de la sección: «Tu compañero» · nota: «Te acompaña en Lumea y sus ojos muestran cómo llegas hoy. Los demás se abren al llegar a una etapa nueva.»
- Error si no cargan: «No pudimos cargar a tus compañeros. Vuelve a abrir esta pantalla en un momento.»
- En cada tarjeta: «Tu compañero» (el elegido) · «Disponible» · «Se abre en la etapa 5» · botones «Elegir», «Elegido» y «Etapa 5»
- Para el lector de pantalla: «Elegir a Luna» · «Elegido: Sol» · «Río, se abre en la etapa 3» · «Tu compañero ahora es Luna.»
- La figura grande: «Tu compañero Sol, tu ánimo de hoy: Bien» y, con la persona, «Tu avatar y tu compañero Sol, tu ánimo de hoy: Bien»

**Camino del cuidado, K3 · Check-in con el compañero**
- «Elige tus colores» y «Mis colores» (arriba, en el selector).
- Sin textos nuevos en los botones del check-in: la palabra de cada estado se queda.

## Pulido final

Misión: `docs/tickets/MISION-pulido.md` (rama `rediseno`, 9 de oct de 2026). Plan P0 aprobado por Isabella; congelamiento a las 12:00 m. Se actualiza al cerrar cada fase.

### P1 · Arreglos que no pueden faltar: LISTA (9 oct 2026)

- **Enchufes de tipografía** (`estilos/componentes.css`, `estilos/inicio.css`): los títulos (`h1`–`h3` y las clases de título) usan `var(--f-titulos, var(--f-familia))` y la clase `.cifra` (`var(--f-cifras, var(--f-familia))` con `tabular-nums lining-nums`) va en la etapa, la racha, las comidas de hoy, las calorías de Registrar, la cifra de la celebración y las semillas de las misiones. No se definieron `--f-titulos` ni `--f-cifras`: son de Isabella (`tokens.css`).
- **Registrar, botón de play de Safari:** `#webcam` lleva `hidden` hasta el evento `playing`; al apagar se detienen las pistas, `srcObject = null` y vuelve a `hidden`. Respaldo en CSS con `::-webkit-media-controls-start-playback-button`. Prueba nueva en `test_camara.py`. **Isabella: comprobar en Safari** (en Chromium no sale el botón, así que la prueba solo asegura que el video está oculto sin cámara).
- **Crear cuenta:** sin peso ni altura (campos, ayuda, validación y payload); `min="11"` con «Lumea es para personas de 11 años en adelante.»; casilla «Mi madre, padre o acudiente sabe que uso Lumea» solo con edad de 11 a 17 (obligatoria solo cuando se ve, error con `aria-describedby`) que envía `acudiente_sabe: true`. Pruebas en `test_crear_cuenta.py` (6) y dos existentes ajustadas.
- **Textos de peso, altura, 14 años e IMC en el frontend** (no se cambiaron): solo `guialumea.html` línea 201, «sin presiones de peso ni comparaciones con otros» (habla de presión, no de pedir el peso). No hay «14 años» ni «IMC».
- **Avatar: la vitrina que tapa la lista de compañeros** se resuelve con el layout nuevo de P2.

### P2 · La persona (DiceBear voxel-art) y el armario por etapas: LISTA (9 oct 2026)

- **Todo DiceBear se dibuja en el navegador** (`vendor/dicebear/`, commit aparte): `persona.js` (módulo ES, `dibujarPersona`, semilla fija `lumea`, fondo transparente, probabilidades en 100 o 0) y `companero.js` (gaze, a partir de los parámetros de la URL que manda el backend). Cada `<img>` lleva su dirección en `data-fuente` y el dibujo en `src` (dirección `data:`). `test_sin_dicebear.py`: ninguna página privada pide nada fuera de la máquina. Un servidor sencillo puede cortar alguna de las ~40 peticiones de módulos que llegan juntas (pasó en las pruebas): por eso hay un reintento al cargar el núcleo; **si en la demo la persona no sale a la primera, recargar**.
- **Avatar** (`avatar.html`, `avatar.js`, `estilos/avatar.css`): la vitrina sticky lleva la persona grande y animada (`slow`) con el compañero pequeño y quieto, la etapa y «Te faltan 35 semillas para la etapa 5: Camisa de cuadros». **Todo lo demás va en cinco pestañas en la columna derecha** (Mi armario, Cómo me veo, Misiones, Calcomanías, Tu compañero; anclas `#armario`, `#como-me-veo`, `#misiones`, `#calcomanias`, `#companero`), así que nada queda debajo del `sticky`. Abre en «Mi armario».
- **Mi armario:** mosaicos con la persona (con sus rasgos) puesta cada prenda; bloqueados atenuados, con candado, «Etapa N» y `aria-disabled`; tocar uno abierto lo pone, tocar el puesto lo quita; la vitrina cambia al instante.
- **Cómo me veo:** radios con `<label>` por rasgo (muestras redondas para los colores, mosaicos dibujados para peinado, ojos y boca, chips para mejillas y barba con «Ninguno»/«Ninguna» → `null`). «Guardar cómo me veo» → `POST /avatar/rasgos` solo con las 8 claves permitidas.
- **Celebración:** «Prenda nueva: Overol de jardín» con la persona puesta esa prenda (pide `GET /avatar` para los rasgos).
- **Respuestas simuladas:** `objetos_avatar.json` y `rasgos_disponibles.json` salen de la configuración REAL del backend (`gamificacion_config` y `gamificacion.rasgos_disponibles()`, importadas en solo lectura); `avatar_estado()` en `conftest.py` arma el cuerpo del contrato. **El proceso que corre en el 5002 (arrancó a las 8:33) es el backend viejo**: sin `persona` ni `/dato-del-dia`. Hay que reiniciarlo para ver P2 con datos reales.
- **Cambiaron, y por qué:** `test_avatar.py` (el armario, la vitrina y las pestañas se reescribieron: ya no hay imágenes por capas ni listas de ropa/accesorios; los de compañeros abren `#companero`); los tests de caras (`test_emociones`, `test_caras_checkin`, `test_progreso`, `test_selector_colores`) leen `data-fuente` en vez de `src`; `test_vocabulario` abre `#misiones`.

### P3 · El Inicio nuevo: LISTA (9 oct 2026)

- **El compañero que saluda** (`index-ingresado.html`, `indexx.js`): junto al «Hola, Ana», grande (140 px en computador, 96 en celular), animado `slow`, con la cara del ánimo de hoy (`neutral` si todavía no hay check-in); al guardar el ánimo cambia a esa cara. Decorativo (`alt=""`, `aria-hidden`). **Es lo único que se mueve en Inicio:** las cinco caras del check-in quedan quietas (`data-caras-quietas`; `companero.js` ya no anima la elegida allí; en Ánimo sigue igual). Ver «Cambiaron» abajo.
- **«¿Sabías que…?» del día:** `obtenerDatoDelDia()` en `api.js`, sin correo ni parámetros; subtítulo con el nombre del alimento; reutiliza «Leer más» (ahora en `leer-mas.js`, compartido con Registrar, que se refactorizó); decorada con emoción y estrella. Si la petición falla o no hay dato, la tarjeta no se dibuja.
- **«Tu semana», en una franja:** los últimos 7 días con hoy a la derecha (`F.ultimosDias`, `lumea-state.js` → `ultimos_dias`), cada uno con su inicial, cuántas comidas y la cara quieta del último ánimo (un círculo vacío si no hubo check-in). Una lista para el lector de pantalla («martes 29: 0 comidas, sin check-in»); la franja entera lleva a `progreso.html` («Ver mi progreso»). Ningún día va en rojo ni se marca como malo.
- **Respuesta simulada** `dato_del_dia.json`: el dato REAL del banano de `Backend/datos/datos_curiosos.csv`.

### P4 · La forma decorativa y Mis registros: LISTA (9 oct 2026)

- **`estilos/formas.css`** (`.con-forma`, roles `comida`, `marca`, `logro`, `emocion`, `mision`; formas `sol`, `luna`, `estrella`, `gota`, `hoja`, `flor` en `img/formas/*.svg`, originales y de un solo trazado; sin dibujo con `forced-colors: active`). La de `marca` no tiene `--c-marca-contenedor` en `paletas.css`: usa un `color-mix` (9 %) de `--c-marca` con `--c-marca-suave`, el máximo que cumple 4,5:1 en las 5 paletas y los dos modos (`test_formas.py`) (si Isabella define ese token, se usa solo).
- **Dónde va:** los bloques de consejo de Registrar («Lo que aporta» comida y hoja; «Para completar tu plato» y «Una idea» marca y flor; «A tener en cuenta» logro y gota, nunca color de alerta), los «¿Sabías que…?» de Registrar (emoción y estrella) y de Inicio, y la tarjeta «Hoy» de Mis registros (comida y sol).
- **Mis registros:** una tarjeta por día («Hoy», «Ayer», «martes 6 de octubre»), del más reciente al más viejo; resumen «3 comidas» con seis marcas de los grupos del plato del ICBF (llenas las que aparecieron; es información, nunca «te faltan»), y una fila por registro con el nombre, el chip de su grupo, los sellos y las calorías en segundo plano (`.cifra`). **Sin hora:** `/historial` manda solo la fecha, así que las filas no llevan hora. **Cambió lo que se ve:** ya no sale la fecha en cada fila (es el título del día) ni «Certeza IA». Estado vacío: «Registrar comida». Sin `grupo` en el backend no se dibujan ni el chip ni las marcas. Las respuestas simuladas de `historial.json` llevan `grupo` y `sellos` (el texto de los sellos es de ejemplo).

### P5 · El computador: LISTA con el recorte (3 problemas) (9 oct 2026)

1. **Inicio:** el dato del día y, a su lado, la misión y la etapa apiladas (antes eran dos franjas de una sola línea a todo el ancho).
2. **Progreso:** la racha y las comidas de la semana, lado a lado (antes cada una ocupaba todo el ancho con casi nada adentro).
3. **Párrafos de unos 70 caracteres** (`max-width: 70ch` en subtítulos y notas).
- Ya estaban: el contenido a unos 1120 px y centrado a la derecha del menú, Mis registros en dos columnas y Avatar con su vitrina. **No se revisaron a 1728×1117 todas las pantallas ni se tocó Registrar**: queda para después.

### P6 · Movimiento con propósito: LISTA con el recorte (9 oct 2026)

- **Entre pantallas:** `@view-transition { navigation: auto; }` dentro de `prefers-reduced-motion: no-preference`, un fundido de `--m-base`; el menú (`menu`) y el logo (`logo`) llevan `view-transition-name`. **Isabella: comprobar en Safari** (el fundido entre páginas lo admite Safari 18.2 o más nuevo; en uno anterior solo no hay fundido).
- **Al tocar:** `:active` sin transición (respuesta inmediata, < 0,1 s) en botones, pestañas, caras, opciones, mosaicos y menú, con el «hundirse» a 0,97. El cursor sigue con `--m-rapido` (120 ms; el token es de Isabella).
- **Barras:** se llenan una vez al cargar (`transition: width var(--m-lento)`); con movimiento reducido, de golpe. **Con movimiento reducido nada se mueve:** ni la persona ni el compañero (pruebas).
- **Cambiaron, y por qué:** `test_movimiento.py` (el R8 prohibía el fundido entre páginas y la barra que se llena; la misión de pulido los pide: se reemplazaron por pruebas del fundido, de `view-transition-name`, de `:active` inmediato y de la barra); `test_index_ingresado.py` (hasta 6 superficies y 6 secciones, por el dato del día y la franja de la semana); `test_camara.py` (los bloques de consejo ahora llevan el color suave de su rol, nunca el de duda ni el de error); `test_caras_checkin.py` (en Inicio los botones van quietos y el compañero que saluda es lo único que se mueve).

### Lo que quedó pendiente / para Isabella

- **El backend que corre en el 5002 es el viejo** (arrancó a las 8:33): sin `persona`, `/dato-del-dia` ni `grupo` en `/historial`. Hay que reiniciarlo con la rama `gamificacion-100` para ver P2 a P4 con datos reales.
- **Si un menor de 18 edita su perfil, hay que volver a mandar `acudiente_sabe: true`:** hoy el frontend no tiene pantalla de editar perfil (`crearOActualizarPerfil` solo se llama desde Crear cuenta), así que no hay nada que cambiar todavía; queda anotado.
- **Safari:** (1) que no salga el botón de play sobre «La cámara está apagada» en Registrar; (2) el fundido entre páginas y que el menú no parpadee; (3) la persona y los compañeros dibujados (SVG animados dentro de `<img>`); (4) `mask` con `-webkit-mask` en las formas decorativas.
- **Servidor de la demo:** `python3 -m http.server` puede cortar alguna de las ~40 peticiones de módulos de DiceBear al abrir una pantalla por primera vez; el código reintenta una vez. Si la persona no sale, recargar.
- **Sin hacer (recorte):** revisión completa del computador a 1728×1117 (P5, solo 3 problemas), Registrar a dos columnas con lista de consejos, y las tarjetas del compañero (K2) en 2 o 3 columnas más compactas.
- **Textos de peso, altura, 14 años e IMC** (P1): solo `guialumea.html` línea 201 («sin presiones de peso…»); no se tocó.

### Textos nuevos (P2) para que Isabella revise

- Armario: «Mi armario» · «Toca una prenda para ponértela y toca la que llevas para quitártela. Lo que se abre al llegar a una etapa nueva es tuyo para siempre.» · «Etapa N» · «Disponible» · «Puesto»
- Cómo me veo: «Cómo me veo» · «Elige cómo eres. Todo está abierto desde el primer día y lo puedes cambiar cuando quieras.» · «Guardar cómo me veo» · «Guardamos cómo te ves.» · «No se pudo guardar cómo te ves.» · los nombres de los rasgos y sus opciones son del backend
- Vitrina: «Te faltan 35 semillas para la etapa 5: Camisa de cuadros»
- Pestañas: «Mi armario» · «Cómo me veo» · «Tu compañero»
- Celebración: «Prenda nueva: Overol de jardín» (también para los accesorios)

### Textos nuevos (P3 a P6) para que Isabella revise

- Inicio: «Tu semana» · «Ver mi progreso» · «martes 29: 0 comidas, sin check-in» (para el lector de pantalla) · «¿Sabías que…?» · «Leer más» / «Leer menos»
- Mis registros: «Hoy» · «Ayer» · «martes 6 de octubre» · «3 comidas» · los nombres cortos de los seis grupos: Cereales, Frutas y verduras, Lácteos, Proteínas, Grasas, Azúcares · «Grupos del plato que aparecieron: …» (para el lector de pantalla) · el botón vacío «Registrar comida»

### Textos nuevos (P1) para que Isabella revise

- Crear cuenta: «Lumea es para personas de 11 años en adelante.» · «Mi madre, padre o acudiente sabe que uso Lumea» (literal de Isabella) · «Marca la casilla para continuar.»

## Para después de unir

(Cambios que necesitan tocar el `<body>` de una página pública o un archivo de Isabella; no se hicieron.)

1. **El pie de las seis páginas públicas** lleva `<span class="fw-bold hero-title">🌿 LUMEA</span>`: un emoji como ícono y «LUMEA» en mayúsculas, que `MARCA.md` prohíbe. Debería ser `<img class="marca" src="img/logo.svg" alt="Lumea">`, igual que el encabezado.
2. **`crear-cuenta.html`**: las cinco opciones de «Objetivo Principal» usan emojis como íconos (🥗 💧 🏃 🌙 🔍). Deberían ser Bootstrap Icons.
3. **«LUMEA» escrito en mayúsculas dentro de los textos** («Bienvenido a LUMEA», «Guía LUMEA», «¿Cómo utilizar LUMEA?»…): el menú y el logo dicen «Lumea». Decide cuál es la forma de la marca y se unifica.
4. **`style="font-size: …"` escritos en el HTML** (`terminos.html` en los `step-badge`, `conocenos.html` en dos párrafos): `publico.css` los lleva a la escala con `!important`. Cuando se unan los textos conviene quitar esos estilos del HTML.
5. (Ya anotado antes) `crear-cuenta.html`, función `mostrarAlerta`, escribe el mensaje con `innerHTML`; y `sesion-nav.js` escribe el correo con `innerHTML`.
