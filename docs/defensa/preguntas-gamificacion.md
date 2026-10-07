# Preguntas que un jurado podría hacerle a Isabella sobre el frontend de la gamificación

Escritas por Claude Code (7 oct 2026). Cada pregunta dice en qué archivo y función está la respuesta, y qué prueba la comprueba.
**Las respuestas las escribe Isabella, con sus palabras:** es quien defiende el proyecto, y si puede explicarlo ella, lo entiende.
(Quién escribió qué está en `docs/bitacora-ia.md`: el código de esta parte es de la IA; las decisiones, los bosquejos y la revisión son de Isabella.)

1. **¿Qué celebra la app y qué nunca celebra? ¿Cómo evitan que se sienta como una app de dieta o una competencia?**
   Dónde: encabezados de `celebracion.js` y `progreso.js` (reglas), `MARCA.md` («Qué NO debe parecer nunca»), `CLAUDE.md` (gramática de color). Pruebas: `pruebas/test_progreso.py::test_no_hay_calorias_ni_comparaciones` y `pruebas/test_avatar.py::test_no_hay_calorias_ni_comparaciones`.
   Respuesta de Isabella:

2. **¿Por qué las celebraciones van en cola, de una en una, y solo la subida de nivel bloquea la pantalla?**
   Dónde: `celebracion.js` → `momentosDe` (el orden), `procesar` (la cola), `momentoNivel` (el único `<dialog>` modal). Prueba: `pruebas/test_celebracion.py::test_los_momentos_van_de_a_uno_y_en_orden`.
   Respuesta de Isabella:

3. **¿Qué pasa con una persona que pide menos movimiento en su sistema? ¿Cómo se respeta?**
   Dónde: `estilos/tokens.css` (`@media (prefers-reduced-motion)`, duraciones en 0), `estilos/celebracion.css`, `estilos/pegatinas.css` y `estilos/avatar.css` (sin animación), `celebracion.js` → `reducido`. Prueba: `pruebas/test_celebracion.py::test_con_movimiento_reducido_nada_se_anima`.
   Respuesta de Isabella:

4. **¿Cómo se usa Avatar solo con el teclado y con un lector de pantalla? ¿Por qué lo bloqueado usa `aria-disabled` y no `disabled`?**
   Dónde: `avatar.js` → `seleccionar` y `conectarPestanas` (patrón ARIA de pestañas: flechas, Inicio, Fin), `tarjetaDePrenda` (el botón bloqueado se puede leer pero no hace nada), `aviso` (lo que se anuncia al ponerse una prenda). Pruebas: `pruebas/test_avatar.py::test_las_flechas_cambian_de_pestana`, `test_lo_bloqueado_dice_el_nivel_y_no_hace_nada`, `test_equipar_con_el_teclado`.
   Respuesta de Isabella:

5. **¿Cómo se calcula la barra de nivel? ¿Qué pasa si alguien perdió XP o llegó al último nivel?**
   Dónde: `formato.js` → `porcentajeNivel` y `textoNivel` (la barra nunca baja de 0 y en el último nivel está llena); el backend guarda el nivel máximo aparte del XP (`Backend/gamificacion.py` → `sumar_actividad`). Pruebas: `pruebas/test_progreso.py::test_la_barra_no_baja_de_cero_si_se_perdio_xp`, `test_nivel_maximo`.
   Respuesta de Isabella:

6. **El backend manda las fechas como «Mon, 05 Oct 2026 00:00:00 GMT». ¿Por qué se leen en UTC y qué pasaría si no?**
   Dónde: `progreso.js` → `claveDeFechaDelServidor`, `semanaDe` y `comidasPorDia`; `mis-registros.html` → `formatearFecha` (`timeZone: "UTC"`). Prueba: `pruebas/test_progreso.py::test_las_fechas_del_servidor_se_leen_en_utc` (corre en hora de Colombia, UTC-5).
   Respuesta de Isabella:

7. **¿Qué pasa si el backend está apagado, es una versión vieja o no manda un campo nuevo?**
   Dónde: `progreso.js` → `cargar` (el progreso es lo esencial; el historial y el ánimo son extras que no tumban la pantalla), `avatar.js` → `cargar`, `celebracion.js` (cada campo es opcional), estados de error con «Intentar otra vez». Pruebas: `pruebas/test_progreso.py::test_si_faltan_los_campos_nuevos_la_pantalla_funciona` y `test_error_de_conexion_se_puede_reintentar`.
   Respuesta de Isabella:

8. **¿Por qué todo texto que llega del servidor se escribe con `textContent` y no con `innerHTML`?**
   Dónde: `celebracion.js` → `crear`, `avatar.js` → `crear`, `mis-registros.html` → `elemento` y `tarjetaDeRegistro`. Pruebas: `test_el_texto_del_servidor_nunca_es_html` en `test_celebracion.py`, `test_avatar.py`, `test_progreso.py` (si aplica) y `test_mis_registros.py`.
   Respuesta de Isabella:

9. **¿Cómo saben que los colores se leen bien en las cinco paletas, en claro y en oscuro?**
   Dónde: `herramientas/generar_paletas.py` (mide contraste y daltonismo al generar `estilos/paletas.css`), `pruebas/test_capturas.py` (`ESTRICTAS`: Progreso y Avatar, las tres pestañas, deben dar 0 errores de contraste con axe-core), `docs/validacion-paletas.md`. Regla de color: maracuyá y mango nunca como texto (`CLAUDE.md`).
   Respuesta de Isabella:

10. **¿Cómo funciona la demo sin internet?**
   Dónde: `vendor/` (Bootstrap 5.3.3 y Bootstrap Icons 1.11.3 copiados dentro del proyecto, licencia MIT), `estilos/tokens.css` (la fuente Bricolage vive en `estilos/fuentes/`), `pegatinas.js` (las calcomanías se dibujan solas en SVG). Lo que sí necesita internet: las caras DiceBear del avatar (si no cargan, queda una silueta o el nombre del ánimo) y las fuentes de Google de las páginas de Sara (si no cargan, cae a la fuente del sistema). Prueba: `pruebas/conftest.py` (`sin_internet` bloquea todo lo de afuera) y `pruebas/test_avatar.py::test_sin_internet_la_cara_queda_en_silueta`.
   Respuesta de Isabella:
