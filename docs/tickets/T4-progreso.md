# T4 · Pantalla de Progreso

**Para:** Claude Code · **Necesita de Isabella:** `bosquejos/isabella/progreso.png` · **Worktree:** `claude --worktree t4-progreso`

## Objetivo
`progreso.html` con datos reales de `GET /progreso` (función `obtenerProgreso` de `api.js`).

## Datos
`nivel`, `xp_total`, `xp_inicio_nivel`, `xp_siguiente_nivel` (es `null` en el nivel máximo), `xp_faltante_siguiente_nivel`, `racha_actual`, `racha_maxima`, `meta_diaria` (`xp_hoy`, `meta`, `cumplida`), `misiones`, `mensaje_regreso` y `reglas.niveles`.

## Hacer
1. Barra de nivel con `.barra-xp`: avance = (`xp_total` − `xp_inicio_nivel`) / (`xp_siguiente_nivel` − `xp_inicio_nivel`).
2. Corrige dos errores que hoy se ven en `index-ingresado.html`: el plural ("1 día", no "1 días") y "20 de 15 XP hoy" (cuando pasa la meta, di que se cumplió y cuánto XP lleva).
3. `mensaje_regreso` se muestra como bienvenida, nunca como reproche.
4. Misiones con `.tarjeta--mision` y `.chip--mision`; XP y racha con `.chip--logro`.
5. Navegación privada con `aria-current="page"` en Progreso.

## Listo cuando
Funciona con el backend real y con tres casos simulados: sin racha, nivel máximo y meta cumplida; 5 paletas × claro/oscuro; T1 pasa si ya existe.
