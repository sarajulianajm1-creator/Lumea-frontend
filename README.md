# Lumea (frontend)

## Qué es Lumea 

Lumea es una aplicación web que promueve hábitos de alimentación saludable en adolescentes. Su principal funcionalidad consiste en el reconocimiento de alimentos mediante dos inteligencias artificiales que muestran la información nutricional correspondiente (calorías aproximadas, sellos de advertencia y un consejo). Asimismo, implementa gamificación que se rige bajo normas inspiradas en la filosofía de San Francisco de Asís, sin prohibir nada ni comparar a ningún usuario con otro.  

## Por qué decidimos crearla 

Lumea es una aplicación que busca responder a una problemática ignorada en Colombia y en el mundo; la falta de hábitos saludables y una alimentación consciente.

En 2024, 400 millones de niños y adolescentes de 5 a 19 años tenían sobrepeso, es decir, el 20 % de ese grupo. De ellos, 170 millones vivían con obesidad. En 1990 la cifra era solo el 8 %. Y esto no es un problema de números; la obesidad adelanta enfermedades como la diabetes tipo 2 y las cardiovasculares. Según datos de la ENSIN (Encuesta Nacional de la Situación Nutriciona), que es la referencia nacional para el análisis de la situación de Colombia, el exceso de peso en escolares de 5 a 12 años subió de 18,8 % en 2010 a 24,4 % en 2015. El 17,9 % de los adolescentes de 13 a 17 años tiene exceso de peso; casi uno de cada cinco.

En nuestro colegio, las soluciones propuestas se condensan en una jornada llamada "Día saludable", en donde una vez por periodo los estudiantes consumen alimentos saludables, la venta de ultraprocesados se prohibe durante ese día y se llevan a cabo actividades lúdicas. Sin embargo, esta propuesta y otras aplicaciones que también prohiben o se enfocan solamente en las calorías, no son efectivas: 

### 2. Por qué prohibir no funciona
   
- Fisher y Birch (1999): en dos experimentos, restringir un alimento apetitoso aumentó el interés de los niños por él, y también cuánto lo escogían y comían. Ojo: el estudio fue con niños de preescolar, no con adolescentes.
- Neumark-Sztainer et al. (2006), su proyecto EAT siguió a 2 516 adolescentes durante 5 años. Arrojando que quienes usaban conductas no saludables para controlar el peso tenían cerca de 3 veces más riesgo de sobrepeso 5 años después (OR 2,7 en chicas y 3,2 en chicos), y tenían unas 6 veces más riesgo de ingesta compulsiva por pérdida del control.
- La Academia Americana de Pediatría (Golden et al., 2016) dice que la prevención debe centrarse en un estilo de vida saludable, no en el peso. Por eso Lumea no pide este dato.


### 3. Por qué es necesaria la constancia y no un día por periodo 
- Lally et al. (2010): En su estudio, 96 adultos registraron a diario un hábito nuevo durante 84 días. En los 39 casos que se pudieron modelar, el promedio para que el hábito se volviera automático fue de 66 días, con un rango de 18 a 254.

Son los hábitos aquellos que generan cambios. 

### 4. Por qué la gamificación
- Suleiman-Martos et al. (2021): En el metaanálisis de 23 ensayos controlados aleatorizados con niños y adolescentes. La gamificación aumentó el consumo de frutas y verduras y el conocimiento sobre grupos de alimentos. En conocimiento nutricional, la diferencia de medias fue de 0,88, con un IC 95 % de 0,05 a 1,75. Esto no tuvo efecto significativo en el IMC. Por eso Lumea promete conocimiento y hábitos, más no la pérdida de peso. 

### 5. Por qué los sellos y los ultraprocesados
- Lane et al. (2024), BMJ: Mediante una revisión de 45 metaanálisis con casi 10 millones de personas. Encontró evidencia convincente de que más ultraprocesados se asocian con mayor mortalidad cardiovascular, diabetes tipo 2 y ansiedad.
  
- Resolución 810 de 2021, modificada por la 2492 de 2022: Define los sellos octagonales, que Lumea también usa, como herramienta educativa.
  
### 6. Lumea responde a lo que pide la ley

Ley 2120 de 2021, sobre entornos alimentarios saludables:
- Art. 6: pide diseñar «herramientas educativas digitales, multiplataforma» sobre hábitos saludables, dirigidas especialmente a la comunidad escolar.
- Art. 9: pide acciones pedagógicas en los colegios, promover el consumo de frutas y verduras, y estrategias para aprender a leer el etiquetado nutricional.

Lumea es ese tipo de herramienta. 

### Los datos de Lumea
- Modelo regional de 35 clases: 77,07 % de exactitud en validación.
- Prueba de campo en feria de ciencia escolar: de 7 a 10 aciertos en 13 fotos.
- 168 alimentos con información nutricional (USDA y TCAC del ICBF).
- Consejos basados en las Guías Alimentarias del ICBF.
- 328 pruebas automáticas en el backend y 865 en el frontend.

