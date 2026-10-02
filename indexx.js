async function cargarDashboard(emailUsuario) {
try {
    // 1. Petición al endpoint de progreso según el contrato
    const response = await fetch(`/progreso?email=${encodeURIComponent(emailUsuario)}`);
    
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
    document.getElementById('user-nivel').textContent = `Nivel ${p.nivel}`;
    document.getElementById('xp-bar').style.width = `${porcentajeXP}%`;
    document.getElementById('xp-text').textContent = textoFaltante;
    
      // Racha (si es 0, muestra un mensaje motivador sin reproches)
    const textoRacha = p.racha_actual > 0 
        ? `${p.racha_actual} días de racha` 
        : "Registra algo hoy para empezar una racha";
    document.getElementById('user-racha').textContent = textoRacha;

      // Meta del día
    const metaCumplida = p.meta_diaria.cumplida;
    document.getElementById('meta-texto').textContent = `${p.meta_diaria.xp_hoy} de ${p.meta_diaria.meta} XP hoy`;
    if (metaCumplida) {
        document.getElementById('meta-mensaje').textContent = "¡Meta cumplida por hoy! 🎉";
    }

      // Aviso de regreso (si no es null, se muestra una sola vez amablemente)
    if (p.mensaje_regreso) {
        const alertaRegreso = document.getElementById('aviso-regreso');
        alertaRegreso.textContent = p.mensaje_regreso;
        alertaRegreso.style.display = 'block'; // O usa clases de Bootstrap como 'alert alert-success'
    }

      // Avatar (Usa DiceBear con el ánimo de hoy si Figma no está listo)
    if (p.avatar && p.avatar.url_con_animo) {
        document.getElementById('user-avatar-img').src = p.avatar.url_con_animo;
    }
    }

} catch (error) {
    console.error("Error de conexión:", error);
    // Mostrar mensaje de sin conexión
}
}