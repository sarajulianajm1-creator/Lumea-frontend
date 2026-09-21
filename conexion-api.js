// conexion-api.js — Conexión del frontend LUMEA con el backend Flask.
//
// Sin autenticación real: el correo es el identificador único del perfil
// (perfil.email es UNIQUE en la base de datos), la contraseña que pide el
// formulario NO se envía al backend. Es una decisión de alcance deliberada
// para datos de hábitos escolares, documentada en DEFENSA_TECNICA_LUMEA.md
// del repo de Backend -- no es un sistema de seguridad real.
//
// Cambia esta URL si el backend corre en otra dirección/puerto (ej. el día
// de la sustentación, si no es localhost).
const API_BASE_URL = "http://127.0.0.1:5001";

async function crearOActualizarPerfil(datosPerfil) {
  const respuesta = await fetch(`${API_BASE_URL}/perfil`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datosPerfil),
  });
  const cuerpo = await respuesta.json();
  return { ok: respuesta.ok, cuerpo };
}

async function buscarPerfilPorCorreo(email) {
  const url = `${API_BASE_URL}/perfil?email=${encodeURIComponent(email)}`;
  const respuesta = await fetch(url);
  const cuerpo = await respuesta.json();
  return { ok: respuesta.ok, cuerpo };
}

// Guarda el correo de la "sesión" (sin autenticación real -- ver nota
// arriba) para que otras páginas puedan saber quién está usando la app.
function guardarSesion(email) {
  localStorage.setItem("lumea_email", email);
}

function obtenerSesion() {
  return localStorage.getItem("lumea_email");
}

function cerrarSesion() {
  localStorage.removeItem("lumea_email");
}

// Envía la foto a /predecir. `email` es opcional (multipart/form-data,
// igual que en app.py) -- si hay sesión activa, la predicción queda ligada
// a ese perfil en historial_comida; si no, igual se predice pero sin dueño.
async function predecirComida(archivoImagen, email) {
  const formulario = new FormData();
  formulario.append("file", archivoImagen);
  if (email) {
    formulario.append("email", email);
  }
  const respuesta = await fetch(`${API_BASE_URL}/predecir`, {
    method: "POST",
    body: formulario,
  });
  const cuerpo = await respuesta.json();
  return { ok: respuesta.ok, cuerpo };
}

async function obtenerHistorial(email) {
  const url = `${API_BASE_URL}/historial?email=${encodeURIComponent(email)}`;
  const respuesta = await fetch(url);
  const cuerpo = await respuesta.json();
  return { ok: respuesta.ok, cuerpo };
}

// Confirma a mano cuál alimento es cuando /predecir respondió
// seleccion_manual=true (certeza baja, o el grupo ajiaco/sancocho/mondongo/
// dulces, que siempre piden confirmación). `email` opcional, mismo patrón
// que predecirComida.
async function confirmarAlimento(alimentoCodigo, email) {
  const cuerpoPeticion = { alimento_codigo: alimentoCodigo };
  if (email) {
    cuerpoPeticion.email = email;
  }
  const respuesta = await fetch(`${API_BASE_URL}/confirmar-alimento`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cuerpoPeticion),
  });
  const cuerpo = await respuesta.json();
  return { ok: respuesta.ok, cuerpo };
}
