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
- **Sello de advertencia (Res. 810):** el octágono mide 148 px para que su texto llegue a 12,8 px; es lo único con `text-transform: uppercase` (la prueba lo exceptúa). `.sello` y `.sello-mini` (Mis registros) comparten la misma regla. **Falta** el nombre accesible en minúsculas (`role="img"` + `aria-label`): va en R5 (cámara) y R6 (Mis registros), donde esas pantallas se rehacen y sus pruebas cambian.
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

## Textos nuevos para que Isabella revise

**Inicio (R2)**
- «Tu día» · «comidas» (en «1 de 3 comidas») · «Registrar comida»
- «Elige la cara que más se parece a tu día» (viene del esquema del documento) · «Guardar mi ánimo» · «Ver mi semana de ánimo»
- «Misión de hoy»
- Títulos que solo oye el lector de pantalla: «Nivel y racha» y «. Ver mi progreso» (al final de la franja del nivel)
- Racha dentro de la franja del nivel: «Te faltan 35 XP para el nivel 3. Racha: 3 días»
- Aviso si falla la foto directa: «No se pudo abrir la foto. Prueba con «Registrar comida».» (antes decía «Cámara en vivo»)

*(Se llena fase por fase.)*

## Para después de unir

(Cambios que necesitan tocar el `<body>` de una página pública o un archivo de Isabella; no se hicieron.)
