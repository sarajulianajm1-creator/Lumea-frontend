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
