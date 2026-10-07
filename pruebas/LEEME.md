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
Internet tampoco hace falta: Bootstrap y Bootstrap Icons están en `vendor/` (copia local, MIT) y las
pruebas miden con ellos de verdad. Lo que viene de fuera (fuentes de Google, caras de DiceBear) se reemplaza por vacío.
