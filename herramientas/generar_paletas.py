"""
LUMEA · generar_paletas.py
--------------------------------------------------------------------------
Genera las 5 paletas de Lumea (cada una en modo claro y oscuro) a partir
de pocos números, y las VALIDA antes de escribirlas:

  1. Contraste WCAG 2.2 de cada par texto/fondo (4.5:1) y de cada
     elemento no textual (3:1).
  2. Distancia perceptual entre las 5 frutas-señal simulando protanopia,
     deuteranopia y tritanopia (matrices de Machado, Oliveira y
     Fernandes, 2009) y en escala de grises.

Salidas:
  estilos/paletas.css         variables CSS de los 10 temas
  estilos/tokens.json         los mismos valores en formato W3C DTCG
  docs/validacion-paletas.md  la tabla de mediciones (para el jurado)

No necesita librerías: la conversión OKLCH -> sRGB está escrita aquí
abajo (Ottosson, 2020), para que se pueda leer y explicar.

Uso (desde la carpeta Lumea-frontend):
    python3 herramientas/generar_paletas.py
"""
import json
import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# =========================================================================
# 1. LA GRAMÁTICA FIJA (el "genoma"): igual en las 5 paletas
# =========================================================================
# Cada fruta significa siempre lo mismo y ocupa siempre su escalón de
# luminosidad (L de OKLCH). El orden mora < aguacate < guayaba < mango <
# maracuyá separa las frutas incluso con daltonismo (ver informe, sección
# "Criterios de diseño derivados").
ROLES = {
    # rol semántico : fruta
    "mision": "mora",
    "comida": "aguacate",
    "emocion": "guayaba",
    "duda": "mango",
    "logro": "maracuya",
}
L_RELLENO = {
    "claro":  {"mora": 0.44, "aguacate": 0.54, "guayaba": 0.67, "mango": 0.79, "maracuya": 0.91},
    "oscuro": {"mora": 0.70, "aguacate": 0.76, "guayaba": 0.80, "mango": 0.84, "maracuya": 0.90},
}
# Bandas de tono permitidas (h de OKLCH, grados). Una paleta puede mover
# cada fruta SOLO dentro de su banda.
BANDAS = {
    "aguacate": (130, 155), "maracuya": (86, 100), "mango": (52, 65),
    "guayaba": (345, 370), "mora": (300, 325),
}

