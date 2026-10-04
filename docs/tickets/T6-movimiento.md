# T6 · Movimiento entre pantallas

**Para:** Claude Code · **Necesita de Isabella:** `docs/tickets/movimiento-isabella.md`, escrito por ella, con las 3 transiciones que quiere · **Worktree:** `claude --worktree t6-movimiento`

## Objetivo
Que Lumea se sienta Fluida, con pocas transiciones bien elegidas.

## Base
`componentes.css` ya tiene `@view-transition { navigation: auto; }`. Usa `view-transition-name` para lo que debe quedarse quieto entre pantallas (la barra de navegación, el avatar).

## Reglas
Cada transición dura 420 ms o menos; un movimiento automático por pantalla; los botones responden al toque en menos de 100 ms (estado `:active` con `var(--m-rapido)`); con `prefers-reduced-motion` no se mueve nada. En navegadores sin soporte, la página cambia normal.

## Listo cuando
Las 3 transiciones de la lista de Isabella funcionan en Chrome y Safari, y nada más se mueve.
