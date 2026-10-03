---
name: lumea-sistema-diseno
description: Amplía y documenta el sistema de diseño de Lumea (colores, tipografía, espacio, componentes, movimiento, accesibilidad) partiendo de estilos/tokens.css, y lo exporta como JSON para Figma, CSS y fichas de componentes. Úsala para cualquier decisión visual de Lumea.
---

# Sistema de diseño de Lumea

Actúa como arquitecta/o de sistemas de diseño. **No empiezas de cero**: Lumea ya tiene un sistema en `estilos/tokens.css` y `estilos/componentes.css`, con una página de referencia viva en `sistema-diseno.html`. Lees eso primero y lo amplías. Si algo del sistema actual te parece mal, lo dices y propones el cambio; no lo reemplazas en silencio.

## Personalidad de marca
Lee `MARCA.md` en la raíz del repo. Si no existe, haz estas 3 preguntas antes de seguir y guarda las respuestas en `MARCA.md`:
1. ¿Qué tres palabras quieres que sienta un estudiante al abrir Lumea?
2. ¿Qué NO debe parecer nunca? (ej. app de dieta, app de hospital, juego infantil)
3. ¿Qué app o lugar real se parece al ambiente que buscas?

Lo que ya está decidido:
- Concepto **plaza de mercado colombiana**. Cinco frutas, cada una con un solo significado: aguacate = marca y comida, maracuyá = logros, guayaba = emociones, mora = misiones, mango = atención (la IA no está segura).
- Cada fruta tiene una rampa de 10 tonos (50–900) calculada en OKLCH. Dos capas de tokens: **primitivos** (`--aguacate-500`) y **semánticos** (`--c-logro`). Las pantallas usan solo semánticos.
- Tipografía: Bricolage Grotesque, archivo local en `estilos/fuentes/` (funciona sin internet). Si propones una segunda familia, justifica qué hace que la primera no pueda hacer.
- Sellos de advertencia: negros y octagonales por la Resolución 810 de 2021. Esto no se rediseña.

## Qué producir (ajustado a Lumea)

1. **Color**: primitivos + semánticos + **modo oscuro** (los semánticos redefinidos dentro de `@media (prefers-color-scheme: dark)` y `[data-tema="oscuro"]`; el modo oscuro NO es invertir: baja la saturación de los rellenos y sube la claridad del texto).
2. **Tipografía en 9 niveles**: amplía la escala actual 1,25 (hoy xs–3xl, 7 niveles) a 9 sin romper los existentes. Para cada nivel: tamaño, peso, interlineado, uso.
3. **Espacio**: retícula de 8 px con medios pasos de 4 px (ya existe `--e-1` a `--e-8`). Explica cuándo se usa 4.
4. **Componentes**: solo los que Lumea usa o va a usar esta versión (máximo unos 20; no inventes 30 para llenar). Lista base: botón (primario, secundario, fantasma, grande), campo, selector de ánimo, chip, tarjeta, tarjeta de color, panel, etiqueta de plaza (resultado de la foto, con variante de duda), opciones top-3, sello, barra de XP, calcomanía de logro, menú lateral/barra inferior, esqueleto de carga, aviso de error, estado vacío, diálogo de confirmación, avatar.
   Para cada uno, **todos los estados**: normal, encima (hover), presionado, foco de teclado, deshabilitado, cargando, error y, si aplica, seleccionado.
5. **Diseño adaptable**: celular hasta 720 px, tableta 721–1024 px, computador desde 1025 px. Qué cambia en cada uno (menú, columnas, tamaños).
6. **Movimiento**: usa los tokens `--m-*`. Solo se anima `transform` y `opacity`. Un solo momento automático por pantalla. Todo respeta `prefers-reduced-motion`.
7. **Accesibilidad WCAG 2.1 AA**: calcula el contraste con un script (fórmula de luminancia relativa de WCAG). **Nunca lo estimes a ojo.** Muestra la tabla de pares texto/fondo con su número. Objetivo de toque mínimo 44 px. Foco siempre visible.

## Formatos de salida
- `estilos/tokens.json` en formato **W3C Design Tokens (DTCG)**: `{ "color": { "aguacate": { "500": { "$type": "color", "$value": "#7FB03F" } } } }`. Los semánticos referencian primitivos con `"{color.aguacate.800}"`. Este archivo se importa a Variables de Figma (con el conector de Figma y la skill figma-generate-library, o con un plugin como Tokens Studio).
- `estilos/tokens.css` y `estilos/componentes.css` actualizados (mismos nombres que el JSON).
- `docs/componentes.md`: una ficha por componente (propósito, anatomía, variantes, estados, tokens que usa, qué NO hacer), escrita para copiar en la descripción del componente en Figma.
- Actualiza `sistema-diseno.html` para que muestre lo nuevo.

## Para que no parezca hecho por IA
Evita: un solo radio para todo, la misma sombra gris debajo de cada tarjeta, degradados de adorno, etiquetas en MAYÚSCULAS sobre cada título, emojis como íconos, numeración 01/02/03 que no sea una secuencia real, flechas "→" en cada botón, fuente monoespaciada para datos pequeños, todo centrado. Cada decoración debe significar algo de Lumea.

## Modo aprendizaje
Si Isabella dice "enséñame": explica la decisión con el porqué (con fuente cuando exista: WCAG, Material, Apple HIG, artículos de color OKLCH), propón y deja que ella escriba el cambio; luego revísalo.
