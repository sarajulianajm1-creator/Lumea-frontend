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
ESTRICTAS = {"progreso.html", "avatar.html",       # pantallas nuevas: 0 errores de contraste
             # K0.5: las seis públicas también (con el fondo blanco y los adornos de las hojas, en las 5 paletas + neutro × claro/oscuro)
             "index.html", "conocenos.html", "guialumea.html", "crear-cuenta.html", "iniciar-sesion.html", "terminos.html"}

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


# ---------- Registrar con un resultado (R5): «IA segura» e «IA duda» ----------
# El contenedor del rol «duda» y el texto encima, y los sellos, se miden con la respuesta puesta (la página vacía no los muestra).
# K0.5 suma «consejos»: los bloques de consejo con el dato curioso largo cortado y con «Leer más» (y el mismo, abierto).

@pytest.mark.parametrize("estado", ["segura", "duda", "consejos", "consejos-abierto"])
@pytest.mark.parametrize("paleta", PALETAS)
@pytest.mark.parametrize("modo", MODOS)
def test_resultado_de_la_camara_sin_errores_de_contraste(pagina, backend, foto, estado, paleta, modo):
    from conftest import cargar_respuesta
    if estado.startswith("consejos"):
        respuesta = cargar_respuesta("predecir_bandeja_paisa")
    else:
        respuesta = (cargar_respuesta("predecir_duda") if estado == "duda"
                     else cargar_respuesta("predecir_segura") | {"sellos_advertencia": ["azucares", "grasas_saturadas"]})
    backend.poner("POST", "/predecir", respuesta)
    guardar_paleta = f"localStorage.setItem('lumea-paleta', '{paleta}'); " if paleta else ""
    pagina.add_init_script(guardar_paleta + f"localStorage.setItem('lumea-modo', '{modo}')")
    pagina.goto(f"{pagina.servidor}/alimentos.html")
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#resultado[data-estado]:not([data-estado=''])").wait_for()
    pagina.wait_for_timeout(300)
    if estado == "consejos-abierto":
        pagina.get_by_role("button", name="Leer más").click()
    CARPETA.mkdir(exist_ok=True)
    pagina.screenshot(path=str(CARPETA / f"alimentos-{estado}__{paleta or 'neutro'}-{modo}.png"), full_page=True)
    errores = Axe().run(pagina, options={"runOnly": ["color-contrast"]}).response["violations"]
    assert sum(len(v["nodes"]) for v in errores) == 0, f"{estado} ({paleta or 'neutro'}-{modo}): contraste bajo"
