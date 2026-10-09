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

  // «Miércoles, 7 de octubre», con la fecha del dispositivo (sin hora y sin ícono: rediseño R1 y R2).
  // Va en un <time>, así que también se le pone su fecha en formato de máquina (datetime).
  function actualizarFechaActual() {
    const ahora = new Date();
    let fecha = ahora.toLocaleDateString("es-ES", { weekday: "long", day: "numeric", month: "long" });
    fecha = fecha.charAt(0).toUpperCase() + fecha.slice(1);
    const iso = `${ahora.getFullYear()}-${String(ahora.getMonth() + 1).padStart(2, "0")}-${String(ahora.getDate()).padStart(2, "0")}`;
    todos(".lumea-bind-fecha").forEach((el) => {
      el.textContent = fecha;
      if (el.tagName === "TIME") el.setAttribute("datetime", iso);
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
    // El compañero se dibuja en el navegador (companero.js, DiceBear local): no se le pide nada a api.dicebear.com
    const img = window.LumeaCompanero ? window.LumeaCompanero.imagen(url, null, "lumea-cara__img") : null;
    if (!img) { contenedor.replaceChildren(siluetaDeCara()); return; }
    img.addEventListener("error", () => contenedor.replaceChildren(siluetaDeCara()));
    contenedor.replaceChildren(img);
  }

  // La fila de los 7 días (L a D) con la cara del compañero de cada uno (Progreso y Ánimo). La palabra del ánimo va en el nombre
  // accesible y en el tooltip (title), no debajo: todas las caras del mismo color, porque el color no ordena los ánimos.
  //   con check-in: la cara sobre un círculo · pasado sin check-in: círculo punteado · hoy: con anillo · futuro: tenue.
  function dibujarSemanaAnimo(fila, semana) {
    fila.replaceChildren();
    semana.forEach((d) => {
      const nombre = d.estado ? (F.NOMBRE_ANIMO[d.estado] || d.estado) : "";
      const lector = d.futuro ? "todavía no llega" : (nombre || "sin check-in");
      const frase = `${d.nombre}${d.esHoy ? " (hoy)" : ""}: ${lector}`;
      const estado = d.estado ? " animo-dia--con" : (d.futuro ? " animo-dia--futuro" : " animo-dia--sin");
      const dia = crear("div", "animo-dia" + estado + (d.esHoy ? " animo-dia--hoy" : ""));
      dia.setAttribute("role", "listitem");
      dia.title = frase;                                           // el tooltip: la palabra del ánimo
      if (d.esHoy) dia.setAttribute("aria-current", "date");
      const circulo = crear("span", "animo-dia__circulo");
      circulo.setAttribute("aria-hidden", "true");
      if (d.estado) {
        const cara = crear("span", "lumea-cara animo-dia__cara");
        ponerCara(cara, d.estado);
        circulo.appendChild(cara);
      }
      const letra = crear("span", "animo-dia__letra", d.dia);
      letra.setAttribute("aria-hidden", "true");
      dia.append(circulo, letra, crear("span", "solo-lector", frase));
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
    poner(".lumea-bind-nivel", `Etapa ${u.nivel}`);

    const pct = F.porcentajeNivel(u);
    todos(".lumea-bind-xp-bar").forEach((barra) => {
      barra.style.width = `${pct}%`;
      barra.setAttribute("aria-valuenow", String(pct));
      barra.setAttribute("aria-label", u.xp_siguiente_nivel == null ? "Etapa máxima" : `Avance hacia la etapa ${u.nivel + 1}`);
    });
    poner(".lumea-bind-xp-text", F.textoNivel(u));
    poner(".lumea-bind-xp-valor", s.meta_diaria ? F.textoMeta(s.meta_diaria) : "--");

    poner(".lumea-bind-racha", F.textoRacha(u.racha_actual));
    poner(".lumea-bind-mejor-racha", F.textoRacha(u.mejor_racha));
    todos(".lumea-bind-racha-nota").forEach((el) => { el.textContent = F.notaRacha(u.racha_actual); });

    poner(".lumea-bind-comidas-count", `${s.comidas_hoy.length} de ${s.meta_comidas}`);
    // La barra de comidas de hoy: lo que lleva sobre la meta de comidas (nunca pasa de 100 %)
    const pctComidas = s.meta_comidas > 0 ? Math.min(100, Math.round((s.comidas_hoy.length / s.meta_comidas) * 100)) : 0;
    todos(".lumea-bind-comidas-bar").forEach((barra) => {
      barra.style.width = `${pctComidas}%`;
      barra.setAttribute("aria-valuenow", String(pctComidas));
    });
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

    // Bienvenida cálida (solo si el backend manda mensaje_regreso; nunca «perdiste semillas»)
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

  // La primera misión sin cumplir, con su recompensa en un chip; si ya están las tres, se celebra sin pedir nada más
  function sincronizarProximaMision(s) {
    const titulo = document.getElementById("proxima-mision-titulo");
    const recompensa = document.getElementById("proxima-mision-xp");
    if (!titulo || !s.misiones.length) return;
    const pendiente = s.misiones.find((m) => !m.cumplida);
    if (!pendiente) {
      titulo.textContent = "Hoy cumpliste tus tres misiones";
      if (recompensa) recompensa.hidden = true;
      return;
    }
    titulo.textContent = pendiente.titulo;
    if (recompensa) {
      recompensa.textContent = `+${F.semillas(pendiente.recompensa)}`;
      recompensa.hidden = false;
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
