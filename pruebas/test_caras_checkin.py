"""caras-checkin.js (rediseño R3): las caras de los cinco botones del check-in, en Inicio y en Ánimo.

Cada persona elige su set de caras («gaze» o «moods»), igual que su paleta; ninguno es predeterminado.
Se prueban los tres estados: sin elección (solo la palabra), con «gaze» y con «moods». En los tres:
la dirección sin datos personales, alt="", aria-pressed, el respaldo sin internet y el redibujo
con «lumea:tema» y «lumea:caras». (Las imágenes no salen a internet: conftest.py las reemplaza.)
"""
from urllib.parse import parse_qs, urlparse

import pytest

from conftest import cargar_respuesta

PAGINAS = ["index-ingresado.html", "emociones.html"]
SETS = [None, "gaze", "moods"]
ESTADOS = ["Muy mal", "Mal", "Neutral", "Bien", "Muy bien"]
BASES = {"gaze": "https://api.dicebear.com/10.x/gaze/svg", "moods": "https://api.dicebear.com/10.x/moods/svg"}
# Todo lo que puede ir en la dirección: ajustes del dibujo, nada de la persona
PARAMETROS_PERMITIDOS = {"seed", "shapeVariant", "faceVariant", "cheeksProbability", "backgroundColor",
                         "eyesVariant", "mouthVariant", "bodyColor", "faceColor", "animationVariant"}
CORTO = "LumeaCelebrar.tiempos.xp = 300; LumeaCelebrar.tiempos.mision = 300; LumeaCelebrar.tiempos.salida = 60;"


def abrir(pagina, backend, nombre, caras=None, paleta=None, modo=None):
    """La página con la sesión de prueba, sin check-in hecho hoy y con el set (y la paleta) pedidos ya guardados."""
    cuerpo = cargar_respuesta("progreso")
    cuerpo["progreso"]["avatar"]["estado_animo_hoy"] = None
    backend.poner("GET", "/progreso", cuerpo)
    backend.poner("GET", "/estado-animo", {"success": True, "cantidad": 0, "historial": []})
    guardado = []
    if caras: guardado.append(f"localStorage.setItem('lumea-caras', '{caras}')")
    if paleta: guardado.append(f"localStorage.setItem('lumea-paleta', '{paleta}')")
    if modo: guardado.append(f"localStorage.setItem('lumea-modo', '{modo}')")
    if guardado:
        pagina.add_init_script(";".join(guardado))
    pagina.goto(f"{pagina.servidor}/{nombre}")
    pagina.locator(".animo-cara").first.wait_for()
    pagina.evaluate(CORTO)


def botones(pagina):
    return pagina.locator(".animo-caras .animo-cara")


def parametros(src):
    return {k: v[0] for k, v in parse_qs(urlparse(src).query).items()}


def sin_ruta(src):
    return src.split("?")[0]


# ---------- Sin elección: solo la palabra ----------

@pytest.mark.parametrize("nombre", PAGINAS)
def test_sin_eleccion_no_hay_ninguna_imagen_solo_la_palabra(pagina, backend, nombre):
    abrir(pagina, backend, nombre)
    assert botones(pagina).locator("img").count() == 0
    assert [b.locator(".animo-cara__nombre").inner_text() for b in botones(pagina).all()] == ESTADOS
    assert pagina.locator(".animo-cara__imagen:visible").count() == 0           # el hueco no ocupa lugar
    assert pagina.evaluate("LumeaCaras.actual()") is None


@pytest.mark.parametrize("valor", ["otro", "", "GAZE", "{}"])
def test_un_valor_guardado_desconocido_es_sin_eleccion(pagina, backend, valor):
    pagina.add_init_script(f"localStorage.setItem('lumea-caras', {valor!r})")
    abrir(pagina, backend, "index-ingresado.html")
    assert pagina.evaluate("LumeaCaras.actual()") is None
    assert botones(pagina).locator("img").count() == 0


# ---------- Con un set elegido ----------

@pytest.mark.parametrize("nombre", PAGINAS)
@pytest.mark.parametrize("caras", ["gaze", "moods"])
def test_con_set_cada_boton_trae_su_cara_distinta_y_quieta(pagina, backend, nombre, caras):
    abrir(pagina, backend, nombre, caras=caras)
    imagenes = botones(pagina).locator("img")
    pagina.wait_for_function("document.querySelectorAll('.animo-caras img').length === 5")
    srcs = [i.get_attribute("src") for i in imagenes.all()]
    assert len(set(srcs)) == 5                                                  # una cara distinta por estado
    for src in srcs:
        assert sin_ruta(src) == BASES[caras]
        assert parametros(src)["animationVariant"] == "none"                     # quietas: nunca cinco moviéndose
        assert parametros(src)["seed"] == "lumea-animo"
    for i in imagenes.all():
        assert i.get_attribute("alt") == ""                                      # la palabra es el nombre accesible


