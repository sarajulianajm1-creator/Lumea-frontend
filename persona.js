// =====================================================================
// persona.js — la persona de Lumea: un avatar voxel-art de DiceBear 10.x (licencia CC0), dibujado AQUÍ,
// en el navegador, con los archivos de vendor/dicebear/. No se le pide nada a api.dicebear.com.
//
// Es un módulo ES. Desde un script clásico (avatar.js) se usa con import():
//   const { dibujarPersona, urlDePersona } = await import("./persona.js");
//   const svg = await dibujarPersona(persona, { animada: true });     // el SVG como texto
//   img.src = await urlDePersona(persona);                            // o una dirección data: para una <img>
//
// `persona` es la de GET /avatar (MISION_PULIDO_BACKEND.md, B3):
//   { rasgos: {skinColor, topVariant, hairColor, eyesVariant, mouthVariant, cheeksVariant|null, beardVariant|null, shirtColor},
//     puesto: { ropa: {parametros}|null, accesorio: {parametros}|null } }
//
// Reglas:
//   - La semilla es fija ('lumea'): NUNCA el correo ni ningún dato de la persona.
//   - El fondo es transparente.
//   - Ningún rasgo visible queda al azar: pelo, lentes, barba y mejillas valen 100 o 0 según lo elegido,
//     y el pantalón y los zapatos son fijos.
//   - Animada solo si se pide y la persona admite movimiento (prefers-reduced-motion).
// =====================================================================

const SEMILLA = "lumea";
const PANTALON = "3b5b8c";                 // si el backend todavía no manda el pantalón y los zapatos (B8), son fijos
const ZAPATOS = "f1f3f5";

// Las claves de rasgos que se aceptan (lo demás se ignora)
const COLORES = ["skinColor", "hairColor", "shirtColor", "pantsColor", "shoesColor"];
const VARIANTES = ["topVariant", "eyesVariant", "mouthVariant", "noseVariant"];
// Las que pueden no estar («Ninguno»): su probabilidad vale 100 si hay opción y 0 si no
const OPCIONALES = { cheeksVariant: "cheeksProbability", beardVariant: "beardProbability", eyebrowsVariant: "eyebrowsProbability" };

let nucleo = null;
// Un servidor sencillo (python -m http.server) puede cortar alguna de las ~40 peticiones de módulos que llegan juntas:
// si pasa, se intenta una vez más antes de rendirse.
function cargarNucleo(intentos = 0) {
  if (!nucleo) {
    nucleo = Promise.all([
      import("./vendor/dicebear/core/index.js"),
      fetch("vendor/dicebear/estilos/voxel-art.json").then((r) => { if (!r.ok) throw new Error("voxel-art.json"); return r.json(); }),
    ]).then(([m, def]) => ({ Avatar: m.Avatar, estilo: new m.Style(def) }))
      .catch((e) => {
        nucleo = null;
        if (intentos >= 7) throw e;
        return new Promise((ok) => setTimeout(ok, 250 * (intentos + 1))).then(() => cargarNucleo(intentos + 1));
      });
  }
  return nucleo;
}

function movimientoReducido() {
  return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
}

// DiceBear pide listas, y los colores en hexadecimal sin «#»
function lista(valor) {
  return [String(valor).replace(/^#/, "")];
}

// Las opciones de DiceBear a partir de la persona. Pura y sin red: es lo que prueban los tests.
export function opcionesDePersona(persona, { animada = false } = {}) {
  const rasgos = (persona && persona.rasgos) || {};
  const puesto = (persona && persona.puesto) || {};
  const opciones = {
    seed: SEMILLA,
    backgroundColor: ["ffffff00"],                 // sin fondo, salvo que la persona elija uno
    pantsColor: [PANTALON],
    shoesColor: [ZAPATOS],
    outfitVariant: ["plain"],                      // sin ropa puesta: la camiseta lisa
    glassesProbability: 0,
    cheeksProbability: 0,
    beardProbability: 0,
    topProbability: 100,
    animationVariant: [animada && !movimientoReducido() ? "slow" : "none"],
  };
  COLORES.concat(VARIANTES).forEach((clave) => { if (rasgos[clave]) opciones[clave] = lista(rasgos[clave]); });
  if (rasgos.backgroundColor) opciones.backgroundColor = lista(rasgos.backgroundColor);
  Object.keys(OPCIONALES).forEach((clave) => {
    if (rasgos[clave]) { opciones[clave] = lista(rasgos[clave]); opciones[OPCIONALES[clave]] = 100; }
    else if (clave in rasgos) opciones[OPCIONALES[clave]] = 0;              // «Ninguno» (null)
  });
  // Lo que la persona tiene puesto: sus parámetros (outfitVariant, glassesVariant, y un color si la prenda lo pide)
  ["ropa", "accesorio"].forEach((tipo) => {
    const objeto = puesto[tipo];
    const parametros = (objeto && objeto.parametros) || {};
    Object.keys(parametros).forEach((clave) => { opciones[clave] = lista(parametros[clave]); });
    if (tipo === "accesorio" && parametros.glassesVariant) opciones.glassesProbability = 100;
  });
  return opciones;
}

// `recorte` ([x, y, ancho, alto] en el lienzo de 128) acerca el dibujo a una parte de la persona (la cara, para los mosaicos de
// ojos, cejas, nariz, boca, mejillas y barba): solo cambia el viewBox del SVG.
export async function dibujarPersona(persona, { animada = false, recorte = null } = {}) {
  const { Avatar, estilo } = await cargarNucleo();
  const svg = new Avatar(estilo, opcionesDePersona(persona, { animada })).toString();
  return recorte ? svg.replace(/viewBox="[^"]*"/, `viewBox="${recorte.join(" ")}"`) : svg;
}

// Una dirección data: lista para <img src>; no sale ninguna petición
export async function urlDePersona(persona, { animada = false, recorte = null } = {}) {
  const svg = await dibujarPersona(persona, { animada, recorte });
  return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
}
