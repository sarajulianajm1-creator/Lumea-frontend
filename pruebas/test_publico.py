"""Páginas públicas (rediseño R7): solo CSS. publico.css les pone la tipografía, los radios y las superficies del rediseño.

Las seis páginas son de Isabella (Bienvenida, Conócenos, Guía, Crear cuenta, Iniciar sesión y Términos): lo único que
cambió en ellas es el <head> (enlaces a hojas de estilo) y el logo del encabezado (.logo-brand). Los textos no se tocan.
"""
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
PUBLICAS = ["index.html", "conocenos.html", "guialumea.html", "crear-cuenta.html", "iniciar-sesion.html", "terminos.html"]
TAMANOS = {"1280": (1280, 800), "390": (390, 844)}
ESCALA = [12.8, 14, 16, 20, 25.008, 31.248, 48.832]                   # --t-xs … --t-3xl
CASOS = [(p, t) for p in PUBLICAS for t in TAMANOS]
IDS = [f"{p[:-5]}-{t}" for p, t in CASOS]


def abrir(pagina, nombre, tamano="1280", paleta=None):
    ancho, alto = TAMANOS[tamano]
    pagina.set_viewport_size({"width": ancho, "height": alto})
    if paleta:
        pagina.add_init_script(f"localStorage.setItem('lumea-paleta', '{paleta}')")
    pagina.goto(f"{pagina.servidor}/{nombre}")
    pagina.wait_for_load_state("networkidle")


def head(nombre):
    s = (RAIZ / nombre).read_text(encoding="utf-8")
    return s[s.index("<head"):s.index("</head>")]


# ---------- El <head> y el logo (lo único del HTML que cambió) ----------

@pytest.mark.parametrize("nombre", PUBLICAS)
def test_publico_css_se_carga_despues_de_style_css(nombre):
    hojas = re.findall(r'<link[^>]*href="([^"]+\.css)"', head(nombre))
    assert "estilos/publico.css" in hojas
    assert hojas.index("estilos/publico.css") > hojas.index("style.css")
    assert hojas.index("estilos/publico.css") > hojas.index("estilos/puente-sara.css")


@pytest.mark.parametrize("nombre", PUBLICAS)
def test_ya_no_piden_fuentes_a_google(nombre):
    assert "fonts.googleapis.com" not in head(nombre) and "fonts.gstatic.com" not in head(nombre)     # la fuente única es local


@pytest.mark.parametrize("nombre", PUBLICAS)
def test_el_logo_del_encabezado_es_una_imagen_y_no_un_emoji_con_mayusculas(pagina, nombre):
    pagina.goto(f"{pagina.servidor}/{nombre}")
    logo = pagina.locator("a.logo-brand")
    assert logo.count() == 1
    assert logo.locator("img.marca[src='img/logo.svg'][alt=Lumea]").count() == 1
    assert logo.inner_text().strip() == ""                                              # sin 🌿 ni «LUMEA» escrito
    assert logo.get_attribute("href") == "index.html"
    assert logo.locator("img").evaluate("e => e.getBoundingClientRect().height") == 32


@pytest.mark.parametrize("nombre", PUBLICAS)
def test_las_paginas_publicas_siguen_con_su_h1_y_sin_errores(pagina, nombre):
    errores = []
    pagina.on("pageerror", lambda e: errores.append(str(e)))
    pagina.goto(f"{pagina.servidor}/{nombre}")
    assert pagina.locator("h1:visible").count() == 1
    assert errores == []


# ---------- El aspecto, medido en el navegador ----------

@pytest.mark.parametrize("nombre,tamano", CASOS, ids=IDS)
def test_todo_border_radius_es_uno_de_los_cuatro_tokens(pagina, nombre, tamano):
    abrir(pagina, nombre, tamano)
    fuera = pagina.evaluate("""() => {
        const raiz = getComputedStyle(document.documentElement);
        const permitidos = new Set(['0px', '50%', ...['--r-control', '--r-tarjeta', '--r-panel', '--r-pildora'].map((t) => raiz.getPropertyValue(t).trim())]);
        const malos = [];
        for (const el of document.querySelectorAll('body, body *')) {
            const c = getComputedStyle(el);
            for (const esquina of ['TopLeft', 'TopRight', 'BottomRight', 'BottomLeft'])
                for (const valor of c['border' + esquina + 'Radius'].split(' '))
                    if (!permitidos.has(valor)) malos.push(valor + ': ' + el.tagName.toLowerCase() + '.' + el.className);
        }
        return [...new Set(malos)];
    }""")
    assert fuera == []


