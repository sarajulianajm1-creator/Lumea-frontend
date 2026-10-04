---
name: lumea-prompts-diseno
description: Convierte especificaciones de Lumea en prompts listos para herramientas de diseño (Figma Make, Google Stitch, Relume, Visily), con la marca, las interacciones y el comportamiento en celular, tableta y computador. Úsala cuando quieras generar pantallas de Lumea en una herramienta de diseño.
---

# Prompts de diseño para Lumea

Actúa como especialista en traducir especificaciones técnicas en prompts efectivos para herramientas de diseño. El objetivo es que la herramienta genere un **punto de partida** que Isabella luego edita a mano en Figma; no un diseño final.

## Antes de escribir
1. Lee `estilos/tokens.css` (colores, fuente, radios, movimiento) y `MARCA.md` si existe.
2. Si hay una especificación (de las skills lumea-mapa-interacciones o lumea-sistema-diseno, o pegada en el mensaje), úsala. Si no, pregunta qué pantalla y para qué herramienta.
3. Pregunta para qué herramienta es si no lo dicen: Figma Make, Google Stitch, Relume (sitios de marketing), Visily, u otra. Ajusta el tono y el largo a esa herramienta.

## Las 5 pantallas por defecto
1. **Página de bienvenida** (`index.html`, la que ve alguien que no ha entrado): aquí sí aplican héroe, sección de funciones, llamado a la acción y pie de página.
2. **Registrar comida**: visor de cámara + etiqueta de plaza con el resultado.
3. **Inicio del estudiante**: saludo, tarjetas de color (registros, racha, ánimo, misión), acceso rápido a la cámara.
4. **Progreso**: nivel y XP, racha, gráfica semanal, misiones, ánimo de la semana.
5. **Crear cuenta**: formulario en pasos con progreso.

Solo la página de bienvenida usa la estructura de sitio de marketing. Las otras 4 son pantallas de app: no les pongas héroe ni pie de página.

## Cada prompt debe
1. Empezar por el resultado final ("Una pantalla de app web que…").
2. Incluir la marca: paleta con los hex de los semánticos y qué significa cada color, la fuente Bricolage Grotesque, el ambiente (plaza de mercado colombiana, fresco, juvenil, sin parecer app de dieta).
3. Nombrar las interacciones concretas: qué pasa al pasar el mouse, al hacer clic, al cargar, al confirmar, qué se anima y cuánto dura (usa los valores de `--m-rapido`, `--m-base`, `--m-lento`).
4. Definir el comportamiento en celular (hasta 720 px), tableta (721–1024) y computador (desde 1025).
5. Nombrar las secciones exactas en orden.
6. Terminar con una línea de **"Evitar:"** (degradados morados, tarjetas idénticas con la misma sombra, emojis como íconos, etiquetas en mayúsculas, ilustraciones genéricas de personas, comida chatarra como villana).
7. Usar contenido real de Lumea (alimentos colombianos, sellos de la Res. 810, XP, misiones), nunca lorem ipsum.

## Estructura base (adaptada)
> "Crea una [pantalla de app web / página de bienvenida] con un ambiente [ambiente]. Color principal: [hex y uso]. Acentos: [hex = significado]. Tipografía: Bricolage Grotesque. Secciones: 1) [sección con elementos concretos], 2) [sección con interacciones], 3) [acción principal y su estilo]. Adaptable: [celular], [tableta], [computador]. Transiciones: [tipo y duración]. Evitar: […]."

## Entrega
- Cada prompt en un bloque de código, en **español** y debajo la versión en **inglés** (muchas herramientas responden mejor en inglés).
- Después de los prompts, una lista corta de qué revisar a mano cuando la herramienta devuelva el diseño (contraste, que los colores signifiquen lo que deben, que el texto sea de Lumea, que no haya decoración sin propósito).
- En Claude Code, guarda los prompts en `docs/prompts-diseno.md`.
