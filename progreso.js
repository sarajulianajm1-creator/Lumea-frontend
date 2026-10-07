// =====================================================================
// progreso.js — dibuja lo propio de progreso.html (el diseño es de Sara): la semana de
// comidas, la semana de ánimo, el álbum y los estados cargando/error.
//
// Nivel, XP, racha y bienvenida los pone lumea-ui.js. Todo sale del estado de lumea-state.js,
// que lee GET /progreso, GET /historial (es_fruta) y GET /estado-animo?dias=7 por api.js.
// Si un dato no llega (backend viejo o sin red), esa parte se omite y la pantalla funciona igual.
// Todo texto del servidor se escribe con textContent.
//
// Lo que NO hace, a propósito: no compara con otras personas, no muestra calorías y nunca
// dice «perdiste XP»: el mensaje de regreso es una bienvenida.
// Necesita api.js, formato.js, lumea-state.js y lumea-ui.js antes.
// =====================================================================
(function () {
  "use strict";

  const F = window.LumeaFormato;
  const UI = window.LumeaUI;
  const $ = (id) => document.getElementById(id);

  // ---------- Comidas de la semana: barras simples; la fruta lleva su ícono, no solo color ----------
  function dibujarSemanaComidas(semana) {
    const caja = $("semana-comidas-caja");
    if (!semana) { caja.hidden = true; return; }
    caja.hidden = false;
    const lista = $("grafica-barras-semana");
    lista.replaceChildren();
    const maximo = Math.max(3, ...semana.map((d) => d.comidas));
    semana.forEach((d) => {
      const altura = d.comidas === 0 ? 12 : Math.min(150, Math.round((d.comidas / maximo) * 130) + 20);
      const columna = UI.crear("div", "bar-col-item" + (d.esHoy ? " today" : "") + (d.futuro ? " bar-col-item--futuro" : ""));
      columna.setAttribute("role", "listitem");
      if (d.esHoy) columna.setAttribute("aria-current", "date");
      const barra = UI.crear("div", "bar-fill-body");
      barra.setAttribute("aria-hidden", "true");
      barra.style.height = `${d.futuro ? 12 : altura}px`;
      if (d.tieneFruta) {
        const fruta = UI.crear("i", "bi bi-apple bar-fruit-floating-icon");
        fruta.setAttribute("aria-hidden", "true");
        barra.appendChild(fruta);
      }
      const letra = UI.crear("span", "bar-day-name", d.dia);
      letra.setAttribute("aria-hidden", "true");
      const detalle = d.futuro ? "todavía no llega"
        : `${F.plural(d.comidas, "comida", "comidas")}${d.tieneFruta ? ", con fruta" : ""}`;
      columna.append(barra, letra, UI.crear("span", "solo-lector", `${d.nombre}${d.esHoy ? " (hoy)" : ""}: ${detalle}`));
      lista.appendChild(columna);
    });
  }

  // ---------- Ánimo de la semana: las caras del avatar; el nombre siempre escrito ----------
  function dibujarSemanaAnimo(semana) {
    const caja = $("semana-animo-caja");
    if (!semana) { caja.hidden = true; return; }
    caja.hidden = false;
    UI.dibujarSemanaAnimo($("animo-semana-fila"), semana);
  }

  function dibujarAlbum(calcomanias) {
    const enlace = $("album-enlace");
    if (!calcomanias) { enlace.hidden = true; return; }
    enlace.textContent = `Mi álbum: ${calcomanias.ganadas} de ${calcomanias.total} calcomanías`;
    enlace.hidden = false;
  }

  // El check-in vive en Ánimo; desde aquí se hace o se mira, según si ya lo hizo hoy
  function dibujarEnlaceCheckin(animoHoy) {
    $("checkin-enlace-texto").textContent = animoHoy.registrado ? "Ver mi check-in de hoy" : "Hacer mi check-in de hoy";
  }

  // ---------- Qué se ve: cargando, error o el contenido ----------
  function dibujar() {
    const store = window.lumeaStore;
    const s = store.obtener();
    $("estado-cargando").hidden = !(store.cargando && !s.cargado);
    $("estado-error").hidden = !store.error;
    $("progreso-contenido").hidden = !s.cargado || store.error;
    if (!s.cargado) return;
    dibujarSemanaComidas(s.comidas_semana);
    dibujarSemanaAnimo(s.animo_hoy.historial_semana);
    dibujarAlbum(s.calcomanias);
    dibujarEnlaceCheckin(s.animo_hoy);
  }

  document.addEventListener("DOMContentLoaded", () => {
    const store = window.lumeaStore;
    $("estado-reintentar").addEventListener("click", () => store.cargarDesdeBackend(store.obtenerEmailUsuario()));
    store.suscribir(dibujar);
    dibujar();
  });
})();