# =========================================================================
# 2. LA PIEL VARIABLE: lo que cambia entre paletas
# =========================================================================
# h: tono de cada fruta (dentro de su banda)
# croma: cuánta saturación tienen las frutas (presupuesto de la paleta)
# claro / oscuro: tono y croma de las superficies, L de la marca
PALETAS = {
    "laguna": {
        "nombre": "Laguna Verde", "caracter": "Original, fresca",
        "origen": "El verde de la Laguna Verde del volcán Azufral viene del azufre y las algas.",
        "h": {"aguacate": 152, "maracuya": 92, "mango": 57, "guayaba": 345, "mora": 314},
        "croma": 0.13, "croma_mango": 0.16, "croma_contenedor": 0.07,
        "claro":  {"h": 178, "c_fondo": 0.016, "L_fondo": 0.968, "L_marca": 0.42},
        "oscuro": {"h": 195, "c_fondo": 0.030, "L_fondo": 0.185},
    },
    "neblina": {
        "nombre": "Neblina", "caracter": "Pastel, tranquila",
        "origen": "La bruma azul plomo de la Laguna de La Cocha, humedal Ramsar.",
        "h": {"aguacate": 148, "maracuya": 95, "mango": 63, "guayaba": 345, "mora": 308},
        "croma": 0.085, "croma_mango": 0.13, "croma_contenedor": 0.045,
        "claro":  {"h": 250, "c_fondo": 0.012, "L_fondo": 0.975, "L_marca": 0.44},
        "oscuro": {"h": 255, "c_fondo": 0.022, "L_fondo": 0.205},
    },
    "carnaval": {
        "nombre": "Carnaval", "caracter": "Fuerte, de alto contraste",
        "origen": "Talco y carbón del Carnaval de Negros y Blancos: la igualdad entre opuestos.",
        "h": {"aguacate": 140, "maracuya": 90, "mango": 63, "guayaba": 345, "mora": 320},
        "croma": 0.32, "croma_mango": 0.32, "croma_contenedor": 0.09,
        "claro":  {"h": 85, "c_fondo": 0.006, "L_fondo": 0.985, "L_marca": 0.24},
        "oscuro": {"h": 300, "c_fondo": 0.012, "L_fondo": 0.160},
    },
    "colibri": {
        "nombre": "Colibrí", "caracter": "Viva, iridiscente",
        "origen": "Colombia tiene más especies de aves que ningún otro país; el brillo del colibrí no es pigmento, nace de capas microscópicas en sus plumas.",
        "h": {"aguacate": 146, "maracuya": 88, "mango": 63, "guayaba": 345, "mora": 305},
        "croma": 0.22, "croma_mango": 0.22, "croma_contenedor": 0.08,
        "claro":  {"h": 265, "c_fondo": 0.010, "L_fondo": 0.965, "L_marca": 0.40},
        "oscuro": {"h": 272, "c_fondo": 0.055, "L_fondo": 0.190},
    },
    # El estado neutro: lo que se ve mientras la persona no ha elegido una paleta (ninguna es
    # predeterminada, decisión de Isabella del 7 de octubre de 2026). Superficies casi blancas y
    # texto sin tono (h 85, croma <= 0,006: no se lee ni crema ni gris), con los MISMOS colores de
    # rol de siempre (los de Laguna), porque llevan significado. No aparece en el selector.
    # «tinte» multiplica el croma de la tinta, los bordes y el visor: 1 = como las demás paletas.
    "neutro": {
        "nombre": "Neutro", "caracter": "Sin elegir todavía",
        "origen": "El estado de Lumea antes de que cada persona elija sus colores: superficies casi blancas y sin tono.",
        "h": {"aguacate": 152, "maracuya": 92, "mango": 57, "guayaba": 345, "mora": 314},
        "croma": 0.13, "croma_mango": 0.16, "croma_contenedor": 0.07,
        "tinte": 0.2,
        "claro":  {"h": 85, "c_fondo": 0.005, "L_fondo": 0.985, "L_marca": 0.42},
        "oscuro": {"h": 85, "c_fondo": 0.004, "L_fondo": 0.190},
    },
    "cosecha": {
        "nombre": "Cosecha", "caracter": "Cálida, de mercado",
        "origen": "La cosecha de papas nativas de Nariño: amarillas, rojas y moradas.",
        "h": {"aguacate": 132, "maracuya": 90, "mango": 54, "guayaba": 10, "mora": 318},
        "croma": 0.17, "croma_mango": 0.17, "croma_contenedor": 0.08,
        # fondo #F3F3E1: el ajuste que hizo Isabella a mano el 3 de octubre
        "claro":  {"h": 106.8, "c_fondo": 0.0237, "L_fondo": 0.9593, "L_marca": 0.41},
        "oscuro": {"h": 55, "c_fondo": 0.014, "L_fondo": 0.190},
    },
}
PREDETERMINADA = "neutro"   # la que cae en :root cuando no hay data-paleta (nadie eligió)
SELLO = "#000000"  # Resolución 810 de 2021: no se rediseña


# =========================================================================
# 3. Matemática del color (OKLCH -> sRGB). Ottosson (2020).
# =========================================================================
def oklch_a_lineal(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def lineal_a_oklab(r, g, b):
    l = 0.4122214708 * r + 0.5363015719 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_)


def en_gamut(rgb, tol=1e-6):
    return all(-tol <= x <= 1 + tol for x in rgb)


