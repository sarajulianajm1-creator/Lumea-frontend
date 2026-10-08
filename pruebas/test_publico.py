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
