# Preguntas que un jurado podría hacerle a Isabella sobre el Camino del cuidado

Escritas por Claude Code (8 oct 2026). Cada pregunta dice en qué archivo está la respuesta y qué prueba la comprueba.
**Las respuestas las escribe Isabella, con sus palabras:** es quien defiende el proyecto, y si puede explicarlo ella, lo entiende.
(Quién escribió qué está en `docs/bitacora-ia.md`: el código es de la IA; la reorientación desde el Cántico de las criaturas, los textos, los valores de la gamificación y las decisiones son de Isabella.)

1. **¿Por qué la cara del check-in es la de tu compañero y no un set de caras que cada persona elija?**
   Dónde: `companero.js` (dibuja las cinco caras desde `avatar.urls_por_estado` y anima solo la elegida), `avatar.js` (la sección «Tu compañero» y la figura grande), `Backend/docs/CONTRATO_GAMIFICACION.md` (los seis compañeros de gaze con su forma y su color, y cómo sus ojos muestran el ánimo), `docs/defensa/privacidad-y-limites-rediseno.md` (qué ve DiceBear ahora y qué cambió). Pruebas: `pruebas/test_caras_checkin.py::test_cada_boton_trae_la_cara_de_su_estado_del_companero_y_quieta`, `test_solo_la_cara_elegida_se_anima_y_la_animacion_la_sigue`, `test_con_movimiento_reducido_las_caras_se_ven_pero_no_piden_animacion`; `pruebas/test_avatar.py::test_elegir_un_companero_lo_guarda_lo_marca_y_el_foco_se_queda`.
   Respuesta de Isabella:

2. **¿Por qué «semillas» y «etapas» en vez de XP y niveles, si el contrato del backend todavía dice `xp_total` y `nivel`?**
   Dónde: `formato.js` (`semillas(n)` y los textos compartidos: el único lugar donde se arman), `lumea-ui.js`, `avatar.js` y `celebracion.js` (lo que se ve), `Backend/docs/CONTRATO_GAMIFICACION.md` (las claves no cambian), `MISION-camino.md` («Vocabulario»). Pruebas: `pruebas/test_vocabulario.py::test_ninguna_pantalla_privada_dice_xp_ni_nivel`, `test_semillas_va_en_singular_solo_con_una`, `test_te_faltan_las_semillas_para_la_etapa_siguiente_con_su_plural`.
   Respuesta de Isabella:
