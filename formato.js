// =====================================================================
// formato.js — textos y cuentas que comparten Progreso y Avatar.
// Sin diseño y sin tocar la página: son funciones puras.
//
//   LumeaFormato.plural(3, "día", "días")   -> "3 días"
//   LumeaFormato.porcentajeNivel(progreso)  -> 0 a 100
//   LumeaFormato.textoNivel(progreso)       -> "Te faltan 35 XP para el nivel 3"
// =====================================================================
(function () {
  "use strict";

  // «1 día», «3 días»
  function plural(n, singular, pluralTexto) {
    return `${n} ${n === 1 ? singular : pluralTexto}`;
  }

  // Cuánto de la barra se llena (0 a 100). Después de perder XP el XP puede quedar por
  // debajo del inicio del nivel: la barra nunca baja de 0. En el último nivel, llena.
  function porcentajeNivel(p) {
    if (p.xp_siguiente_nivel === null || p.xp_siguiente_nivel === undefined) return 100;
    const ancho = p.xp_siguiente_nivel - p.xp_inicio_nivel;
    if (!(ancho > 0)) return 0;
    return Math.round(Math.max(0, Math.min(1, (p.xp_total - p.xp_inicio_nivel) / ancho)) * 100);
  }

  function textoNivel(p) {
    return p.xp_siguiente_nivel === null || p.xp_siguiente_nivel === undefined
      ? "Llegaste al nivel máximo"
      : `Te faltan ${p.xp_faltante_siguiente_nivel} XP para el nivel ${p.nivel + 1}`;
  }

  window.LumeaFormato = { plural, porcentajeNivel, textoNivel };
})();