@pytest.mark.parametrize("nombre,tamano", CASOS, ids=IDS)
def test_nada_en_mayusculas_por_css(pagina, nombre, tamano):
    abrir(pagina, nombre, tamano)
    mayusculas = pagina.evaluate("""[...document.querySelectorAll('body *')]
        .filter((e) => getComputedStyle(e).textTransform === 'uppercase').map((e) => e.tagName.toLowerCase() + '.' + e.className)""")
    assert mayusculas == []


@pytest.mark.parametrize("nombre,tamano", CASOS, ids=IDS)
def test_todo_el_texto_va_en_bricolage_grotesque_y_en_la_escala_de_tipos(pagina, nombre, tamano):
    abrir(pagina, nombre, tamano)
    resultado = pagina.evaluate("""(escala) => {
        const fuentes = new Set(), fuera = [];
        for (const el of document.querySelectorAll('body *')) {
            if (![...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
            const c = getComputedStyle(el);
            fuentes.add(c.fontFamily.split(',')[0].replace(/"/g, ''));
            const t = parseFloat(c.fontSize);
            if (!escala.some((e) => Math.abs(e - t) < 0.06)) fuera.push(t.toFixed(1) + 'px ' + el.tagName.toLowerCase() + '.' + el.className);
        }
        return { fuentes: [...fuentes], fuera: [...new Set(fuera)] };
    }""", ESCALA)
    assert resultado["fuentes"] == ["Bricolage Grotesque"]
    assert resultado["fuera"] == []                                                      # y ningún texto por debajo de 12,8 px


@pytest.mark.parametrize("nombre,tamano", CASOS, ids=IDS)
def test_las_superficies_se_separan_con_borde_y_no_con_sombra(pagina, nombre, tamano):
    abrir(pagina, nombre, tamano)
    sombras = pagina.evaluate("""[...document.querySelectorAll('body, body *')]
        .filter((e) => getComputedStyle(e).boxShadow !== 'none').map((e) => e.tagName.toLowerCase() + '.' + e.className)""")
    assert sombras == []


@pytest.mark.parametrize("nombre,tamano", CASOS, ids=IDS)
def test_no_hay_barra_horizontal(pagina, nombre, tamano):
    abrir(pagina, nombre, tamano)
    assert pagina.evaluate("document.documentElement.scrollWidth") <= TAMANOS[tamano][0]


@pytest.mark.parametrize("nombre", PUBLICAS)
def test_los_botones_son_controles_y_las_insignias_son_pildoras(pagina, nombre):
    abrir(pagina, nombre)
    radios = pagina.evaluate("""() => {
        const r = (sel) => [...document.querySelectorAll(sel)].map((e) => getComputedStyle(e).borderTopLeftRadius);
        const raiz = getComputedStyle(document.documentElement);
        return { botones: r('a.btn, button.btn'), insignias: r('.badge'), control: raiz.getPropertyValue('--r-control').trim(), pildora: raiz.getPropertyValue('--r-pildora').trim() }
    }""")
    assert set(radios["botones"]) <= {radios["control"]}
    assert set(radios["insignias"]) <= {radios["pildora"]}


# ---------- Los colores: neutro, o la paleta que ese navegador ya tiene ----------

def hexa_a_rgb(hexa):
    h = hexa.strip().lstrip("#")
    return "rgb({}, {}, {})".format(*(int(h[i:i + 2], 16) for i in (0, 2, 4)))


def token(pagina, variable, propiedad="backgroundColor"):
    return pagina.evaluate("""([v, p]) => { const e = document.createElement('i'); e.style[p] = `var(${v})`;
        document.body.appendChild(e); const c = getComputedStyle(e)[p]; e.remove(); return c }""", [variable, propiedad])


