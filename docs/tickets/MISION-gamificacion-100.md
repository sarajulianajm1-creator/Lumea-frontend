# Misión: gamificación 100/100 (frontend)

**Para:** Claude Code, en el worktree `.claude/worktrees/gamificacion` (rama `gamificacion-100`).
**Decisión de Isabella, 5 oct 2026:** por falta de tiempo delega esta misión completa a Claude Code. Reemplaza los tickets T1, T3, T4 y T5. Regístralo así en `docs/bitacora-ia.md`: el código es de la IA; las decisiones, los bosquejos y la revisión son de Isabella.
**En paralelo:** otra sesión de Claude Code trabaja el backend (`~/Python_proyects/Lumea`, misión `MISION_GAMIFICACION_100.md`). El contrato nuevo está abajo; cuando el backend lo publique en `Backend/docs/CONTRATO_GAMIFICACION.md`, ese archivo manda.

## Decisiones de Isabella (si no cambió nada aquí, valen las marcadas)

- [x] Diseño: Progreso sigue `bosquejos/10-progreso.svg`; Avatar sigue `bosquejos/06-avatar-a-vitrina.svg` (variante A, aprobada el 4 oct). Lo que no esté en el bosquejo, se pregunta.
- [x] Calcomanías: sí, como álbum dentro de Avatar (cambia la decisión del 27 sep "sin insignias").
- [x] Arte de las calcomanías: provisional (forma troquelada + ícono SVG simple + nombre). Si existe `img/calcomanias/<id>.svg`, se usa ese archivo: Isabella puede dibujarlas después.
- [x] Pérdida de XP por inactividad: sigue en el backend; la pantalla solo muestra `mensaje_regreso` como bienvenida, nunca "perdiste XP".
- [x] Calorías: no aparecen en las pantallas nuevas.

## No tocar

`inicio.html`, `estilos/inicio.css` (Isabella), `sesion-nav.js` (ejercicio de Isabella), `style.css` (Sara), `estilos/paletas.css` y `estilos/tokens.json` (generados). En `alimentos.html` solo agregas el `<script>` de la celebración y la llamada; el rediseño de esa pantalla es otro ticket (T2).
**Nunca** `git add -A` ni `git commit -a`: agrega archivo por archivo.

## Contrato nuevo (provisional, lo implementa el backend)

En la clave `gamificacion` de `/predecir`, `/confirmar-alimento` y `POST /estado-animo`, además de lo que ya existe (`xp_ganado`, `misiones_cumplidas`, `subio_de_nivel`, `nivel`, `meta_diaria`…):

```json
"nivel_anterior": 3,
"desbloqueos": [ {"tipo": "accesorio", "id": "audifonos", "nombre": "Audífonos", "nivel_requerido": 4} ],
"calcomanias_nuevas": [ {"id": "primera_foto", "nombre": "Primera foto", "descripcion": "Registraste tu primera comida.", "rol": "comida"} ]
```

`desbloqueos` y `calcomanias_nuevas` son listas vacías cuando no hay nada. `GET /progreso` suma `"calcomanias": {"ganadas": 3, "total": 10}`. Nuevo `GET /calcomanias?email=`:

```json
{ "success": true, "ganadas": 3, "total": 10,
  "calcomanias": [ {"id": "primera_foto", "nombre": "Primera foto", "descripcion": "Registraste tu primera comida.",
                    "como_se_gana": "Registra tu primera comida.", "rol": "comida", "ganada": true, "fecha": "2026-10-05"} ] }
```

`GET /historial` suma `es_fruta` (booleano) en cada registro. Agrega `obtenerCalcomanias(email)` a `api.js`. Si un campo nuevo no llega (backend viejo), la pantalla funciona igual sin él.

## Reglas de la gamificación (no se negocian)

- Celebra lo que la persona HACE (registrar, contar cómo llega, volver). Nunca juzga la comida, nunca depende de calorías, peso ni de qué ánimo marcó. Sin rankings.
- Nada se pierde: lo ganado y lo desbloqueado no se quita. Ningún texto dice "perdiste".
- Color por rol: XP, nivel y racha = logro (maracuyá); misiones = mision (mora); ánimo y avatar = emocion (guayaba); "la IA dudó" = duda (mango). Maracuyá y mango nunca como texto (usa `--c-ROL-tinta`).
- Movimiento: 420 ms o menos (`--m-lento`), el rebote `--m-resorte` solo para logros, un movimiento automático a la vez. Con `prefers-reduced-motion` nada se mueve: solo aparece.
- Textos con `textContent`; avisos con `aria-live="polite"`; foco visible; todo se usa con teclado.
- Todo funciona en las 5 paletas × claro/oscuro, en 375 px y en 1280 px.

## Fases (en este orden: si el uso se acaba, lo primero ya sirve)