def oklch(L, C, h):
    """Devuelve el color sRGB más cercano: si no cabe, baja el croma
    (búsqueda binaria) y conserva L y h, que son los que importan."""
    if en_gamut(oklch_a_lineal(L, C, h)):
        return oklch_a_lineal(L, C, h), C
    lo, hi = 0.0, C
    for _ in range(40):
        mid = (lo + hi) / 2
        if en_gamut(oklch_a_lineal(L, mid, h)):
            lo = mid
        else:
            hi = mid
    return oklch_a_lineal(L, lo, h), lo


def a_hex(lin):
    def gamma(x):
        x = min(1, max(0, x))
        return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
    return "#" + "".join(f"{round(gamma(x) * 255):02X}" for x in lin)


def hex_a_lineal(hx):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(lin(int(hx[i:i + 2], 16)) for i in (1, 3, 5))


def color(L, C, h):
    lin, _ = oklch(L, C, h % 360)
    return a_hex(lin)


# =========================================================================
# 4. Construcción de los tokens semánticos de un tema
# =========================================================================
def tema(p, modo):
    P = PALETAS[p]
    S = P[modo]
    hs = S["h"]
    t = {}
    oscuro = modo == "oscuro"
    tinte = P.get("tinte", 1.0)          # 1 = como siempre; el estado neutro casi no tiñe la tinta ni los bordes
    if not oscuro:
        t["fondo"] = color(S["L_fondo"], S["c_fondo"], hs)
        t["superficie"] = color(0.995, S["c_fondo"] * 0.35, hs)
        t["superficie-2"] = color(1.0, 0, 0)
        t["tinta"] = color(0.235 if p != "carnaval" else 0.19, 0.02 * tinte, hs)
        t["tinta-suave"] = color(0.46, 0.025 * tinte, hs)
        t["borde"] = color(0.90, S["c_fondo"] * 0.9 + 0.006 * tinte, hs)
        t["borde-fuerte"] = color(0.60, 0.02 * tinte, hs)
        t["visor"] = color(0.23, 0.03 * tinte, hs)
    else:
        L0 = S["L_fondo"]
        t["fondo"] = color(L0, S["c_fondo"], hs)
        t["superficie"] = color(L0 + 0.04, S["c_fondo"] * 1.05, hs)
        t["superficie-2"] = color(L0 + 0.08, S["c_fondo"] * 1.1, hs)
        t["tinta"] = color(0.93, 0.012 * tinte, hs)
        t["tinta-suave"] = color(0.76, 0.02 * tinte, hs)
        t["borde"] = color(L0 + 0.12, S["c_fondo"] * 1.2, hs)
        t["borde-fuerte"] = color(0.58, 0.02 * tinte, hs)
        t["visor"] = color(max(0.10, L0 - 0.05), S["c_fondo"], hs)

    # Marca (aguacate): botón principal, enlaces, selección
    ha = P["h"]["aguacate"]
    if not oscuro:
        Lm = S["L_marca"]
        cm = 0.03 if Lm < 0.3 else P["croma"] * 0.85
        t["marca"] = color(Lm, cm, ha)
        t["marca-hover"] = color(Lm - 0.06, cm, ha)
        t["sobre-marca"] = color(0.99, 0.01, ha)
        t["marca-suave"] = color(0.94, min(0.05, P["croma_contenedor"]), ha)
        t["marca-tinta"] = color(0.44, min(0.14, P["croma"]), ha)
        t["foco"] = color(0.48, min(0.16, P["croma"] + 0.03), ha)
    else:
        cm = min(0.16, P["croma"])
        t["marca"] = color(0.80, cm, ha)
        t["marca-hover"] = color(0.86, cm, ha)
        t["sobre-marca"] = color(0.20, 0.03, ha)
        t["marca-suave"] = color(S["L_fondo"] + 0.12, min(0.06, P["croma_contenedor"]), ha)
        t["marca-tinta"] = color(0.82, cm, ha)
        t["foco"] = color(0.84, cm, ha)

    # Las 5 frutas-señal, 4 papeles cada una
    for rol, fruta in ROLES.items():
        h = P["h"][fruta]
        c = P["croma_mango"] if fruta == "mango" else P["croma"]
        L = L_RELLENO[modo][fruta]
        if oscuro:
            c = c * 0.85  # en oscuro se baja un poco el croma, nunca la luz del oro
        t[rol] = color(L, c, h)
        claro_relleno = L >= 0.6
        if oscuro:
            t[f"sobre-{rol}"] = color(0.18, 0.02 * tinte, hs)   # texto oscuro sobre relleno luminoso
        else:
            t[f"sobre-{rol}"] = t["tinta"] if claro_relleno else color(0.99, 0.01, h)
        if oscuro:
            # amarillo y naranja oscuros = café/oliva (el color menos querido).
            # En oscuro sus fondos casi no llevan croma: el oro lo pone el ícono.
            k = 0.35 if fruta in ("maracuya", "mango") else 1.0
            t[f"{rol}-suave"] = color(S["L_fondo"] + 0.08, min(0.05, P["croma_contenedor"]) * k, h)
            t[f"{rol}-contenedor"] = color(S["L_fondo"] + 0.13, P["croma_contenedor"] * 0.9 * k, h)
            t[f"{rol}-tinta"] = color(0.84, min(0.12, c), h)
        else:
            # el amarillo con poco croma se vuelve beige/caqui (valencia
            # ecológica: rechazado), así que el maracuyá lleva más croma
            k = 1.6 if fruta == "maracuya" else 1.0
            t[f"{rol}-suave"] = color(0.955, P["croma_contenedor"] * 0.55 * k, h)
            t[f"{rol}-contenedor"] = color(0.905, P["croma_contenedor"] * k, h)
            # amarillo y naranja oscuros se vuelven café/oliva: para texto
            # se usa la tinta neutra (informe: valencia ecológica + Radix)
            if fruta in ("maracuya", "mango"):
                t[f"{rol}-tinta"] = t["tinta"]
            else:
                t[f"{rol}-tinta"] = color(0.45, min(0.15, c), h)

    # Error del sistema (nunca se usa sobre comida)
    if not oscuro:
        t["error"] = color(0.50, 0.19, 27)
        t["sobre-error"] = "#FFFFFF"
        t["error-suave"] = color(0.95, 0.03, 27)
    else:
        t["error"] = color(0.74, 0.14, 25)
        t["sobre-error"] = t["fondo"]
        t["error-suave"] = color(S["L_fondo"] + 0.08, 0.05, 25)

    # Fijos de la pantalla de cámara y la calcomanía de logro
    t["sobre-visor"] = color(0.93, 0.012 * tinte, hs)
    hm = P["h"]["maracuya"]
    t["calcomania"] = color(0.80, max(P["croma"], 0.15), hm) if not oscuro else t["logro"]

    t["sello"] = SELLO
    t["sello-placa"] = "transparent" if not oscuro else color(0.92, 0.01 * tinte, hs)
    return t


