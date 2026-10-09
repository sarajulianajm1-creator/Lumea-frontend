"""selector-colores.js (rediseño R4, sin caras desde el Camino del cuidado): dónde cada persona elige sus colores y su modo.

La tarjeta «Elige tus colores» de Inicio y la sección «Mis colores» de Avatar usan el mismo componente.
Ninguna paleta es predeterminada; la elección se aplica y se guarda al instante. Las caras del check-in ya no se
eligen aquí: son las de tu compañero (test_caras_checkin.py).
"""
import json
from pathlib import Path

import pytest

from conftest import cargar_respuesta

RAIZ = Path(__file__).resolve().parent.parent
TOKENS = json.loads((RAIZ / "estilos" / "tokens.json").read_text(encoding="utf-8"))["color"]
PALETAS = [("laguna", "Laguna"), ("neblina", "Neblina"), ("carnaval", "Carnaval"), ("colibri", "Colibrí"), ("cosecha", "Cosecha")]
ROLES = ["comida", "logro", "emocion", "mision", "duda"]
CORTO = "LumeaCelebrar.tiempos.xp = 300; LumeaCelebrar.tiempos.mision = 300; LumeaCelebrar.tiempos.salida = 60;"


def abrir(pagina, backend, nombre="index-ingresado.html", paleta=None, modo=None, listo=False, esquema="light"):
    """Una página con lo que la persona ya hubiera guardado (nada = no ha elegido nada)."""
    pagina.emulate_media(color_scheme=esquema)
    guardado = []
    if paleta: guardado.append(f"localStorage.setItem('lumea-paleta', '{paleta}')")
    if modo: guardado.append(f"localStorage.setItem('lumea-modo', '{modo}')")
    if listo: guardado.append("localStorage.setItem('lumea-colores-listo', '1')")
    if guardado:
        pagina.add_init_script(";".join(guardado))
    pagina.goto(f"{pagina.servidor}/{nombre}")
    pagina.wait_for_load_state("networkidle")


def rgb(hexa):
    h = hexa.lstrip("#")
    return "rgb({}, {}, {})".format(*(int(h[i:i + 2], 16) for i in (0, 2, 4)))


def tarjeta(pagina):
    return pagina.locator("#card-colores")


# ---------- Cuándo aparece la tarjeta de Inicio ----------

def test_sin_nada_elegido_la_tarjeta_aparece_arriba(pagina, backend):
    abrir(pagina, backend)
    assert tarjeta(pagina).is_visible()
    assert tarjeta(pagina).locator("h2").inner_text() == "Elige tus colores"
    # arriba: antes de «Tu día» y del check-in
    cajas = pagina.evaluate("""() => ['card-colores', 'titulo-dia'].map(id => document.getElementById(id).getBoundingClientRect().top)""")
    assert cajas[0] < cajas[1]


def test_con_la_paleta_ya_elegida_no_aparece(pagina, backend):
    abrir(pagina, backend, paleta="carnaval")
    assert not tarjeta(pagina).is_visible()                                           # antes también pedía el set de caras


def test_una_eleccion_vieja_de_caras_no_hace_que_aparezca_ni_que_desaparezca(pagina, backend):
    pagina.add_init_script("localStorage.setItem('lumea-caras', 'gaze')")
    abrir(pagina, backend)
    assert tarjeta(pagina).is_visible()                                               # sin paleta, aparece aunque hubiera set


def test_el_modo_guardado_no_cuenta_como_haber_elegido(pagina, backend):
    abrir(pagina, backend, modo="oscuro")
    assert tarjeta(pagina).is_visible()


def test_no_es_un_dialogo_y_no_impide_registrar_una_comida(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("dialog[open]").count() == 0
    assert tarjeta(pagina).get_attribute("aria-modal") is None and tarjeta(pagina).get_attribute("role") is None
    pagina.get_by_role("link", name="Registrar comida").click()                       # el resto de la pantalla se puede usar
    pagina.wait_for_url("**/alimentos.html")


def test_una_vez_abierta_se_queda_abierta_aunque_elija_la_paleta(pagina, backend):
    abrir(pagina, backend)
    tarjeta(pagina).get_by_label("Neblina").check(force=True)
    assert tarjeta(pagina).is_visible()                                               # se cierra con «Listo» o «Ahora no»


# ---------- Listo y Ahora no ----------

def test_listo_cierra_la_tarjeta_y_no_vuelve_a_aparecer(pagina, backend):
    abrir(pagina, backend)
    tarjeta(pagina).get_by_label("Neblina").check(force=True)
    tarjeta(pagina).get_by_role("button", name="Listo").click()
    assert not tarjeta(pagina).is_visible()
    assert pagina.evaluate("document.activeElement.hasAttribute('data-accion-principal')")      # el foco pasa a la acción principal
    pagina.reload()
    pagina.wait_for_load_state("networkidle")
    assert not tarjeta(pagina).is_visible()                                           # «Listo» se recuerda en el navegador


def test_ahora_no_la_esconde_solo_durante_esta_sesion(pagina, backend):
    abrir(pagina, backend)
    tarjeta(pagina).get_by_role("button", name="Ahora no").click()
    assert not tarjeta(pagina).is_visible()
    assert pagina.evaluate("localStorage.getItem('lumea-colores-listo')") is None      # no se recuerda para siempre
    pagina.reload()
    pagina.wait_for_load_state("networkidle")
    assert not tarjeta(pagina).is_visible()                                           # sigue escondida en la misma sesión
    pagina.evaluate("sessionStorage.removeItem('lumea-colores-ahora-no')")            # una sesión nueva
    pagina.reload()
    pagina.wait_for_load_state("networkidle")
    assert tarjeta(pagina).is_visible()


def test_listo_y_ahora_no_no_son_botones_rellenos(pagina, backend):
    abrir(pagina, backend)
    rellenos = pagina.locator("main .boton:visible:not(.boton--secundario):not(.boton--fantasma)")
    assert rellenos.count() == 1 and rellenos.inner_text().strip() == "Registrar comida"      # una sola acción principal


# ---------- Los dos grupos de opciones ----------

def test_hay_dos_radiogroup_sin_el_grupo_de_caras(pagina, backend):
    abrir(pagina, backend)
    grupos = tarjeta(pagina).locator("[role=radiogroup]")
    assert grupos.count() == 2
    assert [g.locator("legend").inner_text() for g in grupos.all()] == ["Colores", "Modo"]
    assert [l.inner_text().strip() for l in grupos.nth(0).locator("label").all()] == [n for _, n in PALETAS]
    assert [l.inner_text().strip() for l in grupos.nth(1).locator("label").all()] == ["Claro", "Oscuro", "Como mi dispositivo"]
    assert tarjeta(pagina).locator("input[type=radio][value=neutro]").count() == 0     # el estado neutro no aparece en el selector
    texto_tarjeta = tarjeta(pagina).inner_text()
    for ya_no in ("Caras", "Miradas", "Gestos", "caras"):
        assert ya_no not in texto_tarjeta
    assert tarjeta(pagina).locator("img").count() == 0                                 # sin caras de muestra: no sale ninguna imagen


def test_sin_nada_elegido_ninguna_paleta_esta_marcada(pagina, backend):
    abrir(pagina, backend)
    assert tarjeta(pagina).locator("input[name$=-paleta]:checked").count() == 0
    assert tarjeta(pagina).locator("input[name$=-caras]").count() == 0
    assert tarjeta(pagina).locator("input[name$=-modo]:checked").get_attribute("value") == "auto"     # «como mi dispositivo»


@pytest.mark.parametrize("paleta,nombre", PALETAS)
def test_cada_tira_muestra_los_colores_de_rol_de_su_paleta(pagina, backend, paleta, nombre):
    abrir(pagina, backend)
    tira = tarjeta(pagina).locator(f".selector__tira[data-paleta={paleta}]")
    for rol in ROLES:
        color = tira.locator(f".selector__muestra--{rol}").evaluate("e => getComputedStyle(e).backgroundColor")
        assert color == rgb(TOKENS[paleta]["claro"][rol]["$value"]), f"{paleta}/{rol}"


def test_las_tiras_siguen_el_modo_de_ahora(pagina, backend):
    abrir(pagina, backend)
    pagina.evaluate("LumeaTema.ponerModo('oscuro')")
    for paleta, _ in PALETAS:
        color = tarjeta(pagina).locator(f".selector__tira[data-paleta={paleta}] .selector__muestra--comida").evaluate("e => getComputedStyle(e).backgroundColor")
        assert color == rgb(TOKENS[paleta]["oscuro"]["comida"]["$value"]), paleta


# ---------- Elegir aplica y guarda al instante ----------

@pytest.mark.parametrize("paleta,nombre", PALETAS)
def test_elegir_una_paleta_se_aplica_y_se_guarda_al_instante(pagina, backend, paleta, nombre):
    abrir(pagina, backend)
    tarjeta(pagina).get_by_label(nombre, exact=True).check(force=True)
    assert pagina.evaluate("document.documentElement.dataset.paleta") == paleta
    assert pagina.evaluate("localStorage.getItem('lumea-paleta')") == paleta
    fondo = pagina.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--c-fondo').trim()").upper()
    assert fondo == TOKENS[paleta]["claro"]["fondo"]["$value"].upper()


@pytest.mark.parametrize("modo,atributo", [("Claro", "claro"), ("Oscuro", "oscuro"), ("Como mi dispositivo", None)])
def test_elegir_el_modo_se_aplica_y_se_guarda(pagina, backend, modo, atributo):
    abrir(pagina, backend, modo="oscuro" if atributo is None else None)
    tarjeta(pagina).get_by_label(modo, exact=True).check(force=True)
    assert pagina.evaluate("document.documentElement.dataset.modo ?? null") == atributo
    assert pagina.evaluate("localStorage.getItem('lumea-modo')") == atributo


def test_elegir_una_paleta_no_cambia_las_caras_del_check_in_porque_son_del_companero(pagina, backend):
    abrir(pagina, backend)
    pagina.wait_for_function("document.querySelectorAll('.inicio__animo .animo-cara img').length === 5")
    antes = pagina.eval_on_selector_all(".inicio__animo .animo-cara img", "e => e.map(i => i.dataset.fuente)")
    tarjeta(pagina).get_by_label("Carnaval", exact=True).check(force=True)
    assert pagina.evaluate("document.documentElement.dataset.paleta") == "carnaval"
    despues = pagina.eval_on_selector_all(".inicio__animo .animo-cara img", "e => e.map(i => i.dataset.fuente)")
    assert antes == despues                                                            # el color del compañero es suyo, no de la paleta
    assert all("bodyColor=F6B73C" in s for s in despues)
    assert pagina.evaluate("localStorage.getItem('lumea-caras')") is None              # esa clave ya no existe


def test_con_el_teclado_las_flechas_cambian_de_opcion_y_se_aplican(pagina, backend):
    abrir(pagina, backend)
    primera = tarjeta(pagina).locator("input[name$=-paleta]").first
    primera.focus()
    pagina.keyboard.press("ArrowDown")                                                 # radio: la flecha elige la siguiente
    assert pagina.evaluate("LumeaTema.paletaActual()") in ("laguna", "neblina")
    pagina.keyboard.press("ArrowDown")
    assert pagina.evaluate("document.activeElement.name.endsWith('-paleta')")
    assert pagina.evaluate("LumeaTema.paletaActual()") is not None


def test_el_foco_se_ve_en_la_opcion_enfocada(pagina, backend):
    abrir(pagina, backend)
    pagina.evaluate("document.querySelector('#card-colores input[name$=-paleta]').focus()")
    pagina.keyboard.press("Shift+Tab")                                                 # el foco llega con el teclado: es :focus-visible
    pagina.keyboard.press("Tab")
    ancho = pagina.evaluate("""() => { const o = document.activeElement.closest('.selector__opcion'); return parseFloat(getComputedStyle(o).outlineWidth) }""")
    assert ancho >= 3


# ---------- Avatar: «Mis colores» ----------

def test_avatar_tiene_la_seccion_mis_colores_con_el_mismo_selector(pagina, backend):
    abrir(pagina, backend, nombre="avatar.html")
    seccion = pagina.locator("section[aria-labelledby=titulo-mis-colores]")
    assert seccion.locator("h2").inner_text() == "Mis colores"
    assert seccion.locator("[role=radiogroup]").count() == 2
    assert seccion.get_by_role("button").count() == 0                                  # sin «Listo» ni «Ahora no»: se cambia cuando sea


def test_en_avatar_se_cambia_la_paleta_cuando_sea_aunque_ya_haya_elegido(pagina, backend):
    abrir(pagina, backend, nombre="avatar.html", paleta="laguna")
    seccion = pagina.locator("section[aria-labelledby=titulo-mis-colores]")
    assert seccion.locator("input[name$=-paleta]:checked").get_attribute("value") == "laguna"
    seccion.get_by_label("Cosecha", exact=True).check(force=True)
    assert pagina.evaluate("localStorage.getItem('lumea-paleta')") == "cosecha"


def test_la_eleccion_hecha_en_inicio_se_ve_marcada_en_avatar(pagina, backend):
    abrir(pagina, backend)
    tarjeta(pagina).get_by_label("Colibrí", exact=True).check(force=True)
    tarjeta(pagina).get_by_label("Oscuro", exact=True).check(force=True)
    pagina.goto(f"{pagina.servidor}/avatar.html")
    seccion = pagina.locator("section[aria-labelledby=titulo-mis-colores]")
    assert seccion.locator("input[name$=-paleta]:checked").get_attribute("value") == "colibri"
    assert seccion.locator("input[name$=-modo]:checked").get_attribute("value") == "oscuro"
    assert pagina.evaluate("document.documentElement.dataset.modo") == "oscuro"


# ---------- Páginas públicas y Crear cuenta ----------

def test_crear_cuenta_no_tiene_ningun_paso_nuevo(pagina, backend):
    pagina.goto(f"{pagina.servidor}/crear-cuenta.html")
    assert pagina.locator("#card-colores, [data-selector-colores]").count() == 0
    assert "Elige tus colores" not in pagina.locator("body").inner_text()
