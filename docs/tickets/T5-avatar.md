# T5 · Avatar y misiones

**Para:** Claude Code · **Necesita de Isabella:** `bosquejos/isabella/avatar.png` · **Worktree:** `claude --worktree t5-avatar`

## Objetivo
`avatar.html`: ver el avatar con el ánimo de hoy, equipar y quitar lo desbloqueado, y ver las misiones.

## Datos (funciones de `api.js`)
`obtenerAvatar`, `elegirBaseAvatar`, `equiparObjeto(email, tipo, itemId)` con `tipo` = `ropa` o `accesorio`, y `quitarObjeto`. Si `imagen_lista` es `false`, el respaldo es DiceBear (`obtenerAvataresDiceBear`, `elegirAvatarDiceBear`). Objetos y nivel: buzo_verde 1, gafas 2, camiseta_lumea 3, audifonos 4, ruana 6, sombrero_vueltiao 8.

## Hacer
1. Lo bloqueado dice "Se abre en el nivel N", con `aria-disabled="true"` y sin acción.
2. Color: el avatar y el ánimo usan emocion (guayaba); las misiones, mision (mora).
3. Navegación privada con `aria-current="page"` en Avatar.

## Listo cuando
Equipar y quitar funcionan con el backend; todo se usa con teclado; 5 paletas × claro/oscuro; T1 pasa si ya existe.
