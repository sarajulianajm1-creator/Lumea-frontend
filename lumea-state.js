/**
 * LUMEA - Gestor de Estado y Conexión con Backend
 * Los datos se obtienen dinámicamente cuando el usuario se registra o inicia sesión.
 */

// URL del backend (admite 5001, 5000, localhost y ruta relativa)
const LUMEA_BACKEND_URLS = [
  'http://127.0.0.1:5001',
  'http://localhost:5001',
  'http://127.0.0.1:5000',
  'http://localhost:5000',
  '' // Ruta relativa si el frontend se sirve desde el backend
];

class LumeaStore {
  constructor() {
    this.storageKey = "LUMEA_USER_STATE_ACTIVE";
    this.state = null;
    this.cargando = true;
    this.inicializar();
  }

  // Obtiene el email del usuario registrado o logueado
  obtenerEmailUsuario() {
    const urlParams = new URLSearchParams(window.location.search);
    return (
      urlParams.get("email") ||
      localStorage.getItem("lumea_usuario_email") ||
      localStorage.getItem("email") ||
      ""
    );
  }

  // Obtiene el nombre del usuario guardado al registrarse
  obtenerNombreUsuario() {
    return (
      localStorage.getItem("lumea_usuario_nombre") ||
      localStorage.getItem("nombre") ||
      ""
    );
  }

  // Estado inicial limpio para nuevos usuarios (sin datos inventados, avatar vacío)
  crearEstadoVacio(email, nombre) {
    const nombreFinal = nombre || (email ? email.split("@")[0] : "Estudiante");
    return {
      usuario: {
        nombre: nombreFinal,
        correo: email || "",
        nivel: 1,
        xp_total: 0,
        xp_inicio_nivel: 0,
        xp_siguiente_nivel: 100,
        xp_faltante_siguiente_nivel: 100,
        racha_actual: 0,
        mejor_racha: 0,
        mensaje_regreso: null
      },
      animo_hoy: {
        estado: null,
        registrado: false,
        hora: "",
        historial_semana: [
          { dia: "L", nombre: "Lunes", estado: null, cara: "•" },
          { dia: "M", nombre: "Martes", estado: null, cara: "•" },
          { dia: "M", nombre: "Miércoles", estado: null, cara: "•" },
          { dia: "J", nombre: "Jueves", estado: null, cara: "•" },
          { dia: "V", nombre: "Viernes", estado: null, cara: "•" },
          { dia: "S", nombre: "Sábado", estado: null, cara: "•" },
          { dia: "D", nombre: "Domingo", estado: null, cara: "•", esHoy: true }
        ]
      },
      comidas_hoy: [],
      meta_comidas: 3,
      misiones: [
        {
          id: "mision-fruta",
          titulo: "Registra una fruta",
          recompensa: 20,
          cumplida: false,
          icono: "🍎",
          descripcion: "Tu dosis de vitaminas naturales del día."
        },
        {
          id: "mision-comidas",
          titulo: "Registra 3 comidas",
          recompensa: 30,
          progreso_actual: 0,
          progreso_total: 3,
          cumplida: false,
          icono: "🍽️",
          descripcion: "Mantén un registro consciente de tu plato."
        },
        {
          id: "mision-animo",
          titulo: "Haz tu check-in de ánimo",
          recompensa: 10,
          cumplida: false,
          icono: "✨",
          descripcion: "Tus emociones también nutren tu bienestar."
        }
      ],
      avatar: null, // Literalmente vacío: el usuario lo diseña e implementa por su cuenta
      comidas_semana: [
        { dia: "L", comidas: 0, tieneFruta: false },
        { dia: "M", comidas: 0, tieneFruta: false },
        { dia: "M", comidas: 0, tieneFruta: false },
        { dia: "J", comidas: 0, tieneFruta: false },
        { dia: "V", comidas: 0, tieneFruta: false },
        { dia: "S", comidas: 0, tieneFruta: false },
        { dia: "D", comidas: 0, tieneFruta: false, esHoy: true }
      ]
    };
  }

