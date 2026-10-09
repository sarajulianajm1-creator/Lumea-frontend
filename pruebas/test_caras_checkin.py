"""companero.js (Camino del cuidado, K3): las caras de los cinco botones del check-in son las de tu compañero.

Inicio y Ánimo dibujan, en cada botón, la cara que el backend manda en `avatar.urls_por_estado` (gaze 10.x),
quieta; solo la del botón elegido se anima (`animationVariant=medium`), una a la vez. Sin compañero o sin
internet queda la palabra. Antes (R3) la persona elegía un set de caras («gaze» o «moods») que se guardaba
en el navegador: ya no hay set, ni clave `lumea-caras`, ni `caras-checkin.js`.
(Las imágenes no salen a internet: conftest.py las reemplaza.)
"""
from urllib.parse import parse_qs, urlparse

import pytest

from conftest import CORREO_PRUEBA, OJOS_POR_ESTADO, RAIZ, cargar_respuesta, companero, url_companero

PAGINAS = ["index-ingresado.html", "emociones.html"]
ESTADOS = ["Muy mal", "Mal", "Neutral", "Bien", "Muy bien"]
CLAVES = ["muy_mal", "mal", "neutral", "bien", "muy_bien"]
# Todo lo que puede ir en la dirección: ajustes del dibujo, nada de la persona
PARAMETROS_PERMITIDOS = {"seed", "shapeVariant", "bodyColor", "eyesVariant", "animationVariant"}
CORTO = "LumeaCelebrar.tiempos.xp = 300; LumeaCelebrar.tiempos.mision = 300; LumeaCelebrar.tiempos.salida = 60;"


def abrir(pagina, backend, nombre, compa="sol", registrado=None):
    """La página con la sesión de prueba, con el compañero pedido y sin check-in hecho hoy (salvo `registrado`)."""
    cuerpo = cargar_respuesta("progreso")
    if compa is None:
        cuerpo["progreso"].pop("avatar", None)                       # un backend que no manda compañero
    else:
        cuerpo["progreso"]["avatar"] = companero(compa, registrado)
    backend.poner("GET", "/progreso", cuerpo)
    backend.poner("GET", "/estado-animo", {"success": True, "cantidad": 0, "historial": []})
    pagina.goto(f"{pagina.servidor}/{nombre}")
    pagina.locator(".animo-cara").first.wait_for()
    pagina.evaluate(CORTO)
    if compa is not None:
        pagina.wait_for_function("document.querySelectorAll('.animo-caras img').length === 5")


def botones(pagina):
    return pagina.locator(".animo-caras .animo-cara")


def parametros(src):
    return {k: v[0] for k, v in parse_qs(urlparse(src).query).items()}


def srcs(pagina):
    """El src de la imagen de cada botón, en orden (None si el botón no tiene imagen)."""
    return pagina.evaluate("""[...document.querySelectorAll('.animo-cara')].map(b => { const i = b.querySelector('img'); return i ? i.dataset.fuente : null })""")


# ---------- Las cinco caras son las del compañero ----------

@pytest.mark.parametrize("nombre", PAGINAS)
@pytest.mark.parametrize("compa", ["sol", "luna", "colibri"])
def test_cada_boton_trae_la_cara_de_su_estado_del_companero_y_quieta(pagina, backend, nombre, compa):
    abrir(pagina, backend, nombre, compa)
    assert srcs(pagina) == [url_companero(compa, OJOS_POR_ESTADO[e]) for e in CLAVES]           # las del backend, tal cual
    assert len(set(srcs(pagina))) == 5                                                           # cinco caras distintas
    assert all("animationVariant" not in s for s in srcs(pagina))                                # quietas
    assert all(s.startswith("https://api.dicebear.com/10.x/gaze/svg?") for s in srcs(pagina))
    assert [parametros(s)["eyesVariant"] for s in srcs(pagina)] == ["bars", "small", "dots", "happy", "grin"]


@pytest.mark.parametrize("nombre", PAGINAS)
def test_la_direccion_no_lleva_datos_de_la_persona(pagina, backend, nombre):
    abrir(pagina, backend, nombre)
    pagina.get_by_role("button", name="Bien", exact=True).click()                                # incluso la animada
    if nombre == "emociones.html":
        pagina.wait_for_function("document.querySelectorAll('.animo-cara[aria-pressed=true] img[data-fuente*=medium]').length === 1")
    for src in srcs(pagina):
        datos = parametros(src)
        assert set(datos) <= PARAMETROS_PERMITIDOS, f"parámetro de más: {set(datos) - PARAMETROS_PERMITIDOS}"
        assert datos["seed"] == "lumea-sol"                                                      # la semilla fija del compañero
        assert CORREO_PRUEBA.split("@")[0] not in src and "@" not in src and "prueba" not in src.lower()