### Artículos consultados en PubMed:

Fisher JO, Birch LL. Am J Clin Nutr 1999;69(6):1264–72. DOI
Neumark-Sztainer D et al. J Am Diet Assoc 2006;106(4):559–68. DOI
Golden NH et al. Pediatrics 2016;138(3):e20161649. DOI
Suleiman-Martos N et al. Nutrients 2021;13(7):2478. DOI
Lane MM et al. BMJ 2024;384:e077310. DOI

### Referencias: 
OMS: Obesity and overweight: https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight
ENSIN 2015, resumen en ConsultorSalud
ICBF: ENSIN -> https://www.icbf.gov.co/ensin-encuesta-nacional-de-situacion-nutricional-0 
Ministerio de Salud, respuesta del 2 feb 2026 sobre la ENSIN
Lally et al. (2010), revisión en The Behavioral Scientist, DOI del original: 10.1002/ejsp.674: https://www.thebehavioralscientist.com/articles/how-long-to-form-a-habit
Ley 2120 de 2021: https://normativa.colpensiones.gov.co/colpens/compilacion/docs/ley_2120_2021.htm 
Resolución 2492 de 2022:
______________________________________________________________________________________________________________________________________

Las reglas de diseño están en `MARCA.md` y las del trabajo con IA, en `CLAUDE.md`. El estado del proyecto, fase por fase, está en
`docs/tickets/ESTADO-rediseno.md`.

## Cómo correrla

Son dos repositorios: este (el frontend) y el backend (`Lumea/Backend`).

**1. El backend** (puerto **5002**, con MySQL encendido y su archivo `.env`; ver el README del backend):

    cd Backend
    pip install -r requirements.txt
    python3 app.py                 # http://127.0.0.1:5002

**2. El frontend**, desde esta carpeta:

    python3 -m http.server 8001

y abrir `http://localhost:8001/index.html`. La dirección de la API sale del nombre del equipo (`location.hostname` en `api.js`),
así que desde el celular basta con abrir `http://<IP del computador>:8001` en la misma red.

**3. La cuenta demo.** Desde la carpeta del backend, `python3 herramientas/crear_usuario_demo.py` crea (o reinicia) `demo@lumea.co`,
en la etapa 4, con prendas abiertas y con candado; el script imprime la contraseña. Con `--solo-borrar` la quita.

**Safari.** La cámara pide `localhost` o HTTPS: abrir la página con `http://localhost:8001`, no con doble clic. En Safari conviene
revisar el botón de la cámara apagada, el fundido entre pantallas y la persona dibujada (ver el ESTADO). Si la persona no sale a la
primera, se recarga la página.

**Pruebas:**

    python3 -m venv .venv && .venv/bin/pip install -r pruebas/requirements.txt
    .venv/bin/playwright install chromium
    .venv/bin/pytest pruebas                 # el backend se simula: no hace falta encenderlo
    .venv/bin/pytest pruebas -m capturas     # capturas y contraste en 5 paletas × claro/oscuro (lento)

## Las pantallas

| Pantalla | Archivo | Qué hace |
|---|---|---|
| Inicio público, Conócenos, Guía, Términos | `index.html`, `conocenos.html`, `guialumea.html`, `terminos.html` | Presentación del proyecto (textos de Isabella) |
| Crear cuenta · Iniciar sesión | `crear-cuenta.html`, `iniciar-sesion.html` | Perfil sin peso ni altura; edad mínima de 11 años, con aviso al acudiente en menores de 18 |
| **Inicio** | `index-ingresado.html` | El compañero que saluda, «Tu día» con el único botón principal, el check-in de ánimo, «¿Sabías que…?» del día, «Tu semana», la misión y la etapa |
| **Registrar** | `alimentos.html` | Foto → la IA dice qué es → calorías aproximadas, sellos y consejos («Lo que aporta», «Para completar tu plato», «A tener en cuenta») |
| **Mis registros** | `mis-registros.html` | Una tarjeta por día, con los grupos del plato y los sellos |
| **Progreso** | `progreso.html` | Etapa, racha, comidas y ánimo de la semana, álbum de calcomanías |
| **Ánimo** | `emociones.html` | El check-in con las caras de tu compañero |
| **Avatar** | `avatar.html` | La persona (voxel-art), el armario por etapas, «Cómo me veo», misiones, calcomanías y compañeros |

El menú lateral (computador) o la barra de abajo (celular) las une. La lógica de cada pantalla está en su `.js`; la conexión con el
backend, solo en `api.js`.

## Decisiones de diseño

- **Paletas.** Cinco paletas (Laguna, Neblina, Carnaval, Colibrí y Cosecha) × claro y oscuro, más un estado neutro: **nadie tiene una
  predeterminada**, cada persona elige las suyas. Los colores y la tipografía viven en `estilos/tokens.css` y `estilos/paletas.css`
  (los valida `herramientas/generar_paletas.py`); ninguna pantalla escribe un color a mano.
