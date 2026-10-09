// =====================================================================
// leer-mas.js — el bloque largo con «Leer más» (K0.5), compartido por Registrar y por el «¿Sabías que…?» de Inicio.
//
//   const bloque = LumeaLeerMas.conectar(parrafo, boton);   // el <p> con el texto y el <button> «Leer más»
//   bloque.ajustar(true);                                    // después de poner un texto nuevo (true: vuelve a cerrado)
//
// Líneas de unos 65 caracteres (CSS, clase .dato-largo) y, si el texto pasa de 4 líneas, se corta (.dato--cortado) y
// el botón (aria-expanded, aria-controls, sin animación) lo abre y lo cierra. Se vuelve a medir si cambia el ancho.
// =====================================================================
(function () {
  "use strict";

  const LINEAS = 4;

  function conectar(p, boton) {
    if (!p || !boton) return { ajustar() {} };
    let ancho = null;

    function ajustar(reiniciar) {
      if (reiniciar) { boton.setAttribute("aria-expanded", "false"); boton.textContent = "Leer más"; }
      const abierto = boton.getAttribute("aria-expanded") === "true";
      const alto = parseFloat(getComputedStyle(p).lineHeight);
      // scrollHeight es el alto de todo el texto, esté cortado o no
      const lineas = alto > 0 ? Math.round(p.scrollHeight / alto) : 0;
      const largo = lineas > LINEAS;
      boton.hidden = !largo;
      p.classList.toggle("dato--cortado", largo && !abierto);
    }

    boton.addEventListener("click", () => {
      const abrir = boton.getAttribute("aria-expanded") !== "true";
      boton.setAttribute("aria-expanded", String(abrir));
      boton.textContent = abrir ? "Leer menos" : "Leer más";
      ajustar(false);
    });
    // Si cambia el ancho (giro del celular, ventana), el texto ocupa otras líneas: se vuelve a medir.
    // Solo se mira el ancho: cortar el texto cambia el alto y no debe volver a disparar la medida.
    if (window.ResizeObserver) {
      new ResizeObserver(() => {
        if (p.clientWidth === ancho) return;
        ancho = p.clientWidth;
        ajustar(false);
      }).observe(p);
    }
    return { ajustar };
  }

  window.LumeaLeerMas = { conectar };
})();