# =========================================================================
# 5. Validación: contraste WCAG y daltonismo
# =========================================================================
def luminancia(hx):
    r, g, b = hex_a_lineal(hx)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = sorted([luminancia(a), luminancia(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


MACHADO = {  # severidad 1.0, se aplican en RGB lineal
    "protanopia": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    "deuteranopia": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    "tritanopia": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}


def simular(hx, tipo):
    r, g, b = hex_a_lineal(hx)
    if tipo == "grises":
        y = 0.2126 * r + 0.7152 * g + 0.0722 * b
        return lineal_a_oklab(y, y, y)
    m = MACHADO[tipo]
    rr = [min(1, max(0, m[i][0] * r + m[i][1] * g + m[i][2] * b)) for i in range(3)]
    return lineal_a_oklab(*rr)


def delta_e(a, b):
    return math.dist(a, b)


def pares_texto(t):
    p = [("tinta", "fondo"), ("tinta", "superficie"), ("tinta-suave", "fondo"),
         ("tinta-suave", "superficie"), ("sobre-marca", "marca"), ("marca-tinta", "fondo"),
         ("marca-tinta", "superficie"), ("sobre-error", "error"), ("error", "superficie"),
         ("tinta", "marca-suave")]
    for rol in ROLES:
        p += [(f"sobre-{rol}", rol), (f"{rol}-tinta", f"{rol}-suave"), (f"{rol}-tinta", "superficie"),
              ("tinta", f"{rol}-contenedor"), ("tinta-suave", f"{rol}-contenedor")]
    return p


def pares_no_texto(t):
    return [("borde-fuerte", "superficie"), ("foco", "fondo"), ("foco", "superficie"),
            ("sobre-visor", "visor"),
            ("marca", "superficie"), ("marca", "fondo")]


def validar(p, modo, t):
    filas, fallas = [], []
    for a, b in pares_texto(t):
        r = contraste(t[a], t[b])
        filas.append((a, b, r, 4.5))
        if r < 4.5:
            fallas.append(f"{p}/{modo}: {a} sobre {b} = {r:.2f} (< 4.5)")
    for a, b in pares_no_texto(t):
        r = contraste(t[a], t[b])
        filas.append((a, b, r, 3.0))
        if r < 3.0:
            fallas.append(f"{p}/{modo}: {a} junto a {b} = {r:.2f} (< 3)")
    # daltonismo: distancia mínima entre las 5 frutas-señal
    dal = {}
    roles = list(ROLES)
    for tipo in ["normal", "protanopia", "deuteranopia", "tritanopia", "grises"]:
        pts = {r: (lineal_a_oklab(*hex_a_lineal(t[r])) if tipo == "normal" else simular(t[r], tipo)) for r in roles}
        peor = min(((delta_e(pts[a], pts[b]), a, b) for i, a in enumerate(roles) for b in roles[i + 1:]))
        dal[tipo] = peor
    return filas, fallas, dal


# =========================================================================
# 6. Escritura de archivos
# =========================================================================
def bloque(selectores, t, oscuro):
    lineas = [f"  --c-{k}: {v};" for k, v in t.items()]
    lineas.append(f"  color-scheme: {'dark' if oscuro else 'light'};")
    return ",\n".join(selectores) + " {\n" + "\n".join(lineas) + "\n}\n"


def main():
    temas = {p: {m: tema(p, m) for m in ("claro", "oscuro")} for p in PALETAS}
    informe, todas_fallas = [], []
    for p in PALETAS:
        for m in ("claro", "oscuro"):
            filas, fallas, dal = validar(p, m, temas[p][m])
            todas_fallas += fallas
            informe.append((p, m, filas, dal))

    # ---- CSS
    css = [
        "/* =====================================================================\n"
        "   LUMEA · paletas.css — GENERADO por herramientas/generar_paletas.py\n"
        "   No lo edites a mano: cambia los números en el script y vuelve a\n"
        "   correrlo. Así cada color tiene una medición detrás.\n\n"
        "   Dos ejes independientes en <html>:\n"
        "     data-paleta = laguna | neblina | carnaval | colibri | cosecha\n"
        "     data-modo   = claro | oscuro   (sin atributo = sigue al sistema)\n"
        "   ===================================================================== */\n"]
    # La predeterminada (el estado neutro) va PRIMERO: su bloque lleva :root, que tiene la misma
    # especificidad que [data-paleta="x"], y entre dos reglas iguales gana la que está después.
    # Si fuera en medio, taparía a las paletas que quedaran antes.
    for p in [PREDETERMINADA] + [x for x in PALETAS if x != PREDETERMINADA]:
        P = PALETAS[p]
        # [data-paleta] sin :root para que una tarjeta de muestra también
        # pueda llevar su propia paleta (el selector de paletas lo usa).
        sel = f'[data-paleta="{p}"]'
        defecto = p == PREDETERMINADA
        css.append(f"\n/* ---------- {P['nombre']} · {P['caracter']}. {P['origen']} ---------- */\n")
        css.append(bloque(([":root"] if defecto else []) + [sel], temas[p]["claro"], False))
        osc = [f'{sel}[data-modo="oscuro"]', f':root{sel}:not([data-modo])[data-theme="dark"]']
        if defecto:
            osc += [':root:not([data-paleta])[data-modo="oscuro"]',
                    ':root:not([data-paleta]):not([data-modo])[data-theme="dark"]']
        css.append(bloque(osc, temas[p]["oscuro"], True))
        auto = [f':root{sel}:not([data-modo]):not([data-theme="light"])']
        if defecto:
            auto.append(':root:not([data-paleta]):not([data-modo]):not([data-theme="light"])')
        css.append("@media (prefers-color-scheme: dark) {\n" + bloque(auto, temas[p]["oscuro"], True) + "}\n")
    os.makedirs(os.path.join(RAIZ, "estilos"), exist_ok=True)
    with open(os.path.join(RAIZ, "estilos", "paletas.css"), "w") as f:
        f.write("".join(css))

    # ---- DTCG JSON (tema y modo como "modificadores")
    dtcg = {"$description": "Lumea: 5 paletas x 2 modos. Generado por herramientas/generar_paletas.py",
            "color": {}}
    for p in PALETAS:
        dtcg["color"][p] = {}
        for m in ("claro", "oscuro"):
            dtcg["color"][p][m] = {k: {"$type": "color", "$value": v} for k, v in temas[p][m].items()
                                   if v.startswith("#")}
    with open(os.path.join(RAIZ, "estilos", "tokens.json"), "w") as f:
        json.dump(dtcg, f, indent=2, ensure_ascii=False)

    # ---- Informe de validación
    md = ["# Validación de las paletas de Lumea\n",
          "Generado por `herramientas/generar_paletas.py`. Contraste según WCAG 2.2 "
          "(texto ≥ 4.5:1; componentes y foco ≥ 3:1). Daltonismo simulado con las matrices "
          "de Machado, Oliveira y Fernandes (2009), severidad 1.0; distancia en OKLab (ΔE_OK). "
          "Umbral heurístico usado: ΔE_OK ≥ 0.10 en modo claro. En modo oscuro las frutas se "
          "comprimen en luminosidad y **el ícono y la forma son obligatorios** (WCAG 1.4.1).\n"]
    for p, m, filas, dal in informe:
        P = PALETAS[p]
        md.append(f"\n## {P['nombre']} · {m}\n")
        peor = min(filas, key=lambda x: x[2] / x[3])
        md.append(f"- Pares medidos: {len(filas)}. Peor caso: `{peor[0]}` sobre `{peor[1]}` = "
                  f"**{peor[2]:.2f}:1** (mínimo {peor[3]}).\n")
        md.append("- Distancia mínima entre frutas: " + "; ".join(
            f"{k} {v[0]:.3f} ({v[1]}–{v[2]})" for k, v in dal.items()) + "\n")
    md.append("\n## Fallas\n\n" + ("\n".join(f"- {x}" for x in todas_fallas) if todas_fallas else "Ninguna.") + "\n")
    os.makedirs(os.path.join(RAIZ, "docs"), exist_ok=True)
    with open(os.path.join(RAIZ, "docs", "validacion-paletas.md"), "w") as f:
        f.write("".join(md))

    # ---- Resumen en consola
    for p, m, filas, dal in informe:
        peor = min(filas, key=lambda x: x[2] / x[3])
        d = " ".join(f"{k[:4]}={v[0]:.3f}({v[1][:3]}-{v[2][:3]})" for k, v in dal.items())
        print(f"{p:11} {m:7} peor {peor[0]}/{peor[1]} {peor[2]:.2f}  |  {d}")
    if todas_fallas:
        print("\nFALLAS:")
        print("\n".join(todas_fallas))
        sys.exit(1)
    print(f"\nTodo pasa WCAG AA en los {len(PALETAS) * 2} temas.")


if __name__ == "__main__":
    main()
