// =====================================================================
// indexx.js — la lógica de Inicio (index-ingresado.html, el diseño es de Sara).
//
// Los datos (nivel, XP, racha, misiones, canasta) los pone lumea-ui.js desde el estado
// de lumea-state.js; aquí solo está lo que hace esta pantalla por su cuenta:
//   - el check-in rápido de ánimo (POST /estado-animo por el estado, con celebración)
//   - el atajo «Foto directa» (la foto pasa a alimentos.html una sola vez)
//   - cerrar la bienvenida de regreso
// Toda la conexión va por api.js; aquí no hay direcciones ni fetch.
// Necesita api.js, formato.js, lumea-state.js y lumea-ui.js antes.
// =====================================================================
(function () {
  "use strict";

  const F = window.LumeaFormato;
  const LADO_MAX_PX = 1024;                    // igual que la cámara: la foto se reduce antes de pasar
  const $ = (id) => document.getElementById(id);

  // ---------- Check-in rápido de ánimo ----------

  // Marca el estado de hoy; una vez registrado, los demás quedan en reposo (se registra una vez al día)
  function pintarCheckin() {
    const s = window.lumeaStore.obtener();
    if (!s.cargado) return;
    const registrado = s.animo_hoy.registrado;
    document.querySelectorAll(".btn-face-mood").forEach((boton) => {
      const activo = registrado && boton.dataset.estado === s.animo_hoy.estado;
      boton.classList.toggle("active", activo);
      boton.setAttribute("aria-pressed", String(activo));
      boton.disabled = registrado && !activo;
    });
    const aviso = $("checkin-confirmado");
    if (aviso) {
      aviso.hidden = !registrado;
      if (registrado) aviso.textContent = `Hoy llegaste: ${F.NOMBRE_ANIMO[s.animo_hoy.estado] || s.animo_hoy.estado}. Tu check-in ya está registrado.`;
    }
  }

  async function marcarAnimo(estado) {
    const antes = window.lumeaStore.obtener().animo_hoy.registrado;
    const respuesta = await window.lumeaStore.registrarAnimo(estado);
    if (!respuesta || antes) return;
    // Un solo rebote en la forma de la canasta (el CSS lo apaga con movimiento reducido)
    const forma = $("shape-animo");
    if (forma) {
      forma.classList.add("animate-shape-bounce");
      forma.addEventListener("animationend", () => forma.classList.remove("animate-shape-bounce"), { once: true });
    }
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
      window.lumeaStore.mostrarNotificacion("No se pudo abrir la foto. Prueba con «Cámara en vivo».");
    }
  }

  // ---------- Conectar ----------

  document.addEventListener("DOMContentLoaded", () => {
    const store = window.lumeaStore;
    document.querySelectorAll(".btn-face-mood").forEach((boton) => {
      boton.addEventListener("click", () => marcarAnimo(boton.dataset.estado));
    });
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
