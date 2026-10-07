// =====================================================================
// progreso.js — llena progreso.html (sin diseño propio: las clases están en
// estilos/progreso.css y estilos/componentes.css). Necesita api.js y formato.js antes.
//
// Datos (Backend/docs/CONTRATO_GAMIFICACION.md):
//   GET /progreso        nivel, XP, racha, meta, mensaje_regreso, avatar, calcomanias
//   GET /historial       comidas (con es_fruta) -> «Comidas de la semana»
//   GET /estado-animo    ?dias=7 -> «Tu ánimo de la semana»
// Si un dato nuevo no llega (backend viejo), esa parte se omite y la pantalla
// funciona igual. Todo texto del servidor se escribe con textContent.
//
// Lo que NO hace, a propósito: no compara con otras personas, no muestra
// calorías y nunca dice «perdiste XP»: el mensaje de regreso es una bienvenida.
// =====================================================================
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const DIAS_CORTO = ["L", "M", "M", "J", "V", "S", "D"];
  const DIAS_LARGO = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];
  const NOMBRE_ANIMO = { muy_mal: "Muy mal", mal: "Mal", neutral: "Neutral", bien: "Bien", muy_bien: "Muy bien" };
  const NS = "http://www.w3.org/2000/svg";
  // Manzana (Lucide, licencia ISC): marca los días con fruta con un ícono, no solo con color
  const ICONO_FRUTA = ["M12 20.94c1.5 0 2.75 1.06 4 1.06 3 0 6-8 6-12.22A4.91 4.91 0 0 0 17 5c-2.22 0-4 1.44-5 2-1-.56-2.78-2-5-2a4.9 4.9 0 0 0-5 4.78C2 14 5 22 8 22c1.25 0 2.5-1.06 4-1.06Z", "M10 2c1 .5 2 2 2 5"];

  // ---------- Cálculos puros (se prueban solos) ----------

  // plural, porcentajeNivel y textoNivel son comunes con Avatar: viven en formato.js
  const { plural, porcentajeNivel, textoNivel } = window.LumeaFormato;

  function textoRacha(n) {
    return plural(n, "día", "días");
  }

  // Lo que va debajo de la cifra: nunca un reproche si no hay racha
  function notaRacha(n) {
    if (n === 0) return "Registra algo hoy para empezar una racha";
    return n === 1 ? "¡Empezó tu racha!" : "seguidos con actividad";
  }

  function textoMeta(m) {
    return m.cumplida ? `Meta cumplida: ${m.xp_hoy} XP hoy` : `${m.xp_hoy} de ${m.meta} XP hoy`;
  }

  const clave = (a, m, d) => `${a}-${String(m + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;

  // La semana (lunes a domingo) que contiene a `hoy`: [{ clave: "2026-10-05", indice: 0..6 }]
  function semanaDe(hoy) {
    const dia = (hoy.getDay() + 6) % 7;                    // lunes = 0
    return DIAS_LARGO.map((_, i) => {
      const f = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate() - dia + i);
      return { clave: clave(f.getFullYear(), f.getMonth(), f.getDate()), indice: i };
    });
  }

  // El backend manda la fecha como «Mon, 05 Oct 2026 00:00:00 GMT»: medianoche en UTC.
  // Se lee con los campos UTC; con los locales, en Colombia (UTC-5) saldría el día anterior.
  function claveDeFechaDelServidor(texto) {
    const f = new Date(texto);
    if (Number.isNaN(f.getTime())) return null;
    return clave(f.getUTCFullYear(), f.getUTCMonth(), f.getUTCDate());
  }

  // Por cada día de la semana: cuántas comidas y si hubo alguna fruta
  function comidasPorDia(historial, semana) {
    const dias = {};
    semana.forEach((d) => { dias[d.clave] = { comidas: 0, fruta: false }; });
    (historial || []).forEach((r) => {
      const c = claveDeFechaDelServidor(r.fecha);
      if (c && dias[c]) {
        dias[c].comidas += 1;
        if (r.es_fruta === true) dias[c].fruta = true;
      }
    });
    return semana.map((d) => ({ ...d, ...dias[d.clave] }));
  }

  // El último estado de ánimo de cada día de la semana (la lista llega del más reciente al más antiguo)
  function animoPorDia(registros, semana) {
    const porDia = {};
    (registros || []).forEach((r) => {
      const c = claveDeFechaDelServidor(r.fecha);
      if (c && !(c in porDia)) porDia[c] = r.estado;
    });
    return semana.map((d) => ({ ...d, estado: porDia[d.clave] || null }));
  }

  // ---------- Dibujo ----------
  function crear(etiqueta, clase, texto) {
    const el = document.createElement(etiqueta);
    if (clase) el.className = clase;
    if (texto != null) el.textContent = texto;
    return el;
  }

  function iconoFruta() {
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("class", "icono semana__fruta");
    svg.setAttribute("aria-hidden", "true");
    ICONO_FRUTA.forEach((d) => {
      const path = document.createElementNS(NS, "path");
      path.setAttribute("d", d);
      svg.appendChild(path);
    });
    return svg;
  }

  function dibujarNivel(p) {
    $("nivel-titulo").textContent = `Nivel ${p.nivel}`;
    $("nivel-xp").textContent = `${p.xp_total} XP`;
    $("nivel-faltan").textContent = textoNivel(p);
    const pct = porcentajeNivel(p);
    $("nivel-relleno").style.setProperty("--avance", `${pct}%`);
    const riel = $("nivel-riel");
    riel.setAttribute("aria-valuenow", String(pct));
    riel.setAttribute("aria-label", p.xp_siguiente_nivel == null ? "Nivel máximo" : `Avance hacia el nivel ${p.nivel + 1}`);
  }

  function dibujarRacha(p) {
    $("racha-actual").textContent = textoRacha(p.racha_actual);
    $("racha-nota").textContent = notaRacha(p.racha_actual);
    $("racha-mejor").textContent = textoRacha(p.racha_maxima);
    if (p.meta_diaria) {
      $("meta-hoy").textContent = p.meta_diaria.cumplida ? "Meta cumplida" : `${p.meta_diaria.xp_hoy} de ${p.meta_diaria.meta} XP`;
      $("meta-nota").textContent = p.meta_diaria.cumplida ? `${p.meta_diaria.xp_hoy} XP hoy` : "hoy";
    }
  }

  function dibujarSemanaComidas(semana, hoyClave) {
    const lista = $("semana-comidas");
    lista.replaceChildren();
    const maximo = Math.max(1, ...semana.map((d) => d.comidas));
    semana.forEach((d) => {
      const futuro = d.clave > hoyClave;
      const li = crear("li", "semana__dia" + (futuro ? " semana__dia--futuro" : ""));
      if (d.clave === hoyClave) li.setAttribute("aria-current", "date");
      const cifra = crear("span", "semana__cifra numero", futuro ? "" : String(d.comidas));
      cifra.setAttribute("aria-hidden", "true");
      const columna = crear("span", "semana__columna");
      columna.setAttribute("aria-hidden", "true");
      columna.style.setProperty("--alto", `${Math.round((d.comidas / maximo) * 100)}%`);
      const marca = crear("span", "semana__marca");
      marca.setAttribute("aria-hidden", "true");
      if (d.fruta) marca.appendChild(iconoFruta());
      const letra = crear("span", "semana__letra", DIAS_CORTO[d.indice]);
      letra.setAttribute("aria-hidden", "true");
      const detalle = futuro ? "todavía no llega" : `${plural(d.comidas, "comida", "comidas")}${d.fruta ? ", con fruta" : ""}`;
      li.append(marca, cifra, columna, letra, crear("span", "solo-lector", `${DIAS_LARGO[d.indice]}: ${detalle}`));
      lista.appendChild(li);
    });
  }

  function dibujarSemanaAnimo(semana, hoyClave, caras) {
    const lista = $("semana-animo");
    lista.replaceChildren();
    semana.forEach((d) => {
      const futuro = d.clave > hoyClave;
      const li = crear("li", "animo-semana__dia" + (d.estado ? "" : " animo-semana__dia--vacio"));
      if (d.clave === hoyClave) li.setAttribute("aria-current", "date");
      const cara = crear("span", "animo-semana__cara");
      cara.setAttribute("aria-hidden", "true");
      const url = d.estado && caras ? caras[d.estado] : null;
      if (url) {
        const img = document.createElement("img");
        img.alt = "";
        img.src = url;
        img.addEventListener("error", () => img.remove());     // sin internet: queda el nombre escrito
        cara.appendChild(img);
      }
      const nombre = d.estado ? (NOMBRE_ANIMO[d.estado] || d.estado) : "";
      const letra = crear("span", "animo-semana__letra", DIAS_CORTO[d.indice]);
      letra.setAttribute("aria-hidden", "true");
      const texto = crear("span", "animo-semana__nombre", nombre);
      texto.setAttribute("aria-hidden", "true");
      const lector = futuro ? "todavía no llega" : (nombre || "sin check-in");
      li.append(cara, texto, letra, crear("span", "solo-lector", `${DIAS_LARGO[d.indice]}: ${lector}`));
      lista.appendChild(li);
    });
  }

  function dibujarAlbum(p) {
    const enlace = $("album-enlace");
    if (!p.calcomanias) { enlace.hidden = true; return; }
    enlace.textContent = `Mi álbum: ${p.calcomanias.ganadas} de ${p.calcomanias.total} calcomanías`;
    enlace.hidden = false;
  }

  function dibujarBienvenida(p) {
    const caja = $("bienvenida");
    if (p.mensaje_regreso) { caja.textContent = p.mensaje_regreso; caja.hidden = false; }
    else { caja.hidden = true; }
  }

  // ---------- Carga ----------
  function estado(que) {            // "cargando" | "listo" | "error" | "sin-sesion"
    $("estado-cargando").hidden = que !== "cargando";
    $("estado-error").hidden = que !== "error";
    $("sin-sesion").hidden = que !== "sin-sesion";
    $("progreso-contenido").hidden = que !== "listo";
  }

  async function cargar() {
    const email = obtenerSesion();
    if (!email) { estado("sin-sesion"); return; }
    estado("cargando");
    try {
      // El progreso es lo esencial; la semana y el ánimo son un extra que no tumba la pantalla.
      const [progreso, historial, animo] = await Promise.all([
        obtenerProgreso(email),
        obtenerHistorial(email).catch(() => null),
        obtenerEstadosAnimo(email, 7).catch(() => null),
      ]);
      if (!progreso.ok || !progreso.cuerpo.progreso) throw new Error("sin progreso");
      const p = progreso.cuerpo.progreso;

      const hoy = new Date();
      const semana = semanaDe(hoy);
      const hoyClave = clave(hoy.getFullYear(), hoy.getMonth(), hoy.getDate());

      dibujarBienvenida(p);
      dibujarNivel(p);
      dibujarRacha(p);
      dibujarAlbum(p);
      const hayHistorial = historial && historial.ok && Array.isArray(historial.cuerpo.historial);
      $("semana-comidas-caja").hidden = !hayHistorial;
      if (hayHistorial) dibujarSemanaComidas(comidasPorDia(historial.cuerpo.historial, semana), hoyClave);
      const hayAnimo = animo && animo.ok && Array.isArray(animo.cuerpo.historial);
      $("semana-animo-caja").hidden = !hayAnimo;
      if (hayAnimo) dibujarSemanaAnimo(animoPorDia(animo.cuerpo.historial, semana), hoyClave, p.avatar && p.avatar.urls_por_estado);
      estado("listo");
    } catch (e) {
      estado("error");
    }
  }

  window.LumeaProgreso = { plural, porcentajeNivel, textoNivel, textoRacha, notaRacha, textoMeta, semanaDe, comidasPorDia, animoPorDia, claveDeFechaDelServidor };
  document.addEventListener("DOMContentLoaded", () => {
    const reintentar = $("estado-reintentar");
    if (reintentar) reintentar.addEventListener("click", cargar);
    cargar();
  });
})();
