/* =====================================================================
   LUMEA · tema.js — paleta y modo de color
   ---------------------------------------------------------------------
   Va en el <head> de cada página, ANTES de las hojas de estilo, sin
   "defer" ni "async". Así pone la paleta guardada antes de que el
   navegador pinte y no hay un destello del tema equivocado.

   Dos ejes independientes sobre <html>:
     data-paleta = laguna | neblina | carnaval | colibri | cosecha
                   (sin atributo = el estado NEUTRO: ninguna paleta es predeterminada,
                    cada persona elige la suya; el estado neutro no se puede «elegir»)
     data-modo   = claro | oscuro   (sin atributo = sigue al sistema)
   Y uno más, solo para comparar con el diseño original de Sara:
     data-piel   = sara              (?piel=sara en la dirección; ver puente-sara.css)

   Uso desde otra página:
     LumeaTema.ponerPaleta('neblina');
     LumeaTema.ponerModo('oscuro');   // 'claro' | 'oscuro' | 'auto'
     LumeaTema.paletaActual();        // 'neblina', o null si la persona todavía no eligió
     LumeaTema.modoGuardado();        // 'claro' | 'oscuro' | 'auto'
     LumeaTema.ponerPiel('sara');     // 'sara' | 'lumea' (solo esta pestaña)
   ===================================================================== */
(function () {
  var PALETAS = ['laguna', 'neblina', 'carnaval', 'colibri', 'cosecha'];
  // Nombres viejos (4 oct 2026): quien los tenga guardados no pierde su elección
  var RENOMBRADAS = { mopa: 'colibri', potrerillo: 'cosecha' };
  var html = document.documentElement;

  // localStorage puede fallar (modo privado, permisos): nunca rompe la app.
  function leer(clave) { try { return localStorage.getItem(clave); } catch (e) { return null; } }
  function guardar(clave, valor) {
    try { if (valor == null) localStorage.removeItem(clave); else localStorage.setItem(clave, valor); } catch (e) {}
  }

  function ponerPaleta(nombre) {
    if (PALETAS.indexOf(nombre) === -1) return;
    html.dataset.paleta = nombre;
    guardar('lumea-paleta', nombre);
    html.dispatchEvent(new CustomEvent('lumea:tema'));
  }

  function ponerModo(modo) {
    if (modo === 'claro' || modo === 'oscuro') { html.dataset.modo = modo; guardar('lumea-modo', modo); }
    else { delete html.dataset.modo; guardar('lumea-modo', null); }
    html.dispatchEvent(new CustomEvent('lumea:tema'));
  }

  // La paleta que eligió la persona, o null mientras no haya elegido (se ve el estado neutro)
  function paletaActual() {
    return PALETAS.indexOf(html.dataset.paleta) !== -1 ? html.dataset.paleta : null;
  }

  // Lo que eligió de modo: 'claro', 'oscuro' o 'auto' («como mi dispositivo»)
  function modoGuardado() {
    return html.dataset.modo === 'claro' || html.dataset.modo === 'oscuro' ? html.dataset.modo : 'auto';
  }

  function modoEfectivo() {
    if (html.dataset.modo) return html.dataset.modo;
    return window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'oscuro' : 'claro';
  }

  // ---------- Piel de comparación (páginas de Sara + puente-sara.css) ----------
  // ?piel=sara muestra el diseño original de Sara; ?piel=lumea vuelve.
  // Se guarda en sessionStorage, que es de UNA pestaña: dos pestañas lado a
  // lado pueden recorrer el mismo flujo con pieles distintas.
  function leerPestana(clave) { try { return sessionStorage.getItem(clave); } catch (e) { return null; } }
  function guardarPestana(clave, valor) {
    try { if (valor == null) sessionStorage.removeItem(clave); else sessionStorage.setItem(clave, valor); } catch (e) {}
  }
  function ponerPiel(piel) {
    if (piel === 'sara') { html.dataset.piel = 'sara'; guardarPestana('lumea-piel', 'sara'); }
    else { delete html.dataset.piel; guardarPestana('lumea-piel', null); }
    sincronizarBootstrap();
  }
  // Bootstrap tiene sus propios componentes oscuros (menú, flechas de select):
  // se encienden solo con la piel de Lumea en modo oscuro.
  function sincronizarBootstrap() {
    if (html.dataset.piel === 'sara') html.removeAttribute('data-bs-theme');
    else html.setAttribute('data-bs-theme', modoEfectivo() === 'oscuro' ? 'dark' : 'light');
  }

  // Al cargar: aplicar lo guardado (si no hay nada, el estado neutro y el modo del sistema)
  var paleta = leer('lumea-paleta');
  if (RENOMBRADAS[paleta]) { paleta = RENOMBRADAS[paleta]; guardar('lumea-paleta', paleta); }
  var modo = leer('lumea-modo');
  if (PALETAS.indexOf(paleta) !== -1) html.dataset.paleta = paleta;
  if (modo === 'claro' || modo === 'oscuro') html.dataset.modo = modo;

  var pielPedida = null;
  try { pielPedida = new URLSearchParams(location.search).get('piel'); } catch (e) {}
  if (pielPedida === 'sara' || pielPedida === 'lumea') ponerPiel(pielPedida);
  else ponerPiel(leerPestana('lumea-piel') === 'sara' ? 'sara' : 'lumea');

  html.addEventListener('lumea:tema', sincronizarBootstrap);
  if (window.matchMedia) {
    var consulta = matchMedia('(prefers-color-scheme: dark)');
    if (consulta.addEventListener) consulta.addEventListener('change', sincronizarBootstrap);
  }

  window.LumeaTema = { PALETAS: PALETAS, ponerPaleta: ponerPaleta, ponerModo: ponerModo,
                       paletaActual: paletaActual, modoGuardado: modoGuardado,
                       modoEfectivo: modoEfectivo, ponerPiel: ponerPiel };
})();
