// =====================================================================
// avatar.js — llena avatar.html (sin diseño propio: las clases están en
// estilos/avatar.css y estilos/componentes.css). Necesita, antes:
// api.js, formato.js, pegatinas.js y companero.js. La persona se dibuja con persona.js
// (módulo ES: se carga con import()).
//
// La persona es un avatar voxel-art de DiceBear dibujado AQUÍ, en el navegador (vendor/dicebear/):
// no se le pide nada a DiceBear. GET /avatar trae `persona` (rasgos y lo que lleva puesto).
//
// Cinco pestañas (patrón ARIA de «tabs»; abren con #armario, #como-me-veo, #misiones, #calcomanias
// o #companero; la celebración apunta a #armario y #calcomanias):
//   Mi armario    mosaicos: cada uno es la persona con esa prenda puesta. Tocar uno abierto se lo pone; tocar el
//                 que lleva puesto se lo quita; lo que falta por etapa lleva candado y no hace nada.
//   Cómo me veo   los rasgos son libres (piel, peinado, pelo, ojos, boca, pecas o rubor, barba, camiseta):
//                 la vista previa cambia al instante y «Guardar cómo me veo» llama a POST /avatar/rasgos.
//   Misiones      las tres misiones diarias de GET /progreso (con +semillas)
//   Calcomanías   el álbum de GET /calcomanias
//   Tu compañero  los seis compañeros de GET /avatares, quietos; se elige uno con POST /avatar.
//
// La vitrina (sticky, columna izquierda): la persona grande y animada despacio (slow), con el compañero pequeño y
// quieto a su lado. Si GET /avatar no trae `persona` (backend viejo) o no se puede dibujar, el compañero es la figura
// principal, con la cara del ánimo de hoy. Todo lo de la derecha va en pestañas: nada queda debajo de la vitrina.
//
// Reglas: nunca se muestran calorías ni comparaciones; lo bloqueado dice «Etapa N» y no hace nada;
// todo texto del servidor va con textContent.
// =====================================================================
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const { plural, semillas, porcentajeNivel, textoNivel } = window.LumeaFormato;
  const NS = "http://www.w3.org/2000/svg";
  const PESTANAS = ["armario", "como-me-veo", "misiones", "calcomanias", "companero"];
  const NOMBRE_ANIMO = { muy_mal: "Muy mal", mal: "Mal", neutral: "Neutral", bien: "Bien", muy_bien: "Muy bien" };
  // Cada misión diaria tiene su calcomanía (la que se gana la primera vez que se cumple)
  const CALCOMANIA_DE_MISION = { fruta: "fruta", tres_comidas: "tres_al_dia", check_in_animo: "como_llegas" };
  // Los rasgos, en secciones y en el orden en que se muestran. Los que el backend todavía no manda (B8) no se dibujan.
