/**
 * LUMEA UI Helper
 * Renderizador de Avatar por Capas, Fecha Dinámica y Enlace de Datos del Backend
 */

// Formatear la fecha actual de forma dinámica en español
function actualizarFechaActual() {
  const ahora = new Date();
  const opcionesFecha = { weekday: 'long', day: 'numeric', month: 'long' };
  let fechaFormateada = ahora.toLocaleDateString('es-ES', opcionesFecha);
  // Capitalizar la primera letra
  fechaFormateada = fechaFormateada.charAt(0).toUpperCase() + fechaFormateada.slice(1);

  const horaFormateada = ahora.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const badgesFecha = document.querySelectorAll(".lumea-bind-fecha");
  badgesFecha.forEach(el => {
    el.innerHTML = `<i class="bi bi-calendar-event me-1"></i> ${fechaFormateada}`;
  });

  const elemsHora = document.querySelectorAll(".lumea-bind-hora");
  elemsHora.forEach(el => {
    el.textContent = `• ${horaFormateada}`;
  });
}

// Generador de SVG Avatar por capas (Base, Expresión de Ánimo, Ropa, Accesorio)
function renderizarAvatarSVG(opciones = {}) {
  const estado = window.lumeaStore ? window.lumeaStore.obtener() : null;
  const config = {
    expresion: opciones.expresion || (estado && estado.animo_hoy ? estado.animo_hoy.estado : "bien"),
    ropa: opciones.ropa || (estado && estado.avatar ? estado.avatar.ropa : "camiseta-verde"),
    accesorio: opciones.accesorio !== undefined ? opciones.accesorio : (estado && estado.avatar ? estado.avatar.accesorio : "gafas-sol"),
    piel: opciones.piel || "#fdd8b5",
    cabello: opciones.cabello || "#2d3748",
    size: opciones.size || 180
  };

  // Expresiones faciales según estado de ánimo
  let ojosBocaSVG = "";
  switch (config.expresion) {
    case "muy_mal":
      ojosBocaSVG = `
        <path d="M 68 85 Q 80 92 88 88" stroke="#1b281f" stroke-width="3" stroke-linecap="round" fill="none" />
        <path d="M 132 85 Q 120 92 112 88" stroke="#1b281f" stroke-width="3" stroke-linecap="round" fill="none" />
        <circle cx="78" cy="98" r="4.5" fill="#1b281f" />
        <circle cx="122" cy="98" r="4.5" fill="#1b281f" />
        <path d="M 126 104 C 126 108 123 111 123 111 C 123 111 120 108 120 104 C 120 102 121 100 123 100 C 125 100 126 102 126 104 Z" fill="#64b5f6" />
        <path d="M 88 126 Q 100 114 112 126" stroke="#1b281f" stroke-width="3.5" stroke-linecap="round" fill="none" />
      `;
      break;
    case "mal":
      ojosBocaSVG = `
        <path d="M 70 88 Q 80 92 88 89" stroke="#1b281f" stroke-width="2.5" stroke-linecap="round" fill="none" />
        <path d="M 130 88 Q 120 92 112 89" stroke="#1b281f" stroke-width="2.5" stroke-linecap="round" fill="none" />
        <circle cx="78" cy="98" r="4.5" fill="#1b281f" />
        <circle cx="122" cy="98" r="4.5" fill="#1b281f" />
        <path d="M 90 123 Q 100 117 110 123" stroke="#1b281f" stroke-width="3" stroke-linecap="round" fill="none" />
      `;
      break;
    case "neutral":
      ojosBocaSVG = `
        <path d="M 70 88 L 88 88" stroke="#1b281f" stroke-width="2.5" stroke-linecap="round" fill="none" />
        <path d="M 112 88 L 130 88" stroke="#1b281f" stroke-width="2.5" stroke-linecap="round" fill="none" />
        <circle cx="78" cy="98" r="4.5" fill="#1b281f" />
        <circle cx="122" cy="98" r="4.5" fill="#1b281f" />
        <line x1="92" y1="120" x2="108" y2="120" stroke="#1b281f" stroke-width="3" stroke-linecap="round" />
      `;
      break;
    case "muy_bien":
      ojosBocaSVG = `
        <path d="M 70 84 Q 80 80 88 85" stroke="#1b281f" stroke-width="2.5" stroke-linecap="round" fill="none" />
        <path d="M 130 84 Q 120 80 112 85" stroke="#1b281f" stroke-width="2.5" stroke-linecap="round" fill="none" />
        <path d="M 72 98 Q 78 88 84 98" stroke="#1b281f" stroke-width="3.5" stroke-linecap="round" fill="none" />
        <path d="M 116 98 Q 122 88 128 98" stroke="#1b281f" stroke-width="3.5" stroke-linecap="round" fill="none" />
        <circle cx="68" cy="106" r="7" fill="#f4a261" opacity="0.35" />
        <circle cx="132" cy="106" r="7" fill="#f4a261" opacity="0.35" />
        <path d="M 85 116 Q 100 134 115 116 Z" fill="#ffffff" stroke="#1b281f" stroke-width="3" stroke-linejoin="round" />
      `;
      break;
    case "bien":
    default:
      ojosBocaSVG = `
        <path d="M 70 86 Q 80 82 88 86" stroke="#1b281f" stroke-width="2.5" stroke-linecap="round" fill="none" />
        <path d="M 130 86 Q 120 82 112 86" stroke="#1b281f" stroke-width="2.5" stroke-linecap="round" fill="none" />
        <circle cx="78" cy="98" r="4.5" fill="#1b281f" />
        <circle cx="122" cy="98" r="4.5" fill="#1b281f" />
        <circle cx="68" cy="106" r="6" fill="#f4a261" opacity="0.25" />
        <circle cx="132" cy="106" r="6" fill="#f4a261" opacity="0.25" />
        <path d="M 88 118 Q 100 128 112 118" stroke="#1b281f" stroke-width="3.5" stroke-linecap="round" fill="none" />
      `;
      break;
  }

  // Ropa
  let ropaSVG = "";
  if (config.ropa === "sueter-menta") {
    ropaSVG = `
      <path d="M 64 148 Q 100 142 136 148 L 152 210 L 48 210 Z" fill="#a8dadc" />
      <path d="M 82 146 Q 100 156 118 146" stroke="#457b9d" stroke-width="4" fill="none" stroke-linecap="round" />
      <path d="M 100 160 L 100 205" stroke="#ffffff" stroke-dasharray="3,3" stroke-width="2" />
    `;
  } else if (config.ropa === "chaqueta-dorada") {
    ropaSVG = `
      <path d="M 64 148 Q 100 142 136 148 L 152 210 L 48 210 Z" fill="#e9c46a" />
      <path d="M 90 148 L 100 210 L 110 148" fill="#2a9d8f" />
      <circle cx="100" cy="175" r="3" fill="#ffffff" />
      <circle cx="100" cy="192" r="3" fill="#ffffff" />
    `;
  } else if (config.ropa === "buzo-terracota") {
    ropaSVG = `
      <path d="M 64 148 Q 100 142 136 148 L 152 210 L 48 210 Z" fill="#e76f51" />
      <path d="M 75 148 Q 100 162 125 148" fill="#264653" />
    `;
  } else {
    ropaSVG = `
      <path d="M 64 148 Q 100 142 136 148 L 152 210 L 48 210 Z" fill="#1e5e3a" />
      <path d="M 84 146 Q 100 158 116 146" stroke="#74c69d" stroke-width="3.5" fill="none" stroke-linecap="round" />
      <path d="M 100 172 Q 106 166 108 174 Q 100 180 100 172 Z" fill="#74c69d" />
    `;
  }

  // Accesorio
  let accesorioSVG = "";
  if (config.accesorio === "gafas-sol") {
    accesorioSVG = `
      <rect x="68" y="90" width="22" height="15" rx="4" fill="#1b281f" />
      <rect x="110" y="90" width="22" height="15" rx="4" fill="#1b281f" />
      <line x1="90" y1="96" x2="110" y2="96" stroke="#1b281f" stroke-width="3" />
      <line x1="72" y1="93" x2="78" y2="97" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" />
      <line x1="114" y1="93" x2="120" y2="97" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" />
    `;
  } else if (config.accesorio === "auriculares") {
    accesorioSVG = `
      <path d="M 52 100 A 50 50 0 0 1 148 100" fill="none" stroke="#2d6a4f" stroke-width="6" stroke-linecap="round" />
      <rect x="44" y="92" width="12" height="26" rx="6" fill="#1e5e3a" />
      <rect x="144" y="92" width="12" height="26" rx="6" fill="#1e5e3a" />
    `;
  } else if (config.accesorio === "gorra-botanica") {
    accesorioSVG = `
      <path d="M 64 68 Q 100 48 136 68 Q 142 80 60 80 Z" fill="#2d6a4f" />
      <path d="M 130 76 Q 160 80 156 86 Q 130 84 124 78 Z" fill="#1e5e3a" />
    `;
  } else if (config.accesorio === "bufanda-otono") {
    accesorioSVG = `
      <path d="M 75 138 Q 100 154 125 138 Q 120 158 80 158 Z" fill="#e76f51" />
      <rect x="112" y="148" width="16" height="34" rx="4" fill="#e76f51" />
    `;
  }

  return `
    <svg width="${config.size}" height="${config.size * 1.12}" viewBox="0 0 200 224" fill="none" xmlns="http://www.w3.org/2000/svg" class="lumea-avatar-svg">
      <defs>
        <radialGradient id="glowBack" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#d8f3dc" stop-opacity="0.8" />
          <stop offset="100%" stop-color="#ffffff" stop-opacity="0" />
        </radialGradient>
      </defs>
      <circle cx="100" cy="100" r="82" fill="url(#glowBack)" />
      <circle cx="100" cy="85" r="48" fill="${config.cabello}" />
      <rect x="91" y="125" width="18" height="25" fill="${config.piel}" rx="4" />
      <circle cx="100" cy="100" r="42" fill="${config.piel}" />
      <path d="M 62 88 Q 80 58 100 60 Q 126 56 138 88 Q 125 70 100 70 Q 75 70 62 88 Z" fill="${config.cabello}" />
      ${ojosBocaSVG}
      ${ropaSVG}
      ${accesorioSVG}
    </svg>
  `;
}