@pytest.mark.parametrize("nombre", PAGINAS)
@pytest.mark.parametrize("caras", ["gaze", "moods"])
def test_la_direccion_no_lleva_datos_de_la_persona(pagina, backend, nombre, caras):
    abrir(pagina, backend, nombre, caras=caras)
    pagina.wait_for_function("document.querySelectorAll('.animo-caras img').length === 5")
    for i in botones(pagina).locator("img").all():
        src = i.get_attribute("src")
        assert set(parametros(src)) <= PARAMETROS_PERMITIDOS, src
        for dato in ("prueba", "lumea.test", "Ana", "@", "email", "nombre"):    # ni el correo ni el nombre de la cuenta de prueba
            assert dato not in src


@pytest.mark.parametrize("caras", ["gaze", "moods"])
def test_el_boton_se_llama_por_su_palabra_y_se_marca_con_aria_pressed(pagina, backend, caras):
    abrir(pagina, backend, "index-ingresado.html", caras=caras)
    pagina.wait_for_function("document.querySelectorAll('.animo-caras img').length === 5")
    for palabra in ESTADOS:                                                      # la cara (alt vacío) no altera el nombre
        assert pagina.get_by_role("button", name=palabra, exact=True).count() == 1
    assert botones(pagina).evaluate_all("e => e.map(b => b.getAttribute('aria-pressed'))") == ["false"] * 5
    pagina.get_by_role("button", name="Mal", exact=True).click()
    assert pagina.get_by_role("button", name="Mal", exact=True).get_attribute("aria-pressed") == "true"
    assert botones(pagina).evaluate_all("e => e.filter(b => b.getAttribute('aria-pressed') === 'true').length") == 1


def test_se_elige_y_se_guarda_con_el_teclado(pagina, backend):
    abrir(pagina, backend, "emociones.html", caras="gaze")
    boton = pagina.get_by_role("button", name="Neutral", exact=True)
    boton.focus()
    pagina.keyboard.press("Space")
    assert boton.get_attribute("aria-pressed") == "true"
    assert pagina.locator("#btn-guardar-animo").is_enabled()


@pytest.mark.parametrize("caras", ["gaze", "moods"])
def test_solo_la_cara_elegida_se_anima(pagina, backend, caras):
    abrir(pagina, backend, "index-ingresado.html", caras=caras)
    pagina.wait_for_function("document.querySelectorAll('.animo-caras img').length === 5")

    def animadas():
        return pagina.evaluate("""[...document.querySelectorAll('.animo-cara')].map(b => {
            const img = b.querySelector('img'); return img ? new URL(img.src).searchParams.get('animationVariant') : null })""")

    assert animadas() == ["none"] * 5
    pagina.get_by_role("button", name="Bien", exact=True).click()
    pagina.wait_for_function("document.querySelectorAll('.animo-cara[aria-pressed=true] img[src*=medium]').length === 1")
    assert animadas() == ["none", "none", "none", "medium", "none"]
    pagina.get_by_role("button", name="Mal", exact=True).click()                 # el movimiento sigue a lo que la persona hace
    pagina.wait_for_function("document.querySelectorAll('.animo-cara[aria-pressed=true] img[src*=medium]').length === 1")
    assert animadas() == ["none", "medium", "none", "none", "none"]


# ---------- El color sale de la paleta ----------

def color_de_emocion(pagina):
    return pagina.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--c-emocion').trim()").lstrip("#").lower()


@pytest.mark.parametrize("paleta", ["laguna", "carnaval", "cosecha"])
@pytest.mark.parametrize("caras,parametro", [("gaze", "bodyColor"), ("moods", "faceColor")])
def test_el_color_del_cuerpo_es_el_de_emocion_de_la_paleta_activa(pagina, backend, paleta, caras, parametro):
    abrir(pagina, backend, "index-ingresado.html", caras=caras, paleta=paleta)
    pagina.wait_for_function("document.querySelectorAll('.animo-caras img').length === 5")
    esperado = color_de_emocion(pagina)
    for i in botones(pagina).locator("img").all():
        assert parametros(i.get_attribute("src"))[parametro] == esperado


@pytest.mark.parametrize("caras,parametro", [("gaze", "bodyColor"), ("moods", "faceColor")])
def test_al_cambiar_de_paleta_las_caras_se_dibujan_de_nuevo(pagina, backend, caras, parametro):
    abrir(pagina, backend, "emociones.html", caras=caras, paleta="laguna")
    pagina.wait_for_function("document.querySelectorAll('.animo-caras img').length === 5")
    antes = parametros(botones(pagina).locator("img").first.get_attribute("src"))[parametro]
    pagina.evaluate("LumeaTema.ponerPaleta('carnaval')")                         # emite «lumea:tema»
    despues_esperado = color_de_emocion(pagina)
    assert despues_esperado != antes
    pagina.wait_for_function(f"document.querySelector('.animo-caras img').src.includes('{parametro}={despues_esperado}')")
    for i in botones(pagina).locator("img").all():
        assert parametros(i.get_attribute("src"))[parametro] == despues_esperado


