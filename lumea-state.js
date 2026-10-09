/**
 * LUMEA · lumea-state.js — el estado de la persona, compartido por Inicio, Progreso y Ánimo.
 *
 * Diseño de Sara: un solo objeto (window.lumeaStore) que cada pantalla lee, y el evento
 * "lumea:state-changed" cuando algo cambia. Lo que cambió al unirse con la gamificación:
 *   - Una sola conexión: todo va por api.js (el puerto lo fija api.js). Aquí no hay direcciones ni llamadas a mano.
 *   - Una sola sesión: la de api.js (obtenerSesion). El correo ya no se lee de la dirección de la página.
 *   - El XP, la racha, las misiones y el nivel los calcula el BACKEND; aquí no se inventa nada.
 *     Se leen de GET /progreso, GET /historial (con es_fruta) y GET /estado-animo?dias=7.
 *   - Texto que llega del servidor: siempre textContent, nunca HTML armado a mano.
 *
 * Necesita api.js y formato.js antes. Si algo opcional falla (historial, ánimo, perfil),
 * la pantalla sigue con lo que sí llegó; solo si falla /progreso se avisa el error.
 */
(function () {
  "use strict";

  const F = window.LumeaFormato;
  const COMIDAS_PARA_MISION = 3;     // «Registra 3 comidas» (el backend no publica este número)

  // Lo que dice cada misión (los nombres y el XP llegan del backend; esto es solo el apoyo)
  const DESCRIPCION_MISION = {
    fruta: "Tu dosis de vitaminas naturales del día.",
    tres_comidas: "Mantén un registro consciente de tu plato.",
    check_in_animo: "Tus emociones también nutren tu bienestar.",
  };

  class LumeaStore {
    constructor() {
      this.state = this.crearEstadoVacio();
      this.cargando = true;
      this.error = false;
      this.oyentes = [];
      this.inicializar();
    }

    // El correo de la sesión de api.js (también lee la clave vieja de Sara: ver api.js)
    obtenerEmailUsuario() {
      return (typeof obtenerSesion === "function" && obtenerSesion()) || "";
    }

    obtenerNombreUsuario() {
      return this.state.usuario.nombre;
    }

    // Antes de que llegue algo del servidor: sin cifras inventadas
    crearEstadoVacio() {
      return {
        cargado: false,
        usuario: { nombre: "", correo: "", nivel: null, xp_total: 0, xp_inicio_nivel: 0, xp_siguiente_nivel: null,
                   xp_faltante_siguiente_nivel: null, racha_actual: 0, mejor_racha: 0, mensaje_regreso: null },
        meta_diaria: null,
        meta_comidas: COMIDAS_PARA_MISION,
        comidas_hoy: [],
        comidas_semana: null,        // null = el historial no llegó (la pantalla omite esa parte)
        misiones: [],
        avatar: null,
        calcomanias: null,
        animo_hoy: { estado: null, registrado: false, historial_semana: null },
        ultimos_dias: null,          // los últimos 7 días (hoy al final) para la franja de Inicio; null = no llegó ni el historial ni el ánimo
      };
    }

    async inicializar() {
      const email = this.obtenerEmailUsuario();
      if (!email) {                      // las pantallas privadas piden iniciar sesión
        this.cargando = false;
        window.location.href = "iniciar-sesion.html";
        return;
      }
      await this.cargarDesdeBackend(email);
    }

    // GET /progreso es lo esencial; perfil, historial y ánimo son extras que no tumban la pantalla.
    async cargarDesdeBackend(email) {
      this.cargando = true;
      this.error = false;
      this.notificarCambio();
      const [progreso, perfil, historial, animo] = await Promise.allSettled([
        obtenerProgreso(email),
        buscarPerfilPorCorreo(email),
        obtenerHistorial(email),
        obtenerEstadosAnimo(email, 7),
      ]);
      const bien = (r) => (r.status === "fulfilled" && r.value.ok ? r.value.cuerpo : null);
      const cuerpoProgreso = bien(progreso);
      if (!cuerpoProgreso || !cuerpoProgreso.progreso) {
        this.cargando = false;
        this.error = true;
        this.notificarCambio();
        return false;
      }
      const cuerpoPerfil = bien(perfil);
      const cuerpoHistorial = bien(historial);
      const cuerpoAnimo = bien(animo);
      this.aplicar(cuerpoProgreso.progreso, {
        nombre: cuerpoPerfil && cuerpoPerfil.perfil ? cuerpoPerfil.perfil.nombre : null,
        correo: email,
        historial: cuerpoHistorial && Array.isArray(cuerpoHistorial.historial) ? cuerpoHistorial.historial : null,
        animo: cuerpoAnimo && Array.isArray(cuerpoAnimo.historial) ? cuerpoAnimo.historial : null,
      });
      this.cargando = false;
      this.notificarCambio();
      return true;
    }

    // Pasa lo que mandó el backend a la forma de estado que leen las pantallas
    aplicar(p, extra) {
      const hoy = new Date();
      const semana = F.semanaDe(hoy);
      const hoyClave = F.claveDeHoy(hoy);
      const s = this.state;
      s.cargado = true;
      s.progreso = p;
      s.usuario = {
        nombre: extra.nombre || s.usuario.nombre || "",
        correo: extra.correo,
        nivel: p.nivel,
        xp_total: p.xp_total,
        xp_inicio_nivel: p.xp_inicio_nivel,
        xp_siguiente_nivel: p.xp_siguiente_nivel,                       // null en el último nivel
        xp_faltante_siguiente_nivel: p.xp_faltante_siguiente_nivel,
        racha_actual: p.racha_actual,
        mejor_racha: p.racha_maxima,
        mensaje_regreso: p.mensaje_regreso || null,
      };
      s.meta_diaria = p.meta_diaria || null;
      s.avatar = p.avatar || null;
      s.calcomanias = p.calcomanias || null;

      s.misiones = (p.misiones || []).map((m) => ({
        id: m.id,
        titulo: m.nombre,
        recompensa: m.xp,
        cumplida: !!m.cumplida,
        descripcion: DESCRIPCION_MISION[m.id] || "",
      }));

      if (extra.historial) {
        const dias = F.comidasPorDia(extra.historial, semana);
        s.comidas_semana = dias.map((d) => ({
          dia: F.DIAS_CORTO[d.indice], nombre: F.DIAS_LARGO[d.indice], clave: d.clave,
          comidas: d.comidas, tieneFruta: d.fruta, esHoy: d.clave === hoyClave, futuro: d.clave > hoyClave,
        }));
        s.comidas_hoy = extra.historial.filter((r) => F.claveDeFechaDelServidor(r.fecha) === hoyClave);
      } else {
        s.comidas_semana = null;
        s.comidas_hoy = [];
      }

      const dias = extra.animo ? F.animoPorDia(extra.animo, semana) : null;
      const deHoy = dias ? (dias.find((d) => d.clave === hoyClave) || {}).estado : null;
      const estadoHoy = (p.avatar && p.avatar.estado_animo_hoy) || deHoy || null;
      // La franja «Tu semana» de Inicio: los últimos 7 días, con hoy a la derecha (comidas del historial y último ánimo de cada día)
      const ultimos = F.ultimosDias(hoy);
      const comidas = extra.historial ? F.comidasPorDia(extra.historial, ultimos) : null;
      const animos = extra.animo ? F.animoPorDia(extra.animo, ultimos) : null;
      s.ultimos_dias = comidas || animos ? ultimos.map((d, i) => ({
        dia: F.DIAS_CORTO[d.indice], nombre: F.DIAS_LARGO[d.indice], numero: d.numero, clave: d.clave,
        comidas: comidas ? comidas[i].comidas : null, estado: animos ? animos[i].estado : null, esHoy: d.clave === hoyClave,
      })) : null;

      s.animo_hoy = {
        estado: estadoHoy,
        registrado: !!estadoHoy,
        historial_semana: dias && dias.map((d) => ({
          dia: F.DIAS_CORTO[d.indice], nombre: F.DIAS_LARGO[d.indice], estado: d.estado,
          esHoy: d.clave === hoyClave, futuro: d.clave > hoyClave,
        })),
      };
    }

    obtener() {
      return this.state;
    }

    // Quien quiere enterarse de los cambios: devuelve la función para dejar de escuchar
    suscribir(funcion) {
      this.oyentes.push(funcion);
      return () => { this.oyentes = this.oyentes.filter((f) => f !== funcion); };
    }

    notificarCambio() {
      this.oyentes.forEach((f) => { try { f(this.state); } catch (e) { console.error(e); } });
      window.dispatchEvent(new CustomEvent("lumea:state-changed", { detail: this.state }));
    }

    // POST /estado-animo. El check-in cuenta una vez al día (regla de Sara). El XP lo da el
    // backend; aquí solo se celebra con la misma respuesta y se vuelve a leer el estado.
    async registrarAnimo(estado) {
      if (this.state.animo_hoy.registrado) {
        this.mostrarNotificacion("Ya hiciste tu check-in de ánimo de hoy. Se registra una vez al día.");
        return false;
      }
      const email = this.obtenerEmailUsuario();
      if (!email) return false;
      try {
        const { ok, cuerpo } = await registrarEstadoAnimo(email, estado);
        if (!ok || cuerpo.error) throw new Error(cuerpo.error || "el servidor respondió con error");
        if (window.LumeaCelebrar && cuerpo.gamificacion) window.LumeaCelebrar(cuerpo.gamificacion);
        await this.cargarDesdeBackend(email);
        return cuerpo;
      } catch (e) {
        this.mostrarNotificacion("No se pudo guardar tu ánimo. Intenta otra vez.");
        return false;
      }
    }

    // Aviso corto y amable. Vive en una región aria-live para que el lector de pantalla lo lea.
    mostrarNotificacion(texto) {
      let contenedor = document.getElementById("lumea-toast-container");
      if (!contenedor) {
        contenedor = document.createElement("div");
        contenedor.id = "lumea-toast-container";
        contenedor.className = "lumea-toast-container";
        contenedor.setAttribute("role", "status");
        contenedor.setAttribute("aria-live", "polite");
        document.body.appendChild(contenedor);
      }
      const aviso = document.createElement("div");
      aviso.className = "lumea-toast-item";
      aviso.textContent = texto;
      contenedor.appendChild(aviso);
      setTimeout(() => aviso.remove(), 3200);
    }
  }

  window.lumeaStore = new LumeaStore();
})();
