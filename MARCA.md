# Marca de Lumea

Este archivo lo leen las skills de diseño antes de proponer cualquier cosa.
Si cambias algo aquí, cambia la dirección de todo el diseño.

## Qué debe sentir un estudiante al abrir Lumea

**Las tres palabras:** Innovador, Divertido, Fluido.
**La frase de tres letras:** "Wow".
**También:** Interesante, Acogedor, Seguro, Impactante, Atractivo.

## Qué estilo buscamos

Moderno, juguetón (playful), no sobrecargado, pero llamativo.

Cómo se traduce (ver `docs/investigacion-paletas.md`):
- El "Wow" sale de **momentos**, no de pantallas enteras: colores muy saturados en áreas pequeñas (un logro, una calcomanía) sobre superficies tranquilas. La saturación es lo que más activa (Wilms y Oberfeld, 2018); un color pequeño gusta más cuanto más contrasta con su fondo (Schloss y Palmer, 2011).
- "Acogedor" y "Seguro": superficies claras y teñidas, nunca gris puro (el gris se asocia con tristeza en 30 países; Jonauskaite et al., 2020). Nada de rojo sobre la comida.
- "Fluido": transiciones cortas (120–420 ms), un solo movimiento automático por pantalla, todo respeta `prefers-reduced-motion`.

## Qué NO debe parecer nunca

- Una app de dieta o de prohibición. Ningún color funciona como veredicto sobre un alimento (halo verde: Schuldt, 2013).
- Una app infantil. Los adolescentes rechazan que los traten como niños y prefieren colores "con clase" (Nielsen Norman Group, 2005).
- Una app "de niñas" o "de niños". Las paletas llevan nombres de paisajes y patrimonio, nunca de género; la paleta nunca se elige según el género (Weisgram et al., 2014).
- Algo hecho por IA: degradados de adorno, tarjetas idénticas con la misma sombra, emojis como íconos, etiquetas en MAYÚSCULAS, flechas en cada botón.

## Referencias de ambiente

Airbnb, Spotify, Raycast, Duolingo y la fluidez de macOS. Las referencias de color que eligió Isabella (tarjetas de color pastel saturado, fondo crema, formas tipo calcomanía, verde–amarillo–naranja). Y la plaza de mercado de Pasto.

## La gramática de color (no cambia entre paletas)

| Rol | Fruta | Ícono | Significado |
|---|---|---|---|
| comida | aguacate | hoja | lo que comes, la marca, los botones |
| logro | maracuyá | estrella / llama | XP, racha, nivel |
| emocion | guayaba | cara | ánimo y avatar |
| mision | mora | bandera | retos |
| duda | mango | signo de pregunta | la IA no está segura y pide ayuda |
| sello | negro | octágono | advertencia legal (Res. 810 de 2021) |

## Las cinco paletas (nombres de trabajo)

Laguna Verde, Neblina, Carnaval, Colibrí y Cosecha. Cada una con modo claro y oscuro. **Aprobadas el 4 de octubre de 2026.**
**Ninguna es predeterminada** (decisión de Isabella, 7 de octubre de 2026): cada persona elige la suya, igual que el set de caras del check-in. Mientras no elige, Lumea se ve en un **estado neutro**: superficies casi blancas y texto sin tono (croma ≤ 0,006), con los mismos colores de rol de siempre y el botón principal en aguacate. El estado neutro no se puede elegir: no aparece en el selector.
Los valores salen de `herramientas/generar_paletas.py`, que mide contraste y daltonismo.

Colibrí reemplazó a Mopa-mopa y Cosecha a Potrerillo: usar el nombre del barniz de Pasto (patrimonio en salvaguardia urgente, UNESCO 2020) exigía el acuerdo de sus maestros, y una plaza concreta ataba la paleta a un lugar. Los nombres nuevos vienen de criaturas y cosechas, como pide la fraternidad con las criaturas del Cántico de Francisco de Asís.

**Pendiente:** votar los nombres con estudiantes y familias.
