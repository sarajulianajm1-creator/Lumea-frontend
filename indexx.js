// indexx.js — llena la pantalla de inicio del estudiante (index-ingresado.html)
// con GET /progreso (ver Backend/docs/CONTRATO_GAMIFICACION.md). Necesita api.js antes.

// Escribe un texto en un elemento SOLO si existe: si el diseño cambia y un id
// desaparece, la pantalla sigue funcionando en vez de romperse.
function poner(id, texto) {
  const el = document.getElementById(id);
  if (el) el.textContent = texto;
}

async function cargarDashboard(emailUsuario) {
try {
    // 1. Petición al endpoint de progreso según el contrato
    const response = await fetch(`${API_BASE_URL}/progreso?email=${encodeURIComponent(emailUsuario)}`);
    
    // Control de errores (ej. 404 o sin perfil)
    if (!response.ok) {
    if (response.status === 404) {
        console.error("No existe un perfil con ese correo. Vuelve a iniciar sesión.");
        // Redirigir al login o mostrar alerta
        return;
    }
    throw new Error("Error al obtener el progreso del servidor");
    }

    const cuerpo = await response.json();
    
    if (cuerpo.success && cuerpo.progreso) {
    const p = cuerpo.progreso;

      // 2. Cálculo de la barra de XP (evita que baje de 0 y maneja el último nivel)
    const porcentajeXP = p.xp_siguiente_nivel === null ? 100 
        : Math.max(0, p.xp_total - p.xp_inicio_nivel) / (p.xp_siguiente_nivel - p.xp_inicio_nivel) * 100;

      // Texto para el siguiente nivel
    const textoFaltante = p.xp_siguiente_nivel === null 
        ? "¡Nivel máximo alcanzado!" 
        : `Te faltan ${p.xp_faltante_siguiente_nivel} XP para el nivel ${p.nivel + 1}`;

      // 3. Actualizar elementos en tu HTML (asegúrate de tener estos IDs en tu vista)
    poner('user-nivel', `Nivel ${p.nivel}`);
    const barra = document.getElementById('xp-bar');
    if (barra) barra.style.width = `${porcentajeXP}%`;
    poner('xp-text', textoFaltante);
    
      // Racha (si es 0, muestra un mensaje motivador sin reproches)
    const textoRacha = p.racha_actual > 0 
        ? `${p.racha_actual} ${p.racha_actual === 1 ? "día" : "días"} de racha` 
        : "Registra algo hoy para empezar una racha";
    poner('user-racha', textoRacha);

      // Meta del día
    const metaCumplida = p.meta_diaria.cumplida;
    // Si ya pasó la meta no se dice «20 de 15 XP hoy»: se dice que se cumplió.
    poner('meta-texto', metaCumplida
      ? `Meta cumplida: ${p.meta_diaria.xp_hoy} XP hoy`
      : `${p.meta_diaria.xp_hoy} de ${p.meta_diaria.meta} XP hoy`);
    if (metaCumplida) {
        poner('meta-mensaje', "¡Meta cumplida por hoy! 🎉");
    }

      // Aviso de regreso (si no es null, se muestra una sola vez amablemente)
    if (p.mensaje_regreso) {
        const alertaRegreso = document.getElementById('aviso-regreso');
        if (alertaRegreso) { alertaRegreso.textContent = p.mensaje_regreso; alertaRegreso.style.display = 'block'; } // O usa clases de Bootstrap como 'alert alert-success'
    }

      // Avatar (Usa DiceBear con el ánimo de hoy si Figma no está listo)
    if (p.avatar && p.avatar.url_con_animo) {
        const img = document.getElementById('user-avatar-img');
        if (img) img.src = p.avatar.url_con_animo;
    }
    }

} catch (error) {
    console.error("Error de conexión:", error);
    // Mostrar mensaje de sin conexión
}
}

// Arranque: sin sesión -> a iniciar sesión; con sesión -> nombre + progreso.
document.addEventListener("DOMContentLoaded", async () => {
  const email = obtenerSesion();
  if (!email) {
    window.location.href = "iniciar-sesion.html";
    return;
  }
  try {
    const { ok, cuerpo } = await buscarPerfilPorCorreo(email);
    if (ok && cuerpo.perfil) poner("user-name", cuerpo.perfil.nombre);
  } catch (e) {
    poner("user-name", "Sin conexión con el servidor");
  }
  cargarDashboard(email);
});