@pytest.mark.parametrize("nombre", PUBLICAS)
def test_sin_paleta_guardada_los_botones_y_el_fondo_son_los_del_estado_neutro(pagina, nombre):
    pagina.emulate_media(color_scheme="light")
    abrir(pagina, nombre)
    assert pagina.evaluate("document.documentElement.dataset.paleta") is None
    assert pagina.evaluate("getComputedStyle(document.body).backgroundColor") == token(pagina, "--c-fondo")
    boton = pagina.locator("a.btn-lumea, button.btn-lumea").first
    if boton.count():
        assert boton.evaluate("e => getComputedStyle(e).backgroundColor") == token(pagina, "--c-marca")


@pytest.mark.parametrize("paleta", ["laguna", "carnaval", "cosecha"])
@pytest.mark.parametrize("nombre", ["index.html", "crear-cuenta.html"])
def test_con_una_paleta_guardada_la_pagina_publica_la_sigue(pagina, nombre, paleta):
    pagina.emulate_media(color_scheme="light")
    abrir(pagina, nombre, paleta=paleta)
    assert pagina.evaluate("document.documentElement.dataset.paleta") == paleta
    assert pagina.evaluate("getComputedStyle(document.body).backgroundColor") == token(pagina, "--c-fondo")
    boton = pagina.locator("a.btn-lumea, button.btn-lumea").first
    assert boton.evaluate("e => getComputedStyle(e).backgroundColor") == token(pagina, "--c-marca")
    # el verde oscuro de Bootstrap («text-success-emphasis») ya es la tinta de marca de la paleta
    for e in pagina.locator(".text-success-emphasis").all():
        assert e.evaluate("e => getComputedStyle(e).color") == token(pagina, "--c-marca-tinta", "color")


def test_crear_cuenta_no_tiene_ningun_paso_nuevo(pagina):
    """Ese archivo es de Isabella: ni selector de colores ni tarjeta nueva (R4 lo exige)."""
    pagina.goto(f"{pagina.servidor}/crear-cuenta.html")
    assert pagina.locator("[data-selector-colores], #card-colores, script[src*=selector-colores]").count() == 0
    assert pagina.locator("script[src*=caras-checkin]").count() == 0
    assert pagina.locator("form#registroForm, form").count() >= 1


# ---------- Camino del cuidado, K0.5: R7 se conserva y se integra con la paleta, respetando el blanco ----------
# Modo claro: el fondo y las tarjetas son #FFFFFF, sin tinte de la paleta (que solo pone color en los acentos).
# «Claro» es la opción guardada; «Como mi dispositivo» es no guardar nada y que el sistema esté en claro (prefers-color-scheme).
# Los adornos de Sara (hojas, formas y destellos de Lumen.png) vuelven al inicio y a la tarjeta de inicio de sesión,
# pintados de un color plano de la paleta con una opacidad baja.

BLANCO = "rgb(255, 255, 255)"
PALETAS_K05 = [None, "laguna", "neblina", "carnaval", "colibri", "cosecha"]        # None = el estado neutro
SUPERFICIES = "body, .navbar-lumea, .footer-lumea, .auth-card, .quote-box, .card:not([class*='bg-'])"


def preparar(pagina, nombre, paleta=None, modo=None, sistema="light", tamano="1280"):
    """modo: 'claro' | 'oscuro' | None (no guardar nada = «Como mi dispositivo»); sistema: el color-scheme del sistema."""
    pagina.emulate_media(color_scheme=sistema)
    if modo:
        pagina.add_init_script(f"localStorage.setItem('lumea-modo', '{modo}')")
    abrir(pagina, nombre, tamano, paleta)


def fondos(pagina):
    return pagina.eval_on_selector_all(SUPERFICIES, "es => es.filter(e => e.getBoundingClientRect().width > 0).map(e => [e.className || e.tagName, getComputedStyle(e).backgroundColor])")


@pytest.mark.parametrize("paleta", PALETAS_K05, ids=lambda p: p or "neutro")
@pytest.mark.parametrize("nombre", PUBLICAS)
def test_en_modo_claro_el_fondo_y_las_tarjetas_son_blancos_en_toda_paleta(pagina, nombre, paleta):
    preparar(pagina, nombre, paleta, modo="claro")
    lista = fondos(pagina)
    assert lista, "no se encontró ninguna superficie"
    assert [f for f in lista if f[1] != BLANCO] == []
    assert pagina.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--c-fondo').trim().toUpperCase()") == "#FFFFFF"


