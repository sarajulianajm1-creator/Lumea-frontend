/* =====================================================================
   LUMEA · tema.js — paleta y modo de color
   ---------------------------------------------------------------------
   Va en el <head> de cada página, ANTES de las hojas de estilo, sin
   "defer" ni "async". Así pone la paleta guardada antes de que el
   navegador pinte y no hay un destello del tema equivocado.

   Dos ejes independientes sobre <html>:
     data-paleta = laguna | neblina | carnaval | colibri | cosecha
     data-modo   = claro | oscuro   (sin atributo = sigue al sistema)

   Uso desde otra página:
     LumeaTema.ponerPaleta('neblina');
     LumeaTema.ponerModo('oscuro');   // 'claro' | 'oscuro' | 'auto'
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

  function modoEfectivo() {
    if (html.dataset.modo) return html.dataset.modo;
    return window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'oscuro' : 'claro';
  }

  // Al cargar: aplicar lo guardado (si no hay nada, Laguna Verde y modo del sistema)
  var paleta = leer('lumea-paleta');
  if (RENOMBRADAS[paleta]) { paleta = RENOMBRADAS[paleta]; guardar('lumea-paleta', paleta); }
  var modo = leer('lumea-modo');
  if (PALETAS.indexOf(paleta) !== -1) html.dataset.paleta = paleta;
  if (modo === 'claro' || modo === 'oscuro') html.dataset.modo = modo;

  window.LumeaTema = { PALETAS: PALETAS, ponerPaleta: ponerPaleta, ponerModo: ponerModo, modoEfectivo: modoEfectivo };
})();
