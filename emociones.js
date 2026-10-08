// =====================================================================
// emociones.js — la lógica de Ánimo (emociones.html, el diseño es de Sara).
//
// Eliges uno de los cinco estados del backend (muy_mal a muy_bien) y la cara grande, la de TU avatar
// (DiceBear, avatar.urls_por_estado de GET /progreso), cambia en vivo. Los cinco botones llevan las
// caras del set que la persona eligió (caras-checkin.js), o solo la palabra si no eligió. Guardar hace
// POST /estado-animo por api.js y celebra con la misma respuesta (LumeaCelebrar).
// Todos los estados dan las mismas semillas: no se premia estar bien. Sin internet no se ven las
// caras, pero el nombre del estado siempre está escrito.
// Necesita api.js, formato.js, lumea-state.js y lumea-ui.js antes.
// =====================================================================
(function () {
  "use strict";

  const F = window.LumeaFormato;
  const UI = window.LumeaUI;
  const $ = (id) => document.getElementById(id);

  // Lo que dice cada estado (neutro: sin género, sin diagnosticar, sin presionar)
  const DESCRIPCION = {
    muy_mal: { titulo: "Me siento muy mal", sub: "Está bien no estar bien. Tómate una pausa: lo que sientes importa." },
    mal: { titulo: "Me siento mal", sub: "Un día complejo o con cansancio acumulado. Permítete descansar y soltar la presión." },
    neutral: { titulo: "Me siento neutral", sub: "Un día en equilibrio, mirando tu entorno paso a paso." },
    bien: { titulo: "Me siento bien", sub: "Con calma y buena disposición para tus metas y tus alimentos." },
    muy_bien: { titulo: "Me siento muy bien", sub: "¡Con energía y vitalidad! Disfruta tu día." },
  };

  let elegido = null;

  // La cara grande y los textos del estado que se está mirando
  function mostrarEstado(estado) {
    const d = DESCRIPCION[estado];
    $("texto-estado-seleccionado").textContent = d ? d.titulo : "Elige cómo te sientes";
    $("subtexto-estado").textContent = d ? d.sub : "Todas las emociones dan las mismas semillas: no se premia estar siempre bien.";
    UI.ponerCara($("cara-grande"), estado);
    document.querySelectorAll(".animo-cara").forEach((boton) => {
      boton.setAttribute("aria-pressed", String(boton.dataset.estado === estado));   // caras-checkin.js anima la elegida
    });
  }

  function elegir(estado) {
    elegido = estado;
    mostrarEstado(estado);
    $("btn-guardar-animo").disabled = false;
  }

  // Ya registrado hoy: se muestra ese estado y no se puede cambiar (se registra una vez al día)
  function dibujar() {
    const store = window.lumeaStore;
    const s = store.obtener();
    $("estado-error").hidden = !store.error;
    if (!s.cargado) return;
    const guardar = $("btn-guardar-animo");
    const confirmacion = $("confirmacion-animo");
    if (s.animo_hoy.registrado) {
      elegido = s.animo_hoy.estado;
      mostrarEstado(elegido);
      guardar.disabled = true;
      guardar.textContent = "Tu ánimo de hoy ya está registrado";
      confirmacion.hidden = false;
      confirmacion.textContent = "Listo: hoy ya hiciste tu check-in. Se registra una vez al día.";
      document.querySelectorAll(".animo-cara").forEach((b) => { b.disabled = b.dataset.estado !== elegido; });
    } else {
      if (!elegido) mostrarEstado(null);
      guardar.disabled = !elegido;
    }
    const caja = $("semana-animo-caja");
    caja.hidden = !s.animo_hoy.historial_semana;
    if (s.animo_hoy.historial_semana) UI.dibujarSemanaAnimo($("animo-semana-fila"), s.animo_hoy.historial_semana);
  }

  async function guardar() {
    if (!elegido) return;
    const boton = $("btn-guardar-animo");
    boton.disabled = true;
    const respuesta = await window.lumeaStore.registrarAnimo(elegido);   // celebra con la misma respuesta
    if (!respuesta) boton.disabled = false;                               // falló: se puede intentar otra vez
  }

  document.addEventListener("DOMContentLoaded", () => {
    const store = window.lumeaStore;
    document.querySelectorAll(".animo-cara").forEach((boton) => {
      boton.addEventListener("click", () => elegir(boton.dataset.estado));
    });
    $("btn-guardar-animo").addEventListener("click", guardar);
    $("estado-reintentar").addEventListener("click", () => store.cargarDesdeBackend(store.obtenerEmailUsuario()));
    store.suscribir(dibujar);
    dibujar();
  });
})();