def test_al_cambiar_a_modo_oscuro_el_color_sigue_a_la_paleta(pagina, backend):
    abrir(pagina, backend, "index-ingresado.html", caras="gaze", paleta="neblina", modo="claro")
    pagina.wait_for_function("document.querySelectorAll('.animo-caras img').length === 5")
    pagina.evaluate("LumeaTema.ponerModo('oscuro')")
    esperado = color_de_emocion(pagina)
    pagina.wait_for_function(f"document.querySelector('.animo-caras img').src.includes('bodyColor={esperado}')")


# ---------- Elegir el set ----------

@pytest.mark.parametrize("nombre", PAGINAS)
def test_poner_guarda_la_eleccion_y_redibuja_con_lumea_caras(pagina, backend, nombre):
    abrir(pagina, backend, nombre)
    eventos = pagina.evaluate("window.__caras = 0; document.documentElement.addEventListener('lumea:caras', () => window.__caras++); 0")
    pagina.evaluate("LumeaCaras.poner('moods')")
    pagina.wait_for_function("document.querySelectorAll('.animo-caras img').length === 5")
    assert sin_ruta(botones(pagina).locator("img").first.get_attribute("src")) == BASES["moods"]
    assert pagina.evaluate("localStorage.getItem('lumea-caras')") == "moods"
    pagina.evaluate("LumeaCaras.poner('gaze')")
    pagina.wait_for_function("document.querySelector('.animo-caras img').src.includes('/gaze/')")
    assert pagina.evaluate("localStorage.getItem('lumea-caras')") == "gaze"
    assert pagina.evaluate("window.__caras") == 2
    pagina.evaluate("LumeaCaras.poner(null)")                                    # quitar la elección: otra vez solo la palabra
    assert botones(pagina).locator("img").count() == 0
    assert pagina.evaluate("localStorage.getItem('lumea-caras')") is None


def test_poner_ignora_un_set_que_no_existe(pagina, backend):
    abrir(pagina, backend, "index-ingresado.html", caras="gaze")
    pagina.wait_for_function("document.querySelectorAll('.animo-caras img').length === 5")
    pagina.evaluate("LumeaCaras.poner('otro')")
    assert pagina.evaluate("LumeaCaras.actual()") == "gaze"
    assert botones(pagina).locator("img").count() == 5


def test_la_eleccion_dura_entre_paginas_porque_vive_en_el_navegador(pagina, backend):
    abrir(pagina, backend, "index-ingresado.html")
    pagina.evaluate("LumeaCaras.poner('moods')")
    pagina.goto(f"{pagina.servidor}/emociones.html")
    pagina.wait_for_function("document.querySelectorAll('.animo-caras img').length === 5")
    assert sin_ruta(botones(pagina).locator("img").first.get_attribute("src")) == BASES["moods"]


def test_si_localstorage_falla_no_se_rompe_nada(pagina, backend):
    abrir(pagina, backend, "index-ingresado.html")
    resultado = pagina.evaluate("""() => {
        const original = Storage.prototype.getItem, guardar = Storage.prototype.setItem;
        Storage.prototype.getItem = () => { throw new Error('sin permiso'); };
        Storage.prototype.setItem = () => { throw new Error('sin permiso'); };
        try { LumeaCaras.poner('gaze'); return LumeaCaras.actual(); }
        finally { Storage.prototype.getItem = original; Storage.prototype.setItem = guardar; }
    }""")
    assert resultado is None
    assert pagina.errores == []


# ---------- Sin internet ----------

@pytest.mark.parametrize("nombre", PAGINAS)
@pytest.mark.parametrize("caras", ["gaze", "moods"])
def test_sin_internet_se_quita_la_imagen_y_queda_la_palabra_y_el_boton_funciona(pagina, backend, nombre, caras):
    abrir(pagina, backend, nombre, caras=caras)
    pagina.wait_for_function("document.querySelectorAll('.animo-caras img').length === 5")
    pagina.evaluate("document.querySelectorAll('.animo-caras img').forEach(i => i.dispatchEvent(new Event('error')))")
    assert botones(pagina).locator("img").count() == 0
    assert [b.locator(".animo-cara__nombre").inner_text() for b in botones(pagina).all()] == ESTADOS
    pagina.get_by_role("button", name="Bien", exact=True).click()
    assert pagina.get_by_role("button", name="Bien", exact=True).get_attribute("aria-pressed") == "true"


# ---------- Ningún ánimo es mejor que otro ----------

@pytest.mark.parametrize("nombre", PAGINAS)
@pytest.mark.parametrize("caras", [None, "gaze", "moods"])
def test_ningun_boton_dice_xp_ni_tiene_un_color_distinto_por_animo(pagina, backend, nombre, caras):
    abrir(pagina, backend, nombre, caras=caras)
    for b in botones(pagina).all():
        assert "XP" not in b.inner_text()
    estilos = botones(pagina).evaluate_all("""e => e.map(b => { const c = getComputedStyle(b);
        return [c.backgroundColor, c.borderTopColor, c.color].join('|') })""")
    assert len(set(estilos)) == 1                                                # los cinco, idénticos: ni rojo ni verde por ánimo
