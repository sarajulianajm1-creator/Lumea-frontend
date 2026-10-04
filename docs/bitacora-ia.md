# Bitácora de uso de IA

Acuerdo del equipo: 70 % trabajo humano, 30 % IA. Esta tabla es la evidencia para el criterio de uso ético de las TIC.

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

**Balance honesto al 4 de octubre:** en decisiones de diseño la autoría es de Isabella; en código del frontend la IA supera el 30 %. Las pantallas que se diseñan y codifican entre el 5 y el 9 de octubre tienen que invertir esa proporción.