- **Accesibilidad.** Contraste de 4,5:1 medido con axe en las 5 paletas y los dos modos (y con los colores calculados para las
  formas decorativas), textos de 12,8 px o más, controles de 44 px, foco visible, todo con teclado, nombres accesibles y sin barra
  horizontal desde 320 px ni con el zoom al 200 %. Nada se comunica solo con color.
- **Movimiento con propósito.** Una entrada suave por pantalla, un fundido corto entre pantallas (`@view-transition`), respuesta al
  toque inmediata, barras que se llenan una vez y la celebración. Nada más se mueve, y con `prefers-reduced-motion` no se mueve
  nada, ni la persona ni el compañero.
- **Una acción principal por pantalla** y vocabulario propio: «semillas» y «etapas» donde el backend dice XP y niveles.

## Ética y privacidad

- **Lumea no pide peso ni altura.** Los campos se quitaron de Crear cuenta y ya no viajan al servidor.
- **Edad mínima: 11 años, con aviso al acudiente.** Con menos de 18 años hay que marcar «Mi madre, padre o acudiente sabe que uso
  Lumea». Es un **aviso, no una autorización verificada**; para un lanzamiento real, la Ley 1581 de 2012 y el Decreto 1377 de 2013
  piden la autorización del representante legal (ver `DEFENSA_TECNICA_LUMEA.md`, en el repositorio del backend).
- **DiceBear se dibuja dentro de Lumea.** La persona (estilo voxel-art) y los compañeros (estilo gaze) se dibujan en el navegador con
  los archivos de `vendor/dicebear/`; ninguna página le pide nada a `api.dicebear.com` (lo comprueba `pruebas/test_sin_dicebear.py`),
  así que DiceBear no se entera de cómo se ve ni de cómo se siente cada persona, ni de su IP. La semilla es fija; nunca el correo.
- **Las fotos.** Se verificó en el código: el navegador reduce la foto a 1024 px y la manda a `POST /predecir`; el backend la lee en
  memoria (`file.read()` → `predecir_alimento(bytes)`), la procesa con la red y **no la guarda** ni en disco ni en la base de datos.
  El historial guarda solo el nombre del alimento, las calorías aproximadas, la certeza, los sellos y la fecha. La foto de «Tomar foto
  ahora» (Inicio) queda un momento en `sessionStorage` solo para pasarla a Registrar, y se borra al leerla.
- **Sin comparaciones ni juicios.** Ningún día va en rojo, no hay rankings y lo que se muestra de la comida es información, no una meta.
- La IA puede equivocarse: cuando duda, lo dice y pide confirmar. Los datos curiosos son conocimiento general, no evidencia científica.

## Créditos del equipo

- **Isabella Fernanda Obando Ordóñez**: líder técnica y de producto, arquitecta de software. Backend (Python, Flask, MySQL), modelos de IA y datos nutricionales, gamificación «Camino del cuidado», consejos y dirección del rediseño. En este repositorio sus commits salen con su cuenta de GitHub, `Fer-geniee`.
- **Sara Jiménez**: desarrolladora frontend y diseñadora UI (páginas, estilos y primera interfaz web). Los 4 commits de este repositorio que aparecen a nombre de «Laura Jiménez» son suyos: vienen de su correo y su cuenta de GitHub, pero tenía mal configurado su nombre en git.
- **Laura Narváez**: diseñadora UX/UI y redactora de contenidos (diseños en Figma, logo, paleta original, textos de la app, términos y condiciones y «Conócenos»). No tiene commits porque su trabajo fue en Figma y en los textos.
- **Claude (Anthropic)**: consultora (planeación, revisión y acompañamiento). **Claude Code**: asistente de programación bajo la dirección de Isabella; cada aporte está registrado en la bitácora de IA.

## Uso de IA

El trabajo con IA (Claude) está registrado fila por fila en [`docs/bitacora-ia.md`](docs/bitacora-ia.md): qué hizo el equipo y qué
hizo la IA. Las decisiones de diseño y los textos son de Isabella; las preguntas que podría hacer un jurado están en `docs/defensa/`.

## Licencias

- **DiceBear core** (`@dicebear/core` 10.7.0): MIT, `vendor/dicebear/core/LICENSE`.
- **DiceBear estilos «Voxel Art» y «Gaze»**: CC0 1.0, en `vendor/dicebear/estilos/`.
- **Bricolage Grotesque**: SIL OFL 1.1, `estilos/fuentes/OFL-Bricolage.txt` (y cualquier letra nueva que agregue Isabella, con su licencia).
- **Bootstrap** y **Bootstrap Icons**: MIT, en `vendor/bootstrap/` y `vendor/bootstrap-icons/`.
