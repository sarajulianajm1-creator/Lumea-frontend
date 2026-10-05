/**
 * LUMEA - Integración con Backend /progreso y Sincronización Local
 */
async function cargarDashboard(emailUsuario) {
  const email = emailUsuario || (window.lumeaStore ? window.lumeaStore.obtenerEmailUsuario() : localStorage.getItem('lumea_usuario_email') || '');
  if (!email) return;
  try {
    // 1. Petición al endpoint de progreso según el contrato
    const response = await fetch(`/progreso?email=${encodeURIComponent(email)}`);

    if (!response.ok) {
      if (response.status === 404) {
        console.warn("No existe un perfil remoto con ese correo. Usando estado local de demostración.");
        if (window.sincronizarLumeaUI) window.sincronizarLumeaUI();
        return;
      }
      throw new Error("Error al obtener el progreso del servidor");
    }

    const cuerpo = await response.json();

    if (cuerpo.success && cuerpo.progreso) {
      const p = cuerpo.progreso;

      // Cálculo de porcentaje de XP
      const porcentajeXP = p.xp_siguiente_nivel === null ? 100
        : Math.max(0, p.xp_total - p.xp_inicio_nivel) / (p.xp_siguiente_nivel - p.xp_inicio_nivel) * 100;

      const textoFaltante = p.xp_siguiente_nivel === null
        ? "¡Nivel máximo alcanzado!"
        : `Te faltan ${p.xp_faltante_siguiente_nivel} XP para el nivel ${p.nivel + 1}`;

      // Actualizar elementos si existen
      const elNivel = document.getElementById('user-nivel');
      if (elNivel) elNivel.textContent = `Nivel ${p.nivel}`;

      const elBar = document.getElementById('xp-bar');
      if (elBar) elBar.style.width = `${porcentajeXP}%`;

      const elText = document.getElementById('xp-text');
      if (elText) elText.textContent = textoFaltante;

      const textoRacha = p.racha_actual > 0
        ? `${p.racha_actual} días de racha`
        : "Registra algo hoy para empezar una racha";
      const elRacha = document.getElementById('user-racha');
      if (elRacha) elRacha.textContent = textoRacha;

      if (p.meta_diaria) {
        const elMeta = document.getElementById('meta-texto');
        if (elMeta) elMeta.textContent = `${p.meta_diaria.xp_hoy} de ${p.meta_diaria.meta} XP hoy`;
      }

      if (p.mensaje_regreso) {
        const alertaRegreso = document.getElementById('aviso-regreso');
        if (alertaRegreso) {
          alertaRegreso.textContent = p.mensaje_regreso;
          alertaRegreso.style.display = 'flex';
        }
      }

      if (p.avatar && p.avatar.url_con_animo) {
        const elAvatarImg = document.getElementById('user-avatar-img');
        if (elAvatarImg) elAvatarImg.src = p.avatar.url_con_animo;
      }

      // Sincronizar con el store local
      if (window.lumeaStore) {
        const local = window.lumeaStore.obtener();
        local.usuario.nivel = p.nivel;
        local.usuario.xp_total = p.xp_total;
        local.usuario.racha_actual = p.racha_actual;
        window.lumeaStore.guardar(local);
      }
    }

  } catch (error) {
    // Si no hay backend encendido, usar datos del cliente sin romper la interfaz
    console.info("LUMEA: Modo offline/prototipo activo.");
    if (window.sincronizarLumeaUI) {
      window.sincronizarLumeaUI();
    }
  }
}