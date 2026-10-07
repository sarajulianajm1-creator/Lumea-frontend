// =====================================================================
// menu-privado.js — «Cerrar sesión» del menú lateral. El resto del menú es HTML
// que escribe herramientas/menu_privado.py. Necesita api.js antes.
// =====================================================================
document.addEventListener("click", (evento) => {
  const boton = evento.target.closest("[data-cerrar-sesion]");
  if (!boton) return;
  cerrarSesion();                    // api.js: borra la sesión (las dos claves)
  window.location.href = "index.html";
});