@pytest.mark.parametrize("nombre", PAGINAS)
def test_la_imagen_no_se_llama_nada_y_el_hueco_esta_escondido_a_los_lectores(pagina, backend, nombre):
    abrir(pagina, backend, nombre)
    assert botones(pagina).locator("img").evaluate_all("e => e.every(i => i.alt === '')")        # alt vacío: la palabra es el nombre
    for palabra in ESTADOS:
        assert pagina.get_by_role("button", name=palabra, exact=True).count() == 1               # la cara no altera el nombre accesible
    assert pagina.errores == []


@pytest.mark.parametrize("nombre", PAGINAS)
def test_las_caras_no_se_recortan_en_circulo_porque_la_forma_es_el_compañero(pagina, backend, nombre):
    abrir(pagina, backend, nombre)
    estilo = botones(pagina).first.locator(".animo-cara__imagen").evaluate(
        "e => ({ overflow: getComputedStyle(e).overflow, radio: getComputedStyle(e).borderTopLeftRadius })")
    assert estilo == {"overflow": "visible", "radio": "0px"}
    caja = botones(pagina).first.locator("img").bounding_box()
    assert caja["width"] >= 44 and caja["height"] >= 44                                          # lo bastante grande para ver los ojos


# ---------- Elegir ----------

@pytest.mark.parametrize("nombre", PAGINAS)
def test_el_boton_se_marca_con_aria_pressed(pagina, backend, nombre):
    abrir(pagina, backend, nombre)
    assert botones(pagina).evaluate_all("e => e.map(b => b.getAttribute('aria-pressed'))") == ["false"] * 5
    pagina.get_by_role("button", name="Mal", exact=True).click()
    assert pagina.get_by_role("button", name="Mal", exact=True).get_attribute("aria-pressed") == "true"
    assert botones(pagina).evaluate_all("e => e.filter(b => b.getAttribute('aria-pressed') === 'true').length") == 1


def test_se_elige_y_se_guarda_con_el_teclado(pagina, backend):
    abrir(pagina, backend, "emociones.html")
    boton = pagina.get_by_role("button", name="Neutral", exact=True)
    boton.focus()
    pagina.keyboard.press("Space")
    assert boton.get_attribute("aria-pressed") == "true"
    assert pagina.locator("#btn-guardar-animo").is_enabled()


def test_solo_la_cara_elegida_se_anima_y_la_animacion_la_sigue(pagina, backend, nombre="emociones.html"):
    abrir(pagina, backend, nombre)

    def animadas():
        return [parametros(s).get("animationVariant") if s else None for s in srcs(pagina)]

    assert animadas() == [None] * 5
    pagina.get_by_role("button", name="Bien", exact=True).click()
    pagina.wait_for_function("document.querySelectorAll('.animo-cara[aria-pressed=true] img[data-fuente*=medium]').length === 1")
    assert animadas() == [None, None, None, "medium", None]
    assert parametros(srcs(pagina)[3])["eyesVariant"] == "happy"                                 # sigue siendo SU cara
    pagina.get_by_role("button", name="Mal", exact=True).click()                                 # el movimiento sigue a lo que la persona hace
    pagina.wait_for_function("document.querySelectorAll('.animo-cara[aria-pressed=true] img[data-fuente*=medium]').length === 1")
    assert animadas() == [None, "medium", None, None, None]
    assert pagina.locator("img[data-fuente*=medium], img[data-fuente*=slow]").count() == 1                       # nunca dos caras moviéndose


# ---------- Inicio: los botones del check-in quedan quietos y el compañero que saluda es lo único que se mueve ----------

def test_en_inicio_las_cinco_caras_del_check_in_quedan_quietas(pagina, backend):
    abrir(pagina, backend, "index-ingresado.html")
    pagina.get_by_role("button", name="Bien", exact=True).click()
    pagina.wait_for_timeout(250)
    assert all("animationVariant" not in s for s in srcs(pagina))
    assert pagina.locator(".animo-caras img[data-fuente*=medium], .animo-caras img[data-fuente*=slow]").count() == 0


