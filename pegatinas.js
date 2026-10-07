// =====================================================================
// pegatinas.js — dibuja las calcomanías (insignias). Sin diseño propio:
// los colores y la forma vienen de estilos/pegatinas.css.
//
// Uso:  LumeaPegatina.crear(calcomania, { ganada: true })  ->  <span> listo
//       LumeaPegatina.rolDe(calcomania)                    ->  "logro", etc.
//
// Arte propio: la forma troquelada + el ícono son provisionales. Si Isabella
// dibuja una calcomanía, guarda el archivo como img/calcomanias/<id>.svg y
// agrega su id a ARTE_PROPIO (así la página no pide archivos que no existen).
// =====================================================================
(function () {
  "use strict";

  const ARTE_PROPIO = [];                       // ids con archivo en img/calcomanias/
  const ROLES = ["comida", "logro", "mision", "emocion", "duda"];
  const NS = "http://www.w3.org/2000/svg";

  // Forma de sello troquelado (viewBox 0 0 100 100)
  const FORMA = "50,0 61,18 82,10 80,32 100,40 85,56 96,76 74,78 68,100 50,87 32,100 26,78 4,76 15,56 0,40 20,32 18,10 39,18";

  // Íconos de Lucide (licencia ISC), un trazo por rol (24x24)
  const ICONOS = {
    comida: ["M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z", "M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"],
    logro: ["M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"],
    mision: ["M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z", "M4 22v-7"],
    emocion: ["M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z", "M8 14s1.5 2 4 2 4-2 4-2", "M9 9h.01", "M15 9h.01"],
    duda: ["M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z", "M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3", "M12 17h.01"],
  };

  function rolDe(calcomania) {
    const rol = calcomania && calcomania.rol;
    return ROLES.indexOf(rol) !== -1 ? rol : "logro";     // un rol desconocido no rompe nada
  }

  function nodo(etiqueta, atributos) {
    const el = document.createElementNS(NS, etiqueta);
    Object.keys(atributos || {}).forEach((k) => el.setAttribute(k, atributos[k]));
    return el;
  }

  function dibujo(rol) {
    const svg = nodo("svg", { viewBox: "0 0 100 100", focusable: "false" });
    svg.appendChild(nodo("polygon", { class: "pegatina__forma", points: FORMA }));
    const icono = nodo("svg", { x: 30, y: 30, width: 40, height: 40, viewBox: "0 0 24 24", class: "pegatina__icono" });
    ICONOS[rol].forEach((d) => icono.appendChild(nodo("path", { d })));
    svg.appendChild(icono);
    return svg;
  }

  // opciones.ganada (por defecto true): false = solo contorno punteado
  function crear(calcomania, opciones) {
    const ganada = !opciones || opciones.ganada !== false;
    const rol = rolDe(calcomania);
    const caja = document.createElement("span");
    caja.className = `pegatina pegatina--${rol}` + (ganada ? "" : " pegatina--vacia");
    caja.setAttribute("aria-hidden", "true");              // decorativa: el nombre va escrito al lado
    if (ganada && calcomania && ARTE_PROPIO.indexOf(calcomania.id) !== -1) {
      const img = document.createElement("img");
      img.src = `img/calcomanias/${encodeURIComponent(calcomania.id)}.svg`;
      img.alt = "";
      caja.appendChild(img);
    } else {
      caja.appendChild(dibujo(rol));
    }
    return caja;
  }

  window.LumeaPegatina = { crear, rolDe, ARTE_PROPIO };
})();
