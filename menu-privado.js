// =====================================================================
// menu-privado.js — «Cerrar sesión» del menú lateral y el orden de la entrada escalonada de las tarjetas.
// El resto del menú es HTML que escribe herramientas/menu_privado.py. Necesita api.js antes.
// =====================================================================
document.addEventListener("click", (evento) => {
  const boton = evento.target.closest("[data-cerrar-sesion]");
  if (!boton) return;
  cerrarSesion();                    // api.js: borra la sesión (las dos claves)
  window.location.href = "index.html";
});

// Entrada escalonada (P10): a cada bloque de la pantalla (el encabezado y las tarjetas) se le pone su --orden, y el CSS lo desfasa
// 50 ms (--m-escalon). Los bloques que ya se ven cuentan 0, 1, 2…; los que aparecen más tarde (datos que llegan del servidor) cuentan
// dentro de su grupo, y el orden nunca pasa de 6 para que la pantalla entera esté lista en menos de medio segundo.
(function () {
  const bloques = [...document.querySelectorAll("main.contenido :is(header, .tarjeta, .inicio__franja, .camara > section, .avatar-panel)")]
    .filter((e) => !(e.parentElement && e.parentElement.closest(".tarjeta")));
  let visibles = 0;
  const porGrupo = new Map();
  bloques.forEach((e) => {
    const oculto = e.closest("[hidden]");
    let orden;
    if (!oculto) orden = visibles++;
    else if (oculto === e) orden = visibles;
    else { orden = porGrupo.get(oculto) || 0; porGrupo.set(oculto, orden + 1); }
    e.style.setProperty("--orden", String(Math.min(orden, 6)));
  });
})();
