// =====================================================================
// companero.js — el compañero de cada persona (Camino del cuidado).
//
// El compañero es un dibujo de DiceBear 10.x «gaze» (licencia CC0) con forma y color fijos; sus ojos
// muestran el ánimo. El backend manda las direcciones QUIETAS (avatar.urls_por_estado de GET /progreso,
// y la lista de GET /avatares); aquí solo se les agrega animationVariant donde algo responde a una acción:
//   la cara elegida en el check-in      medium
//   el compañero grande de Avatar       slow
// La dirección lleva solo la configuración del dibujo (la semilla es fija, «lumea-<id>»): nunca viaja
// un dato de la persona. La animación vive dentro del SVG y se apaga sola con prefers-reduced-motion;
// además aquí no se pide ninguna si la persona tiene el movimiento reducido.
//
// DIBUJO LOCAL: el compañero se dibuja en el navegador con vendor/dicebear/ (core + gaze.json). La dirección
// que manda el backend solo se LEE (sus parámetros): nunca se pide a api.dicebear.com. Cada <img> trae esa
// dirección en data-fuente (con la animación pedida) y, en src, el dibujo como dirección data:.
//
// Esto reemplaza a caras-checkin.js: ya no hay sets de caras que elegir ni la clave lumea-caras en el
// navegador. Las cinco caras del check-in (Inicio y Ánimo) son siempre las de tu compañero.
//
// Cómo se usa:
//   <span data-cara-checkin="muy_mal"></span>   un hueco por estado, dentro del botón del check-in
//   LumeaCompanero.pintarCheckin()              dibuja las cinco caras; la del botón con aria-pressed="true" se anima
//                                               (salvo dentro de [data-caras-quietas]: en Inicio la única que se mueve es la del saludo)
//   LumeaCompanero.url(direccion, "slow")             la misma dirección con la animación pedida (o quieta si no se pide)
//   LumeaCompanero.imagen(direccion, "slow", clase)   una <img alt=""> del compañero; si no carga, se quita sola
//
// Qué pasa solo:
//   - Nunca hay dos caras moviéndose: solo se anima el botón elegido (uno a la vez).
//   - La imagen lleva alt="": la palabra del botón (o el nombre al lado) es su nombre accesible.
//   - Sin internet (o sin compañero) el hueco queda vacío y no ocupa lugar: queda la palabra, y el botón funciona igual.
// pintarCheckin() necesita lumea-state.js y lumea-ui.js antes (la cara sale de lumeaStore → avatar.urls_por_estado).
// =====================================================================
(function () {
  "use strict";

  // La clave del set de caras que existió del 7 al 8 de octubre: ya no se usa, y no se deja basura en el navegador
  try { localStorage.removeItem("lumea-caras"); } catch (e) { /* modo privado: no importa */ }

  function movimientoReducido() {
    return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }

  // La dirección del compañero, quieta, o con la animación pedida ("medium" | "slow") si la persona admite movimiento.
  // Una dirección que no es http(s) no se usa (nada de javascript: ni data:).
  function url(direccion, animacion) {
    if (!direccion) return null;
    let u;
    try { u = new URL(direccion); } catch (e) { return null; }
    if (u.protocol !== "https:" && u.protocol !== "http:") return null;
    u.searchParams.delete("animationVariant");
    if (animacion && !movimientoReducido()) u.searchParams.set("animationVariant", animacion);
    return u.toString();
  }

  // ---------- El dibujo local (gaze 10.x, CC0) ----------
  const PARAMETROS = ["shapeVariant", "bodyColor", "eyesVariant", "animationVariant"];   // los únicos que se leen de la dirección
  let nucleo = null;
  // Un servidor sencillo (python -m http.server) puede cortar alguna de las ~40 peticiones de módulos que llegan juntas:
  // si pasa, se intenta una vez más antes de rendirse.
  function cargarNucleo(intentos) {
    if (!nucleo) {
      nucleo = Promise.all([
        import("./vendor/dicebear/core/index.js"),
        fetch("vendor/dicebear/estilos/gaze.json").then((r) => { if (!r.ok) throw new Error("gaze.json"); return r.json(); }),
      ]).then(([m, def]) => ({ Avatar: m.Avatar, estilo: new m.Style(def) }))
        .catch((e) => {
          nucleo = null;
          if ((intentos || 0) >= 7) throw e;
          return new Promise((ok) => setTimeout(ok, 250 * ((intentos || 0) + 1))).then(() => cargarNucleo((intentos || 0) + 1));
        });
    }
    return nucleo;
  }

  // Las opciones de DiceBear a partir de la dirección: cada valor va en una lista; la semilla, tal cual
  function opciones(fuente) {
    const parametros = new URL(fuente).searchParams;
    const o = { seed: parametros.get("seed") || "lumea" };
    PARAMETROS.forEach((clave) => { if (parametros.get(clave)) o[clave] = [parametros.get(clave).replace(/^#/, "")]; });
    return o;
  }

  const dibujos = new Map();                               // dirección → dirección data: (no se vuelve a dibujar)
  function dibujar(fuente) {
    if (!dibujos.has(fuente)) {
      dibujos.set(fuente, cargarNucleo().then(({ Avatar, estilo }) =>
        "data:image/svg+xml;charset=utf-8," + encodeURIComponent(new Avatar(estilo, opciones(fuente)).toString())));
      dibujos.get(fuente).catch(() => dibujos.delete(fuente));
    }
    return dibujos.get(fuente);
  }

  // Una <img> del compañero; si no se puede dibujar, se quita sola (lo que haya al lado, como la palabra, queda)
  function imagen(direccion, animacion, clase) {
    const fuente = url(direccion, animacion);
    if (!fuente) return null;
    const img = document.createElement("img");
    img.alt = "";
    img.className = clase || "companero__img";
    img.dataset.fuente = fuente;
    img.addEventListener("error", () => img.remove());
    dibujar(fuente).then((dibujo) => { img.src = dibujo; }, () => img.dispatchEvent(new Event("error")));
    return img;
  }

  // Dibuja las cinco caras del check-in con el compañero de la persona. Se puede llamar las veces que haga falta:
  // una cara que ya está dibujada tal cual no se vuelve a cargar (así no parpadea ni reinicia su animación).
  function pintarCheckin() {
    const UI = window.LumeaUI;
    document.querySelectorAll("[data-cara-checkin]").forEach((hueco) => {
      const boton = hueco.closest("button");
      const elegida = !!boton && boton.getAttribute("aria-pressed") === "true";
      const quieta = UI ? UI.urlDeCara(hueco.dataset.caraCheckin) : null;
      const animacion = elegida && !hueco.closest("[data-caras-quietas]") ? "medium" : null;       // en Inicio, solo se mueve el saludo
      const actual = hueco.firstElementChild;
      if (actual && actual.dataset.fuente === url(quieta, animacion)) return;
      const img = imagen(quieta, animacion, "companero__img");
      if (img) hueco.replaceChildren(img); else hueco.replaceChildren();
    });
  }

  window.LumeaCompanero = { url, imagen, dibujar, pintarCheckin, movimientoReducido };
})();
