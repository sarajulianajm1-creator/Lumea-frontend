// =====================================================================
// companero.js — el compañero de cada persona (Camino del cuidado).
//
// El compañero es un dibujo de DiceBear 10.x «gaze» (licencia CC0) con forma y color fijos; sus ojos
// muestran el ánimo. El backend manda las direcciones QUIETAS (avatar.urls_por_estado de GET /progreso,
// y la lista de GET /avatares); aquí solo se les agrega animationVariant donde algo responde a una acción:
//   el compañero grande de Avatar       slow
// La dirección lleva solo la configuración del dibujo (la semilla es fija, «lumea-<id>»): nunca viaja
// un dato de la persona. La animación vive dentro del SVG y se apaga sola con prefers-reduced-motion;
// además aquí no se pide ninguna si la persona tiene el movimiento reducido.
//
// Cómo se usa:
//   LumeaCompanero.url(direccion, "slow")             la misma dirección con la animación pedida (o quieta si no se pide)
//   LumeaCompanero.imagen(direccion, "slow", clase)   una <img alt=""> del compañero; si no carga, se quita sola
//
// Qué pasa solo:
//   - La imagen lleva alt="": el nombre del compañero va escrito al lado, nunca solo en el dibujo.
//   - Sin internet se quita la imagen y queda lo que haya alrededor (la palabra, la silueta).
// =====================================================================
(function () {
  "use strict";

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

  // Una <img> del compañero; si no carga, se quita sola (lo que haya al lado, como la palabra, queda)
  function imagen(direccion, animacion, clase) {
    const fuente = url(direccion, animacion);
    if (!fuente) return null;
    const img = document.createElement("img");
    img.alt = "";
    img.src = fuente;
    img.className = clase || "companero__img";
    img.dataset.fuente = fuente;
    img.addEventListener("error", () => img.remove());
    return img;
  }

  window.LumeaCompanero = { url, imagen, movimientoReducido };
})();
