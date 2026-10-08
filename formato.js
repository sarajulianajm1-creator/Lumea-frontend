// =====================================================================
// formato.js — textos y cuentas que comparten Progreso y Avatar.
// Sin diseño y sin tocar la página: son funciones puras.
//
//   LumeaFormato.plural(3, "día", "días")   -> "3 días"
//   LumeaFormato.semillas(1) / semillas(5)  -> "1 semilla" / "5 semillas"   (en pantalla, XP = «semillas»)
//   LumeaFormato.porcentajeNivel(progreso)  -> 0 a 100
//   LumeaFormato.textoNivel(progreso)       -> "Te faltan 35 semillas para la etapa 3"   (en pantalla, nivel = «etapa»)
//   LumeaFormato.textoRacha(3)              -> "3 días"      notaRacha(0) -> invita, sin reproche
//   LumeaFormato.textoMeta(meta_diaria)     -> "10 de 15 semillas hoy" / "Meta cumplida: 20 semillas hoy"
//   LumeaFormato.semanaDe(hoy)              -> los 7 días (lunes a domingo) de esa semana
//   LumeaFormato.comidasPorDia(historial, semana), animoPorDia(registros, semana)
//   LumeaFormato.NOMBRE_ANIMO               -> { muy_mal: "Muy mal", ... }
// =====================================================================
(function () {
  "use strict";

  // «1 día», «3 días»
  function plural(n, singular, pluralTexto) {
    return `${n} ${n === 1 ? singular : pluralTexto}`;
  }

  // Camino del cuidado: lo que se ve dice «semillas» donde el contrato dice XP y «etapa» donde dice nivel.
  // Las claves del contrato (xp_total, nivel, xp_siguiente_nivel…) NO cambian: solo el texto en pantalla.
  // «1 semilla», «5 semillas»
  function semillas(n) {
    return plural(n, "semilla", "semillas");
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
      ? "Llegaste a la etapa máxima"
      : `${p.xp_faltante_siguiente_nivel === 1 ? "Te falta" : "Te faltan"} ${semillas(p.xp_faltante_siguiente_nivel)} para la etapa ${p.nivel + 1}`;
  }

  function textoRacha(n) {
    return plural(n, "día", "días");
  }

  // Lo que va debajo de la cifra de la racha: nunca un reproche si no hay racha
  function notaRacha(n) {
    if (n === 0) return "Registra algo hoy para empezar una racha";
    return n === 1 ? "¡Empezó tu racha!" : "seguidos con actividad";
  }

  // La meta del día es de semillas (no de comidas). Si ya pasó la meta: «Meta cumplida: 20 semillas hoy»
  function textoMeta(m) {
    return m.cumplida ? `Meta cumplida: ${semillas(m.xp_hoy)} hoy` : `${m.xp_hoy} de ${semillas(m.meta)} hoy`;
  }

  const NOMBRE_ANIMO = { muy_mal: "Muy mal", mal: "Mal", neutral: "Neutral", bien: "Bien", muy_bien: "Muy bien" };
  const DIAS_CORTO = ["L", "M", "M", "J", "V", "S", "D"];
  const DIAS_LARGO = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];

  const clave = (a, m, d) => `${a}-${String(m + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;

  function claveDeHoy(hoy) {
    return clave(hoy.getFullYear(), hoy.getMonth(), hoy.getDate());
  }

  // La semana (lunes a domingo) que contiene a `hoy`: [{ clave: "2026-10-05", indice: 0..6 }]
  function semanaDe(hoy) {
    const dia = (hoy.getDay() + 6) % 7;                    // lunes = 0
    return DIAS_LARGO.map((_, i) => {
      const f = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate() - dia + i);
      return { clave: clave(f.getFullYear(), f.getMonth(), f.getDate()), indice: i };
    });
  }

  // El backend manda la fecha como «Mon, 05 Oct 2026 00:00:00 GMT»: medianoche en UTC.
  // Se lee con los campos UTC; con los locales, en Colombia (UTC-5) saldría el día anterior.
  function claveDeFechaDelServidor(texto) {
    const f = new Date(texto);
    if (Number.isNaN(f.getTime())) return null;
    return clave(f.getUTCFullYear(), f.getUTCMonth(), f.getUTCDate());
  }

  // Por cada día de la semana: cuántas comidas y si hubo alguna fruta (`es_fruta` de /historial)
  function comidasPorDia(historial, semana) {
    const dias = {};
    semana.forEach((d) => { dias[d.clave] = { comidas: 0, fruta: false }; });
    (historial || []).forEach((r) => {
      const c = claveDeFechaDelServidor(r.fecha);
      if (c && dias[c]) {
        dias[c].comidas += 1;
        if (r.es_fruta === true) dias[c].fruta = true;
      }
    });
    return semana.map((d) => ({ ...d, ...dias[d.clave] }));
  }

  // El último estado de ánimo de cada día de la semana (la lista llega del más reciente al más antiguo)
  function animoPorDia(registros, semana) {
    const porDia = {};
    (registros || []).forEach((r) => {
      const c = claveDeFechaDelServidor(r.fecha);
      if (c && !(c in porDia)) porDia[c] = r.estado;
    });
    return semana.map((d) => ({ ...d, estado: porDia[d.clave] || null }));
  }

  window.LumeaFormato = {
    plural, semillas, porcentajeNivel, textoNivel, textoRacha, notaRacha, textoMeta,
    NOMBRE_ANIMO, DIAS_CORTO, DIAS_LARGO, claveDeHoy, semanaDe, claveDeFechaDelServidor, comidasPorDia, animoPorDia,
  };
})();
