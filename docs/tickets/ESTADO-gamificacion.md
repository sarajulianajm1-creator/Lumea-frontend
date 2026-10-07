# Estado de la misión de gamificación 100/100

Rama `gamificacion-100`. Actualizado al cerrar cada fase.

## F1 · Pruebas: LISTA (5 oct 2026)

**Qué quedó listo**
- `pruebas/`: servidor local, backend simulado (`respuestas/*.json`, con los campos nuevos del contrato: `nivel_anterior`, `desbloqueos`, `calcomanias_nuevas`, `calcomanias`, `es_fruta`), humo en las 14 páginas, cámara (sin sesión, IA segura, IA duda, confirmar) y capturas con axe.
- El entorno vive en `.venv/` (ignorado por git).

**Cómo probarlo**

    .venv/bin/pytest pruebas                 # 38 pasan, 9 xfail, ~25 s
    .venv/bin/pytest pruebas -m capturas     # ~2 min -> pruebas/capturas/ y contraste.txt

**Errores reales que encontraron** (estado al 7 oct)
1. `alimentos.html`: sin sesión se mostraban el aviso y la cámara (`[hidden]` anulado por `style.css`). **Arreglado en F2** (regla `[hidden]` en su `<style>`).
2. `index-ingresado.html` no tenía `h1`. **Arreglado en F5** (el saludo es el `h1`, con el mismo aspecto: se comparó el estilo calculado antes y después).
3. `inicio.html` (de Isabella) enlaza `estilos/___.css` (404) y apunta a `registrar-comida.html`. **Se ignora**: Isabella ya lo corrigió en su copia (por eso la prueba sigue como `xfail`).
4. `mis-registros.html` escribía texto del servidor con `innerHTML`. **Arreglado en F5** (createElement y textContent; una prueba compara cada tarjeta con la que armaba la plantilla anterior).
5. `progreso.html` y `avatar.html` estaban vacías. **Construidas en F3 y F4.**

**Límites**
- Sin internet en las pruebas: las fuentes de Google y las caras de DiceBear se reemplazan por vacío. Bootstrap y Bootstrap Icons ya no: están en `vendor/` y las pruebas miden con ellos de verdad (desde F2).
- El contraste de todas las páginas se reporta en `pruebas/capturas/contraste.txt`; Progreso y Avatar son `ESTRICTAS` y deben dar 0 (dan 0).

## F2 · Celebración: LISTA (7 oct 2026)

**Qué quedó listo**
- `celebracion.js` + `estilos/celebracion.css`: `window.LumeaCelebrar(gamificacion)`. Cola, un momento a la vez: XP (chip que se va a los 3 s, y «Meta de hoy cumplida»), misión cumplida (con su calcomanía pegándose), calcomanía nueva («Ver mi álbum» / «Seguir», sin límite de tiempo) y subida de nivel (el único `<dialog>` modal: «Se abrió en tu armario: …», «Avatar nuevo: …», «Ponérmelo» / «Seguir»; Esc cierra y el foco vuelve).
- `pegatinas.js` + `estilos/pegatinas.css`: la calcomanía (forma troquelada en SVG, color del rol, ganada o contorno punteado). La usarán también el álbum de Avatar y las pruebas. Arte propio: `img/calcomanias/LEEME.md`.
- `lumea-camara.js` la llama después de cada resultado; `alimentos.html` carga los dos scripts. Cómo la conecta Isabella a su check-in de ánimo (una línea) está en el encabezado de `celebracion.js`.
- Respuestas simuladas con el contrato real del backend: `desbloqueos` con `tipo` `avatar`/`ropa`/`accesorio`, `predecir_duda.json` con 3 opciones sin grupo y nombres largos (`predecir_grupo.json` conserva el caso de los grupos), `calcomanias.json` con las 10 reales.
- Errores arreglados (los pidió Isabella el 7 oct): `alimentos.html` ya no depende de Bootstrap para ocultar `#flujo-registro`/`#sin-sesion` con `[hidden]` (la prueba que era `xfail` ahora pasa).
- **Bootstrap 5.3.3 y Bootstrap Icons 1.11.3 en `vendor/`** (copia local, MIT, descargadas de jsDelivr, con su licencia) y enlazados desde las 9 páginas de Sara: la demo y el video funcionan sin internet. Las pruebas ya miden con Bootstrap real. (Las fuentes de Google siguen en línea: si no hay internet las páginas de Sara caen a la fuente del sistema o a Bricolage; no se pidió cambiarlo.)

