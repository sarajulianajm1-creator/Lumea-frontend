# Misión: «Camino del cuidado» en el frontend

**Para:** Claude Code, en el worktree `.claude/worktrees/rediseno` (rama `rediseno`). Es una sesión Local y la única en esta carpeta.

**Decisión de Isabella (8 de octubre de 2026).** Lumea se reorienta desde el Cántico de las criaturas de San Francisco de Asís sin cambiar su arquitectura.
- Isabella escribió los textos y los valores de la gamificación en el backend (`gamificacion_config.py`).
- Otra sesión pone el backend al día con su misión, `MISION_CAMINO_BACKEND.md`.
- Esta misión hace lo mismo en las pantallas.

**Entrega:** viernes 9 de octubre, 11:59 p. m. Esta misión debe quedar lista el jueves en la noche.

## Lo que decidió Isabella

- **Vocabulario.** Lo que se ve dice «semillas» en vez de XP y «etapa» en vez de nivel.
  - Las claves del contrato y las variables **no cambian**: `xp_total`, `nivel`, `xp_siguiente_nivel`, `nivel_requerido`… Cambia solo el texto en pantalla, incluidos los `aria-label`.
  - Plurales correctos: «1 semilla», «5 semillas», «Etapa 3».
- **Compañeros.** Los seis avatares (Sol, Luna, Río, Montaña, Orquídea, Colibrí) son ahora **compañeros** de DiceBear 10.x **gaze**.
  - Cada uno tiene su forma y su color fijos, se desbloquea en una etapa, y sus ojos muestran el ánimo.
  - El backend ya devuelve sus URL quietas: `avatar.urls_por_estado`, `GET /avatar` y los endpoints de `obtenerAvataresDiceBear` y `elegirAvatarDiceBear` en `api.js`.
- **Check-in.** El check-in de ánimo usa **las caras del compañero de cada persona**.
  - Sale el set de caras elegible del 7 de octubre (Miradas/Gestos, gaze/moods).
  - La paleta sigue siendo elegible y sin predeterminada.
- **Persona y compañero.** El avatar por capas (Figma de Laura) es la persona, con su armario, y el compañero la acompaña. Las imágenes de Laura llegan después: mientras `imagen_lista` sea falso, el compañero es la figura principal de Avatar.
- **Animación.**
  - Solo se anima lo que responde a una acción (la cara elegida en el check-in) y el compañero grande en Avatar. Para animarlos, a la URL quieta se le agrega `animationVariant=medium` o `slow`.
  - Nunca hay varias caras moviéndose a la vez.
  - La animación de gaze ya respeta `prefers-reduced-motion` dentro del SVG; compruébalo.

## Antes de empezar

- Isabella tenía `conocenos.html` e `index.html` sin guardar en este worktree. Si `git status` todavía los muestra, **para y pídele que haga su commit**. No los toques.
- Agrega este archivo con su propio commit.
- Lee `docs/tickets/ESTADO-rediseno.md` (incluida la sección «Para después de unir»), `formato.js`, `lumea-ui.js`, `lumea-state.js`, `caras-checkin.js`, `selector-colores.js`, `avatar.js`, `celebracion.js` y `api.js`.
- **Nunca** `git add -A` ni `git commit -a`. No hagas push.

## Fases (en este orden; K0.5 es la prioridad 1 de Isabella)

### K0 · Plan (modo plan)

Muestra un plan de una pantalla y espera la aprobación de Isabella. Incluye:
- la lista de textos que cambian;
- las pruebas que cambian;
- dónde vive el compañero en cada pantalla.

### K0.5 · Consejos en el resultado y páginas públicas (PRIORIDAD 1, va primero)

**Consejos.** El backend agrega `consejo` a `/predecir` y `/confirmar-alimento` (ver `MISION_CAMINO_BACKEND.md`, fase C0.5):

```json
{"grupo": "...", "aporta": "...", "para_completar": "...", "a_tener_en_cuenta": "...",
 "sellos": [{"sello": "sodio", "dato": "...", "idea": "..."}]}
```

En el resultado de Registrar, debajo del nombre, los sellos y las calorías, muestra como máximo cuatro bloques cortos, en este orden:
1. «Lo que aporta» (`aporta`).
2. «Para completar tu plato» (`para_completar`). Si no hay, «Una idea», con la `idea` del primer sello.
3. «A tener en cuenta» (`a_tener_en_cuenta`). Si no hay, el `dato` del primer sello.
4. «¿Sabías que…?» (`dato_curioso`), como hoy.

