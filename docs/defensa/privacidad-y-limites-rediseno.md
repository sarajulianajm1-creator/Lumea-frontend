# Privacidad y límites del rediseño (para la defensa)

Notas de respuesta para el jurado sobre dos decisiones del rediseño. Las respuestas de fondo
(las que se dicen en voz alta) las escribe Isabella en `preguntas-rediseno.md`; esto es el dato
técnico que las respalda.

## Las caras del check-in no llevan ningún dato de la persona

- **Qué se pide a internet:** cada una de las cinco caras es una imagen de DiceBear 10.x
  (`api.dicebear.com/10.x/gaze/svg` o `.../moods/svg`). El código está en `caras-checkin.js`.
- **Qué lleva la dirección:** solo el ajuste del dibujo (la variante de los ojos y de la boca, el color y
  si se anima). La semilla es **fija** para todas las personas (`seed=lumea-animo`): no es el nombre, ni el
  correo, ni un identificador. Hay una prueba que lo comprueba (`pruebas/test_caras_checkin.py`,
  `test_la_direccion_no_lleva_datos_de_la_persona`).
- **Lo que sí ve DiceBear:** como cualquier servidor al que se le pide una imagen, ve la dirección IP del
  navegador y que se pidió una cara. No sabe quién es la persona, ni qué estado de ánimo eligió: las cinco
  caras se piden siempre, elija lo que elija.
- **El ánimo que la persona guarda** va solo al backend de Lumea (`POST /estado-animo`), nunca a DiceBear.
- **Licencia:** los dos estilos son CC0 (dominio público). Está en el README, en «Créditos».
- **Sin internet:** la imagen se quita y queda la palabra («Muy mal» … «Muy bien»); el botón funciona igual.
  Depender de internet para las caras es una decisión aceptada por Isabella (7 de octubre de 2026).

## Límite conocido: la paleta y el set de caras se guardan en el navegador, no en la cuenta

- **Qué significa:** la paleta, el modo (claro / oscuro) y el set de caras se guardan en `localStorage`
  (`lumea-paleta`, `lumea-modo` y `lumea-caras`). Pertenecen al navegador, no a la persona.
- **Consecuencias:**
  - Si la persona entra desde otro dispositivo u otro navegador, vuelve a ver el estado neutro y la tarjeta
    «Elige tus colores y tus caras».
  - Si dos personas comparten un navegador, comparten la elección.
  - Si borra los datos del navegador, la pierde.
- **Por qué se aceptó:** el backend no se toca en esta misión y la elección es estética, no sensible.
  Guardarla en la cuenta (un campo más en el perfil) es el siguiente paso natural si se quiere que viaje.
- **Dónde está el código:** `tema.js` (paleta y modo) y `caras-checkin.js` (set de caras); los dos leen y
  escriben con `try/catch`, así que un navegador que bloquea el almacenamiento no rompe la app.
