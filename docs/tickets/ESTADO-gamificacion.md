# Estado de la misión de gamificación 100/100

Rama `gamificacion-100`. Actualizado al cerrar cada fase.

## F1 · Pruebas: LISTA (5 oct 2026)

**Qué quedó listo**
- `pruebas/`: servidor local, backend simulado (`respuestas/*.json`, con los campos nuevos del contrato: `nivel_anterior`, `desbloqueos`, `calcomanias_nuevas`, `calcomanias`, `es_fruta`), humo en las 14 páginas, cámara (sin sesión, IA segura, IA duda, confirmar) y capturas con axe.
- El entorno vive en `.venv/` (ignorado por git).

**Cómo probarlo**

    .venv/bin/pytest pruebas                 # 38 pasan, 9 xfail, ~25 s
    .venv/bin/pytest pruebas -m capturas     # ~2 min -> pruebas/capturas/ y contraste.txt

**Errores reales que encontraron (no se arreglaron; no eran de este ticket)**
1. `alimentos.html`: sin sesión se muestra el aviso, pero la cámara también, porque `.lumea-dashboard-screen` (`style.css`) anula el atributo `hidden`. Prueba `xfail(strict)`: cuando se arregle, avisará.
2. `index-ingresado.html` no tiene `h1`.
3. `inicio.html` (de Isabella) enlaza `estilos/___.css`, que no existe (404), y su menú apunta a `registrar-comida.html`, que ya no existe.
4. `mis-registros.html` escribe texto del servidor con `innerHTML` (regla de CLAUDE.md: `textContent`). Código de Sara; Isabella decide si se corrige.
5. `progreso.html` y `avatar.html` están vacías (`xfail` hasta F3 y F4).

**Límites**
- Sin internet en las pruebas: Bootstrap y fuentes se reemplazan por vacío (solo queda `.d-none`), así que el contraste de las páginas de Sara se mide sin Bootstrap.
- El contraste de las 14 páginas actuales se reporta en `pruebas/capturas/contraste.txt` sin fallar; en F5 las pantallas nuevas pasan a `ESTRICTAS` y deben dar 0.

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
