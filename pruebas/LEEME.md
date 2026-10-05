# Pruebas de Lumea (frontend)

Revisan que todas las páginas abran sin romperse. El backend se simula:
no necesitas MySQL ni `app.py`.

Instalar (una sola vez, desde la raíz del proyecto):

    python3 -m venv .venv && .venv/bin/pip install -r pruebas/requirements.txt
    .venv/bin/playwright install chromium

Correr:

    .venv/bin/pytest pruebas                 # todo menos las capturas (< 1 min)
    .venv/bin/pytest pruebas -m capturas     # pantallas en 5 paletas x claro/oscuro -> pruebas/capturas/

Las respuestas simuladas están en `pruebas/respuestas/*.json`.
Internet tampoco hace falta: Bootstrap y las fuentes de Google se reemplazan por vacío,
así que las páginas de Sara se miden sin Bootstrap (solo se conserva `.d-none`).