**Cómo probarlo:** `.venv/bin/pytest pruebas` (63 pasan, 8 xfail esperados).

## F3 · Progreso: LISTA (7 oct 2026)

> **Rehecho sobre la pantalla de Sara en F2.5** (decisión de Isabella: la base de Progreso es la de Sara). Lo que sigue describe la primera versión; `progreso.html` ahora es el diseño de Sara conectado, `estilos/progreso.css` ya no existe y `progreso.js` solo dibuja la semana, el álbum y los estados. Ver la sección F2.5.

**Qué quedó listo**
- `progreso.html` + `progreso.js` + `estilos/progreso.css` (bosquejo 10, solo la vista «Semana»): nivel con `.barra-xp` y el número escrito («Te faltan 35 XP para el nivel 3», «Llegaste al nivel máximo»), racha actual y mejor racha (plural correcto), meta de hoy, comidas de la semana de lunes a domingo (barras; la fruta lleva un ícono de manzana, no solo color), ánimo de la semana con las caras del avatar (si no hay internet para DiceBear queda el nombre escrito), `mensaje_regreso` como bienvenida y el enlace «Mi álbum: 3 de 10 calcomanías». Estados: cargando, error con «Intentar otra vez» y sin sesión.
- Si un dato nuevo no llega (backend viejo), esa parte se omite y la pantalla funciona igual.
- `api.js`: `obtenerCalcomanias(email)` y `obtenerEstadosAnimo(email, dias)` (con `dias=7`).
- `indexx.js` (Inicio de Sara), solo esas líneas: «1 día» en singular y «Meta cumplida: 20 XP hoy» en vez de «20 de 15 XP hoy».
- La navegación inferior es la misma de las demás pantallas privadas, con `aria-current="page"` en Progreso.

**Cómo probarlo:** `.venv/bin/pytest pruebas` (20 pruebas de `test_progreso.py`, que corren en hora de Colombia y con el reloj fijo en el miércoles 7 de octubre; 4 de `test_index_ingresado.py`) y `.venv/bin/pytest pruebas -m capturas -k progreso` (0 errores de contraste en las 5 paletas × claro/oscuro).

## F4 · Avatar, misiones, armario y álbum: LISTA (7 oct 2026)

**Qué quedó listo**
- `avatar.html` + `avatar.js` + `estilos/avatar.css` (bosquejo 06, variante A «la vitrina»): avatar grande con nivel y barra de XP, y debajo tres pestañas con el patrón ARIA de «tabs» (flechas, Inicio y Fin; solo la activa entra con Tab). Abren con `#misiones`, `#armario` y `#calcomanias`: a esas anclas apuntan «Ponérmelo» y «Ver mi álbum» de la celebración.
- **Misiones:** las tres diarias de `/progreso` con «+10 XP»; la cumplida lleva «Cumplida hoy» y su calcomanía (fruta → «Fruta del día», tres comidas → «Tres al día», check-in → «Cómo llegas») si ya la ganó.
- **Armario:** ropa y accesorios de `GET /avatar`. «Ponerme» y «Quitar» usan `equiparObjeto` y `quitarObjeto`; el backend responde con el avatar completo y se redibuja, el foco se queda en el mismo botón y el avatar da un saltico (un solo movimiento). Lo bloqueado lleva candado, «Se abre en el nivel N», `aria-disabled="true"` y no hace nada. Si el backend dice 403 o falla, se avisa y no cambia nada.
- **Calcomanías:** el álbum de `GET /calcomanias` (ganadas a color por rol con su fecha; por ganar con contorno punteado y «Cómo se gana: …»). Si el álbum no carga, el resto de la pantalla funciona.
- El avatar grande usa las capas de Laura cuando `imagen_lista` es verdadero en todas; si no, la cara DiceBear con el ánimo de hoy, y sin internet queda una silueta.
- `formato.js`: plural, porcentaje y texto del nivel, compartidos con Progreso.

