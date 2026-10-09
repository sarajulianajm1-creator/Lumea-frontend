# Lumea - reglas para Claude Code -

Lumea es una app web que promueve hábitos de alimentación saludable en adolescentes: la IA reconoce la comida en una foto y la gamificación celebra lo que la persona hace, sin prohibir nada. Concurso Fedesoft 2026; el video se entrega el 9 de octubre.

## El trato (no se negocia)

- Al menos 60 % del trabajo es humano. Isabella decide el diseño, los textos y qué entra al video. Tú ejecutas los tickets de `docs/tickets/`.
- Sin bosquejo no hay diseño. Si algo no está en el bosquejo o en el ticket, pregunta antes de decidirlo.
- Commits pequeños, uno por idea, en español, con la línea `Co-Authored-By: Claude …` (la cuenta `herramientas/balance_ia.py`).
- Al terminar: explica cada cambio en una frase y propón una fila para `docs/bitacora-ia.md`. Isabella la confirma.

## No tocar

- `inicio.html` y `estilos/inicio.css`: los escribe Isabella.
- `style.css`: es el diseño de Sara. Se adapta solo desde `estilos/puente-sara.css`.
- `estilos/paletas.css` y `estilos/tokens.json`: los genera `herramientas/generar_paletas.py`. Si hay que cambiarlos, se cambia el script.
- `.env` y `fotos_prueba/` (fotos de menores): nunca entran al repositorio.

## Sistema de diseño

- Lee `MARCA.md` antes de proponer algo visual.
- Color: solo tokens `--c-*` de `paletas.css`. Gramática fija: comida = aguacate, logro = maracuyá (XP, nivel, racha), emocion = guayaba (ánimo, avatar), mision = mora, duda = mango (la IA no está segura), sello = negro (advertencia legal). Maracuyá y mango nunca van como texto: para texto usa `--c-ROL-tinta`.
- Tamaños, espacios, radios y movimiento: `tokens.css` (`--t-*`, `--e-*`, `--r-*`, `--m-*`). Ningún valor a mano.
- Componentes en `estilos/componentes.css`, con nombres BEM. Fuente única: Bricolage Grotesque, local.
- Movimiento: 420 ms como máximo, un solo movimiento automático por pantalla, y nada se mueve con `prefers-reduced-motion`.
- Nunca: degradados de adorno, emojis como íconos, etiquetas en MAYÚSCULAS, una flecha en cada botón.
- Todo funciona en las 5 paletas y en claro y oscuro (`tema.js`, `data-paleta`, `data-modo`).

## Código

- Texto que llega del servidor: siempre `textContent`, nunca `innerHTML`.
- `api.js` es el único lugar con la dirección del backend. El contrato de ids de la cámara está en el encabezado de `lumea-camara.js`.
- HTML semántico: un `h1` por página, `aria-current="page"` en la navegación, foco visible, contraste WCAG AA (4.5:1 texto, 3:1 controles).
- Navegación privada: Inicio, Mis registros, Registrar (`alimentos.html`), Progreso, Avatar.
- Si existe `pruebas/`, corre `pytest pruebas` antes de terminar.

## Idioma

Español en nombres, comentarios, commits y textos de la app. Escribe comentarios que entienda una principiante.
