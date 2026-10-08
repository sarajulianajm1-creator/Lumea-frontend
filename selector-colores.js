// =====================================================================
// selector-colores.js — dónde cada persona elige sus colores, su modo y sus caras.
//
// Ninguna paleta ni ningún set de caras es predeterminado: mientras la persona no elige, Lumea se ve
// en un estado neutro y los botones del check-in muestran solo la palabra. Este componente lo usan
// Inicio (la tarjeta «Elige tus colores y tus caras») y Avatar (la sección «Mis colores y caras»).
//
// Uso: en el HTML basta con un contenedor vacío,
//   <div data-selector-colores></div>
// y este archivo lo llena con tres grupos de opciones (radiogroup):
//   Colores  Laguna, Neblina, Carnaval, Colibrí, Cosecha: una tira con los colores de cada rol
//   Modo     Claro, Oscuro, Como mi dispositivo
//   Caras    Miradas (gaze) y Gestos (moods): las cinco caras quietas de cada set
// Al elegir, se aplica y se guarda al instante (LumeaTema.ponerPaleta / ponerModo, LumeaCaras.poner).
// Necesita tema.js (en el <head>) y caras-checkin.js antes. Todo se escribe con createElement.
//
// Los grupos son botones de radio de verdad (escondidos con .solo-lector): el teclado, las flechas
// y el lector de pantalla funcionan sin código extra.
// =====================================================================
(function () {
  "use strict";

  const Tema = window.LumeaTema;
  const Caras = window.LumeaCaras;
  if (!Tema) return;

  // Los nombres que ve la persona (provisionales: los decide Isabella)
  const PALETAS = [["laguna", "Laguna"], ["neblina", "Neblina"], ["carnaval", "Carnaval"], ["colibri", "Colibrí"], ["cosecha", "Cosecha"]];
  const MODOS = [["claro", "Claro"], ["oscuro", "Oscuro"], ["auto", "Como mi dispositivo"]];
  const SETS = [["gaze", "Miradas"], ["moods", "Gestos"]];
  const ESTADOS = ["muy_mal", "mal", "neutral", "bien", "muy_bien"];
  const ROLES = ["comida", "logro", "emocion", "mision", "duda"];     // la gramática de color, en este orden

  let contador = 0;                                                   // para que los name de los radios no se pisen

  function crear(etiqueta, clase, texto) {
    const el = document.createElement(etiqueta);
    if (clase) el.className = clase;
    if (texto != null) el.textContent = texto;
    return el;
  }

  // Un grupo de opciones. `dibujarVista` arma lo que se ve en cada opción (la tira, las caras…).
  function grupo(prefijo, id, titulo, opciones, clase, dibujarVista, alElegir) {
    const conjunto = crear("fieldset", "selector__grupo");
    conjunto.setAttribute("role", "radiogroup");
    conjunto.appendChild(crear("legend", "selector__titulo", titulo));
    const lista = crear("div", "selector__opciones " + clase);
    opciones.forEach(([valor, nombre]) => {
      const etiqueta = crear("label", "selector__opcion");
      const radio = crear("input", "solo-lector");
      radio.type = "radio";
      radio.name = `${prefijo}-${id}`;
      radio.value = valor;
      radio.addEventListener("change", () => { if (radio.checked) alElegir(valor); });
      etiqueta.appendChild(radio);
      const vista = dibujarVista(valor);
      if (vista) etiqueta.appendChild(vista);
      etiqueta.appendChild(crear("span", "selector__nombre", nombre));
      lista.appendChild(etiqueta);
    });
    conjunto.appendChild(lista);
    return conjunto;
  }

  // La tira de una paleta: sus cinco colores de rol. El data-paleta de la tira hace que SUS variables
  // --c-* sean las de esa paleta (paletas.css lo permite a propósito), y data-modo, el modo de ahora.
  function tira(paleta) {
    const el = crear("span", "selector__tira");
    el.setAttribute("aria-hidden", "true");
    el.dataset.paleta = paleta;
    el.dataset.modo = Tema.modoEfectivo();
    ROLES.forEach((rol) => el.appendChild(crear("span", `selector__muestra selector__muestra--${rol}`)));
    return el;
  }

  // Las cinco caras quietas de un set (con el color de emoción de la paleta activa)
  function carasDe(set) {
    const el = crear("span", "selector__caras");
    el.setAttribute("aria-hidden", "true");
    el.dataset.set = set;
    return el;
  }

  function pintarCaras(raiz) {
    if (!Caras) return;
    raiz.querySelectorAll(".selector__caras").forEach((contenedor) => {
      contenedor.replaceChildren();
      ESTADOS.forEach((estado) => {
        const celda = crear("span", "selector__cara");
        const img = Caras.imagen(contenedor.dataset.set, estado, false);     // quietas: ninguna se mueve aquí
        if (img) celda.appendChild(img);
        contenedor.appendChild(celda);
      });
    });
  }

  // Marca en los radios lo que está elegido ahora (y las tiras toman el modo de ahora)
  function sincronizar(raiz) {
    const actual = { paleta: Tema.paletaActual(), modo: Tema.modoGuardado(), caras: Caras ? Caras.actual() : null };
    [["paleta", actual.paleta], ["modo", actual.modo], ["caras", actual.caras]].forEach(([id, valor]) => {
      raiz.querySelectorAll(`input[name$="-${id}"]`).forEach((radio) => {
        radio.checked = radio.value === valor;
        radio.closest(".selector__opcion").classList.toggle("selector__opcion--elegida", radio.checked);
      });
    });
    raiz.querySelectorAll(".selector__tira").forEach((t) => { t.dataset.modo = Tema.modoEfectivo(); });
  }

  function montar(contenedor) {
    const prefijo = `selector${++contador}`;
    const raiz = crear("div", "selector");
    raiz.appendChild(grupo(prefijo, "paleta", "Colores", PALETAS, "selector__opciones--paletas", tira, (v) => Tema.ponerPaleta(v)));
    raiz.appendChild(grupo(prefijo, "modo", "Modo", MODOS, "selector__opciones--modos", () => null, (v) => Tema.ponerModo(v)));
    if (Caras) raiz.appendChild(grupo(prefijo, "caras", "Caras", SETS, "selector__opciones--caras", carasDe, (v) => Caras.poner(v)));
    contenedor.replaceChildren(raiz);
    pintarCaras(raiz);
    sincronizar(raiz);
    // Cambió la paleta o el modo (desde aquí o desde otro lado): las tiras, las caras y lo marcado se ponen al día
    document.documentElement.addEventListener("lumea:tema", () => { pintarCaras(raiz); sincronizar(raiz); });
    document.documentElement.addEventListener("lumea:caras", () => sincronizar(raiz));
    return raiz;
  }

  window.LumeaSelector = { montar };
  document.querySelectorAll("[data-selector-colores]").forEach(montar);
})();