**Cómo probarlo:** `.venv/bin/pytest pruebas` (32 pruebas de `test_avatar.py`) y `.venv/bin/pytest pruebas -m capturas -k avatar` (las tres pestañas, en 5 paletas × claro/oscuro, 0 errores de contraste).

## F5 · Integración y cierre: LISTA (7 oct 2026)

**Qué quedó listo**
- **Navegación privada igual** en las cinco pantallas (Inicio, Mis registros, Registrar, Progreso, Avatar), con `aria-current="page"` en la actual: `pruebas/test_navegacion.py`.
- **Pruebas:** `.venv/bin/pytest pruebas` → 142 pasan, 1 `xfail` (el borrador de Inicio de Isabella). `.venv/bin/pytest pruebas -m capturas` → 176 capturas en 5 paletas × claro/oscuro: **0 errores de contraste en todas las páginas, también con Bootstrap real**; solo la piel original de Sara (`?piel=sara`, que no se arregla) tiene 1 a 3 elementos de contraste bajo en 7 páginas. Progreso y Avatar (las tres pestañas) están en `ESTRICTAS`.
- **Para la demo y el video sin internet:** Bootstrap 5.3.3 y Bootstrap Icons 1.11.3 en `vendor/`, enlazados desde las 9 páginas de Sara y también desde Progreso y Avatar.
- **Errores que pidió arreglar Isabella:** `[hidden]` de `alimentos.html` (F2), `h1` de `index-ingresado.html` y `innerHTML` de `mis-registros.html` (F5). `inicio.html`, ignorado.
- **Probado contra el backend real** (rama `gamificacion-100`, cuenta de demostración `demo@lumea.co`): Progreso (nivel 4, racha de 7, 6 de 10 calcomanías, la semana y el ánimo), Avatar (ponerse y quitar de verdad, bloqueado, álbum, misiones) y la cámara con una foto de arepa (+15 XP, «Meta de hoy cumplida» y la calcomanía «Diez registros», sin errores de consola).
- `docs/defensa/preguntas-gamificacion.md`: 10 preguntas de jurado con el archivo y la función donde está la respuesta. **Sin respuestas:** las escribe Isabella.
- Una fila en `docs/bitacora-ia.md` por cada fase (F1 a F5).

**Un hallazgo importante del backend (ya arreglado, ver `ESTADO_GAMIFICACION.md` del backend):** la primera vez que se probó contra el backend real, el servidor se cayó. Progreso y Avatar piden 3 cosas a la vez y el backend compartía UNA conexión MySQL entre hilos: la conexión se corrompía y el proceso a veces moría con un segmentation fault. Se arregló en `Backend/app.py` con un candado que atiende las peticiones de a una, con su prueba (`pruebas/test_concurrencia.py`). **Sin ese arreglo la demo se habría caído al abrir Progreso.** Está en la rama `gamificacion-100` del backend, sin push.

**Errores que encontré y NO arreglé** (no eran de esta misión o son de Isabella)
- `crear-cuenta.html`, función `mostrarAlerta`: escribe el mensaje con `innerHTML`. Si el mensaje viniera del servidor sería el mismo problema que había en Mis registros (se puede arreglar igual: createElement y textContent).
- `sesion-nav.js` (ejercicio de Isabella): escribe el correo guardado con `innerHTML`.
- `index-ingresado.html` usa emojis como íconos (🔥, 🎯), que `CLAUDE.md` prohíbe; es de Sara.
- Las fuentes de Google de las páginas de Sara siguen en línea (sin internet caen a la fuente del sistema).
- No se hizo T2 (rediseño de Registrar con la piel de Lumea) ni T6 (movimiento entre pantallas): no estaban en esta misión.