  // Detecta si la carga actual proviene de una recarga de página (F5 / botón recargar)
  esRecargaDePagina() {
    try {
      const navEntries = performance.getEntriesByType && performance.getEntriesByType('navigation');
      if (navEntries && navEntries.length > 0) {
        return navEntries[0].type === 'reload';
      }
      if (window.performance && window.performance.navigation) {
        return window.performance.navigation.type === 1;
      }
    } catch (e) {}
    return false;
  }

  // Carga inicial sincronizada con backend o persistencia temporal de navegación
  async inicializar() {
    const email = this.obtenerEmailUsuario();
    const nombre = this.obtenerNombreUsuario();

    // REGLA PARA USUARIOS NO REGISTRADOS:
    // Si aún no está registrada y recarga la página (F5) o abre una pestaña nueva,
    // vuelve a estar completamente sin nada (desde cero).
    // Solo se conserva temporalmente mientras navega entre pantallas (ej: ir a cámara).
    const esRecarga = this.esRecargaDePagina();
    const esNuevaSesion = !sessionStorage.getItem("lumea_sesion_activa");

    if (!email && (esRecarga || esNuevaSesion)) {
      try {
        localStorage.removeItem(this.storageKey);
        localStorage.removeItem("LUMEA_USER_STATE_ACTIVE");
        sessionStorage.removeItem(this.storageKey);
      } catch (e) {}
      sessionStorage.setItem("lumea_sesion_activa", "1");
      this.state = this.crearEstadoVacio("", "");
      this.cargando = false;
      this.guardar();
      this.notificarCambio();
      return;
    }

    sessionStorage.setItem("lumea_sesion_activa", "1");

    // 1. Intentamos leer la sesión guardada en este navegador (sessionStorage o localStorage)
    try {
      const cache = sessionStorage.getItem(this.storageKey) || localStorage.getItem(this.storageKey);
      if (cache) {
        const parsed = JSON.parse(cache);
        // Si hay un email activo pero el cache pertenece a otro correo, no usarlo
        if (email && parsed && parsed.usuario && parsed.usuario.correo && parsed.usuario.correo !== email) {
          this.state = null;
        } else {
          this.state = parsed;
        }
      }
    } catch (e) {
      console.warn("Error al leer cache local:", e);
    }

    // 2. Si no hay estado en cache, creamos el estado inicial limpio
    if (!this.state) {
      this.state = this.crearEstadoVacio(email, nombre);
      this.guardar();
    } else {
      // Normalización: si el usuario no tiene correo registrado, aseguramos nivel 1 inicial sin avatar
      if (!email && this.state.usuario) {
        if (this.state.usuario.nivel > 1 && !this.state.usuario.correo) {
          this.state.usuario.nivel = 1;
          this.state.usuario.xp_inicio_nivel = 0;
          this.state.usuario.xp_siguiente_nivel = 100;
          this.state.usuario.xp_total = Math.min(this.state.usuario.xp_total, 25);
          this.state.usuario.xp_faltante_siguiente_nivel = 100 - this.state.usuario.xp_total;
          this.guardar();
        }
      }
    }

    // 3. Si hay correo registrado, sincronizamos con el backend
    if (email) {
      await this.cargarDesdeBackend(email);
    } else {
      this.cargando = false;
      this.notificarCambio();
    }
  }

  // Petición real al backend según contrato GET /progreso y GET /estado-animo
  async cargarDesdeBackend(email) {
    let exito = false;

    for (const baseUrl of LUMEA_BACKEND_URLS) {
      try {
        const urlProgreso = `${baseUrl}/progreso?email=${encodeURIComponent(email)}`;
        const resProgreso = await fetch(urlProgreso);

        if (resProgreso.ok) {
          const json = await resProgreso.json();
          const datosProgreso = json.progreso || (json.nivel !== undefined ? json : (json.data || null));
          if (datosProgreso) {
            this.aplicarProgresoBackend(datosProgreso);
            window.LUMEA_BACKEND_ACTIVO = baseUrl;
            exito = true;
            break;
          }
        }
      } catch (err) {
        // Continúa con la siguiente URL si falla la conexión
      }
    }

    // Consultar estado de ánimo al backend
    const urlBaseParaAnimo = window.LUMEA_BACKEND_ACTIVO ? [window.LUMEA_BACKEND_ACTIVO, ...LUMEA_BACKEND_URLS] : LUMEA_BACKEND_URLS;
    for (const baseUrl of urlBaseParaAnimo) {
      try {
        const urlAnimo = `${baseUrl}/estado-animo?email=${encodeURIComponent(email)}`;
        const resAnimo = await fetch(urlAnimo);
        if (resAnimo.ok) {
          const jsonAnimo = await resAnimo.json();
          if (jsonAnimo.animo_hoy) {
            this.state.animo_hoy.estado = jsonAnimo.animo_hoy.estado || this.state.animo_hoy.estado;
            this.state.animo_hoy.registrado = true;
          }
          if (Array.isArray(jsonAnimo.historial_semana)) {
            this.state.animo_hoy.historial_semana = jsonAnimo.historial_semana;
          }
          break;
        }
      } catch (e) {}
    }

    this.cargando = false;
    this.guardar();
    this.notificarCambio();
    return exito;
  }

