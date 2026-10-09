# Preguntas que un jurado podría hacerle a Isabella sobre el pulido final

Escritas por Claude Code (9 oct 2026). Cada pregunta dice en qué archivo está la respuesta y qué prueba la comprueba.
**Las respuestas las escribe Isabella, con sus palabras.**

1. **¿Por qué los rasgos (piel, peinado, ojos…) no se bloquean y la ropa sí?**
   Dónde: `avatar.js` («Cómo me veo» frente a «Mi armario»), `Backend/docs/CONTRATO_GAMIFICACION.md` («La persona»: «la identidad no es un premio»). Pruebas: `pruebas/test_avatar.py` (los rasgos nunca se bloquean; lo bloqueado del armario no se puede poner).
   Respuesta de Isabella:

2. **¿Por qué Lumea no le pide nada a DiceBear y dibuja a la persona y a los compañeros en el navegador?**
   Dónde: `persona.js`, `companero.js`, `vendor/dicebear/README.md` (licencias MIT y CC0), `docs/defensa/privacidad-y-limites-rediseno.md`. Pruebas: `pruebas/test_sin_dicebear.py` (ninguna página pide nada fuera de la máquina).
   Respuesta de Isabella:
