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

**Falta:** F2 a F5.
