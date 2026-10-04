# T1 · Pruebas de humo y capturas

**Para:** Claude Code · **Necesita de Isabella:** nada · **Worktree:** `claude --worktree t1-pruebas`

## Objetivo
Una red de seguridad en Python (el lenguaje que Isabella domina) que abre todas las páginas y avisa si algo se rompe mientras varias personas editan.

## Hacer
1. `pruebas/requirements.txt` con `pytest` y `pytest-playwright`, y un `pruebas/LEEME.md` de 10 líneas: cómo instalar y correr.
2. `pruebas/conftest.py`: sirve la carpeta del proyecto con `http.server` en un puerto libre y simula el backend con `page.route("http://127.0.0.1:5002/**")`, usando respuestas en `pruebas/respuestas/*.json` con la forma que esperan `api.js`, `lumea-camara.js` e `indexx.js`.
3. `pruebas/test_humo.py`, para cada `.html` de la raíz: sin errores en consola, sin archivos locales 404, `<html lang="es">`, un solo `h1`, imágenes con `alt`, botones con nombre accesible. Si una regla falla en una página de Sara, márcala `xfail` con la razón; no arregles la página en este ticket.
4. `pruebas/test_camara.py` sobre `alimentos.html`: sin sesión se ve `#sin-sesion`; con sesión y una foto de prueba generada (sin caras) se ve IA segura con logros; IA duda muestra botones agrupados; confirmar guarda. La foto se sube con `set_input_files` sobre `input[type=file]`.
5. `pruebas/test_capturas.py`, marcado `@pytest.mark.capturas` (no corre por defecto): captura cada página en las 5 paletas × claro/oscuro y con `?piel=sara`, en `pruebas/capturas/` (agrégala a `.gitignore`). La paleta y el modo se ponen con `localStorage` (`lumea-paleta`, `lumea-modo`) antes de cargar.
6. Si puedes, revisa contraste con axe-core (regla `color-contrast`) en las capturas.

## No hacer
No cambies archivos de la app. Si una prueba descubre un error real, repórtalo en tu resumen.

## Listo cuando
`pip install -r pruebas/requirements.txt && playwright install chromium && pytest pruebas` pasa en menos de 1 minuto, y `pytest pruebas -m capturas` llena `pruebas/capturas/`.