// Sincronizar todos los elementos con los datos dinámicos recibidos del backend
function sincronizarLumeaUI() {
  actualizarFechaActual();
  if (!window.lumeaStore) return;
  const s = window.lumeaStore.obtener();
  if (!s || !s.usuario) return;

  const u = s.usuario;

  // 1. Nombre de usuario
  const nombreFinal = u.nombre || "Estudiante";
  document.querySelectorAll(".lumea-bind-nombre").forEach(el => {
    el.textContent = nombreFinal;
  });

  // 2. Nivel
  document.querySelectorAll(".lumea-bind-nivel").forEach(el => {
    el.textContent = `Nivel ${u.nivel || 1}`;
  });

  // 3. Barra y Texto de XP
  const xpTotal = u.xp_total || 0;
  const xpInicio = u.xp_inicio_nivel || 0;
  const xpFin = u.xp_siguiente_nivel || 100;
  const rango = Math.max(1, xpFin - xpInicio);
  const porcXP = Math.min(100, Math.max(0, ((xpTotal - xpInicio) / rango) * 100));

  document.querySelectorAll(".lumea-bind-xp-bar").forEach(bar => {
    bar.style.width = `${porcXP}%`;
  });

  const faltante = u.xp_faltante_siguiente_nivel !== undefined
    ? u.xp_faltante_siguiente_nivel
    : Math.max(0, xpFin - xpTotal);

  document.querySelectorAll(".lumea-bind-xp-text").forEach(el => {
    el.textContent = `Te faltan ${faltante} XP para el nivel ${(u.nivel || 1) + 1}`;
  });

  document.querySelectorAll(".lumea-bind-xp-valor").forEach(el => {
    el.textContent = `${xpTotal}/${xpFin} XP`;
  });

  // 4. Rachas
  document.querySelectorAll(".lumea-bind-racha").forEach(el => {
    el.textContent = `${u.racha_actual || 0} días`;
  });

  document.querySelectorAll(".lumea-bind-mejor-racha").forEach(el => {
    el.textContent = `${u.mejor_racha || u.racha_actual || 0} días`;
  });

  // 5. Canasta: Comidas de hoy
  const cantComidas = Array.isArray(s.comidas_hoy) ? s.comidas_hoy.length : 0;
  const metaComidas = s.meta_comidas || 3;
  document.querySelectorAll(".lumea-bind-comidas-count").forEach(el => {
    el.textContent = `${cantComidas} de ${metaComidas}`;
  });

  // 6. Canasta: Misiones cumplidas
  const misiones = Array.isArray(s.misiones) ? s.misiones : [];
  const misionesCumplidas = misiones.filter(m => m.cumplida).length;
  document.querySelectorAll(".lumea-bind-misiones-count").forEach(el => {
    el.textContent = `${misionesCumplidas} de ${misiones.length || 3}`;
  });

  // 7. Próxima misión sugerida (la primera pendiente)
  const proxMision = misiones.find(m => !m.cumplida) || misiones[0];
  const elMisionTit = document.getElementById("proxima-mision-titulo");
  const elMisionXP = document.getElementById("proxima-mision-xp");
  if (elMisionTit && proxMision) {
    elMisionTit.textContent = proxMision.titulo;
    if (elMisionXP) {
      elMisionXP.innerHTML = `<span class="badge text-bg-warning text-dark me-1 fw-bold">+${proxMision.recompensa || 20} XP</span> ${proxMision.descripcion || ''}`;
    }
  }

  // 8. Canasta: Ánimo de hoy
  const emojis = { muy_mal: "😢", mal: "🙁", neutral: "😐", bien: "🙂", muy_bien: "😄" };
  const nombresAnimo = { muy_mal: "Muy mal", mal: "Mal", neutral: "Neutral", bien: "Bien", muy_bien: "Muy bien" };

  document.querySelectorAll(".lumea-bind-animo-hoy").forEach(el => {
    if (s.animo_hoy && s.animo_hoy.registrado) {
      const estado = s.animo_hoy.estado || "bien";
      el.textContent = `${emojis[estado] || "🙂"} ${nombresAnimo[estado] || "Bien"}`;
    } else {
      el.textContent = `Sin registrar`;
    }
  });

  // 9. Mensaje de bienvenida de regreso (solo si el backend lo envía)
  const avisoRegreso = document.getElementById("aviso-regreso");
  if (avisoRegreso) {
    if (u.mensaje_regreso) {
      avisoRegreso.style.display = "flex";
      const textoRegreso = avisoRegreso.querySelector(".fw-bold");
      if (textoRegreso) textoRegreso.textContent = u.mensaje_regreso;
    } else {
      avisoRegreso.style.display = "none";
    }
  }

  // 10. Avatar en contenedores: Se deja literalmente vacío porque el usuario implementa su propio avatar
  document.querySelectorAll(".lumea-render-avatar").forEach(container => {
    container.innerHTML = "";
  });

  // Miniatura de avatar con cara de ánimo (solo si ya registró ánimo)
  const estadoEmoji = (s.animo_hoy && s.animo_hoy.registrado)
    ? (emojis[s.animo_hoy.estado] || "🙂")
    : "👤";
  document.querySelectorAll(".lumea-avatar-mini-emoji").forEach(el => {
    el.textContent = estadoEmoji;
  });
}

// Iniciar y escuchar eventos
document.addEventListener("DOMContentLoaded", () => {
  sincronizarLumeaUI();
  window.addEventListener("lumea:state-changed", () => {
    sincronizarLumeaUI();
  });
});
