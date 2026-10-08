// Decisión de Isabella, 7 oct 2026: se muestran.
// true  -> el resultado trae UNA línea secundaria: «Calorías aproximadas: 60 kcal por 100 g»
//          (sin color de alerta ni juicio).
// false -> las calorías no se dibujan.
// Es lo único que hay que cambiar para quitarlas de la pantalla.
const MOSTRAR_CALORIAS = true;

// =====================================================================
// lumea-camara.js — LÓGICA de la cámara (sin diseño). Necesita api.js antes.
//
// Funciona con CUALQUIER diseño, siempre que la página tenga estos id
// (los que faltan se ignoran; ninguno rompe la página):
//
//   Cámara:     webcam (<video>), btn-encender, btn-tomar, btn-otra,
//               btn-apagar, btn-subir, visor-vacio (se esconde con cámara o foto)
//   Resultado:  resultado (el contenedor: lleva data-estado="segura" o "duda"
//               cuando hay respuesta, para que el CSS pinte «IA segura» o «IA duda»),
//               backend-alimento, backend-precision, backend-medidor, backend-energia,
//               backend-sellos, backend-consejos (bloques de consejo), backend-dato (+ btn-dato-mas: «Leer más»), backend-mensaje,
//               backend-opciones (botones para confirmar), backend-estado,
//               backend-foto (<img> con la foto que se analiza),
//               backend-logros (<ul>: semillas, misiones, calcomanías, etapa, meta del día)
//   Celebración: si la página carga pegatinas.js y celebracion.js (en ese
//               orden), después de cada resultado se llama a
//               LumeaCelebrar(r.gamificacion). Si no están, no pasa nada.
//   Sesión:     sin-sesion (aviso) y flujo-registro (la cámara): sin
//               correo guardado se muestra el aviso y no se registra nada
//
// Flujo: getUserMedia -> <video> -> <canvas> -> JPEG -> File -> FormData
//        (campo "file" + correo de la sesión) -> POST /predecir (api.js)
// Todo el texto del servidor se escribe con textContent (nunca innerHTML).
// =====================================================================
(function () {
  "use strict";

  const LADO_MAX_PX = 1024;            // la foto se reduce antes de subirla
  const TEXTO_SELLO = {                // códigos de Backend/sellos.py
    sodio: "EXCESO EN SODIO",
    azucares: "EXCESO EN AZÚCARES",
    grasas_saturadas: "EXCESO EN GRASAS SATURADAS",
    grasas_trans: "EXCESO EN GRASAS TRANS",
    edulcorantes: "CONTIENE EDULCORANTES",
  };

  const $ = (id) => document.getElementById(id);
  const poner = (id, texto) => { const el = $(id); if (el) el.textContent = texto; };
  // «EXCESO EN AZÚCARES» -> «Exceso en azúcares»: el nombre accesible del sello va en minúsculas normales
  // para que el lector de pantalla lo lea como una frase y no lo deletree
  const enFrase = (t) => t.charAt(0) + t.slice(1).toLowerCase();

  let stream = null, ocupado = false, catalogo = null;
  const video = $("webcam");
  const canvas = document.createElement("canvas");            // invisible: solo para capturar
  const inputArchivo = Object.assign(document.createElement("input"),
    { type: "file", accept: "image/*", hidden: true });
  document.body.appendChild(inputArchivo);
  const email = (typeof obtenerSesion === "function") ? obtenerSesion() : null;

  // ---------- Sin sesión: nada se registra sin dueño (de registrar-comida.html) ----------
  if (!email && $("sin-sesion")) {
    $("sin-sesion").hidden = false;
    if ($("flujo-registro")) $("flujo-registro").hidden = true;
    return;
  }

  // ---------- Estado de los botones (un solo lugar decide) ----------
  function actualizarBotones() {
    const on = stream !== null;
    const set = (id, deshabilitado) => { const b = $(id); if (b) b.disabled = deshabilitado; };
    set("btn-encender", on || ocupado);
    set("btn-tomar", !on || ocupado);
    set("btn-apagar", !on || ocupado);
    set("btn-otra", ocupado);
    set("btn-subir", ocupado);
    actualizarVisor();
  }

  // El visor vacío («La cámara está apagada» + «Encender cámara») solo se ve con la cámara apagada y sin foto
  function actualizarVisor() {
    const vacio = $("visor-vacio");
    if (vacio) vacio.hidden = stream !== null || urlFoto !== null;
  }

  // ---------- Cámara ----------
  async function encender() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      poner("backend-estado", location.protocol === "file:"
        ? "Abre esta página desde un servidor (http://localhost), no con doble clic."
        : "Este navegador no permite la cámara en esta dirección.");
      return;
    }
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 1280 }, height: { ideal: 960 } }, audio: false });
      if (video) { video.srcObject = stream; await video.play(); }
      poner("backend-estado", "Cámara lista. Pon el plato dentro del cuadro.");
    } catch (e) {
      stream = null;
      const causas = {
        NotAllowedError: "Permiso de cámara denegado: permítela en el navegador y en Ajustes del Sistema → Privacidad → Cámara.",
        NotFoundError: "No se encontró ninguna cámara.",
        NotReadableError: "Otra aplicación está usando la cámara.",
      };
      poner("backend-estado", causas[e.name] || `No se pudo abrir la cámara (${e.name}). Usa «Subir foto».`);
    }
    actualizarBotones();
  }

  function apagar() {
    if (stream) stream.getTracks().forEach((t) => t.stop());
    stream = null;
    if (video) video.srcObject = null;
    actualizarBotones();
  }

  function capturar() {
    const w = video ? video.videoWidth : 0, h = video ? video.videoHeight : 0;
    if (!w || !h) return Promise.reject(new Error("la cámara aún no está lista"));
    const k = Math.min(1, LADO_MAX_PX / Math.max(w, h));
    canvas.width = Math.round(w * k);
    canvas.height = Math.round(h * k);
    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
    return new Promise((ok, mal) => canvas.toBlob((b) => (b ? ok(b) : mal(new Error("no se pudo crear la imagen"))), "image/jpeg", 0.9));
  }

  // ---------- Datos ----------
  async function cargarCatalogo() {
    try {
      const r = await fetch(`${API_BASE_URL}/alimentos`);
      const c = await r.json();
      catalogo = c.alimentos || [];
    } catch { catalogo = null; }
  }

  function kcalDe(r) {
    if (r.calorias != null) return r.calorias;
    if (!catalogo) return null;
    const a = catalogo.find((x) => x.alimento_codigo === r.alimento_codigo);
    return a ? a.calorias : null;
  }

  // ---------- Mostrar resultado ----------
  function mostrarSellos(sellos) {
    const caja = $("backend-sellos");
    if (!caja) return;
    caja.replaceChildren();
    if (sellos === null || sellos === undefined) { caja.textContent = "—"; return; }   // null = no se sabe: no se afirma nada
    if (sellos.length === 0) { caja.textContent = "Sin sellos de advertencia"; return; }   // nunca «saludable»
    // Los sellos van dentro de un .sellos: en modo oscuro esa envoltura les pone una placa clara alrededor
    // (el negro solo no se ve, WCAG 1.4.11). El filtro no puede ir en el sello mismo porque su clip-path lo recorta.
    const envoltura = document.createElement("div");
    envoltura.className = "sellos";
    sellos.forEach((s) => {
      const el = document.createElement("span");
      el.className = "sello";
      el.textContent = TEXTO_SELLO[s] || String(s).toUpperCase();
      el.setAttribute("role", "img");                 // el nombre accesible, en minúsculas normales
      el.setAttribute("aria-label", enFrase(el.textContent));
      envoltura.appendChild(el);
    });
    caja.appendChild(envoltura);
  }

  // Consejos (K0.5). El backend manda r.consejo = {aporta, para_completar, a_tener_en_cuenta, sellos: [{sello, dato, idea}]}.
  // Se dibujan, en este orden y como máximo cuatro, bloques cortos con título (el cuarto es el dato curioso):
  //   1. «Lo que aporta»            <- aporta
  //   2. «Para completar tu plato»  <- para_completar; si no hay, «Una idea» <- idea del primer sello
  //   3. «A tener en cuenta»        <- a_tener_en_cuenta; si no hay, el dato del primer sello
  //   4. «¿Sabías que…?»            <- dato_curioso (su título solo sale si hay consejo)
  // Un bloque vacío no se dibuja. Sin consejo (backend viejo) no se dibuja nada nuevo. Es información,
  // no una alerta: sin color de advertencia ni íconos. Todo el texto entra con textContent.
  function mostrarConsejos(r) {
    const caja = $("backend-consejos");
    if (caja) caja.replaceChildren();
    const c = r.consejo && typeof r.consejo === "object" ? r.consejo : null;
    // Mientras la IA duda no se sabe qué es el plato: no se aconseja sobre una suposición (igual que las calorías y los sellos)
    const hay = c !== null && !r.seleccion_manual;
    const dato = $("backend-dato");
    const titulo = $("titulo-dato");
    if (titulo) titulo.hidden = !(hay && dato && dato.textContent.trim() !== "");
    if (!caja || !hay) return;
    const limpio = (v) => (typeof v === "string" ? v.trim() : "");
    const sello = (Array.isArray(c.sellos) && c.sellos[0]) || {};
    [
      ["Lo que aporta", limpio(c.aporta)],
      limpio(c.para_completar) ? ["Para completar tu plato", limpio(c.para_completar)] : ["Una idea", limpio(sello.idea)],
      ["A tener en cuenta", limpio(c.a_tener_en_cuenta) || limpio(sello.dato)],
    ].forEach(([tit, texto]) => {
      if (!texto) return;
      const bloque = document.createElement("div");
      bloque.className = "consejo";
      const h = document.createElement("h3");
      h.className = "consejo__titulo";
      h.textContent = tit;
      const p = document.createElement("p");
      p.className = "consejo__texto";
      p.textContent = texto;
      bloque.append(h, p);
      caja.appendChild(bloque);
    });
  }

  // El dato curioso puede ser largo (500 a 860 caracteres). Líneas de unos 65 caracteres (CSS) y, si pasa de
  // LINEAS_DATO líneas, se corta y el botón «Leer más» (aria-expanded, sin animación) lo abre y lo cierra.
  const LINEAS_DATO = 4;
  let anchoDato = null;
  function ajustarDato(reiniciar) {
    const p = $("backend-dato"), boton = $("btn-dato-mas");
    if (!p || !boton) return;
    if (reiniciar) { boton.setAttribute("aria-expanded", "false"); boton.textContent = "Leer más"; }
    const abierto = boton.getAttribute("aria-expanded") === "true";
    const alto = parseFloat(getComputedStyle(p).lineHeight);
    // scrollHeight es el alto de todo el texto, esté cortado o no
    const lineas = alto > 0 ? Math.round(p.scrollHeight / alto) : 0;
    const largo = lineas > LINEAS_DATO;
    boton.hidden = !largo;
    p.classList.toggle("dato--cortado", largo && !abierto);
  }
  (function conectarDato() {
    const p = $("backend-dato"), boton = $("btn-dato-mas");
    if (!p || !boton) return;
    boton.addEventListener("click", () => {
      const abrir = boton.getAttribute("aria-expanded") !== "true";
      boton.setAttribute("aria-expanded", String(abrir));
      boton.textContent = abrir ? "Leer menos" : "Leer más";
      ajustarDato(false);
    });
    // Si cambia el ancho (giro del celular, ventana), el texto ocupa otras líneas: se vuelve a medir.
    // Solo se mira el ancho: cortar el texto cambia el alto y no debe volver a disparar la medida.
    if (window.ResizeObserver) {
      new ResizeObserver(() => {
        const ancho = p.clientWidth;
        if (ancho === anchoDato) return;
        anchoDato = ancho;
        ajustarDato(false);
      }).observe(p);
    }
  })();

  function mostrarOpciones(r) {
    const caja = $("backend-opciones");
    if (!caja) return;
    caja.replaceChildren();
    const opciones = r.opciones_detalle ||
      (r.opciones_sugeridas || []).map((codigo) => ({ codigo, nombre: codigo.replace(/_/g, " ") }));
    if (!r.seleccion_manual || opciones.length === 0) return;
    const grupos = new Map();                       // grupo -> opciones, en el orden en que llegan
    opciones.forEach((o) => {
      const g = o.grupo || "";
      if (!grupos.has(g)) grupos.set(g, []);
      grupos.get(g).push(o);
    });
    grupos.forEach((lista, grupo) => {
      if (grupos.size > 1 && grupo) {               // título solo si hay varios grupos
        const t = document.createElement("p");
        t.className = "opciones__grupo";
        t.textContent = grupo;
        caja.appendChild(t);
      }
      lista.forEach((o) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "opciones__boton";
        b.textContent = o.nombre;
        b.addEventListener("click", () => confirmar(o.codigo));
        caja.appendChild(b);
      });
    });
  }

  // «1 semilla», «5 semillas» (en pantalla XP = semillas; formato.js es el único lugar de los plurales)
  const semillas = (n) => (window.LumeaFormato ? window.LumeaFormato.semillas(n) : `${n} semillas`);

  // Semillas, misiones, etapa y meta del día (contrato de gamificación). Nunca es un
  // juicio sobre la comida: celebra lo que la persona hizo.
  function mostrarLogros(g) {
    const lista = $("backend-logros");
    if (!lista) return false;
    lista.replaceChildren();
    if (!g) return true;
    const frases = [];
    if (g.xp_ganado > 0) frases.push(`+${semillas(g.xp_ganado)}`);
    (g.misiones_cumplidas || []).forEach((m) => frases.push(`Misión cumplida: ${m.nombre}`));
    (g.calcomanias_nuevas || []).forEach((c) => frases.push(`Calcomanía nueva: ${c.nombre}`));
    if (g.subio_de_nivel) frases.push(`Llegaste a la etapa ${g.nivel}`);
    if (g.meta_diaria && g.meta_diaria.recien_cumplida) frases.push("Cumpliste la meta de hoy");
    frases.forEach((f) => {
      const li = document.createElement("li");
      li.textContent = f;
      lista.appendChild(li);
    });
    return true;
  }

  // La foto queda quieta sobre el video mientras la IA la analiza
  let urlFoto = null;
  function mostrarFoto(archivo) {
    const img = $("backend-foto");
    if (!img) return;
    if (urlFoto) URL.revokeObjectURL(urlFoto);
    urlFoto = archivo ? URL.createObjectURL(archivo) : null;
    if (urlFoto) img.src = urlFoto; else img.removeAttribute("src");
    img.hidden = !urlFoto;
    actualizarVisor();
  }

  function mostrar(r) {
    const opcionesDuda = r.seleccion_manual && (r.opciones_detalle || r.opciones_sugeridas || []).length > 0;
    // IA duda con opciones: el título es la pregunta, no "No identificado"
    poner("backend-alimento", opcionesDuda ? "¿Cuál de estos es?" : (r.alimento_app || r.alimento || "No identificado"));
    // «IA segura» o «IA duda»: el CSS pinta el contenedor según este estado (la duda va en el rol «duda»)
    const resultado = $("resultado");
    if (resultado) resultado.dataset.estado = r.seleccion_manual ? "duda" : "segura";
    // La certeza, en palabras y en número (y el medidor la acompaña, no la reemplaza)
    const medidor = $("backend-medidor");
    if (medidor) {
      if (r.certeza != null) medidor.style.setProperty("--certeza", `${Math.min(100, Math.max(0, Math.round(r.certeza)))}%`);
      else medidor.style.removeProperty("--certeza");
    }
    poner("backend-precision", r.certeza != null
      ? `${r.seleccion_manual ? "La IA no está segura" : "La IA está segura"}: ${Math.round(r.certeza)} %`
      : (r.seleccion_manual ? "La IA no está segura" : ""));
    const kcal = kcalDe(r);
    const energia = $("backend-energia");
    if (energia) {
      // Mientras la IA duda todavía no se sabe qué es: no se muestran las calorías de una suposición
      const verla = MOSTRAR_CALORIAS && kcal != null && !r.seleccion_manual;
      energia.hidden = !verla;
      energia.textContent = verla ? `Calorías aproximadas: ${kcal} kcal por 100 g` : "";   // el catálogo da kcal por cada 100 g
    }
    mostrarSellos(r.sellos_advertencia);
    poner("backend-dato", r.dato_curioso || "");
    ajustarDato(true);
    mostrarConsejos(r);
    let msg = r.mensaje_educativo || "";
    if (r.seleccion_manual && !(r.opciones_detalle || r.opciones_sugeridas || []).length) {
      msg = "La IA no está segura. Intenta con más luz o más cerca del plato.";
    } else if (r.seleccion_manual) {
      // Grupo de confusión: el backend explica por qué hay que elegir. Si la IA
      // dudó (opciones sin grupo), el texto del backend es técnico: se reemplaza.
      const detalle = r.opciones_detalle || [];
      const iaDudo = detalle.length > 0 && detalle.every((o) => !o.grupo);
      msg = ((iaDudo ? "La IA no está segura." : (r.mensaje || "")) + " Toca el que es para guardarlo en tu historial.").trim();
    } else if (r.guardado_baseDatos) {
      msg = (msg ? msg + " " : "") + "Guardado en tu historial.";
    }
    const hayLista = mostrarLogros(r.gamificacion);
    if (!hayLista && r.gamificacion && r.gamificacion.xp_ganado) msg += ` +${semillas(r.gamificacion.xp_ganado)}`;
    poner("backend-mensaje", msg);
    mostrarOpciones(r);
    if (window.LumeaCelebrar) LumeaCelebrar(r.gamificacion);
  }

  // ---------- Acciones ----------
  async function analizar(archivo) {
    ocupado = true; actualizarBotones();
    mostrarFoto(archivo);
    poner("backend-estado", "Analizando…");
    try {
      const { ok, cuerpo } = await predecirComida(archivo, email);   // api.js
      if (!ok || cuerpo.error) throw new Error(cuerpo.error || "el servidor respondió con error");
      mostrar(cuerpo);
      poner("backend-estado", "");
    } catch (e) {
      poner("backend-estado", `No se pudo analizar: ${e.message}. ¿Está corriendo app.py?`);
    } finally {
      ocupado = false; actualizarBotones();
    }
  }

  async function confirmar(codigo) {
    ocupado = true; actualizarBotones();
    try {
      const { ok, cuerpo } = await confirmarAlimento(codigo, email);  // api.js
      if (!ok || cuerpo.error) throw new Error(cuerpo.error || "error al confirmar");
      mostrar(cuerpo);
    } catch (e) {
      poner("backend-estado", `No se pudo confirmar: ${e.message}`);
    } finally {
      ocupado = false; actualizarBotones();
    }
  }

  async function tomarFoto() {
    if (!stream || ocupado) return;
    try {
      const blob = await capturar();
      await analizar(new File([blob], "foto.jpg", { type: "image/jpeg" }));
    } catch (e) {
      poner("backend-estado", `No se pudo tomar la foto: ${e.message}`);
    }
  }

  // ---------- Conectar botones ----------
  const al = (id, fn) => { const el = $(id); if (el) el.addEventListener("click", fn); };
  al("btn-encender", encender);
  al("btn-apagar", apagar);
  al("btn-tomar", tomarFoto);
  al("btn-otra", () => { mostrarFoto(null); poner("backend-estado", "Lista para otra foto."); });
  al("btn-subir", () => inputArchivo.click());
  inputArchivo.addEventListener("change", async () => {
    const f = inputArchivo.files[0];
    if (f) await analizar(f);
    inputArchivo.value = "";
  });
  document.addEventListener("keydown", (e) => {          // barra espaciadora = tomar foto
    if (e.code === "Space" && !["INPUT", "TEXTAREA", "BUTTON"].includes(document.activeElement.tagName)) {
      e.preventDefault(); tomarFoto();
    }
  });
  window.addEventListener("beforeunload", apagar);

  // «Foto directa» de Inicio: la foto llega UNA vez en sessionStorage (ya reducida) y se borra al leerla
  async function fotoDeInicio() {
    let url = null;
    try { url = sessionStorage.getItem("lumea_foto_temporal"); sessionStorage.removeItem("lumea_foto_temporal"); } catch (e) {}
    if (!url) return;
    try {
      const blob = await (await fetch(url)).blob();
      await analizar(new File([blob], "foto.jpg", { type: blob.type || "image/jpeg" }));
    } catch (e) {
      poner("backend-estado", "No se pudo abrir la foto que tomaste en Inicio. Usa «Subir foto».");
    }
  }

  actualizarBotones();
  cargarCatalogo();
  fotoDeInicio();
})();
