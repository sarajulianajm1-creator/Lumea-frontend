# Bitácora de uso de IA

Acuerdo del equipo (actualizado el 4 de octubre): al menos 60 % trabajo humano y como máximo 40 % IA. Esta tabla es la evidencia para el criterio de uso ético de las TIC.

Las primeras filas se reconstruyeron el 4 de octubre de 2026 a partir de la conversación con la IA. **Isabella: revísalas y corrige lo que no sea exacto**, sobre todo la columna de lo que hiciste tú, porque la IA no ve todo tu trabajo.

| Fecha | Tarea | Lo que hizo Isabella (o el equipo) | Lo que hizo la IA (Claude) | Evidencia | Humano / IA |
|---|---|---|---|---|---|
| 1–2 oct | Feria escolar: póster y demo de la cámara | Definió el propósito real del proyecto (hábitos, no prohibición) y corrigió el planteamiento del problema; presentó en la feria | Borradores de textos del póster, página de demo de cámara, diagnóstico de los modelos (regla en cascada) | Rama `feria-2026-10-02`, tag `v-feria` | por estimar |
| 3 oct | Reorganización del backend | Decidió reorganizar y conservar las etapas; ejecutó git y las pruebas (31/31 con MySQL) | Script de reorganización, cambios de rutas, documentación en la defensa técnica | Rama `reorganizacion-carpetas` | por estimar |
| 3 oct | Sistema de diseño, primera versión | Rechazó el diseño de la IA, pidió una paleta más viva, ajustó el fondo a `#F3F3E1` a mano | Tokens, componentes, página de referencia | Commits `66efea9`, `6839cd6`, `069deee` | Decisiones: humano. Código: sobre todo IA |
| 3–4 oct | Cinco paletas con modo oscuro | Dio las palabras de marca y los criterios (psicología del color, estereotipos, base filosófica); aprobó y cambió los nombres | Investigación con fuentes, generador y validación de contraste y daltonismo | `docs/investigacion-paletas.md`, `herramientas/generar_paletas.py`, tag `paletas-aprobadas` | Decisiones: humano. Código: IA |
| 4 oct | Plan de pantallas | Pendiente: elegir navegación y variantes, diseñar en Figma, dibujar el logo | Plan, bosquejos grises, estrategia para integrar el trabajo de Sara | Doc "Plan de pantallas de Lumea", carpeta `bosquejos/` | Plan: IA. Diseño: por hacer (humano) |
| 4 oct | Esqueleto de Inicio (lección 1) | Escribió `inicio.html` y `estilos/inicio.css`: estructura semántica, saludo neutro, avatar como enlace, `.gitignore`; decidió la navegación B | Explicó conceptos (cascada, variables, BEM, Elements) y revisó | Commit `6adef5b` | Humano |
| 4 oct | Navegación de las páginas de Sara | Decidió: la parte pública sin Registrar ni Mis registros; el menú privado con los cinco destinos | Editó 8 archivos de Sara (menús, botón de inicio, estilo de pestaña activa) | Commit `57e8651` | Decisión: humano. Edición: IA (revisar el diff) |
| 4 oct | Fusión de las dos páginas de cámara | Decidió que no podían existir dos páginas con la misma función | Fusionó `registrar-comida.html` en `alimentos.html` (aviso sin sesión, opciones agrupadas, logros, foto quieta al analizar) y la probó con respuestas simuladas | Commit `8c22482` | Decisión: humano. Código: IA (revisar el diff) |
| 4 oct | Piel de Lumea para las páginas de Sara | Pidió dos opciones comparables sin perder el trabajo de Sara | Puente de estilos, `?piel=sara` por pestaña, medición de contraste con axe-core | Commit `3ac2c6b` | Decisión: humano. Código: IA |
| 4 oct | Plan hasta el 9 de octubre y tickets para Claude Code | Pidió el plan, el reparto ético y trabajar en paralelo | Doc "Plan de trabajo de Lumea hasta el 9 de octubre", `CLAUDE.md` y 6 tickets en `docs/tickets/` | Commit de esta fila | Plan: IA. Decisiones abiertas: humano |
| 5 oct | Delegar la gamificación completa a Claude Code | Decidió delegarla por falta de tiempo; fijó como especificación los bosquejos 06, 10 y 11 (aprobados el 4 oct) y las reglas éticas; revisará cada fase | Escribió las dos misiones (frontend y backend) en el chat | `docs/tickets/MISION-gamificacion-100.md` y `MISION_GAMIFICACION_100.md` del backend | Decisión: humano. Código que salga de la misión: IA |

**Balance medido el 4 de octubre** (líneas añadidas por commit; un commit cuenta como IA si dice `Co-Authored-By: Claude`): en código escrito a mano (HTML, CSS, JS y Python, sin archivos que genera un script) la IA suma 3.301 de 9.995 líneas, **33 %**. Con los archivos generados, **51 %**. Ojo: algunos commits viejos sin esa línea pudieron tener ayuda de IA, así que el número real de IA puede ser mayor.

En decisiones de diseño la autoría es de Isabella. Lo que falta hasta el 9 de octubre (Inicio, bosquejos, top 3 en el backend, `balance_ia.py`, guion y pruebas con usuarios) tiene que inclinar la balanza hacia el trabajo humano.
