"""P10 · 2: un rol de color por tarjeta (60-30-10), el botón principal en --c-marca-tinta y los mensajes con el fondo de su sentido."""
import re

import pytest

from conftest import cargar_respuesta

PALETAS = ["laguna", "neblina", "carnaval", "colibri", "cosecha", None]
MODOS = ["claro", "oscuro"]


def luminancia(c):
    def canal(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * canal(c[0]) + 0.7152 * canal(c[1]) + 0.0722 * canal(c[2])


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def a_rgb(texto):
    n = [float(x) for x in re.findall(r"[\d.]+", texto)]
    return tuple(n[:3]) if texto.startswith("rgb") else tuple(v * 255 for v in n[:3])


def abrir_inicio(pagina, backend, ancho=1280):
    pagina.set_viewport_size({"width": ancho, "height": 900})
    pagina.goto(f"{pagina.servidor}/index-ingresado.html")
    pagina.locator("#card-dato-dia").wait_for()


# Resuelve cualquier color CSS (var(), color-mix) a «rgb(...)»
RESOLVER = """(c) => { const e = document.createElement('i'); e.style.color = c; document.body.appendChild(e); const r = getComputedStyle(e).color; e.remove(); return r }"""


def test_cada_tarjeta_de_inicio_lleva_un_rol_y_una_forma(pagina, backend):
    abrir_inicio(pagina, backend)
    clases = lambda sel: pagina.locator(sel).get_attribute("class")
    assert "con-forma--logro" in clases("section.inicio__dia") and "con-forma--sol" in clases("section.inicio__dia")
    assert "con-forma--emocion" in clases("#card-checkin-inicio") and "con-forma--luna" in clases("#card-checkin-inicio")


@pytest.mark.parametrize("ancho", [390, 1280])
def test_nunca_dos_tarjetas_vecinas_con_el_mismo_rol(pagina, backend, ancho):
    abrir_inicio(pagina, backend, ancho)
    roles = pagina.evaluate("""() => [...document.querySelectorAll('main .tarjeta:not(#card-colores)')].filter(e => e.offsetParent !== null).map(e => {
        const m = e.className.match(/con-forma--(comida|marca|logro|emocion|mision)/); return m ? m[1] : 'neutro' })""")
    assert len(roles) >= 4
    for a, b in zip(roles, roles[1:]):
        assert a == b == "neutro" or a != b, roles                              # dos neutras seguidas no son «un rol repetido»


def test_las_tarjetas_de_color_no_llevan_degradado_ni_sombra(pagina, backend):
    abrir_inicio(pagina, backend)
    for sel in ("section.inicio__dia", "#card-checkin-inicio", "#card-dato-dia"):
        e = pagina.locator(sel).evaluate("e => { const c = getComputedStyle(e); return [c.backgroundImage, c.boxShadow] }")
        assert e == ["none", "none"], (sel, e)


@pytest.mark.parametrize("paleta", PALETAS)
@pytest.mark.parametrize("modo", MODOS)
def test_el_boton_principal_es_marca_tinta_con_contraste_de_4_5_en_todas_las_paletas(pagina, backend, paleta, modo):
    guardar = f"localStorage.setItem('lumea-paleta', '{paleta}'); " if paleta else ""
    pagina.add_init_script(guardar + f"localStorage.setItem('lumea-modo', '{modo}')")
    for ancho, selector in ((1280, "[data-accion-principal]"), (390, ".nav-app__enlace--registrar")):
        abrir_inicio(pagina, backend, ancho)
        m = pagina.locator(selector).first.evaluate("e => { const c = getComputedStyle(e); return [c.backgroundColor, c.color] }")
        tinta = pagina.evaluate("() => getComputedStyle(document.documentElement).getPropertyValue('--c-marca-tinta').trim()")
        assert a_rgb(m[0]) == a_rgb(pagina.evaluate(RESOLVER, tinta)), (selector, m, tinta)
        assert contraste(a_rgb(m[0]), a_rgb(m[1])) >= 4.5, (paleta, modo, selector, m)


def test_los_mensajes_toman_el_fondo_suave_de_su_sentido(pagina, backend):
    abrir_inicio(pagina, backend)
    r = pagina.evaluate("""() => {
        const medir = (clase, atributos) => { const e = document.createElement('div'); e.className = clase; Object.entries(atributos || {}).forEach(([k, v]) => e.setAttribute(k, v));
            document.body.appendChild(e); const c = getComputedStyle(e); const x = [c.backgroundColor, c.backgroundImage, c.boxShadow]; e.remove(); return x };
        const suave = (v) => { const e = document.createElement('i'); e.style.backgroundColor = `var(${v})`; document.body.appendChild(e); const c = getComputedStyle(e).backgroundColor; e.remove(); return c };
        return { error: medir('estado-pantalla', { role: 'alert' }), exito: medir('inicio__confirmacion'), bienvenida: medir('card-bienvenida-calida'),
                 errorSuave: suave('--c-error-suave'), logroSuave: suave('--c-logro-suave') } }""")
    assert r["error"][0] == r["errorSuave"] and r["exito"][0] == r["logroSuave"] and r["bienvenida"][0] == r["logroSuave"]
    assert all(x[1:] == ["none", "none"] for x in (r["error"], r["exito"], r["bienvenida"]))


def test_marca_md_anota_la_regla_de_un_rol_por_tarjeta():
    from pathlib import Path
    texto = (Path(__file__).resolve().parent.parent / "MARCA.md").read_text()
    assert "Un rol de color por tarjeta" in texto and "Nunca dos tarjetas vecinas con el mismo rol" in texto
