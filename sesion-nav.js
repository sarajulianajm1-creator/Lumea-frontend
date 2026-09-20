// sesion-nav.js — Llena el bloque de sesión de la barra de navegación
// (botones de Iniciar Sesión/Crear Cuenta, o el correo + Cerrar Sesión si
// ya hay una "sesión" activa -- ver la nota de conexion-api.js: es solo el
// correo guardado en localStorage, no autenticación real).
document.addEventListener("DOMContentLoaded", () => {
  const contenedor = document.getElementById("navSesion");
  if (!contenedor) return;

  const email = obtenerSesion();

  if (email) {
    contenedor.innerHTML = `
      <span class="small text-secondary me-2"><i class="bi bi-person-check me-1"></i>${email}</span>
      <button id="btnCerrarSesion" class="btn btn-lumea-outline rounded-pill px-3 py-2">
        <i class="bi bi-box-arrow-right me-1"></i> Cerrar Sesión
      </button>
    `;
    document.getElementById("btnCerrarSesion").addEventListener("click", () => {
      cerrarSesion();
      window.location.href = "index.html";
    });
  } else {
    contenedor.innerHTML = `
      <a href="iniciar-sesion.html" class="btn btn-lumea-outline rounded-pill px-3 py-2 text-decoration-none text-center">
        <i class="bi bi-box-arrow-in-right me-1"></i> Iniciar Sesión
      </a>
      <a href="crear-cuenta.html" class="btn btn-lumea rounded-pill px-3 py-2 text-decoration-none text-center">
        <i class="bi bi-person-plus me-1"></i> Crear Cuenta
      </a>
    `;
  }
});