def test_el_companero_saluda_con_la_cara_neutral_y_despacio_si_hoy_no_hay_check_in(pagina, backend):
    abrir(pagina, backend, "index-ingresado.html")
    saludo = pagina.locator(".inicio__saludo #companero-saluda img")
    saludo.wait_for()
    datos = parametros(saludo.get_attribute("data-fuente"))
    assert datos["eyesVariant"] == "dots" and datos["animationVariant"] == "slow" and datos["seed"] == "lumea-sol"
    assert saludo.get_attribute("alt") == "" and pagina.locator("#companero-saluda").get_attribute("aria-hidden") == "true"
    assert pagina.locator("img[data-fuente*=slow], img[data-fuente*=medium]").count() == 1                 # lo único que se mueve en Inicio
    caja = saludo.bounding_box()
    assert 130 <= caja["width"] <= 150                                                                       # unos 140 px en computador


def test_el_companero_que_saluda_mide_96_en_el_celular(pagina, backend):
    pagina.set_viewport_size({"width": 375, "height": 800})
    abrir(pagina, backend, "index-ingresado.html")
    pagina.locator("#companero-saluda img").wait_for()
    assert 90 <= pagina.locator("#companero-saluda img").bounding_box()["width"] <= 100
    assert pagina.evaluate("document.documentElement.scrollWidth") <= 375


def test_al_guardar_el_animo_el_companero_que_saluda_cambia_a_esa_cara(pagina, backend):
    abrir(pagina, backend, "index-ingresado.html")
    pagina.locator("#companero-saluda img").wait_for()
    backend.poner("GET", "/progreso", _progreso_registrado("mal"))
    backend.poner("GET", "/estado-animo", {"success": True, "cantidad": 1, "historial": [{"id": 1, "fecha": "Thu, 08 Oct 2026 00:00:00 GMT", "estado": "mal"}]})
    pagina.get_by_role("button", name="Mal", exact=True).click()
    pagina.locator("#btn-guardar-animo-inicio").click()
    pagina.wait_for_function("document.querySelector('#companero-saluda img') && document.querySelector('#companero-saluda img').dataset.fuente.includes('eyesVariant=small')")
    assert pagina.locator("img[data-fuente*=slow], img[data-fuente*=medium]").count() == 1


def test_si_no_hay_companero_el_saludo_queda_sin_imagen(pagina, backend):
    abrir(pagina, backend, "index-ingresado.html", compa=None)
    pagina.wait_for_timeout(300)
    assert pagina.locator("#companero-saluda img").count() == 0
    assert pagina.locator("h1").inner_text().startswith("Hola")


def _progreso_registrado(estado):
    cuerpo = cargar_respuesta("progreso")
    cuerpo["progreso"]["avatar"] = companero("sol", estado)
    return cuerpo


@pytest.mark.parametrize("nombre", PAGINAS)
def test_con_movimiento_reducido_las_caras_se_ven_pero_no_piden_animacion(pagina, backend, nombre):
    pagina.emulate_media(reduced_motion="reduce")
    abrir(pagina, backend, nombre)
    pagina.get_by_role("button", name="Bien", exact=True).click()
    pagina.wait_for_timeout(200)
    assert all(s is not None and "animationVariant" not in s for s in srcs(pagina))


def test_las_demas_caras_no_se_vuelven_a_cargar_al_elegir_otra(pagina, backend, nombre="emociones.html"):
    """Una cara que ya está dibujada tal cual no parpadea ni reinicia su animación."""
    abrir(pagina, backend, nombre)
    pagina.evaluate("document.querySelectorAll('.animo-cara img').forEach((i, n) => { i.dataset.marca = n })")
    pagina.get_by_role("button", name="Bien", exact=True).click()
    pagina.wait_for_function("document.querySelectorAll('.animo-cara[aria-pressed=true] img[data-fuente*=medium]').length === 1")
    marcas = pagina.evaluate("[...document.querySelectorAll('.animo-cara')].map(b => { const i = b.querySelector('img'); return i && i.dataset.marca || null })")
    assert marcas == ["0", "1", "2", None, "4"]                       # solo la elegida es una imagen nueva


def test_ya_registrado_hoy_la_cara_de_hoy_es_la_elegida(pagina, backend):
    abrir(pagina, backend, "index-ingresado.html", registrado="mal")
    assert pagina.get_by_role("button", name="Mal", exact=True).get_attribute("aria-pressed") == "true"
    assert "animationVariant" not in srcs(pagina)[1]                                             # en Inicio los botones quedan quietos
    assert "eyesVariant=small" in pagina.locator("#companero-saluda img").get_attribute("data-fuente")        # y el que saluda lleva esa cara


# ---------- Sin compañero o sin internet: queda la palabra ----------