const SECCIONES = [
  { titulo: "Cara", claves: ["skinColor", "eyesVariant", "eyebrowsVariant", "noseVariant", "mouthVariant", "cheeksVariant", "beardVariant"] },
  { titulo: "Pelo", claves: ["topVariant", "hairColor"] },
  { titulo: "Ropa", claves: ["shirtColor", "pantsColor", "shoesColor"] },
  { titulo: "Fondo", claves: ["backgroundColor"] },
];
const RASGOS_ORDEN = SECCIONES.flatMap((x) => x.claves);
const RASGOS_COLOR = ["skinColor", "hairColor", "shirtColor", "pantsColor", "shoesColor", "backgroundColor"];   // muestras redondas
const RASGOS_MOSAICO = ["topVariant", "eyesVariant", "eyebrowsVariant", "noseVariant", "mouthVariant", "cheeksVariant", "beardVariant"];
// El mosaico se acerca a la parte de la cara que cambia ([x, y, ancho, alto] en el lienzo de 128 de la persona)
const RECORTES = {
  eyesVariant: [31, 26, 56, 56], eyebrowsVariant: [31, 26, 56, 56], noseVariant: [41, 50, 34, 34],
  mouthVariant: [40, 60, 36, 36], cheeksVariant: [30, 40, 56, 56], beardVariant: [38, 56, 42, 42],
};
const HEX = /^[0-9a-f]{6}$/i;

  // Íconos de Lucide (licencia ISC), 24x24
  const ICONOS = {
    ropa: ["M20.38 3.46 16 2a4 4 0 0 1-8 0L3.62 3.46a2 2 0 0 0-1.34 2.23l.58 3.47a1 1 0 0 0 .99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V10h2.15a1 1 0 0 0 .99-.84l.58-3.47a2 2 0 0 0-1.34-2.23z"],
    accesorio: ["M6 11a4 4 0 1 0 0 8 4 4 0 0 0 0-8z", "M18 11a4 4 0 1 0 0 8 4 4 0 0 0 0-8z", "M14 15a2 2 0 0 0-2-2 2 2 0 0 0-2 2", "M2.5 13 5 7c.7-1.3 1.4-2 3-2", "M21.5 13 19 7c-.7-1.3-1.5-2-3-2"],
    candado: ["M5 11h14a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2z", "M7 11V7a5 5 0 0 1 10 0v4"],
    check: ["M20 6 9 17l-5-5"],
    bandera: ["M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z", "M4 22v-7"],
    persona: ["M12 3a5 5 0 1 0 0 10 5 5 0 0 0 0-10z", "M20 21a8 8 0 0 0-16 0"],
  };

  const estado = { email: null, progreso: null, avatar: null, calcomanias: null, companeros: null, ocupado: false,
                   rasgos: null, armarioSucio: false, rasgosDibujados: false, figura: 0 };

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

  // ---------- La persona (persona.js, DiceBear voxel-art local) ----------
  let moduloPersona = null;
  function cargarPersona() {            // un servidor sencillo puede cortar una petición del montón: un reintento
    if (!moduloPersona) {
      moduloPersona = import("./persona.js")
        .catch(() => new Promise((ok) => setTimeout(ok, 200)).then(() => import("./persona.js")))
        .catch((e) => { moduloPersona = null; throw e; });
    }
    return moduloPersona;
  }

  // La dirección data: de la persona con esos rasgos y esa ropa; null si no se puede dibujar
  async function dibujoDePersona(persona, animada, recorte) {
    try { return await (await cargarPersona()).urlDePersona(persona, { animada: !!animada, recorte: recorte || null }); } catch (e) { return null; }
  }

  // Lo que la persona lleva puesto ahora, con `objeto` (de ropa o accesorio) en lugar de lo que hubiera de su tipo
  function personaCon(objeto, rasgos) {
    const actual = (estado.avatar.persona && estado.avatar.persona.puesto) || {};
    const puesto = { ropa: actual.ropa || null, accesorio: actual.accesorio || null };
    if (objeto) puesto[objeto.tipo] = objeto;
    return { rasgos: rasgos || estado.rasgos, puesto };
  }

  function conPersona() { return !!(estado.avatar && estado.avatar.persona && estado.rasgos); }

  // ---------- El avatar grande ----------
  // Sin compañero o sin internet: una silueta (el nombre y el ánimo van escritos en el aria-label y al lado)
  function silueta() {
    const respaldo = crear("span", "avatar-figura__silueta");
    respaldo.appendChild(icono("persona"));
    return respaldo;
  }

  async function dibujarFigura() {
    const caja = $("avatar-figura");
    const turno = ++estado.figura;
    const p = estado.progreso;
    const c = (p && p.avatar) || null;                     // el compañero, con las caras de cada ánimo (GET /progreso)
    const respaldo = (estado.avatar && estado.avatar.respaldo_dicebear) || null;
    const animo = c && c.estado_animo_hoy;
    const nombre = (c && c.nombre) || (respaldo && respaldo.nombre) || "";
    const direccion = (c && (c.url_con_animo || c.url)) || (respaldo && respaldo.url) || null;
    const detalleAnimo = `${nombre ? ` ${nombre}` : ""}${animo ? `, tu ánimo de hoy: ${NOMBRE_ANIMO[animo] || animo}` : ""}`;

    const dibujo = conPersona() ? await dibujoDePersona(personaCon(null), true) : null;
    if (turno !== estado.figura) return;                    // llegó otro dibujo más nuevo (un rasgo que cambió)

    const vista = $("rasgos-vista-img");                    // la vista previa pequeña de «Cómo me veo» (celular)
    if (vista && dibujo) vista.src = dibujo;
    if (dibujo) {                                           // la persona grande y animada; el compañero pequeño y quieto
      caja.setAttribute("aria-label", `Tu avatar y tu compañero${detalleAnimo}`);
      let img = caja.querySelector(".avatar-figura__persona-img");
      if (img) {                                            // solo cambia el dibujo: el compañero no se reinicia, salvo que ya sea otro
        img.src = dibujo;
        const actual = caja.querySelector(".avatar-figura__companero");
        const nuevo = LumeaCompanero.imagen(direccion, null, "avatar-figura__companero");
        if (nuevo && (!actual || actual.dataset.fuente !== nuevo.dataset.fuente)) { if (actual) actual.replaceWith(nuevo); else caja.appendChild(nuevo); }
        return;
      }
      caja.replaceChildren();
      caja.classList.add("avatar-figura--con-persona");
      img = document.createElement("img");
      img.alt = "";
      img.className = "avatar-figura__persona-img";
      img.src = dibujo;
      const persona = crear("div", "avatar-figura__persona");
      persona.appendChild(img);
      caja.appendChild(persona);
      const compa = LumeaCompanero.imagen(direccion, null, "avatar-figura__companero");    // el pequeño va quieto
      if (compa) caja.appendChild(compa);
      return;
    }
    // El compañero es la figura principal: grande, con el ánimo de hoy y despacio. Sin internet queda una silueta.
    caja.replaceChildren();
    caja.classList.remove("avatar-figura--con-persona");
    caja.setAttribute("aria-label", `Tu compañero${detalleAnimo}`);
    const img = LumeaCompanero.imagen(direccion, "slow", "avatar-figura__cara");
    if (!img) { caja.appendChild(silueta()); return; }
    img.addEventListener("error", () => caja.replaceChildren(silueta()));
    caja.appendChild(img);
  }

  // «Te faltan 35 semillas para la etapa 5: Camisa de cuadros»: lo que se abre en la etapa que viene
  function proximaPrenda(p) {
    const objetos = (estado.avatar && estado.avatar.objetos) || {};
    const todos = (objetos.ropa || []).concat(objetos.accesorio || []);
    const siguiente = todos.find((o) => o.nivel_requerido === p.nivel + 1);
    return siguiente ? siguiente.nombre : null;
  }

  function dibujarCabeza() {
    const p = estado.progreso;
    if (!p) return;
    $("avatar-nivel").textContent = `Etapa ${p.nivel}`;
    const prenda = p.xp_siguiente_nivel == null ? null : proximaPrenda(p);
    $("avatar-faltan").textContent = textoNivel(p) + (prenda ? `: ${prenda}` : "");
    const pct = porcentajeNivel(p);
    $("avatar-relleno").style.setProperty("--avance", `${pct}%`);
    const riel = $("avatar-riel");
    riel.setAttribute("aria-valuenow", String(pct));
    riel.setAttribute("aria-label", p.xp_siguiente_nivel == null ? "Etapa máxima" : `Avance hacia la etapa ${p.nivel + 1}`);
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
      fila.appendChild(crear("span", "chip chip--mision numero cifra", `+${semillas(m.xp)}`));
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

  // ---------- Mi armario ----------
  // Una cuadrícula de mosaicos: cada uno muestra a la persona, con sus propios rasgos, con esa prenda puesta.
  function dibujarArmario(enfocarId) {
    const lista = $("armario-lista");
    lista.replaceChildren();
    const objetos = (estado.avatar && estado.avatar.objetos) || {};
    (objetos.ropa || []).concat(objetos.accesorio || [])
      .sort((a, b) => a.nivel_requerido - b.nivel_requerido)
      .forEach((o) => lista.appendChild(mosaicoDePrenda(o)));
    estado.armarioSucio = false;
    if (enfocarId) {
      const boton = lista.querySelector(`[data-objeto="${enfocarId}"]`);
      if (boton) boton.focus();
    }
  }

  function mosaicoDePrenda(o) {
    const bloqueado = !o.desbloqueado;
    const puesto = !!o.puesto && !bloqueado;
    const li = crear("li", "prenda" + (bloqueado ? " prenda--bloqueada" : "") + (puesto ? " prenda--puesta" : ""));
    const boton = crear("button", "prenda__mosaico");
    boton.type = "button";
    boton.dataset.objeto = o.id;
    const imagen = crear("span", "prenda__imagen");
    imagen.setAttribute("aria-hidden", "true");
    if (conPersona()) {
      const img = document.createElement("img");
      img.alt = "";
      img.className = "prenda__persona";
      imagen.appendChild(img);
      dibujoDePersona(personaCon(o), false).then((dibujo) => { if (dibujo) img.src = dibujo; else img.replaceWith(icono(o.tipo)); });
    } else {
      imagen.appendChild(icono(bloqueado ? "candado" : o.tipo));
    }
    if (bloqueado) imagen.appendChild(icono("candado", "prenda__candado-grande"));
    boton.appendChild(imagen);
    boton.appendChild(crear("span", "prenda__nombre", o.nombre));
    const detalle = crear("span", "prenda__estado");
    if (bloqueado) detalle.appendChild(icono("candado", "prenda__candado"));
    detalle.appendChild(document.createTextNode(bloqueado ? `Etapa ${o.nivel_requerido}` : (puesto ? "Puesto" : "Disponible")));
    boton.appendChild(detalle);

    if (bloqueado) {
      boton.setAttribute("aria-disabled", "true");            // se puede enfocar y leer, pero no hace nada
      boton.setAttribute("aria-label", `${o.nombre}, se abre en la etapa ${o.nivel_requerido}`);
    } else {
      boton.setAttribute("aria-pressed", String(puesto));
      boton.setAttribute("aria-label", o.nombre);
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
    if (estado.ocupado || !objeto.desbloqueado) return;
    estado.ocupado = true;
    const ponerse = !objeto.puesto;
    try {
      const { ok, cuerpo } = ponerse
        ? await equiparObjeto(estado.email, objeto.tipo, objeto.id)       // api.js
        : await quitarObjeto(estado.email, objeto.tipo);
      if (!ok || !cuerpo.objetos) {
        const faltan = cuerpo && cuerpo.niveles_faltantes;
        throw new Error(faltan ? `Todavía no se abre: te ${faltan === 1 ? "falta 1 etapa" : `faltan ${faltan} etapas`}.` : "No se pudo guardar el cambio.");
      }
      estado.avatar = cuerpo;                                              // el backend responde con el avatar completo
      dibujarFigura();                                                     // la persona de la vitrina cambia al instante
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

  // ---------- Cómo me veo: los rasgos son libres ----------
  function rasgosDisponibles() { return (estado.avatar && estado.avatar.rasgos_disponibles) || {}; }

  // Las opciones de un rasgo en el orden del servidor; en mejillas y barba, primero «Ninguno» (que se guarda como null)
  function opcionesDe(info) {
    const lista = Object.entries(info.opciones || {});
    if (info.ninguno) lista.unshift(["", info.ninguno]);
    return lista;
  }

  // El mayor divisor de n que no pasa de tope: las muestras de color se reparten sin dejar una huérfana (12 → 6 + 6, 8 → 4 + 4)
  function columnasSinHuerfanas(n, tope) {
    for (let c = Math.min(n, tope); c > 1; c--) if (n % c === 0) return c;
    return n;
  }

  function dibujarRasgos() {
    const form = $("rasgos-form");
    form.replaceChildren();
    const disponibles = rasgosDisponibles();
    $("rasgos-guardar").hidden = !RASGOS_ORDEN.some((k) => disponibles[k]);
    SECCIONES.forEach((seccion) => {
      const claves = seccion.claves.filter((k) => disponibles[k]);
      if (!claves.length) return;
      const caja = crear("section", "rasgos-seccion");
      caja.appendChild(crear("h3", "rasgos-seccion__titulo", seccion.titulo));
      claves.forEach((clave) => caja.appendChild(grupoDeRasgo(clave, disponibles[clave])));
      form.appendChild(caja);
    });
    estado.rasgosDibujados = true;
    redibujarMiniaturas();
  }

  // Un rasgo: un <fieldset> con su <legend> y un radio con su <label> por opción
  function grupoDeRasgo(clave, info) {
    const esColor = RASGOS_COLOR.includes(clave);
    const grupo = crear("fieldset", `rasgo rasgo--${esColor ? "color" : "mosaico"} rasgo--${clave}`);
    grupo.appendChild(crear("legend", "rasgo__nombre", info.nombre));
    const opciones = crear("div", "rasgo__opciones");
    const lista = opcionesDe(info);
    if (esColor) {
      opciones.style.setProperty("--cols-m", String(columnasSinHuerfanas(lista.length, 6)));
      opciones.style.setProperty("--cols-g", String(columnasSinHuerfanas(lista.length, 8)));
    }
    lista.forEach(([valor, nombre]) => {
      const etiqueta = crear("label", "rasgo__opcion");
      const radio = document.createElement("input");
      radio.type = "radio";
      radio.name = `rasgo-${clave}`;
      radio.value = valor;
      radio.className = "rasgo__radio";
      radio.checked = String(estado.rasgos[clave] == null ? "" : estado.rasgos[clave]) === valor;
      radio.addEventListener("change", () => cambiarRasgo(clave, valor));
      etiqueta.appendChild(radio);
      if (esColor) {
        const muestra = crear("span", "rasgo__muestra" + (valor === "" ? " rasgo__muestra--ninguna" : ""));
        if (HEX.test(valor)) muestra.style.backgroundColor = `#${valor}`;
        etiqueta.appendChild(muestra);
        etiqueta.appendChild(crear("span", "solo-lector", nombre));
        etiqueta.title = nombre;
      } else {
        const mini = crear("span", "rasgo__mini");
        mini.setAttribute("aria-hidden", "true");
        const img = document.createElement("img");
        img.alt = "";
        img.dataset.rasgo = clave;
        img.dataset.valor = valor;
        mini.appendChild(img);
        etiqueta.appendChild(mini);
        etiqueta.appendChild(crear("span", "rasgo__texto", nombre));
      }
      opciones.appendChild(etiqueta);
    });
    grupo.appendChild(opciones);
    return grupo;
  }

  // Los mosaicos (peinado, ojos, cejas, nariz, boca, mejillas y barba) muestran a la persona con esa opción y sus otros rasgos de
  // ahora; los de la cara se acercan a la parte que cambia, para que se note la diferencia
  let tiempoMiniaturas = null;
  function redibujarMiniaturas() {
    clearTimeout(tiempoMiniaturas);
    tiempoMiniaturas = setTimeout(() => {
      document.querySelectorAll("#rasgos-form img[data-rasgo]").forEach((img) => {
        const clave = img.dataset.rasgo;
        const rasgos = { ...estado.rasgos, [clave]: img.dataset.valor };
        dibujoDePersona(personaCon(null, rasgos), false, RECORTES[clave] || null).then((dibujo) => { if (dibujo) img.src = dibujo; });
      });
    }, 60);
  }

  function cambiarRasgo(clave, valor) {
    estado.rasgos[clave] = valor === "" ? null : valor;     // «Ninguno» solo existe en mejillas y barba
    estado.armarioSucio = true;                              // los mosaicos del armario se vuelven a dibujar al abrirlo
    dibujarFigura();                                         // la vista previa cambia al instante
    redibujarMiniaturas();
  }

  async function guardarRasgos() {
    if (estado.ocupado) return;
    estado.ocupado = true;
    try {
      const disponibles = rasgosDisponibles();
      const rasgos = {};                                     // solo las claves permitidas
      RASGOS_ORDEN.forEach((k) => { if (disponibles[k] && k in estado.rasgos) rasgos[k] = estado.rasgos[k]; });
      const { ok, cuerpo } = await guardarRasgosAvatar(estado.email, rasgos);               // api.js
      if (!ok || !cuerpo.persona) throw new Error("No se pudo guardar cómo te ves.");
      estado.avatar = cuerpo;
      estado.rasgos = { ...cuerpo.persona.rasgos };
      estado.armarioSucio = true;
      dibujarFigura();
      aviso("Guardamos cómo te ves.");
    } catch (e) {
      aviso(e.message && !/fetch|network/i.test(e.message) ? e.message : "No se pudo conectar. Inténtalo otra vez.");
    } finally {
      estado.ocupado = false;
    }
  }

  // ---------- Tu compañero ----------
  // La misma tarjeta que una prenda del armario: imagen, nombre, estado y un botón. Lo bloqueado se puede enfocar y leer,
  // pero no hace nada (aria-disabled); el compañero de ahora también: ya está elegido.
  function tarjetaDeCompanero(c) {
    const bloqueado = !c.desbloqueado;
    const elegido = !bloqueado && !!c.seleccionado;
    const li = crear("li", "prenda" + (bloqueado ? " prenda--bloqueada" : "") + (elegido ? " prenda--puesta" : ""));
    const imagen = crear("span", "prenda__imagen prenda__imagen--companero");
    imagen.setAttribute("aria-hidden", "true");
    const img = LumeaCompanero.imagen(c.url, null, "companero__img");                  // quieto: aquí nada se mueve
    if (img) {
      img.addEventListener("error", () => imagen.replaceChildren(icono("persona")));   // sin internet: una silueta
      imagen.appendChild(img);
    } else {
      imagen.appendChild(icono("persona"));
    }
    li.appendChild(imagen);
    li.appendChild(crear("p", "prenda__nombre", c.nombre));
    const detalle = crear("p", "prenda__estado");
    if (bloqueado) detalle.appendChild(icono("candado", "prenda__candado"));
    detalle.appendChild(document.createTextNode(bloqueado ? `Se abre en la etapa ${c.nivel_requerido}` : (elegido ? "Tu compañero" : "Disponible")));
    li.appendChild(detalle);

    const boton = crear("button", "boton boton--secundario prenda__boton");      // la acción principal de Avatar es el armario
    boton.type = "button";
    boton.dataset.companero = c.id;
    if (bloqueado) {
      boton.setAttribute("aria-disabled", "true");
      boton.textContent = `Etapa ${c.nivel_requerido}`;
      boton.setAttribute("aria-label", `${c.nombre}, se abre en la etapa ${c.nivel_requerido}`);
    } else if (elegido) {
      boton.setAttribute("aria-disabled", "true");
      boton.textContent = "Elegido";
      boton.setAttribute("aria-label", `Elegido: ${c.nombre}`);
    } else {
      boton.textContent = "Elegir";
      boton.setAttribute("aria-label", `Elegir a ${c.nombre}`);
      boton.addEventListener("click", () => elegirCompanero(c));
    }
    li.appendChild(boton);
    return li;
  }

  function dibujarCompaneros(enfocarId) {
    const datos = estado.companeros;
    const lista = $("companeros-lista");
    lista.replaceChildren();
    $("companeros-error").hidden = !!datos;
    if (!datos) return;
    datos.avatares.forEach((c) => lista.appendChild(tarjetaDeCompanero(c)));
    if (enfocarId) {
      const boton = Array.from(lista.querySelectorAll("button")).find((b) => b.dataset.companero === enfocarId);
      if (boton) boton.focus();
    }
  }

  async function elegirCompanero(c) {
    if (estado.ocupado) return;
    estado.ocupado = true;
    try {
      const { ok, cuerpo } = await elegirAvatarDiceBear(estado.email, c.id);          // api.js
      if (!ok || !cuerpo.avatar) {
        const faltan = cuerpo && cuerpo.niveles_faltantes;
        throw new Error(faltan ? `Todavía no se abre: te ${faltan === 1 ? "falta 1 etapa" : `faltan ${faltan} etapas`}.` : "No se pudo guardar el cambio.");
      }
      estado.companeros.avatar_actual = c.id;
      estado.companeros.avatares.forEach((x) => { x.seleccionado = x.id === c.id; });
      // GET /progreso trae al compañero nuevo con las caras de cada ánimo; POST /avatar solo trae la de ojos neutros
      const nuevo = await obtenerProgreso(estado.email).catch(() => null);
      if (nuevo && nuevo.ok && nuevo.cuerpo.progreso) estado.progreso = nuevo.cuerpo.progreso;
      else estado.progreso = { ...estado.progreso, avatar: { ...cuerpo.avatar, estado_animo_hoy: null } };
      dibujarFigura();
      dibujarCompaneros(c.id);
      aviso(`Tu compañero ahora es ${c.nombre}.`);
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
  const sinMovimiento = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  const tokenCss = (nombre) => getComputedStyle(document.documentElement).getPropertyValue(nombre).trim();
  let primeraSeleccion = true;                             // al abrir la pantalla el panel no se anima

  // El panel nuevo entra con fundido y 12 px de desplazamiento desde el lado de la pestaña elegida, y la columna cambia de alto sin saltar
  // (duración y curva de --m-base y --m-salida; con prefers-reduced-motion no se anima nada).
  function animarPanel(panel, columna, altoAntes, haciaLaDerecha) {
    const duracion = parseFloat(tokenCss("--m-base")) || 0;
    if (!duracion) return;
    const opciones = { duration: duracion, easing: tokenCss("--m-salida") || "ease-out" };
    panel.animate([{ opacity: 0, transform: `translateX(${haciaLaDerecha ? 12 : -12}px)` }, { opacity: 1, transform: "none" }], opciones);
    const altoDespues = columna.offsetHeight;
    if (altoAntes && altoDespues && altoAntes !== altoDespues) {
      columna.style.overflow = "hidden";                   // solo mientras dura el cambio de alto
      const alto = columna.animate([{ height: `${altoAntes}px` }, { height: `${altoDespues}px` }], opciones);
      alto.onfinish = alto.oncancel = () => { columna.style.overflow = ""; };
    }
  }

  function seleccionar(nombre, { enfocar = false, escribirHash = true } = {}) {
    const previa = PESTANAS.find((n) => $(`pestana-${n}`).getAttribute("aria-selected") === "true");
    const columna = $("pestanas").parentElement;
    const animar = !primeraSeleccion && previa && previa !== nombre && !sinMovimiento();
    const altoAntes = animar ? columna.offsetHeight : 0;
    primeraSeleccion = false;
    PESTANAS.forEach((n) => {
      const activa = n === nombre;
      const pestana = $(`pestana-${n}`);
      pestana.setAttribute("aria-selected", String(activa));
      pestana.tabIndex = activa ? 0 : -1;                   // solo la activa entra con Tab; las flechas mueven
      $(`panel-${n}`).hidden = !activa;
      if (activa && enfocar) pestana.focus({ preventScroll: true });
      if (activa) {                                         // si la pestaña queda fuera de vista, la fila se desliza suave hasta centrarla (sin mover la página)
        const fila = pestana.parentElement;
        const fuera = pestana.offsetLeft < fila.scrollLeft || pestana.offsetLeft + pestana.offsetWidth > fila.scrollLeft + fila.clientWidth;
        if (fuera) fila.scrollTo({ left: Math.max(0, pestana.offsetLeft - (fila.clientWidth - pestana.offsetWidth) / 2), behavior: sinMovimiento() ? "auto" : "smooth" });
      }
    });
    moverIndicador($(`pestana-${nombre}`), true);
    if (nombre === "armario" && estado.armarioSucio) dibujarArmario();
    if (nombre === "como-me-veo" && estado.avatar && !estado.rasgosDibujados) dibujarRasgos();
    if (animar) animarPanel($(`panel-${nombre}`), columna, altoAntes, PESTANAS.indexOf(nombre) > PESTANAS.indexOf(previa));
    if (escribirHash && location.hash !== `#${nombre}`) history.replaceState(null, "", `#${nombre}`);
  }

  // El indicador de la pestaña activa: una píldora (aria-hidden) que se desliza hasta ella. La primera vez, y al cambiar el tamaño de la
  // ventana, se coloca sin deslizarse. Si la pestaña no se ve todavía (ancho 0), no se pone y la pestaña activa lleva su propio fondo.
  function moverIndicador(pestana, animar) {
    const fila = pestana.parentElement;
    if (!pestana.offsetWidth) return;
    let indicador = fila.querySelector(".pestanas__indicador");
    const nuevo = !indicador;
    if (nuevo) {
      indicador = document.createElement("span");
      indicador.className = "pestanas__indicador";
      indicador.setAttribute("aria-hidden", "true");
      fila.prepend(indicador);
    }
    if (nuevo || !animar) indicador.style.transition = "none";
    indicador.style.width = `${pestana.offsetWidth}px`;
    indicador.style.transform = `translateX(${pestana.offsetLeft}px)`;
    if (nuevo || !animar) { indicador.getBoundingClientRect(); indicador.style.transition = ""; }
    fila.dataset.indicador = "1";
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
    window.addEventListener("resize", () => { const activa = document.querySelector(".pestana[aria-selected='true']"); if (activa) moverIndicador(activa, false); });
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
      // Avatar y progreso son lo esencial; el álbum y los compañeros son extras que no tumban la pantalla.
      const [avatar, progreso, album, companeros] = await Promise.all([
        obtenerAvatar(estado.email),
        obtenerProgreso(estado.email),
        obtenerCalcomanias(estado.email).catch(() => null),
        obtenerAvataresDiceBear(estado.email).catch(() => null),
      ]);
      if (!avatar.ok || !avatar.cuerpo.objetos || !progreso.ok || !progreso.cuerpo.progreso) throw new Error("sin datos");
      estado.avatar = avatar.cuerpo;
      estado.rasgos = avatar.cuerpo.persona ? { ...avatar.cuerpo.persona.rasgos } : null;
      estado.progreso = progreso.cuerpo.progreso;
      estado.calcomanias = album && album.ok && Array.isArray(album.cuerpo.calcomanias) ? album.cuerpo : null;
      estado.companeros = companeros && companeros.ok && Array.isArray(companeros.cuerpo.avatares) ? companeros.cuerpo : null;

      dibujarFigura();
      dibujarCabeza();
      dibujarPuesto();
      dibujarMisiones();
      dibujarArmario();
      dibujarCompaneros();
      dibujarAlbum();
      pantalla("listo");
      seleccionar(pestanaDelHash() || "armario", { escribirHash: false });
    } catch (e) {
      pantalla("error");
    }
  }

  window.LumeaAvatar = { fechaCorta, CALCOMANIA_DE_MISION };
  document.addEventListener("DOMContentLoaded", () => {
    conectarPestanas();
    $("rasgos-guardar").addEventListener("click", guardarRasgos);
    $("estado-reintentar").addEventListener("click", cargar);
    cargar();
  });
})();
