# Arte de las calcomanías

Por ahora cada calcomanía se dibuja sola: una forma troquelada de color según su rol y un
ícono simple (ver `pegatinas.js`). Es provisional.

Para poner un dibujo propio de una calcomanía:

1. Guarda el SVG aquí como `<id>.svg` (por ejemplo `primera_foto.svg`). Los ids están en
   `Backend/gamificacion_config.py` (`CALCOMANIAS`): primera_foto, diez_registros, tres_al_dia,
   fruta, como_llegas, ayudaste_ia, racha_3, racha_7, volviste, nivel_5.
2. Agrega ese id a la lista `ARTE_PROPIO` al comienzo de `pegatinas.js`.

Se pide así (y no «si existe el archivo») para que la página no haga peticiones a archivos
que todavía no están.