  // Mapea los datos del backend al estado de la aplicación
  aplicarProgresoBackend(p) {
    const u = this.state.usuario;
    u.nivel = typeof p.nivel === 'number' ? p.nivel : u.nivel;
    u.xp_total = typeof p.xp_total === 'number' ? p.xp_total : u.xp_total;
    u.xp_inicio_nivel = p.xp_inicio_nivel || 0;
    u.xp_siguiente_nivel = p.xp_siguiente_nivel || (u.nivel * 100);
    u.xp_faltante_siguiente_nivel = typeof p.xp_faltante_siguiente_nivel === 'number'
      ? p.xp_faltante_siguiente_nivel
      : (u.xp_siguiente_nivel - u.xp_total);
    u.racha_actual = typeof p.racha_actual === 'number' ? p.racha_actual : u.racha_actual;
    u.mejor_racha = typeof p.mejor_racha === 'number' ? p.mejor_racha : Math.max(u.mejor_racha, u.racha_actual);

    // Mensaje de regreso si el backend lo manda
    u.mensaje_regreso = p.mensaje_regreso || null;

    if (p.nombre) u.nombre = p.nombre;

    // Meta diaria
    if (p.meta_diaria) {
      this.state.meta_comidas = p.meta_diaria.meta || 3;
    }

    // Comidas registradas devueltas por el backend
    if (Array.isArray(p.comidas_hoy)) {
      this.state.comidas_hoy = p.comidas_hoy;
    }

    // Historial semanal de comidas devuelto por el backend
    if (Array.isArray(p.comidas_semana)) {
      this.state.comidas_semana = p.comidas_semana;
    }

    // Misiones del backend
    if (Array.isArray(p.misiones) && p.misiones.length > 0) {
      this.state.misiones = p.misiones;
    }

    // Avatar recibido desde el backend (si existe)
    if (p.avatar) {
      this.state.avatar = p.avatar;
    }
  }

  obtener() {
    return this.state;
  }

