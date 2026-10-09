// api.js — Conexión del frontend LUMEA con el backend Flask.
//
// ÚNICO lugar donde está la dirección del backend. Todas las páginas llaman
// al backend con las funciones de este archivo; ninguna escribe la URL a
// mano. Guía completa: Backend/GUIA_FRONTEND_SARA.md.
//
// Todas las funciones devuelven { ok, cuerpo }: ok es true si el backend
// respondió 2xx, y cuerpo es el JSON de la respuesta.
//
// Sesión: el login con contraseña (POST /login, Bcrypt) verifica la
// contraseña; después, el correo se guarda en localStorage y las demás rutas
// identifican a la persona por el correo (todavía no hay token de sesión).
//
// Cambia esta URL si el backend corre en otra dirección/puerto (ej. el día
// de la sustentación, si no es localhost).
const API_BASE_URL = `http://${location.hostname}:5002`;

// Ayudantes internos: hacen el fetch y convierten la respuesta a JSON.
async function _getJSON(ruta, parametros) {
  const url = new URL(`${API_BASE_URL}${ruta}`);
  Object.entries(parametros || {}).forEach(([clave, valor]) => url.searchParams.set(clave, valor));
  const respuesta = await fetch(url);
  const cuerpo = await respuesta.json();
  return { ok: respuesta.ok, cuerpo };
}

async function _postJSON(ruta, datos) {
  const respuesta = await fetch(`${API_BASE_URL}${ruta}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
  const cuerpo = await respuesta.json();
  return { ok: respuesta.ok, cuerpo };
}

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
  localStorage.removeItem("lumea_usuario_email");   // clave vieja de las páginas de Sara: una sola sesión
}

// Una sola sesión para toda la app. Lee también `lumea_usuario_email`, la clave
// que guardaban las páginas de Sara antes de unirse: quien ya la tenía no pierde la sesión.
function obtenerSesion() {
  return localStorage.getItem("lumea_email") || localStorage.getItem("lumea_usuario_email");
}

function cerrarSesion() {
  localStorage.removeItem("lumea_email");
  localStorage.removeItem("lumea_usuario_email");
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

// ===== Login con contraseña =====
// POST /login responde 200 con el perfil, o 401 con el MISMO mensaje si el
// correo no existe o la contraseña está mal (y una "ayuda" para cuentas de
// antes de las contraseñas). Para crear la cuenta, crearOActualizarPerfil()
// debe llevar "contraseña" (mínimo 6 caracteres).
function iniciarSesion(email, contrasena) {
  return _postJSON("/login", { email, "contraseña": contrasena });
}

// ===== Estado de ánimo =====
// estado: "muy_mal" | "mal" | "neutral" | "bien" | "muy_bien"
function registrarEstadoAnimo(email, estado) {
  return _postJSON("/estado-animo", { email, estado });
}

// `dias` es opcional: con 7 solo llegan los registros de los últimos 7 días
// (hoy cuenta), aunque haya muchos. Sin `dias` llegan los últimos 30.
// Respuesta: { historial: [{ id, fecha: "Mon, 05 Oct 2026 00:00:00 GMT", estado }] }
function obtenerEstadosAnimo(email, dias) {
  const parametros = { email };
  if (dias) parametros.dias = dias;
  return _getJSON("/estado-animo", parametros);
}

// ===== Gamificación (Backend/CONTRATO_GAMIFICACION.md) =====
function obtenerProgreso(email) {
  return _getJSON("/progreso", { email });
}

// Calcomanías (el álbum): las 10, con `ganada` y `fecha`. 404 si el correo no tiene perfil.
// Respuesta: { ganadas, total, calcomanias: [{ id, nombre, descripcion, como_se_gana, rol, ganada, fecha }] }
function obtenerCalcomanias(email) {
  return _getJSON("/calcomanias", { email });
}

// Avatar por capas (Figma): base + ropa + accesorio.
function obtenerAvatar(email) {
  return _getJSON("/avatar", { email });
}

function elegirBaseAvatar(email, baseId) {
  return _postJSON("/avatar/base", { email, base_id: baseId });
}

// tipo: "ropa" | "accesorio"
function equiparObjeto(email, tipo, itemId) {
  return _postJSON("/avatar/equipar", { email, tipo, item_id: itemId });
}

function quitarObjeto(email, tipo) {
  return _postJSON("/avatar/quitar", { email, tipo });
}

// Avatares DiceBear (respaldo si no llegan las imágenes de Figma).
function obtenerAvataresDiceBear(email) {
  return _getJSON("/avatares", { email });
}

function elegirAvatarDiceBear(email, avatarId) {
  return _postJSON("/avatar", { email, avatar_id: avatarId });
}
