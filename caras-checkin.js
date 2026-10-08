// =====================================================================
// caras-checkin.js — las caras de los cinco botones del check-in (Inicio y Ánimo).
//
// Cada persona elige su set de caras, igual que su paleta: ninguno es predeterminado.
// Mientras no elija, los botones muestran solo la palabra («Muy mal» … «Muy bien»).
// La elección se guarda en el navegador (localStorage, clave «lumea-caras»), no en la cuenta.
//
// Las caras vienen de DiceBear 10.x por internet (estilos «gaze» y «moods», licencia CC0).
// La dirección de cada cara lleva SOLO la configuración del dibujo: la semilla es fija
// («lumea-animo»), así que no viaja ningún dato de la persona.
//
// Cómo se usa en una página:
//   <span data-cara-checkin="muy_mal"></span>      un hueco por estado, dentro del botón
//   <script src="caras-checkin.js"></script>       después de tema.js (que está en el <head>)
//
//   LumeaCaras.poner("gaze" | "moods")   elige el set (null lo quita), lo guarda y vuelve a dibujar
//   LumeaCaras.actual()                  "gaze", "moods" o null
//   LumeaCaras.imagen(set, estado, animada)  una <img> con la cara (el selector de R4 la usa)
//
// Qué pasa solo:
//   - El color del cuerpo es --c-emocion de la paleta activa: cambia con el evento «lumea:tema».
//   - Las caras están quietas (animationVariant=none); solo la del botón con aria-pressed="true"
//     se anima: el movimiento responde a lo que la persona hizo y nunca hay cinco caras moviéndose.
//     (La animación vive dentro del SVG y se apaga sola con prefers-reduced-motion.)
//   - La imagen lleva alt="": la palabra del botón es su nombre accesible.
//   - Si la imagen no carga (sin internet), se quita y queda la palabra; el botón funciona igual.
// =====================================================================
(function () {
  "use strict";

  // Sets de caras. Para cambiar un dibujo, cambia su palabra aquí (los nombres de las variantes
  // salen de @dicebear/styles 10.6.0; las diez direcciones se comprobaron cargando en el navegador).
  const ESTILOS = {
    gaze: {
      base: "https://api.dicebear.com/10.x/gaze/svg",
      fijos: { seed: "lumea-animo", shapeVariant: "circle" },
      color: "bodyColor",
      caras: {
        muy_mal: { eyesVariant: "bars" },
        mal: { eyesVariant: "small" },
        neutral: { eyesVariant: "dots" },
        bien: { eyesVariant: "happy" },
        muy_bien: { eyesVariant: "grin" },
      },
    },
    moods: {
      base: "https://api.dicebear.com/10.x/moods/svg",
      fijos: { seed: "lumea-animo", faceVariant: "circle", cheeksProbability: 0, backgroundColor: "ffffff00" },
      color: "faceColor",
      caras: {
        muy_mal: { eyesVariant: "lookDown", mouthVariant: "frown" },
        mal: { eyesVariant: "pupils", mouthVariant: "wavy" },
        neutral: { eyesVariant: "pupils", mouthVariant: "line" },
        bien: { eyesVariant: "pupils", mouthVariant: "smile" },
        muy_bien: { eyesVariant: "happy", mouthVariant: "laugh" },
      },
    },
  };

  const CLAVE = "lumea-caras";
  const html = document.documentElement;

  // localStorage puede fallar (modo privado, permisos): nunca rompe la app, igual que tema.js
  function leer() { try { return localStorage.getItem(CLAVE); } catch (e) { return null; } }
  function guardar(valor) {
    try { if (valor == null) localStorage.removeItem(CLAVE); else localStorage.setItem(CLAVE, valor); } catch (e) {}
  }

  // El set elegido; un valor guardado que no existe (o ninguno) es «sin elección»
  function actual() {
    const guardado = leer();
    return Object.prototype.hasOwnProperty.call(ESTILOS, guardado) ? guardado : null;
  }

  // --c-emocion de la paleta activa como hexadecimal SIN «#» (así lo pide DiceBear)
  function colorDeEmocion() {
    const valor = getComputedStyle(html).getPropertyValue("--c-emocion").trim();
    const m = /^#([0-9a-f]{6})$/i.exec(valor);
    return m ? m[1].toLowerCase() : null;
  }

  // La dirección de la cara de un estado. `animada` solo para la cara elegida.
  function url(set, estado, animada) {
    const estilo = ESTILOS[set];
    if (!estilo || !estilo.caras[estado]) return null;
    const direccion = new URL(estilo.base);
    const parametros = { ...estilo.fijos, ...estilo.caras[estado], animationVariant: animada ? "medium" : "none" };
    const color = colorDeEmocion();
    if (color) parametros[estilo.color] = color;
    Object.entries(parametros).forEach(([nombre, valor]) => direccion.searchParams.set(nombre, valor));
    return direccion.toString();
  }

  // Una <img> con la cara; si no carga, se quita sola (la palabra queda en el botón)
  function imagen(set, estado, animada) {
    const direccion = url(set, estado, animada);
    if (!direccion) return null;
    const img = document.createElement("img");
    img.alt = "";
    img.src = direccion;
    img.className = "caras-checkin__img";
    img.addEventListener("error", () => img.remove());
    return img;
  }

  // Dibuja (o borra) la cara de UN hueco. Se anima si su botón está elegido.
  function dibujarUno(hueco) {
    const set = actual();
    const boton = hueco.closest("button");
    const elegida = !!boton && boton.getAttribute("aria-pressed") === "true";
    const img = set ? imagen(set, hueco.dataset.caraCheckin, elegida) : null;
    if (img) hueco.replaceChildren(img); else hueco.replaceChildren();
  }

  function dibujar() {
    document.querySelectorAll("[data-cara-checkin]").forEach(dibujarUno);
  }

  // Elegir un set (o quitarlo con null): se guarda y todas las caras se vuelven a dibujar
  function poner(set) {
    if (set != null && !Object.prototype.hasOwnProperty.call(ESTILOS, set)) return;
    guardar(set);
    dibujar();
    html.dispatchEvent(new CustomEvent("lumea:caras"));
  }

  // Cambió la paleta: el color del cuerpo es otro. Cambió el set: otras caras.
  html.addEventListener("lumea:tema", dibujar);
  html.addEventListener("lumea:caras", dibujar);

  // Cuando un botón cambia de aria-pressed, solo su cara se vuelve a dibujar (la elegida se anima)
  new MutationObserver((cambios) => {
    cambios.forEach((c) => {
      const hueco = c.target.querySelector && c.target.querySelector("[data-cara-checkin]");
      if (hueco) dibujarUno(hueco);
    });
  }).observe(document.documentElement, { attributes: true, attributeFilter: ["aria-pressed"], subtree: true });

  window.LumeaCaras = { ESTILOS, actual, poner, url, imagen, dibujar };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", dibujar);
  else dibujar();
})();