  guardar() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.state));
      sessionStorage.setItem(this.storageKey, JSON.stringify(this.state));
    } catch (e) {
      console.warn("No se pudo guardar en almacenamiento:", e);
    }
    this.notificarCambio();
  }

  notificarCambio() {
    window.dispatchEvent(new CustomEvent("lumea:state-changed", { detail: this.state }));
  }

  sumarXP(cantidad) {
    const u = this.state.usuario;
    u.xp_total += cantidad;
    if (u.xp_total >= u.xp_siguiente_nivel) {
      u.nivel += 1;
      u.xp_inicio_nivel = u.xp_siguiente_nivel;
      u.xp_siguiente_nivel += 100;
      u.xp_faltante_siguiente_nivel = u.xp_siguiente_nivel - u.xp_total;
      this.mostrarNotificacion(`🎉 ¡Subiste al Nivel ${u.nivel}!`);
    } else {
      u.xp_faltante_siguiente_nivel = u.xp_siguiente_nivel - u.xp_total;
    }
    this.guardar();
    return u;
  }

  registrarAnimo(estado) {
    // REGLA: El estudiante solo puede registrar su estado de ánimo una vez al día
    if (this.state.animo_hoy && this.state.animo_hoy.registrado) {
      this.mostrarNotificacion("Ya completaste tu check-in de ánimo por hoy. Solo se puede registrar una vez al día.");
      return false;
    }

    this.state.animo_hoy.estado = estado;
    this.state.animo_hoy.registrado = true;
    this.state.animo_hoy.hora = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    if (this.state.avatar) {
      this.state.avatar.expresion = estado;
    }

    const caritas = { muy_mal: "😢", mal: "🙁", neutral: "😐", bien: "🙂", muy_bien: "😄" };
    const hoy = this.state.animo_hoy.historial_semana.find(d => d.esHoy);
    if (hoy) {
      hoy.estado = estado;
      hoy.cara = caritas[estado] || "🙂";
    }

    const misionAnimo = this.state.misiones.find(m => m.id === "mision-animo");
    if (misionAnimo && !misionAnimo.cumplida) {
      misionAnimo.cumplida = true;
      this.sumarXP(misionAnimo.recompensa);
    } else {
      this.sumarXP(5);
    }

    // Sincronizar con backend si hay correo registrado
    const email = this.obtenerEmailUsuario();
    if (email) {
      const baseUrls = [
        window.LUMEA_BACKEND_ACTIVO || 'http://127.0.0.1:5001',
        'http://127.0.0.1:5001',
        'http://localhost:5001',
        'http://127.0.0.1:5000',
        ''
      ];
      for (const base of baseUrls) {
        fetch(`${base}/estado-animo`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email, estado: estado })
        }).then(r => r.ok ? r.json() : null)
          .then(res => {
            if (res && res.progreso) this.aplicarProgresoBackend(res.progreso);
          }).catch(() => {});
        break;
      }
    }

    this.guardar();
    this.notificarCambio();
    return true;
  }

  registrarComida(alimento) {
    const nuevaComida = {
      id: Date.now(),
      nombre: alimento.nombre || "Alimento",
      tipo: alimento.tipo || "Comida",
      hora: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      calorias: alimento.calorias || 100,
      esFruta: alimento.esFruta || false,
      icono: alimento.icono || (alimento.esFruta ? "🍎" : "🍽️")
    };

    this.state.comidas_hoy.push(nuevaComida);
    this.sumarXP(10);

    if (alimento.esFruta) {
      const mFruta = this.state.misiones.find(m => m.id === "mision-fruta");
      if (mFruta && !mFruta.cumplida) {
        mFruta.cumplida = true;
        this.sumarXP(mFruta.recompensa);
      }
    }

    const mComidas = this.state.misiones.find(m => m.id === "mision-comidas");
    if (mComidas) {
      mComidas.progreso_actual = this.state.comidas_hoy.length;
      if (mComidas.progreso_actual >= (mComidas.progreso_total || 3) && !mComidas.cumplida) {
        mComidas.cumplida = true;
        this.sumarXP(mComidas.recompensa);
      }
    }

    if (this.state.usuario.racha_actual === 0) {
      this.state.usuario.racha_actual = 1;
    }

    this.guardar();
    return nuevaComida;
  }

  equiparPrenda(itemId, tipo) {
    if (tipo === "ropa") {
      this.state.avatar.ropa = itemId;
    } else if (tipo === "accesorio") {
      this.state.avatar.accesorio = this.state.avatar.accesorio === itemId ? null : itemId;
    }
    this.guardar();
  }

  mostrarNotificacion(texto) {
    let container = document.getElementById("lumea-toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "lumea-toast-container";
      container.style.position = "fixed";
      container.style.bottom = "90px";
      container.style.right = "20px";
      container.style.zIndex = "9999";
      container.style.display = "flex";
      container.style.flexDirection = "column";
      container.style.gap = "10px";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = "lumea-toast-item";
    toast.innerHTML = `
      <div style="background: #1b4332; color: #fff; padding: 12px 18px; border-radius: 14px; box-shadow: 0 10px 25px rgba(0,0,0,0.25); font-weight: 600; font-size: 0.9rem; display: flex; align-items: center; gap: 10px; border: 1px solid #74c69d;">
        <span>✨</span>
        <span>${texto}</span>
      </div>
    `;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(10px)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }
}

window.lumeaStore = new LumeaStore();