@pytest.mark.parametrize("paleta", [None, "carnaval"], ids=lambda p: p or "neutro")
@pytest.mark.parametrize("nombre", ["index.html", "iniciar-sesion.html", "crear-cuenta.html"])
def test_como_mi_dispositivo_con_el_sistema_en_claro_tambien_es_blanco(pagina, nombre, paleta):
    preparar(pagina, nombre, paleta, modo=None, sistema="light")
    assert pagina.evaluate("document.documentElement.dataset.modo") is None             # no hay opción guardada
    assert [f for f in fondos(pagina) if f[1] != BLANCO] == []


@pytest.mark.parametrize("paleta", [None, "neblina", "cosecha"], ids=lambda p: p or "neutro")
@pytest.mark.parametrize("nombre", ["index.html", "iniciar-sesion.html"])
def test_claro_guardado_es_blanco_aunque_el_sistema_este_en_oscuro(pagina, nombre, paleta):
    preparar(pagina, nombre, paleta, modo="claro", sistema="dark")
    assert [f for f in fondos(pagina) if f[1] != BLANCO] == []


@pytest.mark.parametrize("paleta", [None, "laguna", "colibri"], ids=lambda p: p or "neutro")
@pytest.mark.parametrize("nombre", ["index.html", "iniciar-sesion.html", "terminos.html"])
def test_como_mi_dispositivo_con_el_sistema_en_oscuro_sigue_la_paleta_oscura(pagina, nombre, paleta):
    preparar(pagina, nombre, paleta, modo=None, sistema="dark")
    fondo = pagina.evaluate("getComputedStyle(document.body).backgroundColor")
    assert fondo != BLANCO and fondo == token(pagina, "--c-fondo")
    assert pagina.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--c-fondo').trim().toUpperCase()") != "#FFFFFF"
    assert pagina.evaluate("getComputedStyle(document.querySelector('.auth-card, .card')).backgroundColor") != BLANCO


@pytest.mark.parametrize("paleta", [None, "carnaval"], ids=lambda p: p or "neutro")
@pytest.mark.parametrize("nombre", ["index.html", "iniciar-sesion.html"])
def test_oscuro_guardado_sigue_la_paleta_oscura_aunque_el_sistema_este_en_claro(pagina, nombre, paleta):
    preparar(pagina, nombre, paleta, modo="oscuro", sistema="light")
    fondo = pagina.evaluate("getComputedStyle(document.body).backgroundColor")
    assert fondo != BLANCO and fondo == token(pagina, "--c-fondo")


@pytest.mark.parametrize("paleta", ["laguna", "carnaval"])
def test_la_paleta_sigue_poniendo_el_color_en_los_acentos_aunque_el_fondo_sea_blanco(pagina, paleta):
    preparar(pagina, "index.html", paleta, modo="claro")
    boton = pagina.locator("a.btn-lumea, button.btn-lumea").first
    assert boton.evaluate("e => getComputedStyle(e).backgroundColor") == token(pagina, "--c-marca")
    assert token(pagina, "--c-marca") != BLANCO
    enlace = pagina.locator(".logo-brand, .text-success-emphasis").first
    assert enlace.evaluate("e => getComputedStyle(e).color") != "rgb(0, 0, 0)"


def test_la_piel_de_comparacion_de_sara_no_cambia(pagina):
    pagina.emulate_media(color_scheme="light")
    pagina.goto(f"{pagina.servidor}/index.html?piel=sara")
    assert pagina.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(248, 250, 248)"       # --lumea-bg-page de Sara


ADORNOS = [("index.html", ".hero-section"), ("iniciar-sesion.html", ".auth-container"), ("crear-cuenta.html", ".auth-container")]


def adorno(pagina, selector):
    return pagina.locator(selector).first.evaluate("""e => { const c = getComputedStyle(e, '::before');
        return { mascara: c.maskImage || c.webkitMaskImage, opacidad: parseFloat(c.opacity), color: c.backgroundColor,
                 z: c.zIndex, eventos: c.pointerEvents, posicion: c.position } }""")


