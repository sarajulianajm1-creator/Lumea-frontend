# T3 · Celebración de XP, misión, nivel y meta

**Para:** Claude Code · **Necesita de Isabella:** `bosquejos/isabella/celebracion.png` con cuatro respuestas: dónde aparece, qué se mueve, cuánto dura y qué dice · **Worktree:** `claude --worktree t3-celebracion`

## Objetivo
Que registrar una comida o contar cómo llegas se sienta como un logro, sin convertir la comida en un juicio.

## Hacer
1. `celebracion.js`, sin diseño (como `lumea-camara.js`), que expone `window.LumeaCelebrar(gamificacion)` con los campos `xp_ganado`, `misiones_cumplidas`, `subio_de_nivel`, `nivel` y `meta_diaria.recien_cumplida`.
2. `estilos/celebracion.css` solo con tokens. Color: logro = maracuyá.
3. `lumea-camara.js` la llama después de `mostrar()`, solo si existe.
4. Texto con `textContent` y anunciado con `aria-live="polite"`.

## Reglas
Un movimiento por evento. Dura `var(--m-lento)` (420 ms) o menos; el rebote `var(--m-resorte)` solo para logros. Con `prefers-reduced-motion`, aparece sin moverse. Sin confeti de emojis. Nunca dice nada sobre si la comida es buena o mala.

## Listo cuando
Los cuatro eventos se ven con respuestas simuladas, se pueden cerrar con teclado y funcionan en 5 paletas × claro/oscuro.
