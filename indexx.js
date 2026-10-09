// =====================================================================
// indexx.js — la lógica de Inicio (index-ingresado.html).
//
// Los datos (nivel, XP, racha, misión, comidas) los pone lumea-ui.js desde el estado
// de lumea-state.js; aquí solo está lo que hace esta pantalla por su cuenta:
//   - el check-in de ánimo: eliges una cara de tu compañero (aria-pressed; la elegida se anima, companero.js)
//     y la guardas con «Guardar mi ánimo» (POST /estado-animo por el estado, con celebración)
//   - el atajo «Foto directa» (la foto pasa a alimentos.html una sola vez)
//   - la tarjeta «Elige tus colores» (cuándo se muestra y cómo se cierra)
//   - cerrar la bienvenida de regreso
// Toda la conexión va por api.js; aquí no hay direcciones ni llamadas a mano.
// Necesita api.js, formato.js, lumea-state.js y lumea-ui.js antes.
// =====================================================================
(function () {
  "use strict";

  const F = window.LumeaFormato;
  const LADO_MAX_PX = 1024;                    // igual que la cámara: la foto se reduce antes de pasar
  const $ = (id) => document.getElementById(id);

  // ---------- Check-in de ánimo ----------

  let elegido = null;                          // el estado que la persona tocó (todavía sin guardar)
  let guardando = false;

  // Dibuja el check-in según lo elegido y lo ya registrado hoy. Se registra UNA vez al día:
  // una vez registrado, los demás estados quedan en reposo y el botón de guardar se esconde.
  function pintarCheckin() {
    const s = window.lumeaStore.obtener();
    const registrado = s.cargado && s.animo_hoy.registrado;
    if (registrado) elegido = s.animo_hoy.estado;
    document.querySelectorAll(".animo-cara").forEach((boton) => {
      const activo = boton.dataset.estado === elegido;
      boton.setAttribute("aria-pressed", String(activo));
      boton.disabled = registrado && !activo;
    });
    const guardar = $("btn-guardar-animo-inicio");
    guardar.hidden = registrado;
    guardar.disabled = !elegido || guardando;
    const aviso = $("checkin-confirmado");
    aviso.hidden = !registrado;
    if (registrado) aviso.textContent = `Hoy llegaste: ${F.NOMBRE_ANIMO[s.animo_hoy.estado] || s.animo_hoy.estado}. Tu check-in ya está registrado.`;
    if (window.LumeaCompanero) window.LumeaCompanero.pintarCheckin();       // las cinco caras, quietas (data-caras-quietas)
    pintarSaludo();
  }

  // El compañero que saluda junto al «Hola, Ana»: la cara del ánimo de hoy (neutral si todavía no hay check-in), despacio.
  // Es lo único que se mueve en Inicio; al guardar el ánimo cambia a esa cara. Decorativo: sin imagen, el saludo queda igual.
  function pintarSaludo() {
    const hueco = $("companero-saluda");
    const C = window.LumeaCompanero, UI = window.LumeaUI;
    if (!hueco || !C || !UI) return;
    const s = window.lumeaStore.obtener();
    const estado = s.cargado && s.animo_hoy.registrado ? s.animo_hoy.estado : "neutral";
    const direccion = UI.urlDeCara(estado);
    const actual = hueco.firstElementChild;
    if (actual && actual.dataset.fuente === C.url(direccion, "slow")) return;     // la misma cara: no se reinicia
    const img = C.imagen(direccion, "slow", "inicio__companero-img");
    if (img) { img.addEventListener("error", () => hueco.replaceChildren()); hueco.replaceChildren(img); } else hueco.replaceChildren();
  }

  async function guardarAnimo() {
    if (!elegido || guardando) return;
    guardando = true;
    pintarCheckin();
    await window.lumeaStore.registrarAnimo(elegido);   // celebra con la misma respuesta; si falla, avisa y se puede intentar otra vez
    guardando = false;
    pintarCheckin();
  }

  // ---------- ¿Sabías que…? del día ----------
  // El dato curioso de hoy (el mismo para todas las personas). Sin dato o con la petición caída, la tarjeta no se dibuja.
  async function cargarDatoDelDia() {
    const tarjeta = $("card-dato-dia");
    if (!tarjeta || typeof obtenerDatoDelDia !== "function") return;
    try {
      const { ok, cuerpo } = await obtenerDatoDelDia();                       // api.js
      const texto = ok && cuerpo && typeof cuerpo.dato_curioso === "string" ? cuerpo.dato_curioso.trim() : "";
      if (!texto) return;
      $("dato-dia-alimento").textContent = cuerpo.nombre || "";
      $("dato-dia-texto").textContent = texto;
      tarjeta.hidden = false;
      if (window.LumeaLeerMas) window.LumeaLeerMas.conectar($("dato-dia-texto"), $("dato-dia-mas")).ajustar(true);
    } catch (e) { /* sin dato: la tarjeta no se dibuja */ }
  }

  // ---------- Elige tus colores ----------

  // localStorage y sessionStorage pueden fallar (modo privado): nunca rompen la pantalla
  function leer(almacen, clave) { try { return window[almacen].getItem(clave); } catch (e) { return null; } }
  function guardar(almacen, clave, valor) { try { window[almacen].setItem(clave, valor); } catch (e) {} }

  // La tarjeta se abre al entrar si todavía falta la paleta y la persona no la cerró.
  // Una vez abierta se queda abierta aunque elija una paleta: se cierra con «Listo» o «Ahora no».
  //   Listo     -> no vuelve a aparecer (se recuerda en el navegador; todo se cambia luego en Avatar)
  //   Ahora no  -> se esconde solo durante esta sesión
  function prepararTarjetaDeColores() {
    const tarjeta = $("card-colores");
    if (!tarjeta || !window.LumeaTema) return;
    const falta = !window.LumeaTema.paletaActual();
    const cerrada = leer("localStorage", "lumea-colores-listo") === "1" || leer("sessionStorage", "lumea-colores-ahora-no") === "1";
    tarjeta.hidden = !(falta && !cerrada);
    const cerrar = (almacen, clave) => {
      guardar(almacen, clave, "1");
      tarjeta.hidden = true;
      const principal = document.querySelector("[data-accion-principal]");
      if (principal) principal.focus();                  // el foco no se pierde: pasa a la acción principal
    };
    $("btn-colores-listo").addEventListener("click", () => cerrar("localStorage", "lumea-colores-listo"));
    $("btn-colores-ahora-no").addEventListener("click", () => cerrar("sessionStorage", "lumea-colores-ahora-no"));
  }

  // ---------- Foto directa: del celular a la cámara de registro ----------

  // Reduce la foto y la deja en sessionStorage para que alimentos.html la analice (y la borre)
  async function pasarFotoALaCamara(archivo) {
    try {
      const imagen = await createImageBitmap(archivo);
      const k = Math.min(1, LADO_MAX_PX / Math.max(imagen.width, imagen.height));
      const lienzo = document.createElement("canvas");
      lienzo.width = Math.round(imagen.width * k);
      lienzo.height = Math.round(imagen.height * k);
      lienzo.getContext("2d").drawImage(imagen, 0, 0, lienzo.width, lienzo.height);
      sessionStorage.setItem("lumea_foto_temporal", lienzo.toDataURL("image/jpeg", 0.9));
      window.location.href = "alimentos.html";
    } catch (e) {
      window.lumeaStore.mostrarNotificacion("No se pudo abrir la foto. Prueba con «Registrar comida».");
    }
  }

  // ---------- Conectar ----------

  document.addEventListener("DOMContentLoaded", () => {
    const store = window.lumeaStore;
    document.querySelectorAll(".animo-cara").forEach((boton) => {
      boton.addEventListener("click", () => { elegido = boton.dataset.estado; pintarCheckin(); });
    });
    $("btn-guardar-animo-inicio").addEventListener("click", guardarAnimo);
    prepararTarjetaDeColores();
    cargarDatoDelDia();
    const foto = $("input-foto-directa-home");
    if (foto) foto.addEventListener("change", () => { if (foto.files[0]) pasarFotoALaCamara(foto.files[0]); });
    const cerrar = document.querySelector("[data-cerrar-aviso]");
    if (cerrar) cerrar.addEventListener("click", () => { $("aviso-regreso").style.display = "none"; });

    let avisoError = false;
    store.suscribir(() => {
      pintarCheckin();
      if (store.error && !avisoError) {
        avisoError = true;
        store.mostrarNotificacion("No pudimos cargar tu progreso. ¿Está encendido el servidor?");
      }
    });
    pintarCheckin();
  });
})();
