# Preguntas que un jurado podría hacerle a Isabella sobre el rediseño

Escritas por Claude Code (7 oct 2026). Cada pregunta dice en qué archivo está la respuesta y qué prueba la comprueba.
**Las respuestas las escribe Isabella, con sus palabras:** es quien defiende el proyecto, y si puede explicarlo ella, lo entiende.
(Quién escribió qué está en `docs/bitacora-ia.md`: el código del rediseño es de la IA; el plan, las decisiones, los textos y la revisión son de Isabella.)

1. **¿Por qué ninguna paleta es la predeterminada? ¿Cómo se ve Lumea mientras la persona todavía no elige?**
   Dónde: `herramientas/generar_paletas.py` (la paleta «neutro»: superficies casi blancas y sin tono, con los mismos colores de rol, y por qué va primero en el CSS), `tema.js` (no cae en ninguna paleta), `selector-colores.js` y `index-ingresado.html` (la tarjeta «Elige tus colores y tus caras»), `MARCA.md`. Pruebas: `pruebas/test_paletas.py::test_las_superficies_y_el_texto_del_neutro_no_tienen_tono`, `test_sin_paleta_guardada_se_ve_el_estado_neutro_y_no_laguna`, `pruebas/test_selector_colores.py`.
   Respuesta de Isabella:

2. **Las caras del check-in vienen de internet (DiceBear). ¿Qué datos de la persona viajan? ¿Qué pasa sin conexión?**
   Dónde: `caras-checkin.js` (la semilla es fija, `lumea-animo`; solo viaja el ajuste del dibujo), `docs/defensa/privacidad-y-limites-rediseno.md` (qué ve DiceBear y qué no), `README.md` («Créditos»: CC0). Pruebas: `pruebas/test_caras_checkin.py::test_la_direccion_no_lleva_datos_de_la_persona` y `test_sin_internet_se_quita_la_imagen_y_queda_la_palabra_y_el_boton_funciona`.
   Respuesta de Isabella:

3. **La paleta y las caras se guardan en el navegador, no en la cuenta. ¿Por qué, y qué límite tiene?**
   Dónde: `tema.js` y `caras-checkin.js` (`localStorage`, con `try/catch`), `docs/defensa/privacidad-y-limites-rediseno.md` (el límite conocido y el siguiente paso). Pruebas: `pruebas/test_selector_colores.py::test_la_eleccion_hecha_en_inicio_se_ve_marcada_en_avatar`, `pruebas/test_caras_checkin.py::test_si_localstorage_falla_no_se_rompe_nada`.
   Respuesta de Isabella:

4. **¿Cómo se asegura que el rediseño se puede usar con teclado, con lector de pantalla y con zoom, y que los colores se leen bien en las cinco paletas y en el estado neutro?**
   Dónde: `pruebas/test_accesibilidad.py` (recorrido con Tab: todo se alcanza, no hay trampas y el foco siempre se ve; reflujo a 200 % de zoom y a 320 px), `pruebas/test_rediseno.py` (texto ≥ 12,8 px, áreas táctiles ≥ 44 px), `pruebas/test_capturas.py` (contraste con axe-core en las 5 paletas + el neutro × claro/oscuro, también con los resultados «IA segura» e «IA duda»), `herramientas/generar_paletas.py` (contraste WCAG y daltonismo al generar), `estilos/componentes.css` (`--c-foco`).
   Respuesta de Isabella:

5. **¿Cómo evitan que la gamificación se sienta como una competencia o un juicio sobre cómo se siente la persona?**
   Dónde: `index-ingresado.html` y `indexx.js` (el XP aparece solo en tres lugares; ningún botón de ánimo lo promete; «Guardar mi ánimo» es secundario y el XP se ve en la celebración), `estilos/app.css` (la cara elegida lleva el mismo color para los cinco ánimos), `MARCA.md` («Qué NO debe parecer nunca»). Pruebas: `pruebas/test_index_ingresado.py::test_el_xp_aparece_tres_veces_como_maximo`, `pruebas/test_caras_checkin.py::test_ningun_boton_dice_xp_ni_tiene_un_color_distinto_por_animo`, `pruebas/test_progreso.py::test_no_hay_calorias_ni_comparaciones`.
   Respuesta de Isabella:

6. **¿Qué pasa con una persona que pide menos movimiento en su sistema, y por qué casi nada se mueve en la app?**
   Dónde: `estilos/tokens.css` (`prefers-reduced-motion`: las tres duraciones valen 0 ms), `estilos/app.css` sección 9 (una sola entrada por pantalla de 220 ms; el cambio de paleta solo transiciona el fondo y el texto), `estilos/celebracion.css`, `caras-checkin.js` (solo la cara elegida se anima). Pruebas: `pruebas/test_movimiento.py::test_al_abrir_la_pantalla_se_mueve_una_sola_cosa_la_entrada`, `test_con_movimiento_reducido_nada_se_mueve_las_cosas_solo_aparecen`, `test_ninguna_hoja_escribe_una_duracion_a_mano`.
   Respuesta de Isabella:
