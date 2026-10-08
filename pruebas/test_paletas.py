"""Paletas (rediseño R4): ninguna es predeterminada; sin elegir, Lumea se ve en un estado neutro.

Dos partes:
  1. El generador (herramientas/generar_paletas.py): el estado neutro pasa las mismas pruebas de contraste y
     daltonismo, no tiene tono, conserva los colores de rol y va primero en el CSS; y los archivos
     generados (paletas.css, tokens.json y el informe) están al día con el script.
  2. En el navegador: sin paleta guardada se ve el neutro (no Laguna), elegir una la aplica, y el neutro no
     se puede «elegir».
"""
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "herramientas"))
import generar_paletas as g                                    # noqa: E402  (se importa sin correrlo: main() está protegido)

TOKENS = json.loads((RAIZ / "estilos" / "tokens.json").read_text(encoding="utf-8"))["color"]
ROLES = ("comida", "logro", "emocion", "mision", "duda")
CINCO = ["laguna", "neblina", "carnaval", "colibri", "cosecha"]


def croma(hx):
    """Cuánto «tono» tiene un color (croma en OKLab): 0 es gris puro."""
    _, a, b = g.lineal_a_oklab(*g.hex_a_lineal(hx))
    return math.hypot(a, b)


# ---------- El generador ----------

@pytest.mark.parametrize("modo", ["claro", "oscuro"])
def test_el_neutro_pasa_el_mismo_contraste_wcag_que_las_demas(modo):
    filas, fallas, _ = g.validar("neutro", modo, g.tema("neutro", modo))
    assert fallas == []
    assert len(filas) == len(g.validar("laguna", modo, g.tema("laguna", modo))[0])    # mide los mismos pares


@pytest.mark.parametrize("modo", ["claro", "oscuro"])
def test_el_neutro_separa_las_cinco_frutas_igual_que_laguna_en_daltonismo(modo):
    _, _, neutro = g.validar("neutro", modo, g.tema("neutro", modo))
    _, _, laguna = g.validar("laguna", modo, g.tema("laguna", modo))
    for tipo in ("normal", "protanopia", "deuteranopia", "tritanopia", "grises"):
        assert neutro[tipo][0] == pytest.approx(laguna[tipo][0])                       # mismas frutas, mismo orden de luz


@pytest.mark.parametrize("modo", ["claro", "oscuro"])
def test_las_superficies_y_el_texto_del_neutro_no_tienen_tono(modo):
    t = g.tema("neutro", modo)
    for nombre in ("fondo", "superficie", "superficie-2", "tinta", "tinta-suave", "borde", "borde-fuerte"):
        assert croma(t[nombre]) <= 0.006, f"{nombre} ({t[nombre]}) tiene tono"           # ni verde ni azul: croma <= 0,006


@pytest.mark.parametrize("modo", ["claro", "oscuro"])
def test_el_neutro_conserva_los_colores_de_rol_y_la_marca(modo):
    """Los colores de rol llevan significado (comida = aguacate, logro = maracuyá…): son los mismos de siempre,
    los de Laguna. Lo que cambia son las superficies y el texto, que pierden el tono."""
    neutro, laguna = TOKENS["neutro"][modo], TOKENS["laguna"][modo]
    for rol in ROLES:
        assert neutro[rol]["$value"] == laguna[rol]["$value"], rol                      # el relleno de cada rol
    for nombre in ("marca", "marca-hover", "sobre-marca", "marca-tinta", "foco"):         # el botón principal sigue en aguacate
        assert neutro[nombre]["$value"] == laguna[nombre]["$value"], nombre
    # los fondos suave y contenedor de cada rol siguen siendo de SU tono (no se vuelven grises)
    for rol in ROLES:
        for papel in ("suave", "contenedor"):
            assert croma(neutro[f"{rol}-{papel}"]["$value"]) > 0.01, f"{rol}-{papel} perdió su color"


def test_el_neutro_es_la_predeterminada_y_va_primero_en_el_css():
    css = (RAIZ / "estilos" / "paletas.css").read_text(encoding="utf-8")
    assert g.PREDETERMINADA == "neutro"
    assert css.count(":root,\n[data-paleta=") == 1 and ':root,\n[data-paleta="neutro"] {' in css
    posicion_neutro = css.index(':root,\n[data-paleta="neutro"]')
    for paleta in CINCO:
        # su regla [data-paleta="x"] tiene la misma especificidad que :root: si el neutro estuviera después, la taparía
        assert css.index(f'\n[data-paleta="{paleta}"] {{') > posicion_neutro, paleta
    assert ':root,\n[data-paleta="laguna"]' not in css                                  # Laguna ya no es la de :root


def test_los_archivos_generados_estan_al_dia_con_el_script(tmp_path):
    """paletas.css, tokens.json y el informe solo se cambian con el script: al correrlo no debe cambiar nada."""
    (tmp_path / "herramientas").mkdir()
    shutil.copy(RAIZ / "herramientas" / "generar_paletas.py", tmp_path / "herramientas" / "generar_paletas.py")
    resultado = subprocess.run([sys.executable, "herramientas/generar_paletas.py"], cwd=tmp_path, capture_output=True, text=True)
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr
    for archivo in ("estilos/paletas.css", "estilos/tokens.json", "docs/validacion-paletas.md"):
        assert (tmp_path / archivo).read_text(encoding="utf-8") == (RAIZ / archivo).read_text(encoding="utf-8"), \
            f"{archivo} no coincide con lo que genera el script: corre python3 herramientas/generar_paletas.py"


# ---------- En el navegador ----------

def valor(pagina, variable):
    return pagina.evaluate(f"getComputedStyle(document.documentElement).getPropertyValue('{variable}').trim()").upper()


def hex_de(paleta, modo, nombre):
    return TOKENS[paleta][modo][nombre]["$value"].upper()


@pytest.mark.parametrize("pagina_nombre", ["index-ingresado.html", "index.html", "progreso.html"])
@pytest.mark.parametrize("esquema,modo", [("light", "claro"), ("dark", "oscuro")])
def test_sin_paleta_guardada_se_ve_el_estado_neutro_y_no_laguna(pagina, pagina_nombre, esquema, modo):
    pagina.emulate_media(color_scheme=esquema)
    pagina.goto(f"{pagina.servidor}/{pagina_nombre}")
    assert pagina.evaluate("document.documentElement.dataset.paleta") is None
    assert pagina.evaluate("LumeaTema.paletaActual()") is None
    for nombre in ("fondo", "superficie", "tinta", "marca"):
        esperado = hex_de("neutro", modo, nombre)
        if pagina_nombre == "index.html" and modo == "claro" and nombre in ("fondo", "superficie"):
            esperado = "#FFFFFF"        # K0.5: las páginas públicas en modo claro son blancas (publico.css); el resto sigue al neutro
        assert valor(pagina, f"--c-{nombre}") == esperado
    assert valor(pagina, "--c-fondo") != hex_de("laguna", modo, "fondo")


@pytest.mark.parametrize("paleta", CINCO)
def test_elegir_una_paleta_aplica_la_suya_y_se_guarda(pagina, paleta):
    pagina.emulate_media(color_scheme="light")
    pagina.goto(f"{pagina.servidor}/index-ingresado.html")
    pagina.evaluate(f"LumeaTema.ponerPaleta('{paleta}')")
    assert pagina.evaluate("document.documentElement.dataset.paleta") == paleta
    assert pagina.evaluate("LumeaTema.paletaActual()") == paleta
    assert valor(pagina, "--c-fondo") == hex_de(paleta, "claro", "fondo")
    assert pagina.evaluate("localStorage.getItem('lumea-paleta')") == paleta


@pytest.mark.parametrize("paleta", CINCO)
def test_una_paleta_guardada_se_aplica_tambien_en_las_paginas_publicas(pagina, paleta):
    pagina.emulate_media(color_scheme="light")
    pagina.add_init_script(f"localStorage.setItem('lumea-paleta', '{paleta}')")
    pagina.goto(f"{pagina.servidor}/index.html")
    # K0.5: en claro el fondo de las públicas es blanco, así que la paleta se comprueba por sus acentos y su tinta
    assert valor(pagina, "--c-fondo") == "#FFFFFF"
    for nombre in ("marca", "marca-suave", "marca-tinta", "tinta", "borde"):
        assert valor(pagina, f"--c-{nombre}") == hex_de(paleta, "claro", nombre), nombre


def test_el_estado_neutro_no_se_puede_elegir(pagina):
    pagina.goto(f"{pagina.servidor}/index-ingresado.html")
    assert "neutro" not in pagina.evaluate("LumeaTema.PALETAS")
    pagina.evaluate("LumeaTema.ponerPaleta('neutro')")
    assert pagina.evaluate("LumeaTema.paletaActual()") is None
    assert pagina.evaluate("localStorage.getItem('lumea-paleta')") is None


def test_un_nombre_viejo_de_paleta_guardado_sigue_funcionando(pagina):
    pagina.add_init_script("localStorage.setItem('lumea-paleta', 'mopa')")                # Mopa-mopa pasó a Colibrí
    pagina.goto(f"{pagina.servidor}/index-ingresado.html")
    assert pagina.evaluate("LumeaTema.paletaActual()") == "colibri"


@pytest.mark.parametrize("guardado,esperado", [(None, "auto"), ("claro", "claro"), ("oscuro", "oscuro"), ("raro", "auto")])
def test_el_modo_guardado_es_claro_oscuro_o_como_mi_dispositivo(pagina, guardado, esperado):
    if guardado:
        pagina.add_init_script(f"localStorage.setItem('lumea-modo', '{guardado}')")
    pagina.goto(f"{pagina.servidor}/index-ingresado.html")
    assert pagina.evaluate("LumeaTema.modoGuardado()") == esperado
