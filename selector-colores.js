// =====================================================================
// selector-colores.js — dónde cada persona elige sus colores y su modo.
//
// Ninguna paleta es predeterminada: mientras la persona no elige, Lumea se ve en un estado neutro.
// Este componente lo usan Inicio (la tarjeta «Elige tus colores») y Avatar (la sección «Mis colores»).
// Las caras del check-in ya no se eligen aquí: son las de tu compañero (companero.js).
//
// Uso: en el HTML basta con un contenedor vacío,
//   <div data-selector-colores></div>
// y este archivo lo llena con dos grupos de opciones (radiogroup):
//   Colores  Laguna, Neblina, Carnaval, Colibrí, Cosecha: una tira con los colores de cada rol
//   Modo     Claro, Oscuro, Como mi dispositivo
// Al elegir, se aplica y se guarda al instante (LumeaTema.ponerPaleta / ponerModo).
// Necesita tema.js (en el <head>). Todo se escribe con createElement.
//
// Los grupos son botones de radio de verdad (escondidos con .solo-lector): el teclado, las flechas
// y el lector de pantalla funcionan sin código extra.
// =====================================================================
(function () {
  "use strict";

  const Tema = window.LumeaTema;
  if (!Tema) return;

  // Los nombres que ve la persona (provisionales: los decide Isabella)
  const PALETAS = [["laguna", "Laguna"], ["neblina", "Neblina"], ["carnaval", "Carnaval"], ["colibri", "Colibrí"], ["cosecha", "Cosecha"]];
  const MODOS = [["claro", "Claro"], ["oscuro", "Oscuro"], ["auto", "Como mi dispositivo"]];
  const ROLES = ["comida", "logro", "emocion", "mision", "duda"];     // la gramática de color, en este orden

  let contador = 0;                                                   // para que los name de los radios no se pisen

  function crear(etiqueta, clase, texto) {
    const el = document.createElement(etiqueta);
    if (clase) el.className = clase;
    if (texto != null) el.textContent = texto;
    return el;
  }

  // Un grupo de opciones. `dibujarVista` arma lo que se ve en cada opción (la tira de colores).
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

  // Marca en los radios lo que está elegido ahora (y las tiras toman el modo de ahora)
  function sincronizar(raiz) {
    const actual = { paleta: Tema.paletaActual(), modo: Tema.modoGuardado() };
    [["paleta", actual.paleta], ["modo", actual.modo]].forEach(([id, valor]) => {
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
    contenedor.replaceChildren(raiz);
    sincronizar(raiz);
    // Cambió la paleta o el modo (desde aquí o desde otro lado): las tiras y lo marcado se ponen al día
    document.documentElement.addEventListener("lumea:tema", () => sincronizar(raiz));
    return raiz;
  }

  window.LumeaSelector = { montar };
  document.querySelectorAll("[data-selector-colores]").forEach(montar);
})();