**Cómo probarlo todo**

    .venv/bin/pytest pruebas
    .venv/bin/pytest pruebas -m capturas        # ~3 min
    # contra el backend real (desde ~/Python_proyects/Lumea/Backend, en otra terminal):
    python3 herramientas/crear_usuario_demo.py --borrar     # imprime la contraseña; el correo es demo@lumea.co
    python3 app.py
    # y abrir el frontend con un servidor estático, con lumea_email = demo@lumea.co en localStorage

## F2.5 · Integración con las pantallas de Sara: LISTA (7 oct 2026)

Isabella decidió el 7 de oct (la unión estaba pendiente de esa decisión). Rama de trabajo: `integracion-sara` (sale de `gamificacion-100`).

**Cómo se unió.** Con `git merge origin/main` (commit `2a360e4`), sin copiar archivos: el commit `b89dc7d` queda en la historia con su autoría (git lo muestra como «Laura Jiménez» con el correo de Sara: **revisar que la autoría quede como Isabella quiere**). Conflictos resueltos como pidió Isabella: la cámara (`alimentos.html`) y el Avatar, los nuestros; Inicio, Progreso, Ánimo, login y `style.css`, los de Sara. Los cambios van en commits aparte para que se vean uno por uno.

**Qué cambió (todo sobre el diseño de Sara, que sigue siendo suyo)**
- **Una sola conexión:** todo por `api.js` (puerto 5002). Se quitó `LUMEA_BACKEND_URLS` (5001/5000) y los `fetch` escritos a mano de `lumea-state.js`, `indexx.js`, `emociones.html`, `crear-cuenta.html` e `iniciar-sesion.html`. Una prueba revisa el código fuente: ningún archivo de Sara tiene `fetch(`, `127.0.0.1`, `5001`, `5000`, `?email=` ni `innerHTML`.
- **Una sola sesión:** `obtenerSesion()` también lee `lumea_usuario_email` (quien ya la tenía no pierde la sesión) y `guardarSesion()` deja una sola clave. El correo ya no se lee de la dirección (`?email=`): hay una prueba. Crear cuenta ahora manda la contraseña a la API y entra directo a Inicio.
- **Contrato real:** `lumea-state.js` lee `GET /progreso`, `GET /historial` (con `es_fruta`) y `GET /estado-animo?dias=7`. Ya no inventa XP ni niveles en el navegador (antes sumaba XP local y subía de nivel de a 100).
- **Arreglos que pidió Isabella:** «0 de 15 comidas» (15 es la meta de XP: ahora «N de 3»), «210/250 XP del día» (era el XP total del nivel: ahora «10 de 15 XP hoy» o «Meta cumplida: 20 XP hoy»), «+20 XP» por misión (son +10, y sale del backend), los rótulos «Versión 1.1», y los errores `lumeaStore.suscribir is not a function` y `null.style` (había un banner y un modal que no existían en la página).
- **Caras de ánimo:** los emojis pasaron a las caras DiceBear del avatar (`avatar.urls_por_estado`), que cambian en vivo al elegir en Ánimo. El nombre del estado siempre está escrito; sin internet se quita la imagen y queda el nombre. Los emojis de ícono (racha, estrella, hoja, bandera, canasta, corazón) pasaron a Bootstrap Icons.
- **Celebración:** `LumeaCelebrar` se llama con la respuesta de `POST /estado-animo` desde el estado compartido, así que celebra igual en Ánimo y en el check-in rápido de Inicio.
- **Menú:** el lateral de Sara con los cinco destinos (Inicio, Mis registros, Registrar, Progreso, Avatar) en las seis pantallas privadas, y su barra inferior con la cámara al centro en celular. Ánimo no está en el menú: se abre desde Inicio y desde Progreso. Lo escribe `herramientas/menu_privado.py` (idempotente) para que las páginas no se desvíen.
- **Paletas:** `conectar_puente.py` cubre las pantallas nuevas y Bootstrap local (`vendor/`); `puente-sara.css` (sección 10) pasa cada color fijo y degradado de Sara a tokens por rol (comida = aguacate, logro = maracuyá, emoción = guayaba, misión = mora) y apaga el movimiento con `prefers-reduced-motion`. Piezas nuevas en `estilos/pantallas-sara.css`.
- **Textos del servidor:** `textContent` en todas las páginas de Sara (también la alerta de `crear-cuenta.html`).
- **Progreso (F3) sobre la base de Sara:** `progreso.html` es el de Sara; `progreso.js` solo dibuja la semana (comidas con fruta, ánimo con caras), el álbum y los estados de carga/error. Las cuentas puras (semana, plural, meta) están en `formato.js` y las comparten Inicio, Progreso y Ánimo.

