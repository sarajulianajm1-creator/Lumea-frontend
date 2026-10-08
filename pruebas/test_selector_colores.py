"""selector-colores.js (rediseño R4): dónde cada persona elige sus colores, su modo y sus caras.

La tarjeta «Elige tus colores y tus caras» de Inicio y la sección «Mis colores y caras» de Avatar usan el mismo
componente. Ninguna paleta ni set de caras es predeterminado; la elección se aplica y se guarda al instante.
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


def abrir(pagina, backend, nombre="index-ingresado.html", paleta=None, caras=None, modo=None, listo=False, esquema="light"):
    """Una página con lo que la persona ya hubiera guardado (nada = no ha elegido nada)."""
    pagina.emulate_media(color_scheme=esquema)
    guardado = []
    if paleta: guardado.append(f"localStorage.setItem('lumea-paleta', '{paleta}')")
    if caras: guardado.append(f"localStorage.setItem('lumea-caras', '{caras}')")
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
    assert tarjeta(pagina).locator("h2").inner_text() == "Elige tus colores y tus caras"
    # arriba: antes de «Tu día» y del check-in
    cajas = pagina.evaluate("""() => ['card-colores', 'titulo-dia'].map(id => document.getElementById(id).getBoundingClientRect().top)""")
    assert cajas[0] < cajas[1]


@pytest.mark.parametrize("paleta,caras", [("neblina", None), (None, "gaze")])
def test_mientras_falte_la_paleta_o_las_caras_la_tarjeta_aparece(pagina, backend, paleta, caras):
    abrir(pagina, backend, paleta=paleta, caras=caras)
    assert tarjeta(pagina).is_visible()


def test_con_la_paleta_y_las_caras_ya_elegidas_no_aparece(pagina, backend):
    abrir(pagina, backend, paleta="carnaval", caras="moods")
    assert not tarjeta(pagina).is_visible()


def test_el_modo_guardado_no_cuenta_como_haber_elegido(pagina, backend):
    abrir(pagina, backend, modo="oscuro")
    assert tarjeta(pagina).is_visible()


def test_no_es_un_dialogo_y_no_impide_registrar_una_comida(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("dialog[open]").count() == 0
    assert tarjeta(pagina).get_attribute("aria-modal") is None and tarjeta(pagina).get_attribute("role") is None
    pagina.get_by_role("link", name="Registrar comida").click()                       # el resto de la pantalla se puede usar
    pagina.wait_for_url("**/alimentos.html")


def test_una_vez_abierta_se_queda_abierta_aunque_elija_las_dos_cosas(pagina, backend):
    abrir(pagina, backend)
    tarjeta(pagina).get_by_label("Neblina").check(force=True)
    tarjeta(pagina).get_by_label("Miradas").check(force=True)
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
    assert not tarjeta(pagina).is_visible()                                           # aunque todavía falten las caras


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


# ---------- Los tres grupos de opciones ----------

def test_hay_tres_radiogroup_con_sus_opciones(pagina, backend):
    abrir(pagina, backend)
    grupos = tarjeta(pagina).locator("[role=radiogroup]")
    assert grupos.count() == 3
    assert [g.locator("legend").inner_text() for g in grupos.all()] == ["Colores", "Modo", "Caras"]
    assert [l.inner_text().strip() for l in grupos.nth(0).locator("label").all()] == [n for _, n in PALETAS]
    assert [l.inner_text().strip() for l in grupos.nth(1).locator("label").all()] == ["Claro", "Oscuro", "Como mi dispositivo"]
    assert [l.inner_text().strip() for l in grupos.nth(2).locator("label").all()] == ["Miradas", "Gestos"]
    assert tarjeta(pagina).locator("input[type=radio][value=neutro]").count() == 0     # el estado neutro no aparece en el selector


def test_sin_nada_elegido_ninguna_paleta_ni_caras_estan_marcadas(pagina, backend):
    abrir(pagina, backend)
    assert tarjeta(pagina).locator("input[name$=-paleta]:checked").count() == 0
    assert tarjeta(pagina).locator("input[name$=-caras]:checked").count() == 0
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


@pytest.mark.parametrize("nombre,set_", [("Miradas", "gaze"), ("Gestos", "moods")])
def test_elegir_el_set_de_caras_se_guarda_y_cambia_los_botones_del_check_in_al_instante(pagina, backend, nombre, set_):
    abrir(pagina, backend)
    assert pagina.locator(".inicio__animo .animo-cara img").count() == 0              # antes: solo la palabra
    tarjeta(pagina).get_by_label(nombre, exact=True).check(force=True)
    assert pagina.evaluate("localStorage.getItem('lumea-caras')") == set_
    pagina.wait_for_function("document.querySelectorAll('.inicio__animo .animo-cara img').length === 5")
    assert all(f"/10.x/{set_}/" in i.get_attribute("src") for i in pagina.locator(".inicio__animo .animo-cara img").all())


def test_al_elegir_paleta_las_caras_toman_su_color_de_emocion(pagina, backend):
    abrir(pagina, backend, caras="gaze")
    tarjeta(pagina).get_by_label("Carnaval", exact=True).check(force=True)
    esperado = TOKENS["carnaval"]["claro"]["emocion"]["$value"].lstrip("#").lower()
    pagina.wait_for_function(f"document.querySelector('.inicio__animo .animo-cara img').src.includes('bodyColor={esperado}')")
    # y las caras de muestra del propio selector también
    pagina.wait_for_function(f"document.querySelector('#card-colores .selector__cara img').src.includes('bodyColor={esperado}')")


def test_las_caras_de_muestra_son_cinco_por_set_y_van_quietas(pagina, backend):
    abrir(pagina, backend)
    for set_ in ("gaze", "moods"):
        imgs = tarjeta(pagina).locator(f".selector__caras[data-set={set_}] img")
        assert imgs.count() == 5
        for i in imgs.all():
            assert i.get_attribute("alt") == "" and "animationVariant=none" in i.get_attribute("src")


def test_sin_internet_en_el_selector_quedan_los_nombres(pagina, backend):
    abrir(pagina, backend)
    pagina.evaluate("document.querySelectorAll('#card-colores img').forEach(i => i.dispatchEvent(new Event('error')))")
    assert tarjeta(pagina).locator("img").count() == 0
    assert tarjeta(pagina).get_by_label("Miradas", exact=True).count() == 1           # la opción sigue ahí, con su nombre


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


# ---------- Avatar: «Mis colores y caras» ----------

def test_avatar_tiene_la_seccion_mis_colores_y_caras_con_el_mismo_selector(pagina, backend):
    abrir(pagina, backend, nombre="avatar.html")
    seccion = pagina.locator("section[aria-labelledby=titulo-mis-colores]")
    assert seccion.locator("h2").inner_text() == "Mis colores y caras"
    assert seccion.locator("[role=radiogroup]").count() == 3
    assert seccion.get_by_role("button").count() == 0                                  # sin «Listo» ni «Ahora no»: se cambia cuando sea


def test_en_avatar_se_cambia_la_paleta_cuando_sea_aunque_ya_haya_elegido(pagina, backend):
    abrir(pagina, backend, nombre="avatar.html", paleta="laguna", caras="gaze")
    seccion = pagina.locator("section[aria-labelledby=titulo-mis-colores]")
    assert seccion.locator("input[name$=-paleta]:checked").get_attribute("value") == "laguna"
    assert seccion.locator("input[name$=-caras]:checked").get_attribute("value") == "gaze"
    seccion.get_by_label("Cosecha", exact=True).check(force=True)
    seccion.get_by_label("Gestos", exact=True).check(force=True)
    assert pagina.evaluate("[localStorage.getItem('lumea-paleta'), localStorage.getItem('lumea-caras')]") == ["cosecha", "moods"]


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
