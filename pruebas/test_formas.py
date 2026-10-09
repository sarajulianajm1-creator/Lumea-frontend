"""formas.css (P4): la forma decorativa de una tarjeta.

El texto cumple 4,5:1 sobre el fondo de la tarjeta y sobre la forma, en las 5 paletas y el estado neutro, en los dos modos.
(axe no puede medir un pseudoelemento, así que se mide con los colores calculados.)
"""
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
PALETAS = ["laguna", "neblina", "carnaval", "colibri", "cosecha", None]
MODOS = ["claro", "oscuro"]
ROLES = ["comida", "marca", "logro", "emocion", "mision"]
FORMAS = ["sol", "luna", "estrella", "gota", "hoja", "flor"]


def luminancia(c):
    def canal(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c
    return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def a_rgb(texto):
    """'rgb(1, 2, 3)' o 'color(srgb 0.1 0.2 0.3)' (lo que devuelve color-mix) → (r, g, b) de 0 a 255."""
    n = [float(x) for x in re.findall(r"[\d.]+", texto)]
    return tuple(n[:3]) if texto.startswith("rgb") else tuple(v * 255 for v in n[:3])


MEDIR = """(rol) => {
  const d = document.createElement('div');
  d.className = `con-forma con-forma--${rol} con-forma--hoja`;
  document.body.appendChild(d);
  const fondo = getComputedStyle(d).backgroundColor, forma = getComputedStyle(d, '::after').backgroundColor;
  const raiz = getComputedStyle(document.documentElement);
  const r = { fondo, forma, tinta: raiz.getPropertyValue('--c-tinta').trim(), suave: raiz.getPropertyValue('--c-tinta-suave').trim() };
  d.remove();
  return r;
}"""


@pytest.mark.parametrize("paleta", PALETAS)
@pytest.mark.parametrize("modo", MODOS)
def test_el_texto_cumple_4_5_sobre_el_fondo_y_sobre_la_forma(pagina, paleta, modo):
    guardar = f"localStorage.setItem('lumea-paleta', '{paleta}'); " if paleta else ""
    pagina.add_init_script(guardar + f"localStorage.setItem('lumea-modo', '{modo}')")
    pagina.goto(f"{pagina.servidor}/mis-registros.html")
    pagina.wait_for_load_state("networkidle")
    for rol in ROLES:
        m = pagina.evaluate(MEDIR, rol)
        tinta = a_rgb(pagina.evaluate("(c) => { const e = document.createElement('i'); e.style.color = c; document.body.appendChild(e); const r = getComputedStyle(e).color; e.remove(); return r }", m["tinta"]))
        suave = a_rgb(pagina.evaluate("(c) => { const e = document.createElement('i'); e.style.color = c; document.body.appendChild(e); const r = getComputedStyle(e).color; e.remove(); return r }", m["suave"]))
        for nombre, texto in (("tinta", tinta), ("tinta-suave", suave)):
            for sobre, color in (("el fondo", m["fondo"]), ("la forma", m["forma"])):
                c = contraste(texto, a_rgb(color))
                assert c >= 4.5, f"{rol} {paleta or 'neutro'} {modo}: {nombre} sobre {sobre} da {c:.2f}:1"


def test_las_seis_formas_existen_son_de_un_solo_trazado_y_originales():
    for nombre in FORMAS:
        svg = (RAIZ / "img" / "formas" / f"{nombre}.svg").read_text(encoding="utf-8")
        assert svg.count("<path") == 1 and "<image" not in svg and "href" not in svg           # de un solo trazado, sin imágenes de afuera
        assert f'url("../img/formas/{nombre}.svg")' in (RAIZ / "estilos" / "formas.css").read_text(encoding="utf-8")


def test_la_forma_es_decorativa_no_recibe_toques_ni_tiene_texto(pagina):
    pagina.goto(f"{pagina.servidor}/mis-registros.html")
    datos = pagina.evaluate("""() => { const d = document.createElement('div'); d.className = 'con-forma con-forma--logro con-forma--gota'; document.body.appendChild(d);
        const c = getComputedStyle(d, '::after'); const r = [c.pointerEvents, c.content, c.zIndex, getComputedStyle(d).overflow, getComputedStyle(d).isolation, getComputedStyle(d).position]; d.remove(); return r }""")
    assert datos == ["none", '""', "-1", "hidden", "isolate", "relative"]


def test_con_colores_forzados_la_forma_no_se_dibuja():
    css = re.sub(r"/\*.*?\*/", "", (RAIZ / "estilos" / "formas.css").read_text(encoding="utf-8"), flags=re.S)
    bloque = css[css.index("@media (forced-colors: active)"):]
    assert "display: none" in bloque and ".con-forma::after" in bloque


def test_la_forma_va_recortada_por_el_borde_de_la_tarjeta(pagina):
    pagina.goto(f"{pagina.servidor}/mis-registros.html")
    sobresale = pagina.evaluate("""() => { const d = document.createElement('div'); d.className = 'con-forma con-forma--comida con-forma--sol'; d.style.cssText = 'width:300px;height:200px'; document.body.appendChild(d);
        const c = getComputedStyle(d, '::after'); const r = [parseFloat(c.right) < 0, parseFloat(c.bottom) < 0, c.transform !== 'none']; d.remove(); return r }""")
    assert sobresale == [True, True, True]                                                   # sale un poco del borde, girada