@pytest.mark.parametrize("nombre,selector", ADORNOS)
def test_las_hojas_y_los_destellos_de_sara_vuelven_con_baja_opacidad(pagina, nombre, selector):
    preparar(pagina, nombre, "laguna", modo="claro")
    a = adorno(pagina, selector)
    assert "hojas-mascara.png" in a["mascara"]
    assert 0 < a["opacidad"] <= 0.25                                                   # si queda turbio en una paleta, se baja esto
    assert a["z"] == "-1" and a["eventos"] == "none" and a["posicion"] == "absolute"    # detrás del contenido y sin tapar nada
    # el fondo de la sección sigue siendo blanco: el color va solo en el adorno
    assert pagina.locator(selector).first.evaluate("e => getComputedStyle(e).backgroundColor") == BLANCO


@pytest.mark.parametrize("nombre,selector", ADORNOS)
def test_el_adorno_es_un_color_plano_de_la_paleta_y_cambia_con_ella(pagina, nombre, selector):
    colores = {}
    for paleta in ["laguna", "neblina", "carnaval", "cosecha"]:
        preparar(pagina, nombre, paleta, modo="claro")
        a = adorno(pagina, selector)
        assert a["color"] == token(pagina, "--c-marca-tinta"), paleta                      # un token de la paleta, sin mezclas
        colores[paleta] = a["color"]
    assert len(set(colores.values())) >= 3, colores                                     # cada paleta lo tiñe distinto


@pytest.mark.parametrize("nombre,selector", ADORNOS)
def test_en_oscuro_el_adorno_es_mas_suave_y_sigue_las_superficies_de_la_paleta(pagina, nombre, selector):
    preparar(pagina, nombre, "colibri", modo="claro")
    claro = adorno(pagina, selector)["opacidad"]
    pagina.evaluate("LumeaTema.ponerModo('oscuro')")                                   # como lo haría la persona (el script de arranque vuelve a poner «claro»)
    oscuro = adorno(pagina, selector)
    assert 0 < oscuro["opacidad"] < claro
    assert pagina.evaluate("getComputedStyle(document.body).backgroundColor") == token(pagina, "--c-fondo")


@pytest.mark.parametrize("nombre,tamano", [("index.html", "390"), ("iniciar-sesion.html", "390"), ("iniciar-sesion.html", "1280")])
def test_el_adorno_no_tapa_ni_desborda_nada(pagina, nombre, tamano):
    preparar(pagina, nombre, "carnaval", modo="claro", tamano=tamano)
    assert pagina.evaluate("document.documentElement.scrollWidth") <= TAMANOS[tamano][0]
    # el centro de cada botón y de cada campo sigue siendo suyo: nada del adorno queda encima
    tapados = pagina.evaluate("""() => [...document.querySelectorAll('main a.btn, main button, main input')]
        .filter(e => e.getBoundingClientRect().width > 0).filter(e => { const r = e.getBoundingClientRect();
            const arriba = document.elementFromPoint(r.left + r.width / 2, Math.min(r.top + r.height / 2, innerHeight - 1));
            return arriba && arriba !== e && !e.contains(arriba) && !arriba.contains(e) && e.getBoundingClientRect().top < innerHeight }).length""")
    assert tapados == 0


def test_la_mascara_de_las_hojas_es_un_png_con_transparencia_y_liviano():
    import struct
    datos = (RAIZ / "img" / "hojas-mascara.png").read_bytes()
    assert datos[:8] == b"\x89PNG\r\n\x1a\n"
    ancho, alto, profundidad, tipo = struct.unpack(">IIBB", datos[16:26])
    assert (ancho, alto) == (1152, 768) and tipo == 6                                    # RGBA: el alpha es la máscara
    assert len(datos) < 300_000                                                          # liviana: se carga en la página de inicio
    assert (RAIZ / "herramientas" / "hojas_mascara.py").exists()                         # y sale de Lumen.png con esta herramienta


@pytest.mark.parametrize("nombre", ["index.html", "iniciar-sesion.html"])
def test_los_textos_de_isabella_siguen_igual_con_los_adornos(pagina, nombre):
    """El adorno es un ::before con `content: ""`: no agrega ni quita texto a la página."""
    preparar(pagina, nombre, "laguna", modo="claro")
    assert pagina.evaluate("getComputedStyle(document.querySelector('.hero-section, .auth-container'), '::before').content") in ('""', "''")
