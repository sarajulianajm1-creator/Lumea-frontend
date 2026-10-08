"""Capturas de cada página en 5 paletas x claro/oscuro, más el estado neutro (y con ?piel=sara).

No corre por defecto:  pytest pruebas -m capturas
Deja las imágenes en pruebas/capturas/ y un resumen de contraste (axe-core,
regla color-contrast) en pruebas/capturas/contraste.txt.
Las páginas de ESTRICTAS no pueden tener ningún error de contraste.
"""
from pathlib import Path

import pytest
from axe_playwright_python.sync_playwright import Axe

from test_humo import PAGINAS, VACIAS

CARPETA = Path(__file__).resolve().parent / "capturas"
PALETAS = ["laguna", "neblina", "carnaval", "colibri", "cosecha", None]      # None = el estado neutro: nadie ha elegido paleta
MODOS = ["claro", "oscuro"]
ESTRICTAS = {"progreso.html", "avatar.html"}      # pantallas nuevas: 0 errores de contraste

pytestmark = pytest.mark.capturas
_resumen = []


# Avatar tiene tres pestañas y solo se ve una a la vez: se mide cada una
ANCLAS = {"avatar.html": ["", "#armario", "#calcomanias"]}


def _combinaciones():
    for nombre in PAGINAS:
        for ancla in ANCLAS.get(nombre, [""]):
            for paleta in PALETAS:
                for modo in MODOS:
                    yield nombre, paleta, modo, False, ancla
            yield nombre, "laguna", "claro", True, ancla          # el diseño original de Sara


@pytest.mark.parametrize("nombre,paleta,modo,sara,ancla", list(_combinaciones()))
def test_captura(pagina, nombre, paleta, modo, sara, ancla):
    if nombre in VACIAS:
        pytest.skip(f"página vacía: {VACIAS[nombre]}")
    # sin paleta guardada se ve el estado neutro (ninguna paleta es predeterminada)
    guardar_paleta = f"localStorage.setItem('lumea-paleta', '{paleta}'); " if paleta else ""
    pagina.add_init_script(guardar_paleta + f"localStorage.setItem('lumea-modo', '{modo}')")
    pagina.goto(f"{pagina.servidor}/{nombre}" + ("?piel=sara" if sara else "") + ancla)
    pagina.wait_for_load_state("networkidle")
    etiqueta = ("sara" if sara else f"{paleta or 'neutro'}-{modo}") + (f"-{ancla[1:]}" if ancla else "")
    CARPETA.mkdir(exist_ok=True)
    pagina.screenshot(path=str(CARPETA / f"{nombre[:-5]}__{etiqueta}.png"), full_page=True)

    resultado = Axe().run(pagina, options={"runOnly": ["color-contrast"]})
    errores = resultado.response["violations"]
    nodos = sum(len(v["nodes"]) for v in errores)
    _resumen.append(f"{nombre:26} {etiqueta:30} {nodos} elementos con contraste bajo")
    if nombre in ESTRICTAS and not sara:
        assert nodos == 0, f"{nombre} ({etiqueta}): {nodos} errores de contraste"


@pytest.fixture(scope="module", autouse=True)
def _guardar_resumen():
    yield
    if _resumen:
        CARPETA.mkdir(exist_ok=True)
        (CARPETA / "contraste.txt").write_text("\n".join(sorted(_resumen)) + "\n", encoding="utf-8")
