# Lumea (frontend)

Lumea es una app web que promueve hábitos de alimentación saludable en adolescentes: la IA reconoce
la comida en una foto y la gamificación celebra lo que la persona hace, sin prohibir nada.
Concurso Fedesoft 2026.

Las reglas de diseño están en `MARCA.md` y las del trabajo con IA, en `CLAUDE.md`.

## Ver la demo

Con el backend en el puerto 5002 y esta carpeta servida:

    python3 -m http.server 8001

y abrir `http://localhost:8001/index.html`.

## Pruebas

    python3 -m venv .venv && .venv/bin/pip install -r pruebas/requirements.txt
    .venv/bin/pytest pruebas                 # el backend se simula: no hace falta encenderlo
    .venv/bin/pytest pruebas -m capturas     # capturas y contraste en 5 paletas × claro/oscuro (lento)

## Créditos

- Caras del check-in: [DiceBear](https://www.dicebear.com) (estilos «gaze» y «moods», CC0).
- Fuente: Bricolage Grotesque (SIL OFL 1.1, `estilos/fuentes/OFL-Bricolage.txt`).
- Íconos: Bootstrap Icons (MIT, en `vendor/bootstrap-icons/`).
