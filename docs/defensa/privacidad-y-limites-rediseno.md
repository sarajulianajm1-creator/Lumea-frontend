# Privacidad y límites del rediseño (para la defensa)

Notas de respuesta para el jurado sobre dos decisiones del rediseño. Las respuestas de fondo
(las que se dicen en voz alta) las escribe Isabella en `preguntas-rediseno.md`; esto es el dato
técnico que las respalda.

## Las caras del check-in y el compañero no llevan ningún dato de la persona

*(Actualizado el 8 de octubre, Camino del cuidado: antes eran dos sets de caras que la persona elegía, con
la semilla fija `lumea-animo`; `caras-checkin.js` ya no existe.)*

- **Qué se pide a internet:** cada cara es una imagen de DiceBear 10.x, estilo *gaze*
  (`api.dicebear.com/10.x/gaze/svg`): las cinco del check-in, el compañero grande de Avatar y los seis de
  «Tu compañero». Las direcciones las manda el backend (`avatar.urls_por_estado`, `GET /avatares`) y
  `companero.js` solo les agrega `animationVariant` donde algo se anima.
- **Qué lleva la dirección:** solo el ajuste del dibujo (la forma, el color, la variante de los ojos y si se
  anima). La semilla es **fija por compañero** (`seed=lumea-sol`, `lumea-luna`…): son seis valores iguales
  para todas las personas, no el nombre, ni el correo, ni un identificador. Hay pruebas que lo comprueban
  (`pruebas/test_caras_checkin.py::test_la_direccion_no_lleva_datos_de_la_persona` y
  `pruebas/test_avatar.py::test_los_seis_van_quietos_sin_datos_de_la_persona_y_con_alt_vacio`).
- **Lo que sí ve DiceBear:** como cualquier servidor al que se le pide una imagen, ve la dirección IP del
  navegador y qué se pidió: cuál de los seis compañeros y con qué ojos. **Esto cambió:** antes, las cinco
  caras se pedían siempre y no se sabía cuál se elegía. Ahora la cara elegida se vuelve a pedir con
  `animationVariant=medium`, y Avatar pide al compañero con los ojos del ánimo de hoy. Así que DiceBear
  puede ver, junto a una IP, «este compañero con estos ojos»: un ánimo del momento, **sin nombre ni
  correo**. No es un dato que identifique a la persona, pero tampoco es «no ve nada».
- **Cómo se cerraría:** descargar los SVG y servirlos desde Lumea (el contrato del backend ya lo sugiere,
  también para cuando no haya internet). Habría que resolver la animación, que hoy la pide la dirección.
- **El ánimo que la persona guarda** va solo al backend de Lumea (`POST /estado-animo`), nunca a DiceBear.
- **Licencia:** el estilo es CC0 (dominio público). Está en el README, en «Créditos».
- **Sin internet:** la imagen se quita y queda la palabra («Muy mal» … «Muy bien»); el botón funciona igual.
  Depender de internet para las caras es una decisión aceptada por Isabella (7 de octubre de 2026).

## Límite conocido: la paleta y el modo se guardan en el navegador, no en la cuenta

- **Qué significa:** la paleta y el modo (claro / oscuro) se guardan en `localStorage`
  (`lumea-paleta` y `lumea-modo`). Pertenecen al navegador, no a la persona. (El set de caras y su clave
  `lumea-caras` ya no existen: el compañero sí vive en la cuenta, en el backend; `companero.js` borra la clave
  vieja si la encuentra.)
- **Consecuencias:**
  - Si la persona entra desde otro dispositivo u otro navegador, vuelve a ver el estado neutro y la tarjeta
    «Elige tus colores».
  - Si dos personas comparten un navegador, comparten la elección.
  - Si borra los datos del navegador, la pierde.
- **Por qué se aceptó:** el backend no se toca en esta misión y la elección es estética, no sensible.
  Guardarla en la cuenta (un campo más en el perfil) es el siguiente paso natural si se quiere que viaje.
- **Dónde está el código:** `tema.js` (paleta y modo); lee y escribe con `try/catch`, así que un navegador que
  bloquea el almacenamiento no rompe la app (`companero.js` también protege su único acceso).
