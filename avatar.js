// =====================================================================
// avatar.js — llena avatar.html (sin diseño propio: las clases están en
// estilos/avatar.css y estilos/componentes.css). Necesita, antes:
// api.js, formato.js y pegatinas.js.
//
// Tres pestañas (patrón ARIA de «tabs»; abren con #misiones, #armario o
// #calcomanias, que es a donde apuntan los botones de la celebración):
//   Misiones     las tres misiones diarias de GET /progreso (con +XP)
//   Armario      ropa y accesorios de GET /avatar; ponerse y quitarse
//   Calcomanías  el álbum de GET /calcomanias
//
// El avatar grande: si las imágenes por capas de Laura están listas
// (imagen_lista), se apilan; si no, se usa la cara DiceBear con el ánimo de
// hoy (la que manda GET /progreso). Si un dato no llega, esa parte se omite.
//
// Reglas: nunca se muestran calorías ni comparaciones; lo bloqueado dice «Se
// abre en el nivel N» y no hace nada; todo texto del servidor va con textContent.
// =====================================================================
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const { plural, porcentajeNivel, textoNivel } = window.LumeaFormato;
  const NS = "http://www.w3.org/2000/svg";
  const PESTANAS = ["misiones", "armario", "calcomanias"];
  const NOMBRE_ANIMO = { muy_mal: "Muy mal", mal: "Mal", neutral: "Neutral", bien: "Bien", muy_bien: "Muy bien" };
  // Cada misión diaria tiene su calcomanía (la que se gana la primera vez que se cumple)
  const CALCOMANIA_DE_MISION = { fruta: "fruta", tres_comidas: "tres_al_dia", check_in_animo: "como_llegas" };
  const TITULO_TIPO = { ropa: "Ropa", accesorio: "Accesorios" };

  // Íconos de Lucide (licencia ISC), 24x24
  const ICONOS = {
    ropa: ["M20.38 3.46 16 2a4 4 0 0 1-8 0L3.62 3.46a2 2 0 0 0-1.34 2.23l.58 3.47a1 1 0 0 0 .99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V10h2.15a1 1 0 0 0 .99-.84l.58-3.47a2 2 0 0 0-1.34-2.23z"],
    accesorio: ["M6 11a4 4 0 1 0 0 8 4 4 0 0 0 0-8z", "M18 11a4 4 0 1 0 0 8 4 4 0 0 0 0-8z", "M14 15a2 2 0 0 0-2-2 2 2 0 0 0-2 2", "M2.5 13 5 7c.7-1.3 1.4-2 3-2", "M21.5 13 19 7c-.7-1.3-1.5-2-3-2"],
    candado: ["M5 11h14a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2z", "M7 11V7a5 5 0 0 1 10 0v4"],
    check: ["M20 6 9 17l-5-5"],
    bandera: ["M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z", "M4 22v-7"],
    persona: ["M12 3a5 5 0 1 0 0 10 5 5 0 0 0 0-10z", "M20 21a8 8 0 0 0-16 0"],
  };

  const estado = { email: null, progreso: null, avatar: null, calcomanias: null, ocupado: false };

  function crear(etiqueta, clase, texto) {
    const el = document.createElement(etiqueta);
    if (clase) el.className = clase;
    if (texto != null) el.textContent = texto;
    return el;
  }

  function icono(nombre, clase) {
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("class", "icono" + (clase ? " " + clase : ""));
    svg.setAttribute("aria-hidden", "true");
    ICONOS[nombre].forEach((d) => {
      const path = document.createElementNS(NS, "path");
      path.setAttribute("d", d);
      svg.appendChild(path);
    });
    return svg;
  }

  function aviso(texto) {              // lo anuncia el lector de pantalla, sin interrumpir
    $("avatar-aviso").textContent = texto;
  }

  // ---------- El avatar grande ----------
  function capasListas(av) {
    return !!av && Array.isArray(av.capas) && av.capas.length > 0 && av.capas.every((c) => c.imagen_lista);
  }

  function dibujarFigura() {
    const caja = $("avatar-figura");
    caja.replaceChildren();
    const av = estado.avatar, p = estado.progreso;
    const animo = p && p.avatar && p.avatar.estado_animo_hoy;
    const caraUrl = (p && p.avatar && (p.avatar.url_con_animo || p.avatar.url)) || (av && av.respaldo_dicebear && av.respaldo_dicebear.url);
    caja.setAttribute("aria-label", animo ? `Tu avatar, tu ánimo de hoy: ${NOMBRE_ANIMO[animo] || animo}` : "Tu avatar");

    if (capasListas(av)) {                                  // el diseño de Laura: una imagen encima de otra
      av.capas.forEach((c) => {
        const img = document.createElement("img");
        img.className = "avatar-figura__capa";
        img.alt = "";
        img.src = c.url;
        caja.appendChild(img);
      });
      return;
    }
    // Respaldo: la cara DiceBear con el ánimo de hoy. Sin internet queda una silueta.
    const respaldo = crear("span", "avatar-figura__silueta");
    respaldo.appendChild(icono("persona"));
    caja.appendChild(respaldo);
    if (caraUrl) {
      const img = document.createElement("img");
      img.className = "avatar-figura__cara";
      img.alt = "";
      img.src = caraUrl;
      img.addEventListener("error", () => img.remove());
      caja.appendChild(img);
    }
  }

  function dibujarCabeza() {
    const p = estado.progreso;
    if (!p) return;
    $("avatar-nivel").textContent = `Nivel ${p.nivel}`;
    $("avatar-faltan").textContent = textoNivel(p);
    const pct = porcentajeNivel(p);
    $("avatar-relleno").style.setProperty("--avance", `${pct}%`);
    const riel = $("avatar-riel");
    riel.setAttribute("aria-valuenow", String(pct));
    riel.setAttribute("aria-label", p.xp_siguiente_nivel == null ? "Nivel máximo" : `Avance hacia el nivel ${p.nivel + 1}`);
  }

  function dibujarPuesto() {
    const puesto = estado.avatar && estado.avatar.puesto;
    const nombres = puesto ? ["ropa", "accesorio"].map((t) => puesto[t] && puesto[t].nombre).filter(Boolean) : [];
    $("avatar-puesto").textContent = nombres.length ? `Puesto: ${nombres.join(" y ")}` : "Todavía no te pusiste nada.";
  }

  // ---------- Misiones ----------
  function calcomaniaGanada(id) {
    const lista = estado.calcomanias && estado.calcomanias.calcomanias;
    return lista ? lista.find((c) => c.id === id && c.ganada) || null : null;
  }

  function dibujarMisiones() {
    const lista = $("misiones-lista");
    lista.replaceChildren();
    const misiones = (estado.progreso && estado.progreso.misiones) || [];
    misiones.forEach((m) => {
      const li = crear("li", "mision tarjeta" + (m.cumplida ? " mision--cumplida" : ""));
      const cabeza = crear("div", "mision__cuerpo");
      cabeza.appendChild(crear("h3", "mision__nombre", m.nombre));
      const fila = crear("p", "mision__fila");
      fila.appendChild(crear("span", "chip chip--mision numero", `+${m.xp} XP`));
      const estadoTexto = crear("span", "mision__estado");
      if (m.cumplida) estadoTexto.appendChild(icono("check"));
      estadoTexto.appendChild(document.createTextNode(m.cumplida ? "Cumplida hoy" : "Para hoy"));
      fila.appendChild(estadoTexto);
      cabeza.appendChild(fila);
      li.appendChild(cabeza);
      // La misión cumplida lleva su calcomanía (si ya la ganó)
      const c = m.cumplida ? calcomaniaGanada(CALCOMANIA_DE_MISION[m.id]) : null;
      if (c) {
        const lado = crear("div", "mision__pegatina");
        lado.appendChild(LumeaPegatina.crear(c));
        lado.appendChild(crear("span", "solo-lector", `Calcomanía: ${c.nombre}`));
        li.appendChild(lado);
      }
      lista.appendChild(li);
    });
    $("misiones-vacio").hidden = misiones.length > 0;
  }

  // ---------- Armario ----------
  function dibujarArmario(enfocarId) {
    const caja = $("armario-grupos");
    caja.replaceChildren();
    const objetos = (estado.avatar && estado.avatar.objetos) || {};
    ["ropa", "accesorio"].forEach((tipo) => {
      const lista = objetos[tipo] || [];
      if (!lista.length) return;
      const grupo = crear("section", "armario__grupo");
      const titulo = crear("h3", "armario__titulo", TITULO_TIPO[tipo]);
      grupo.appendChild(titulo);
      const ul = crear("ul", "armario__lista");
      ul.setAttribute("aria-label", TITULO_TIPO[tipo]);
      lista.forEach((o) => ul.appendChild(tarjetaDePrenda(o)));
      grupo.appendChild(ul);
      caja.appendChild(grupo);
    });
    if (enfocarId) {
      const boton = caja.querySelector(`[data-objeto="${enfocarId}"]`);
      if (boton) boton.focus();
    }
  }

  function tarjetaDePrenda(o) {
    const bloqueado = !o.desbloqueado;
    const li = crear("li", "prenda" + (bloqueado ? " prenda--bloqueada" : "") + (o.puesto ? " prenda--puesta" : ""));
    const imagen = crear("span", "prenda__imagen");
    imagen.setAttribute("aria-hidden", "true");
    if (o.imagen_lista && !bloqueado) {
      const img = document.createElement("img");
      img.alt = "";
      img.src = o.url;
      imagen.appendChild(img);
    } else {
      imagen.appendChild(icono(bloqueado ? "candado" : o.tipo));
    }
    li.appendChild(imagen);
    li.appendChild(crear("p", "prenda__nombre", o.nombre));
    li.appendChild(crear("p", "prenda__estado", bloqueado ? `Se abre en el nivel ${o.nivel_requerido}` : (o.puesto ? "Puesto" : "Disponible")));

    const boton = crear("button", "boton prenda__boton" + (o.puesto ? " boton--secundario" : ""));
    boton.type = "button";
    boton.dataset.objeto = o.id;
    if (bloqueado) {
      boton.classList.add("boton--secundario");
      boton.setAttribute("aria-disabled", "true");          // se puede enfocar y leer, pero no hace nada
      boton.textContent = `Nivel ${o.nivel_requerido}`;
      boton.setAttribute("aria-label", `${o.nombre}, se abre en el nivel ${o.nivel_requerido}`);
    } else {
      boton.textContent = o.puesto ? "Quitar" : "Ponerme";
      boton.setAttribute("aria-label", `${o.puesto ? "Quitar" : "Ponerme"} ${o.nombre}`);
      boton.addEventListener("click", () => alternar(o));
    }
    li.appendChild(boton);
    return li;
  }

  function saltico() {                       // un solo movimiento: el avatar da un saltico al ponerse algo
    const figura = $("avatar-figura");
    figura.classList.remove("avatar-figura--saltico");
    void figura.offsetWidth;                 // reinicia la animación si ya estaba puesta
    figura.classList.add("avatar-figura--saltico");
    figura.addEventListener("animationend", () => figura.classList.remove("avatar-figura--saltico"), { once: true });
  }

  async function alternar(objeto) {
    if (estado.ocupado) return;
    estado.ocupado = true;
    const ponerse = !objeto.puesto;
    try {
      const { ok, cuerpo } = ponerse
        ? await equiparObjeto(estado.email, objeto.tipo, objeto.id)       // api.js
        : await quitarObjeto(estado.email, objeto.tipo);
      if (!ok || !cuerpo.objetos) {
        const faltan = cuerpo && cuerpo.niveles_faltantes;
        throw new Error(faltan ? `Todavía no se abre: te ${faltan === 1 ? "falta 1 nivel" : `faltan ${faltan} niveles`}.` : "No se pudo guardar el cambio.");
      }
      estado.avatar = cuerpo;                                              // el backend responde con el avatar completo
      dibujarFigura();
      dibujarPuesto();
      dibujarArmario(objeto.id);
      aviso(ponerse ? `Te pusiste ${objeto.nombre}.` : `Te quitaste ${objeto.nombre}.`);
      if (ponerse) saltico();
    } catch (e) {
      aviso(e.message && !/fetch|network/i.test(e.message) ? e.message : "No se pudo conectar. Inténtalo otra vez.");
    } finally {
      estado.ocupado = false;
    }
  }

  // ---------- Álbum de calcomanías ----------
  function fechaCorta(iso) {
    if (!iso) return "";
    const f = new Date(`${iso}T00:00:00Z`);                // «2026-10-05»: un día sin hora, se lee en UTC
    return Number.isNaN(f.getTime()) ? "" : f.toLocaleDateString("es-CO", { day: "numeric", month: "long", timeZone: "UTC" });
  }

  function dibujarAlbum() {
    const datos = estado.calcomanias;
    const lista = $("album-lista");
    lista.replaceChildren();
    $("album-error").hidden = !!datos;
    $("album-resumen").hidden = !datos;
    if (!datos) return;
    $("album-resumen").textContent = `${datos.ganadas} de ${datos.total} calcomanías`;
    datos.calcomanias.forEach((c) => {
      const li = crear("li", "album__item" + (c.ganada ? " album__item--ganada" : " album__item--vacia"));
      li.appendChild(LumeaPegatina.crear(c, { ganada: c.ganada }));
      li.appendChild(crear("h3", "album__nombre", c.nombre));
      if (c.ganada) {
        li.appendChild(crear("p", "album__texto", c.descripcion));
        const f = fechaCorta(c.fecha);
        if (f) li.appendChild(crear("p", "album__fecha", `Ganada el ${f}`));
      } else {
        li.appendChild(crear("p", "album__texto", `Cómo se gana: ${c.como_se_gana}`));
      }
      lista.appendChild(li);
    });
  }

  // ---------- Pestañas (patrón ARIA de «tabs») ----------
  function seleccionar(nombre, { enfocar = false, escribirHash = true } = {}) {
    PESTANAS.forEach((n) => {
      const activa = n === nombre;
      const pestana = $(`pestana-${n}`);
      pestana.setAttribute("aria-selected", String(activa));
      pestana.tabIndex = activa ? 0 : -1;                   // solo la activa entra con Tab; las flechas mueven
      $(`panel-${n}`).hidden = !activa;
      if (activa && enfocar) pestana.focus();
    });
    if (escribirHash && location.hash !== `#${nombre}`) history.replaceState(null, "", `#${nombre}`);
  }

  function pestanaDelHash() {
    const n = location.hash.slice(1);
    return PESTANAS.indexOf(n) !== -1 ? n : null;
  }

  function conectarPestanas() {
    PESTANAS.forEach((n) => {
      $(`pestana-${n}`).addEventListener("click", () => seleccionar(n));
    });
    $("pestanas").addEventListener("keydown", (e) => {
      const i = PESTANAS.findIndex((n) => $(`pestana-${n}`) === document.activeElement);
      if (i < 0) return;
      const destino = { ArrowRight: (i + 1) % PESTANAS.length, ArrowLeft: (i + PESTANAS.length - 1) % PESTANAS.length, Home: 0, End: PESTANAS.length - 1 }[e.key];
      if (destino === undefined) return;
      e.preventDefault();
      seleccionar(PESTANAS[destino], { enfocar: true });
    });
    window.addEventListener("hashchange", () => { const n = pestanaDelHash(); if (n) seleccionar(n, { escribirHash: false }); });
  }

  // ---------- Carga ----------
  function pantalla(que) {            // "cargando" | "listo" | "error" | "sin-sesion"
    $("estado-cargando").hidden = que !== "cargando";
    $("estado-error").hidden = que !== "error";
    $("sin-sesion").hidden = que !== "sin-sesion";
    $("avatar-contenido").hidden = que !== "listo";
  }

  async function cargar() {
    estado.email = obtenerSesion();
    if (!estado.email) { pantalla("sin-sesion"); return; }
    pantalla("cargando");
    try {
      // Avatar y progreso son lo esencial; el álbum es un extra que no tumba la pantalla.
      const [avatar, progreso, album] = await Promise.all([
        obtenerAvatar(estado.email),
        obtenerProgreso(estado.email),
        obtenerCalcomanias(estado.email).catch(() => null),
      ]);
      if (!avatar.ok || !avatar.cuerpo.objetos || !progreso.ok || !progreso.cuerpo.progreso) throw new Error("sin datos");
      estado.avatar = avatar.cuerpo;
      estado.progreso = progreso.cuerpo.progreso;
      estado.calcomanias = album && album.ok && Array.isArray(album.cuerpo.calcomanias) ? album.cuerpo : null;

      dibujarFigura();
      dibujarCabeza();
      dibujarPuesto();
      dibujarMisiones();
      dibujarArmario();
      dibujarAlbum();
      pantalla("listo");
      seleccionar(pestanaDelHash() || "misiones", { escribirHash: false });
    } catch (e) {
      pantalla("error");
    }
  }

  window.LumeaAvatar = { fechaCorta, CALCOMANIA_DE_MISION };
  document.addEventListener("DOMContentLoaded", () => {
    conectarPestanas();
    $("estado-reintentar").addEventListener("click", cargar);
    cargar();
  });
})();