**Cómo probarlo**

    .venv/bin/pytest pruebas                                   # todas verdes
    .venv/bin/pytest pruebas -m capturas                       # contraste: Inicio, Progreso, Ánimo y Avatar con 0 errores en 5 paletas × claro/oscuro

**Lo que no se hizo / hay que saber**
- `inicio.html` y `estilos/inicio.css` (de Isabella): no se tocaron.
- Avatar (F4) sigue el bosquejo 06: `bosquejos/laura/` todavía no existe.
- Se descartó el rediseño de la cámara de Sara (`alimentos.html`: dock de controles, esquinas de enfoque, variante «hoja») porque no maneja IA duda ni el contrato; quedó la nuestra con el menú de Sara.
- `sesion-nav.js` (ejercicio de Isabella) escribe el correo con `innerHTML`: no se tocó.
- En celular el menú no tiene «Cerrar sesión» (en computador está al pie del menú lateral): falta decidir dónde va.
- `animo.html` (de Sara) es solo un atajo a `emociones.html`; se le agregó un `h1` y un enlace.

## Decisiones provisionales para Isabella

Elegí la opción más sobria y reversible cuando algo no estaba en el bosquejo ni en la misión. Dime si alguna no te gusta.

1. **Dónde aparece el XP.** El chip va fijo arriba al centro (la «h1» de Registrar está oculta, así que «junto al título» no se puede). Reversible: es una regla de `.celebracion` en `celebracion.css`.
2. **La calcomanía suelta no se va sola.** Tiene botones, y un aviso con botones que desaparece a solas no es accesible (WCAG 2.2.1). Se cierra con «Seguir», con Esc o al tocar «Ver mi álbum». No le quita el foco a nadie, salvo que se haya perdido (p. ej. cuando los botones de confirmar se reemplazan).
3. **Una calcomanía de rol «misión» se pega junto a su misión** en un solo momento; las demás tienen el suyo.
4. **«Meta de hoy cumplida»** es un segundo chip pequeño junto al de XP (no estaba en la lista de momentos; antes salía como línea de texto).
5. **Se mantiene la lista de texto `#backend-logros`** de la cámara como registro que no desaparece, al lado de la celebración. Ahora también anota la calcomanía nueva.
6. **El título de la duda es siempre «¿Cuál de estos es?»**. Cuando la IA dudó (opciones sin grupo) el mensaje dice «La IA no está segura. Toca el que es…» en vez del texto técnico del backend; en un grupo de confusión se sigue mostrando el texto del backend.
7. **Arte de las calcomanías por lista, no por archivo.** En vez de «si existe `img/calcomanias/<id>.svg`» (que pide archivos que no existen y llena la consola de 404), la lista `ARTE_PROPIO` de `pegatinas.js` dice cuáles tienen dibujo propio.
8. **`celebracion.css` es autónomo** (no carga `componentes.css`): en las páginas de Sara `componentes.css` cambiaría los márgenes de los títulos y párrafos.
9. **La fila de la bitácora de F1 la redacté yo** (no tenía a mano la que se había propuesto en el chat); revísala.
10. **Progreso y Avatar usan el cascarón de las páginas de Sara** (Bootstrap local + `style.css` + `puente-sara.css` + la barra inferior) con piezas de Lumea (`componentes.css`) por dentro. Así la navegación es idéntica en las cinco pantallas privadas, como pide F5. Reversible cuando T2 rediseñe Registrar con la piel de Lumea: se cambia el encabezado de las dos páginas.
11. **«Meta de hoy» se agregó a Progreso** como tercera tarjeta junto a las rachas (los datos llegan en `/progreso`; en el bosquejo no hay una tarjeta para ella). Se puede borrar sin tocar nada más (`.progreso__meta` en `progreso.html`).
12. **Racha en cero:** la tarjeta dice «0 días» y «Registra algo hoy para empezar una racha»; con 1 día, «¡Empezó tu racha!».
13. **Semana de lunes a domingo según la fecha del dispositivo.** Los días que todavía no llegan salen con borde punteado y sin cifra.
14. **No agregué** la sugerencia de «hablar con alguien» del bosquejo 11 (es la decisión ética tuya que el bosquejo deja abierta; además esa pantalla no está en estas fases).
15. **Sin selector de base en Avatar.** El bosquejo no lo tiene y las imágenes de las bases todavía no existen; `elegirBaseAvatar` ya está en `api.js` para cuando se decida.
16. **Con las capas de Laura la cara del ánimo no se dibuja** (esas imágenes no llevan cara; el backend dice que el ánimo siempre usa DiceBear). Hoy, sin las imágenes, se ve la cara DiceBear con el ánimo.
17. **Lo bloqueado** dice «Se abre en el nivel N» (como pedía T5) y el botón «Nivel N» es `aria-disabled`; no se esconde ni se desactiva con `disabled` para que el lector de pantalla pueda leerlo.
18. **En computador** (≥ 840 px) Avatar usa dos columnas: la vitrina queda fija a la izquierda y las pestañas a la derecha. En celular, una debajo de la otra, como el bosquejo.
19. **Textos nuevos que escribí y tú debes revisar** (no estaban en los bosquejos): subtítulo de Progreso «Cómo vas en la semana, sin compararte con nadie.», de Avatar «Cámbiale la ropa, mira tus misiones y tu álbum de calcomanías.», nota del armario «Lo que se abre al subir de nivel es tuyo para siempre.», «Todavía no te pusiste nada.», «Puesto: …», «Cumplida hoy» / «Para hoy», «Mi álbum», «Intentar otra vez», y los avisos «Te pusiste …» / «Te quitaste …».
20. **Ánimo sin estado preseleccionado:** Sara dejaba «Bien» elegido; ahora hay que elegir para poder guardar (así nadie guarda un «Bien» sin querer).
21. **Textos de Ánimo sin género:** «Tranquila…» y «eres valiosa» pasaron a «Con calma y buena disposición…» y «lo que sientes importa». Revisar.
22. **Se quitó «Hablar con orientación escolar»** (el botón y el modal no existían en la página y «Mensaje enviado» era falso: no hay a dónde enviarlo). Quedó la frase del bosquejo 11 como texto: «Si te sientes mal varios días, hablar con alguien ayuda.» La decisión ética sigue siendo tuya.
23. **Se quitó «LUMEA no te penaliza ni quita experiencia si te ausentas»:** el backend sí descuenta XP por inactividad; la pantalla solo muestra `mensaje_regreso` como bienvenida.
24. **Textos nuevos que escribí:** «Cómo vas en la semana, sin compararte con nadie.», «Un check-in de diez segundos.», «Hoy cumpliste tus tres misiones», «Hoy llegaste: Bien. Tu check-in ya está registrado.», «Tu ánimo de hoy ya está registrado», «Meta del día», «Misiones del día», «Ver mi armario», «Cerrar sesión».
25. **«Registra 3 comidas» usa 3 como constante** en el frontend (el backend no publica ese número en `reglas`).