@pytest.mark.parametrize("nombre", PAGINAS)
def test_sin_internet_se_quita_la_imagen_y_queda_la_palabra_y_el_boton_funciona(pagina, backend, nombre):
    abrir(pagina, backend, nombre)
    pagina.evaluate("document.querySelectorAll('.animo-caras img').forEach(i => i.dispatchEvent(new Event('error')))")
    assert botones(pagina).locator("img").count() == 0
    assert [b.locator(".animo-cara__nombre").inner_text() for b in botones(pagina).all()] == ESTADOS
    assert pagina.locator(".animo-cara__imagen:visible").count() == 0                           # el hueco no ocupa lugar
    pagina.get_by_role("button", name="Bien", exact=True).click()
    assert pagina.get_by_role("button", name="Bien", exact=True).get_attribute("aria-pressed") == "true"


@pytest.mark.parametrize("nombre", PAGINAS)
def test_si_localstorage_falla_no_se_rompe_nada(pagina, backend, nombre):
    """companero.js borra la clave vieja con try/catch: un navegador que bloquea el almacenamiento no rompe el check-in."""
    pagina.add_init_script("Storage.prototype.removeItem = () => { throw new Error('sin permiso'); };")
    abrir(pagina, backend, nombre)
    assert botones(pagina).locator("img").count() == 5
    assert pagina.errores == []


@pytest.mark.parametrize("nombre", PAGINAS)
def test_si_el_backend_no_manda_companero_solo_se_ve_la_palabra(pagina, backend, nombre):
    abrir(pagina, backend, nombre, compa=None)
    pagina.wait_for_timeout(300)
    assert botones(pagina).locator("img").count() == 0
    assert [b.locator(".animo-cara__nombre").inner_text() for b in botones(pagina).all()] == ESTADOS
    pagina.get_by_role("button", name="Neutral", exact=True).click()
    assert pagina.get_by_role("button", name="Neutral", exact=True).get_attribute("aria-pressed") == "true"
    assert pagina.errores == []


@pytest.mark.parametrize("nombre", PAGINAS)
def test_una_direccion_que_no_es_http_no_se_dibuja(pagina, backend, nombre):
    cuerpo = cargar_respuesta("progreso")
    cuerpo["progreso"]["avatar"] = companero("sol", None)
    cuerpo["progreso"]["avatar"]["urls_por_estado"]["mal"] = "javascript:alert(1)"
    backend.poner("GET", "/progreso", cuerpo)
    pagina.goto(f"{pagina.servidor}/{nombre}")
    pagina.wait_for_function("document.querySelectorAll('.animo-caras img').length === 4")
    assert botones(pagina).nth(1).locator("img").count() == 0                                   # esa queda con su palabra


# ---------- Ya no hay sets de caras ni clave en el navegador ----------

@pytest.mark.parametrize("nombre", PAGINAS)
def test_una_eleccion_vieja_de_set_se_borra_y_no_cambia_las_caras(pagina, backend, nombre):
    pagina.add_init_script("localStorage.setItem('lumea-caras', 'moods')")
    abrir(pagina, backend, nombre)
    assert pagina.evaluate("localStorage.getItem('lumea-caras')") is None
    assert all("/10.x/gaze/" in s for s in srcs(pagina))


def test_caras_checkin_ya_no_existe_ni_se_carga(pagina, backend):
    assert not (RAIZ / "caras-checkin.js").exists()
    for nombre in ["index-ingresado.html", "emociones.html", "avatar.html"]:
        html = (RAIZ / nombre).read_text(encoding="utf-8")
        assert "caras-checkin" not in html and "LumeaCaras" not in html
    abrir(pagina, backend, "index-ingresado.html")
    assert pagina.evaluate("typeof LumeaCaras") == "undefined"
    assert pagina.evaluate("typeof LumeaCompanero") == "object"


# ---------- Ningún ánimo es mejor que otro ----------

@pytest.mark.parametrize("nombre", PAGINAS)
def test_ningun_boton_dice_xp_ni_tiene_un_color_distinto_por_animo(pagina, backend, nombre):
    abrir(pagina, backend, nombre)
    for b in botones(pagina).all():
        assert "XP" not in b.inner_text() and "semilla" not in b.inner_text()
    estilos = botones(pagina).evaluate_all("""e => e.map(b => { const c = getComputedStyle(b);
        return [c.backgroundColor, c.borderTopColor, c.color].join('|') })""")
    assert len(set(estilos)) == 1                                                # los cinco, idénticos: ni rojo ni verde por ánimo
