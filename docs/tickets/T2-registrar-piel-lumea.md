# T2 · Registrar comida con el lenguaje visual de Lumea

**Para:** Claude Code · **Necesita de Isabella:** `bosquejos/isabella/registrar.png` · **Worktree:** `claude --worktree t2-registrar`

## Objetivo
`alimentos.html` es la escena principal del video. Hoy usa el diseño de Sara con el puente de estilos. Este ticket la rehace con `componentes.css` siguiendo el bosquejo de Isabella. `ejemplo-camara.html` es la referencia de componentes, no el diseño final.

## Hacer
1. Conserva TODOS los id del contrato de `lumea-camara.js` (lista en su encabezado), la navegación privada y `aria-current` en Registrar.
2. Carga `tema.js`, `tokens.css`, `paletas.css` y `componentes.css`. Sin Bootstrap, sin `style.css`, sin puente.
3. Cuatro estados: sin sesión (tarjeta); analizando (`.esqueleto`, la foto quieta en el visor); IA segura (`.etiqueta`, sellos, chips de logro); IA duda (`.etiqueta--duda` con `.opciones` agrupadas).
4. Si `lumea-camara.js` necesita cambiar (por ejemplo, la clase de los botones de opción), que sea el cambio mínimo y sin romper el contrato.
5. Calorías: sigue la decisión de Isabella en el plan. Si no la hay, pregunta antes de mostrarlas.

## No hacer
Nada que no esté en el bosquejo. No tocar el backend. El diseño de Sara queda en git: `git show camara-sara:alimentos.html`.

## Listo cuando
IA segura e IA duda funcionan con el backend real; los 4 estados se ven bien en 5 paletas × claro/oscuro; axe no reporta problemas de contraste; T1 pasa si ya existe.
