// =====================================================================
// celebracion.js — celebra lo que la persona HIZO (sin diseño propio:
// los estilos están en estilos/celebracion.css y estilos/pegatinas.css).
//
//   window.LumeaCelebrar(gamificacion)
//
// `gamificacion` es la clave del mismo nombre que devuelven /predecir,
// /confirmar-alimento y POST /estado-animo (Backend/docs/CONTRATO_GAMIFICACION.md).
// Cada campo es opcional: si el backend no manda uno, ese momento no ocurre.
//
// Los momentos van en cola, UNO A LA VEZ, del más pequeño al más grande:
//   1. XP        un chip «+10 semillas» que se va solo (y «Meta de hoy cumplida»)
//   2. Misión    «Misión cumplida: …» (con su calcomanía pegándose, si la hay)
//   3. Calcomanía nueva: se pega; botones «Ver mi álbum» y «Seguir»
//   4. Nivel     el único modal: <dialog> con «Llegaste a la etapa N» y lo que se abrió («Prenda nueva: …», con la
//                persona puesta esa prenda, dibujada en el navegador)
// Solo la subida de nivel bloquea la pantalla; lo demás deja seguir registrando.
//
// Todo texto que llega del servidor se escribe con textContent.
// Esc cierra el nivel (y la calcomanía que esté a la vista); al cerrar el
// nivel el foco vuelve a donde estaba.
//
// Cómo conectarla al check-in de ánimo (una línea, la pone Isabella): después
// de recibir la respuesta de registrarEstadoAnimo(), pasa su clave gamificacion:
//     const { cuerpo } = await registrarEstadoAnimo(email, estado);
//     if (window.LumeaCelebrar) LumeaCelebrar(cuerpo.gamificacion);
// =====================================================================
(function () {
  "use strict";

  // Cuánto dura cada momento que se va solo (en milisegundos). Las pruebas los acortan.
  const TIEMPOS = { xp: 3000, mision: 3500, salida: 220 };

  const cola = [];
  let ocupada = false;
  let region = null;

  const reducido = () => !!(window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);
  const esperar = (ms) => new Promise((fin) => setTimeout(fin, ms));

  function crear(etiqueta, clase, texto) {
    const el = document.createElement(etiqueta);
    if (clase) el.className = clase;
    if (texto != null) el.textContent = texto;
    return el;
  }

  // Zona donde aparecen los avisos pequeños. role=status + aria-live: se anuncian sin interrumpir.
  function asegurarRegion() {
    if (region && document.body.contains(region)) return region;
    region = crear("div", "celebracion");
    region.setAttribute("role", "status");
    region.setAttribute("aria-live", "polite");
    document.body.appendChild(region);
    return region;
  }

  async function quitar(nodo) {
    nodo.classList.add("momento--saliendo");
    await esperar(reducido() ? 0 : TIEMPOS.salida);
    nodo.remove();
  }

  async function mostrarUnRato(nodos, ms) {
    nodos.forEach((n) => asegurarRegion().appendChild(n));
    await esperar(ms);
    await Promise.all(nodos.map(quitar));
  }

  // ---------- 1. XP y meta ----------
  function momentoXP(g) {
    return () => {
      const nodos = [];
      const xp = crear("p", "celebracion__chip momento momento--logro", `+${(window.LumeaFormato ? window.LumeaFormato.semillas(g.xp_ganado) : g.xp_ganado + " semillas")}`);
      nodos.push(xp);
      if (g.meta_diaria && g.meta_diaria.recien_cumplida) {
        nodos.push(crear("p", "celebracion__chip celebracion__chip--meta momento", "Meta de hoy cumplida"));
      }
      return mostrarUnRato(nodos, TIEMPOS.xp);
    };
  }

  // ---------- 2. Misión cumplida (con su calcomanía, si la ganó con ella) ----------
  function momentoMision(mision, pegatina) {
    return () => {
      const tarjeta = crear("div", "celebracion__tarjeta celebracion__tarjeta--mision momento momento--logro");
      if (pegatina) {
        const dibujo = LumeaPegatina.crear(pegatina);
        dibujo.classList.add("pegatina--pegandose");
        tarjeta.appendChild(dibujo);
      }
      tarjeta.appendChild(crear("p", "celebracion__titulo", `Misión cumplida: ${mision.nombre}`));
      if (pegatina) tarjeta.appendChild(crear("p", "celebracion__texto", `Calcomanía nueva: ${pegatina.nombre}`));
      return mostrarUnRato([tarjeta], TIEMPOS.mision);
    };
  }

  // ---------- 3. Calcomanía nueva: espera a que la persona toque «Seguir» ----------
  function momentoPegatina(c) {
    return () => new Promise((terminar) => {
      const tarjeta = crear("div", `celebracion__tarjeta celebracion__tarjeta--${LumeaPegatina.rolDe(c)} momento momento--logro`);
      const dibujo = LumeaPegatina.crear(c);
      dibujo.classList.add("pegatina--pegandose");
      tarjeta.appendChild(dibujo);
      tarjeta.appendChild(crear("p", "celebracion__titulo", `Calcomanía nueva: ${c.nombre}`));
      if (c.descripcion) tarjeta.appendChild(crear("p", "celebracion__texto", c.descripcion));

      const acciones = crear("div", "celebracion__acciones");
      const album = crear("a", "celebracion__boton", "Ver mi álbum");
      album.href = "avatar.html#calcomanias";
      const seguir = crear("button", "celebracion__boton celebracion__boton--secundario", "Seguir");
      seguir.type = "button";
      acciones.append(album, seguir);
      tarjeta.appendChild(acciones);

      let cerrada = false;
      const cerrar = async () => {
        if (cerrada) return;
        cerrada = true;
        document.removeEventListener("keydown", alTeclear);
        await quitar(tarjeta);
        terminar();
      };
      const alTeclear = (e) => { if (e.key === "Escape") cerrar(); };
      seguir.addEventListener("click", cerrar);
      album.addEventListener("click", cerrar);
      document.addEventListener("keydown", alTeclear);

      asegurarRegion().appendChild(tarjeta);
      // No le quita el foco a nadie, salvo que se haya perdido (p. ej. al reemplazarse los botones).
      const activo = document.activeElement;
      if (!activo || activo === document.body) seguir.focus();
    });
  }

  // La persona con la prenda nueva puesta: se dibuja en el navegador (persona.js) con los rasgos de GET /avatar.
  // Es un adorno: si algo falla (sin parámetros, sin red, sin persona) queda solo el texto.
  async function ponerPersona(hueco, d) {
    try {
      if (!d.parametros || typeof obtenerAvatar !== "function" || typeof obtenerSesion !== "function") return;
      const email = obtenerSesion();
      if (!email) return;
      const { ok, cuerpo } = await obtenerAvatar(email);
      if (!ok || !cuerpo.persona) return;
      const puesto = { ropa: null, accesorio: null, ...(cuerpo.persona.puesto || {}) };
      puesto[d.tipo] = { parametros: d.parametros };
      const { urlDePersona } = await import("./persona.js");
      const img = document.createElement("img");
      img.alt = "";
      img.className = "celebracion__persona-img";
      img.src = await urlDePersona({ rasgos: cuerpo.persona.rasgos, puesto });
      hueco.appendChild(img);
    } catch (e) { /* queda el texto */ }
  }

  // ---------- 4. Subida de nivel (modal) ----------
  function momentoNivel(g) {
    return () => new Promise((terminar) => {
      const anterior = document.activeElement;
      const lista = Array.isArray(g.desbloqueos) ? g.desbloqueos : [];
      const objetos = lista.filter((d) => d.tipo === "ropa" || d.tipo === "accesorio");
      const avatares = lista.filter((d) => d.tipo === "avatar");

      const dialogo = crear("dialog", "celebracion__nivel");
      dialogo.setAttribute("aria-labelledby", "celebracion-nivel-titulo");
      dialogo.appendChild(crear("p", "celebracion__numero cifra", String(g.nivel)));
      const titulo = crear("h2", null, `Llegaste a la etapa ${g.nivel}`);
      titulo.id = "celebracion-nivel-titulo";
      dialogo.appendChild(titulo);

      objetos.forEach((d) => {                          // «Prenda nueva: Overol de jardín», con la persona puesta esa prenda
        const figura = crear("figure", "celebracion__prenda");
        const hueco = crear("span", "celebracion__persona");
        hueco.setAttribute("aria-hidden", "true");
        figura.appendChild(hueco);
        figura.appendChild(crear("figcaption", "celebracion__titulo", `Prenda nueva: ${d.nombre}`));
        dialogo.appendChild(figura);
        ponerPersona(hueco, d);
      });
      if (avatares.length) {
        dialogo.appendChild(crear("p", null, "Compañero nuevo:"));
        const ul = crear("ul", "celebracion__lista");
        avatares.forEach((d) => ul.appendChild(crear("li", null, d.nombre)));
        dialogo.appendChild(ul);
      }
      if (!lista.length) dialogo.appendChild(crear("p", null, "Gracias por volver a registrar."));

      const acciones = crear("div", "celebracion__acciones");
      if (objetos.length) {
        const ponerme = crear("a", "celebracion__boton", "Ponérmelo");
        ponerme.href = "avatar.html#armario";
        acciones.appendChild(ponerme);
      }
      const seguir = crear("button", "celebracion__boton celebracion__boton--secundario", "Seguir");
      seguir.type = "button";
      seguir.addEventListener("click", () => dialogo.close());
      acciones.appendChild(seguir);
      dialogo.appendChild(acciones);

      // Esc o «Seguir» disparan «close»: ahí se limpia y el foco vuelve a donde estaba.
      dialogo.addEventListener("close", () => {
        dialogo.remove();
        if (anterior && document.body.contains(anterior) && typeof anterior.focus === "function") anterior.focus();
        terminar();
      });
      document.body.appendChild(dialogo);
      if (typeof dialogo.showModal === "function") dialogo.showModal();
      else dialogo.setAttribute("open", "");
    });
  }

  // ---------- Armar la cola ----------
  function momentosDe(g) {
    const momentos = [];
    const nuevas = Array.isArray(g.calcomanias_nuevas) ? g.calcomanias_nuevas.slice() : [];
    const misiones = Array.isArray(g.misiones_cumplidas) ? g.misiones_cumplidas : [];

    if (g.xp_ganado > 0) momentos.push(momentoXP(g));

    // Una calcomanía de rol «mision» se pega junto con su misión; las demás tienen su momento.
    misiones.forEach((m) => {
      const i = nuevas.findIndex((c) => c.rol === "mision");
      momentos.push(momentoMision(m, i >= 0 ? nuevas.splice(i, 1)[0] : null));
    });
    nuevas.forEach((c) => momentos.push(momentoPegatina(c)));

    if (g.subio_de_nivel) momentos.push(momentoNivel(g));
    return momentos;
  }

  async function procesar() {
    if (ocupada) return;
    ocupada = true;
    while (cola.length) {
      const siguiente = cola.shift();
      try { await siguiente(); } catch (e) { console.warn("Celebración omitida:", e); }
    }
    ocupada = false;
  }

  window.LumeaCelebrar = function (gamificacion) {
    if (!gamificacion || typeof gamificacion !== "object") return;     // null = nada que celebrar
    cola.push(...momentosDe(gamificacion));
    procesar();
  };
  window.LumeaCelebrar.tiempos = TIEMPOS;
})();
