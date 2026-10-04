---
name: lumea-bitacora-ia
description: Lleva la bitácora de uso de IA del proyecto Lumea (docs/bitacora-ia.md), vigila el acuerdo 70 % humano / 30 % IA y redacta la declaración de uso ético de IA para el video y la sustentación. Úsala al cerrar cada sesión o cuando pregunten cuánto hizo la IA.
---

# Bitácora de uso de IA de Lumea

El equipo de Lumea se comprometió a que el trabajo sea 70 % humano y 30 % IA, y el concurso evalúa el uso ético de las TIC. Esta skill deja evidencia honesta de quién hizo qué.

## Al cerrar una sesión de trabajo
Agrega una fila a la tabla de `docs/bitacora-ia.md` (créalo si no existe; si no tienes acceso al repo, entrégale la fila a Isabella para que la pegue):

| Fecha | Tarea | Lo que hizo Isabella (o el equipo) | Lo que hizo la IA | Evidencia | Humano / IA |

- **Lo que hizo Isabella:** decisiones, diseños, código que escribió, pruebas que corrió. **Nunca lo inventes:** si no lo sabes, pregúntale.
- **Lo que hizo la IA:** qué herramienta (Claude en claude.ai, Claude Code, otras) y qué produjo.
- **Evidencia:** commits, archivos, docs.
- **Humano / IA:** una estimación honesta. Criterio: separa *decidir* de *producir*. Quien decidió qué se hace y por qué cuenta como autor de la decisión; quien escribió el archivo cuenta como autor de la producción. No infles la parte humana para que el número se vea bien.

## Vigilar el 70/30
Lleva la cuenta por área: investigación, diseño visual, código del frontend, código del backend, textos. Si en un área la IA supera el 30 % acumulado, dilo claramente y propone cómo equilibrar: que Isabella escriba la siguiente pieza, que comente y explique el código que hizo la IA, o que rehaga una parte.

## Declaración para el video y la sustentación
Cuando la pidan, redacta un texto corto en primera persona del equipo que diga:
1. Qué herramientas de IA se usaron y para qué.
2. Qué fue humano: decisiones, diseño, escritura, pruebas.
3. Cómo se verificó lo que hizo la IA (pruebas, mediciones, revisión con fuentes).
4. Qué aprendieron a hacer por su cuenta.

Debe ser verificable con la bitácora. Nada de "la IA solo ayudó un poquito" si la bitácora dice otra cosa.

## Commits
Los commits que la IA hace en nombre de Isabella llevan la línea `Co-Authored-By` de la IA, para que el historial de git también diga la verdad.