Además:
- Los bloques vacíos no se dibujan.
- Sin `consejo` (backend viejo), la pantalla queda como hoy.
- Los textos se escriben con `textContent`; ninguno lleva color de alerta ni íconos de advertencia.
- Los títulos de los bloques son textos nuevos: van a la lista de revisión de Isabella.
- Agrega respuestas simuladas con `consejo` para banano, gaseosa y bandeja paisa, y sus pruebas.

**Diseño de Registrar.** Isabella prefiere el diseño de `ejemplo-camara.html` («Registrar comida», «Lumea cree que es…»). Verifica que `alimentos.html` lo siga, y si algo se aparta, alinéalo con esa referencia.

**Páginas públicas.** A Isabella le gusta cómo las hizo Sara: el inicio con su fondo y el inicio de sesión.
- Quita `estilos/publico.css` del `<head>` de las seis páginas públicas.
- Vuelve a poner la marca de Sara en el encabezado mientras llega el logo de Isabella.
- No toques sus textos. Isabella tiene cambios en `conocenos.html` e `index.html`, y los guarda con su propio commit antes de que empieces.

### K1 · Semillas y etapas

**Dónde.** Todo el texto visible con «XP» o «nivel» pasa al vocabulario nuevo:
- Inicio: la meta («10 de 15 semillas hoy») y la franja de la etapa («Te faltan 35 semillas para la etapa 3»);
- Progreso, Avatar (misiones «+10 semillas»), la celebración («Llegaste a la etapa 4»), Ánimo y el resultado de Registrar;
- `formato.js`, que tiene los textos compartidos y los plurales.

**Qué no se toca.**
- Los nombres de las misiones y de las calcomanías vienen del backend: no los escribas a mano.
- `sistema-diseno.html` y `ejemplo-camara.html` son de referencia. Cámbialos solo si es trivial.

**Datos de prueba.** Pon al día las respuestas simuladas (`pruebas/respuestas/*.json`) con los textos y valores del commit de Isabella en el backend. Léelos de `~/Python_proyects/Lumea/Backend/gamificacion_config.py`, sin inventarlos.

### K2 · El compañero en Avatar

- **Elegir compañero.** Una sección «Tu compañero» con los seis compañeros quietos, su nombre y la etapa en que se desbloquean.
  - Los bloqueados llevan candado, «Etapa N» y `aria-disabled="true"`.
  - Se elige con `elegirAvatarDiceBear`.
  - Usa el patrón de opciones y el foco que ya existen en Avatar.
- **La figura grande.**
  - Si `imagen_lista` es verdadero, la persona por capas y el compañero a su lado, más pequeño.
  - Si no, el compañero grande, con la cara del ánimo de hoy y animado (`slow`).
- **La acción principal de Avatar** sigue siendo ponerte algo del armario.

### K3 · El check-in con el compañero

- Los cinco botones del check-in (Inicio y Ánimo) muestran las caras del compañero desde `avatar.urls_por_estado`, quietas. La cara elegida se anima (`medium`).
  - Sin internet, queda la palabra.
  - El nombre accesible es la palabra, la selección se marca con `aria-pressed` y la imagen lleva `alt=""`.
- Quita el grupo «Caras» de `selector-colores.js` y la clave `lumea-caras`. La tarjeta pasa a llamarse «Elige tus colores» y la sección de Avatar «Mis colores». Esos dos textos van a la lista de revisión de Isabella.
- `caras-checkin.js` se simplifica o se elimina. Explica en el commit lo que hiciste.
- `test_caras_checkin.py` y `test_selector_colores.py` pasan a probar esto, con la URL de gaze y sin datos personales en ella.

### K4 · La semana de ánimo y Progreso

Usan `[data-cara]` con `urls_por_estado`, así que ya muestran al compañero. Verifica que se vean quietas y bien, y que las capturas no tengan errores de contraste.

### K5 · Pruebas, capturas y cierre

- `pytest pruebas` en verde. Toda prueba que cambie queda en el ESTADO con su razón; nunca borres una para que pase.
- `pytest pruebas -m capturas` con 0 errores de contraste en las pantallas privadas.
- Una fila por fase en `docs/bitacora-ia.md`.
- **ESTADO:** una sección «Camino del cuidado» en `docs/tickets/ESTADO-rediseno.md`, con «Textos nuevos para que Isabella revise» al día.
- **`docs/defensa/`:** dos preguntas nuevas sin respuesta. Por ejemplo, por qué la cara del check-in es la del compañero, o por qué «semillas».

## Cómo trabajar

- Un commit por idea, en español, con `Co-Authored-By: Claude …`.
- Los textos nuevos de interfaz son provisionales: van a la lista de revisión de Isabella.
- Si el uso se acaba, termina el commit en curso y deja el ESTADO al día; la siguiente sesión sigue con `claude --continue`.
- Si algo no está aquí, pregunta.
