/**
 * LUMEA · lumea-ui.js — pone en la pantalla lo que dice window.lumeaStore (lumea-state.js).
 *
 * Diseño de Sara: el HTML marca dónde va cada dato con clases «lumea-bind-…» y este archivo
 * las llena. Cambios al unirse con la gamificación:
 *   - Los números salen del backend tal cual (nada de «210/250 XP del día»: eso era el XP
 *     total del nivel; el XP del día es meta_diaria, y la meta es de XP, no de comidas).
 *   - Las caras de ánimo son las DiceBear del avatar (avatar.urls_por_estado). Sin internet
 *     la imagen se quita y queda el nombre del estado, que siempre está escrito.
 *   - Se quitó el avatar SVG de ejemplo: el avatar real vive en avatar.html.
 *   - Texto del servidor: textContent, nunca HTML armado a mano.
 * Necesita formato.js y lumea-state.js antes.
 */
(function () {
  "use strict";

  const F = window.LumeaFormato;
  const todos = (selector) => document.querySelectorAll(selector);
  const poner = (selector, texto) => todos(selector).forEach((el) => { el.textContent = texto; });

  function crear(etiqueta, clase, texto) {
    const el = document.createElement(etiqueta);
    if (clase) el.className = clase;
    if (texto != null) el.textContent = texto;
    return el;
  }

  // «Miércoles 7 de octubre», con la fecha del dispositivo (la hora ya no se muestra: rediseño R1)
  function actualizarFechaActual() {
    const ahora = new Date();
    let fecha = ahora.toLocaleDateString("es-ES", { weekday: "long", day: "numeric", month: "long" });
    fecha = fecha.charAt(0).toUpperCase() + fecha.slice(1);
    todos(".lumea-bind-fecha").forEach((el) => {
      const icono = crear("i", "bi bi-calendar-event me-1");
      icono.setAttribute("aria-hidden", "true");
      el.replaceChildren(icono, document.createTextNode(` ${fecha}`));
    });
  }

  // ---------- Caras de ánimo: las del avatar (DiceBear) ----------

  function urlDeCara(estado) {
    const a = window.lumeaStore && window.lumeaStore.obtener().avatar;
    if (!a) return null;
    if (estado) return (a.urls_por_estado && a.urls_por_estado[estado]) || null;
    return a.url_con_animo || a.url || null;
  }

  // Una silueta de Bootstrap Icons para cuando no hay cara (sin avatar o sin internet)
  function siluetaDeCara() {
    const icono = crear("i", "bi bi-person-fill lumea-cara__silueta");
    icono.setAttribute("aria-hidden", "true");
    return icono;
  }

  // Dibuja la cara de `estado` (o la del ánimo de hoy si no se pasa) dentro de `contenedor`.
  // Sin URL o sin internet queda la silueta: el nombre del estado va siempre escrito al lado.
  function ponerCara(contenedor, estado) {
    const url = urlDeCara(estado);
    if (!url) { contenedor.replaceChildren(siluetaDeCara()); return; }
    const img = document.createElement("img");
    img.alt = "";
    img.src = url;
    img.className = "lumea-cara__img";
    img.addEventListener("error", () => contenedor.replaceChildren(siluetaDeCara()));
    contenedor.replaceChildren(img);
  }

  // La fila de los 7 días con la cara del avatar de cada uno (Progreso y Ánimo). El nombre siempre va escrito.
  function dibujarSemanaAnimo(fila, semana) {
    fila.replaceChildren();
    semana.forEach((d) => {
      const dia = crear("div", "animo-day-pill" + (d.esHoy ? " today" : ""));
      dia.setAttribute("role", "listitem");
      if (d.esHoy) dia.setAttribute("aria-current", "date");
      const cara = crear("span", "lumea-cara animo-day-pill__cara");
      cara.setAttribute("aria-hidden", "true");
      if (d.estado) ponerCara(cara, d.estado);
      const nombre = d.estado ? (F.NOMBRE_ANIMO[d.estado] || d.estado) : "";
      const letra = crear("small", "animo-day-pill__letra fw-bold d-block", d.dia + (d.esHoy ? " (hoy)" : ""));
      letra.setAttribute("aria-hidden", "true");
      const rotulo = crear("span", "animo-day-pill__nombre", nombre);
      rotulo.setAttribute("aria-hidden", "true");
      const lector = d.futuro ? "todavía no llega" : (nombre || "sin check-in");
      dia.append(cara, letra, rotulo, crear("span", "solo-lector", `${d.nombre}${d.esHoy ? " (hoy)" : ""}: ${lector}`));
      fila.appendChild(dia);
    });
  }

  // ---------- Sincronizar todo con el estado ----------

  function sincronizarLumeaUI() {
    actualizarFechaActual();
    const store = window.lumeaStore;
    if (!store) return;
    const s = store.obtener();
    if (!s.cargado) return;                       // mientras llega, quedan los «--» del HTML
    const u = s.usuario;

    poner(".lumea-bind-nombre", u.nombre || (u.correo ? u.correo.split("@")[0] : "Estudiante"));
    poner(".lumea-bind-nivel", `Nivel ${u.nivel}`);

    const pct = F.porcentajeNivel(u);
    todos(".lumea-bind-xp-bar").forEach((barra) => {
      barra.style.width = `${pct}%`;
      barra.setAttribute("aria-valuenow", String(pct));
      barra.setAttribute("aria-label", u.xp_siguiente_nivel == null ? "Nivel máximo" : `Avance hacia el nivel ${u.nivel + 1}`);
    });
    poner(".lumea-bind-xp-text", F.textoNivel(u));
    poner(".lumea-bind-xp-valor", s.meta_diaria ? F.textoMeta(s.meta_diaria) : "--");

    poner(".lumea-bind-racha", F.textoRacha(u.racha_actual));
    poner(".lumea-bind-mejor-racha", F.textoRacha(u.mejor_racha));
    todos(".lumea-bind-racha-nota").forEach((el) => { el.textContent = F.notaRacha(u.racha_actual); });

    poner(".lumea-bind-comidas-count", `${s.comidas_hoy.length} de ${s.meta_comidas}`);
    const hechas = s.misiones.filter((m) => m.cumplida).length;
    poner(".lumea-bind-misiones-count", `${hechas} de ${s.misiones.length || 3}`);

    sincronizarProximaMision(s);

    // Ánimo de hoy: el nombre escrito y la cara del avatar
    const estado = s.animo_hoy.registrado ? s.animo_hoy.estado : null;
    poner(".lumea-bind-animo-hoy", estado ? (F.NOMBRE_ANIMO[estado] || estado) : "Sin registrar");
    todos("[data-cara]").forEach((el) => {
      const cual = el.getAttribute("data-cara");
      ponerCara(el, cual === "hoy" ? estado : cual);
    });

    // Bienvenida cálida (solo si el backend manda mensaje_regreso; nunca «perdiste XP»)
    const aviso = document.getElementById("aviso-regreso");
    if (aviso) {
      const texto = aviso.querySelector(".lumea-bind-regreso");
      if (u.mensaje_regreso) {
        if (texto) texto.textContent = u.mensaje_regreso;
        aviso.style.display = "flex";
      } else {
        aviso.style.display = "none";
      }
    }
  }

  // La primera misión sin cumplir; si ya están las tres, se celebra sin pedir nada más
  function sincronizarProximaMision(s) {
    const titulo = document.getElementById("proxima-mision-titulo");
    const detalle = document.getElementById("proxima-mision-xp");
    if (!titulo || !s.misiones.length) return;
    const pendiente = s.misiones.find((m) => !m.cumplida);
    if (!pendiente) {
      titulo.textContent = "Hoy cumpliste tus tres misiones";
      if (detalle) detalle.replaceChildren(document.createTextNode("Lo que registres ahora suma a tu día."));
      return;
    }
    titulo.textContent = pendiente.titulo;
    if (detalle) {
      detalle.replaceChildren(crear("span", "badge text-bg-warning me-1 fw-bold", `+${pendiente.recompensa} XP`),
                              document.createTextNode(pendiente.descripcion || ""));
    }
  }

  window.sincronizarLumeaUI = sincronizarLumeaUI;
  window.actualizarFechaActual = actualizarFechaActual;
  window.LumeaUI = { crear, ponerCara, urlDeCara, dibujarSemanaAnimo, sincronizar: sincronizarLumeaUI };

  document.addEventListener("DOMContentLoaded", () => {
    sincronizarLumeaUI();
    if (window.lumeaStore) window.lumeaStore.suscribir(sincronizarLumeaUI);
  });
})();