### F0 · Plan (modo plan)
Lee `CLAUDE.md`, `MARCA.md`, los bosquejos 06, 10 y 11, `estilos/componentes.css`, `ejemplo-camara.html`, `api.js`, `lumea-camara.js` e `indexx.js`. Muestra un plan de una pantalla: archivos que crearás, qué cambia en cada fase y qué dudas tienes. Espera la aprobación de Isabella.

### F1 · Pruebas (red de seguridad)
Haz lo que pide `docs/tickets/T1-pruebas.md` (pytest + Playwright en Python, backend simulado con `page.route`). Agrega respuestas simuladas con los campos nuevos del contrato. Desde aquí, cada fase termina con `pytest pruebas` en verde.

### F2 · Celebración de XP, misión, calcomanía y nivel
- `celebracion.js` sin diseño (como `lumea-camara.js`): `window.LumeaCelebrar(gamificacion)`. `estilos/celebracion.css` solo con tokens.
- Cola, un momento a la vez, del más pequeño al más grande:
  1. **XP:** un chip "+10 XP" junto al título, entra en 420 ms, se va solo a los 3 s.
  2. **Misión cumplida:** "Misión cumplida: Tres comidas", con su calcomanía pegándose.
  3. **Calcomanía nueva:** la calcomanía se pega (giro leve y rebote). Botones "Ver mi álbum" (va a `avatar.html#calcomanias`) y "Seguir".
  4. **Subida de nivel:** el momento grande, en un `<dialog>`. "Nivel 4" y "Se abrió en tu armario: Audífonos" (de `desbloqueos`). Botón "Ponérmelo" (`avatar.html#armario`) y "Seguir". Esc cierra y el foco vuelve a donde estaba.
- Solo la subida de nivel es modal; lo demás no bloquea registrar otra comida.
- `lumea-camara.js` la llama después de `mostrar()` si existe. Deja documentado cómo Isabella la conecta a su check-in de ánimo en una línea (ella lo hace).

### F3 · Progreso (`progreso.html`, bosquejo 10)
- Nivel con barra `.barra-xp` y el número escrito ("Te faltan 35 XP para el nivel 3"; en el último nivel, "Llegaste al nivel máximo").
- Racha actual y mejor racha (`.chip--logro`). Plural correcto: "1 día", "3 días".
- Comidas de la semana (lunes a domingo, de `/historial`): barras simples; si ese día hubo fruta (`es_fruta`), un ícono de fruta, no solo un color.
- Ánimo de la semana (de `GET /estado-animo`) con las caras del avatar (`avatar.urls_por_estado` de `/progreso`); si no hay internet para DiceBear, el nombre del estado.
- `mensaje_regreso` como bienvenida cálida arriba. Enlace "Mi álbum: 3 de 10 calcomanías".
- Arregla en `indexx.js` (Inicio de Sara) el plural "1 días" y "20 de 15 XP hoy" (si pasa la meta: "Meta cumplida: 20 XP hoy"). Solo esas líneas.
- Las pestañas Hoy/Semana/Todo del bosquejo quedan fuera: solo Semana.

### F4 · Avatar, misiones, armario y álbum (`avatar.html`, bosquejo 06)
- Avatar grande con la cara del ánimo de hoy (capas si `imagen_lista`, si no DiceBear), nivel y XP.
- Pestañas accesibles (patrón ARIA de tabs, flechas del teclado) que abren con `#misiones`, `#armario` y `#calcomanias`:
  - **Misiones:** las tres diarias de `/progreso`, con +10 XP. La cumplida lleva su calcomanía.
  - **Armario:** ropa y accesorios de `GET /avatar`. Equipar y quitar con `api.js`. Lo bloqueado lleva candado, "Nivel N", `aria-disabled="true"`. Al ponerse algo, el avatar da un saltico (un solo movimiento).
  - **Calcomanías:** el álbum de `GET /calcomanias`. Ganadas a color por rol con su fecha; no ganadas en contorno punteado con "Cómo se gana".

### F5 · Integración y cierre
- Navegación privada igual en todas las pantallas privadas, con `aria-current` en la actual (Inicio todavía apunta a `index-ingresado.html`).
- `pytest pruebas` en verde, y `pytest pruebas -m capturas` con las pantallas nuevas en 5 paletas × 2 modos, sin errores de contraste de axe.
- Una fila por fase en `docs/bitacora-ia.md`.
- `docs/defensa/preguntas-gamificacion.md`: 10 preguntas que un jurado podría hacerle a Isabella sobre este código, cada una con el archivo y la función donde está la respuesta. **Sin respuestas:** las escribe ella, porque es quien defiende el proyecto.

## Cómo trabajar

- Un commit por idea, en español, con `Co-Authored-By: Claude …`.
- Al terminar cada fase, actualiza `docs/tickets/ESTADO-gamificacion.md`: qué quedó listo, cómo probarlo y qué falta. Si el límite de uso se acaba a mitad de camino, primero termina el commit en curso y deja ese archivo al día; la siguiente sesión arranca con `claude --continue`.
- Si una decisión no está en este archivo ni en el bosquejo, pregunta. No inventes pantallas ni textos de marca.
