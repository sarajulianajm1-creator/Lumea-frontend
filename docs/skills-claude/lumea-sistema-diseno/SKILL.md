---
name: lumea-sistema-diseno
description: Amplía y documenta el sistema de diseño de Lumea (colores, tipografía, espacio, componentes, movimiento, accesibilidad) partiendo de estilos/tokens.css y de las 5 paletas generadas, y lo exporta como JSON para Figma, CSS y fichas de componentes. Úsala para cualquier decisión visual de Lumea.
---

# Sistema de diseño de Lumea

Actúa como arquitecta/o de sistemas de diseño. **No empiezas de cero**: Lumea ya tiene un sistema en `estilos/tokens.css` y `estilos/componentes.css`, con una página de referencia viva en `sistema-diseno.html`. Lees eso primero y lo amplías (si no tienes los archivos, pídeselos a Isabella). Si algo del sistema actual te parece mal, lo dices y propones el cambio; no lo reemplazas en silencio.

## Personalidad de marca
Lee `MARCA.md` en la raíz del repo. Si no existe, haz estas 3 preguntas antes de seguir y guarda las respuestas en `MARCA.md`:
1. ¿Qué tres palabras quieres que sienta un estudiante al abrir Lumea?
2. ¿Qué NO debe parecer nunca? (ej. app de dieta, app de hospital, juego infantil)
3. ¿Qué app o lugar real se parece al ambiente que buscas?

Lo que ya está decidido (ver `docs/investigacion-paletas.md`):
- Concepto **plaza de mercado de Nariño**. Gramática fija en todas las paletas: comida = aguacate (hoja), logro = maracuyá (estrella), emoción = guayaba (cara), misión = mora (bandera), duda = mango (signo de pregunta; "la IA no está segura"). Cada significado va SIEMPRE con color + ícono + texto (WCAG 1.4.1).
- **5 paletas × 2 modos**: Laguna Verde (predeterminada), Neblina (pastel), Carnaval (fuerte), Mopa-mopa (viva, de joya), Potrerillo (cálida, de mercado). Ninguna es "la normal". Nombres de trabajo: se validan con estudiantes y familias; Mopa-mopa requiere acuerdo y créditos de un taller de barniz de Pasto.
- Los colores NO se escriben a mano: salen de `herramientas/generar_paletas.py`, que genera `estilos/paletas.css` y `estilos/tokens.json` y valida contraste WCAG y daltonismo (Machado et al., 2009). Para cambiar un color, cambia los parámetros del script y vuelve a correrlo; si falla, no se publica.
- Escalones de luz fijos (OKLCH L) en claro: mora 0.44 < aguacate 0.54 < guayaba 0.67 < mango 0.79 < maracuyá 0.91. Bandas de tono: aguacate 130–155°, maracuyá 86–100°, mango 52–65°, guayaba 345–10° (nunca 20–40°, es el rojo), mora 300–325°.
- Cada rol tiene 4 papeles: `--c-ROL` (relleno), `--c-sobre-ROL`, `--c-ROL-tinta`, `--c-ROL-suave` y `--c-ROL-contenedor`. Maracuyá y mango nunca como texto sobre claro (se vuelven café/oliva, el color menos querido); su tinta es la tinta neutra.
- Dos ejes en `<html>`: `data-paleta` y `data-modo` (sin atributo = sigue al sistema). `tema.js` en el `<head>` evita el destello del tema equivocado.
- Tipografía: Bricolage Grotesque, archivo local en `estilos/fuentes/`.
- Sellos de advertencia: negros y octagonales por la Resolución 810 de 2021; en modo oscuro llevan placa clara (`--c-sello-placa`).
- Mitos que no se afirman nunca (lista en el informe): "el rojo abre el apetito", "el azul calma", "el modo oscuro cuida los ojos", "60-30-10 es la proporción áurea".

## Qué producir (ajustado a Lumea)

1. **Color**: ya resuelto por el generador. Si te piden un cambio, edita los parámetros de `PALETAS` en `herramientas/generar_paletas.py`, córrelo y muestra la tabla de `docs/validacion-paletas.md`. El modo oscuro NO es invertir: cada paleta tiene su oscuro como par.
2. **Tipografía en 9 niveles**: amplía la escala actual 1,25 (hoy xs–3xl, 7 niveles) a 9 sin romper los existentes. Para cada nivel: tamaño, peso, interlineado, uso.
3. **Espacio**: retícula de 8 px con medios pasos de 4 px (ya existe `--e-1` a `--e-8`). Explica cuándo se usa 4.
4. **Componentes**: solo los que Lumea usa o va a usar esta versión (máximo unos 20; no inventes 30 para llenar). Lista base: botón (primario, secundario, fantasma, grande), campo, selector de ánimo, chip, tarjeta, tarjeta de color, panel, etiqueta de plaza (resultado de la foto, con variante de duda), opciones top-3, sello, barra de XP, calcomanía de logro, menú lateral/barra inferior, esqueleto de carga, aviso de error, estado vacío, diálogo de confirmación, avatar.
   Para cada uno, **todos los estados**: normal, encima (hover), presionado, foco de teclado, deshabilitado, cargando, error y, si aplica, seleccionado.
5. **Diseño adaptable**: celular hasta 720 px, tableta 721–1024 px, computador desde 1025 px. Qué cambia en cada uno (menú, columnas, tamaños).
6. **Movimiento**: usa los tokens `--m-*`. Solo se anima `transform` y `opacity`. Un solo momento automático por pantalla. Todo respeta `prefers-reduced-motion`.
7. **Accesibilidad WCAG 2.1 AA**: calcula el contraste con un script (fórmula de luminancia relativa de WCAG). **Nunca lo estimes a ojo.** Muestra la tabla de pares texto/fondo con su número. Objetivo de toque mínimo 44 px. Foco siempre visible.

## Formatos de salida
- `estilos/tokens.json` en formato **W3C Design Tokens (DTCG)**, lo escribe el generador: `color.<paleta>.<modo>.<rol>` (ej. `color.neblina.oscuro.logro`). En Figma se importa como una colección de Variables con 10 modos (5 paletas × claro/oscuro), con el conector de Figma y la skill figma-generate-library, o con un plugin como Tokens Studio.
- `estilos/tokens.css` (lo que no es color) y `estilos/componentes.css` actualizados, con los mismos nombres que el JSON.
- `docs/componentes.md`: una ficha por componente (propósito, anatomía, variantes, estados, tokens que usa, qué NO hacer), escrita para copiar en la descripción del componente en Figma.
- Actualiza `sistema-diseno.html` para que muestre lo nuevo.

## Para que no parezca hecho por IA
Evita: un solo radio para todo, la misma sombra gris debajo de cada tarjeta, degradados de adorno, etiquetas en MAYÚSCULAS sobre cada título, emojis como íconos, numeración 01/02/03 que no sea una secuencia real, flechas "→" en cada botón, fuente monoespaciada para datos pequeños, todo centrado. Cada decoración debe significar algo de Lumea.

## Modo aprendizaje
Si Isabella dice "enséñame": explica la decisión con el porqué (con fuente cuando exista: WCAG, Material, Apple HIG, artículos de color OKLCH), propón y deja que ella escriba el cambio; luego revísalo.
