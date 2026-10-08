"""Recorrido de accesibilidad de las seis pantallas privadas (rediseño R9), hecho por la prueba en vez de a mano:

  - Con teclado, sin mouse: cada control se alcanza con Tab, no hay trampa de teclado y el foco SIEMPRE se ve.
  - A 200 % de zoom (640 px de ancho CSS) y a 320 px de ancho, sin barra horizontal (WCAG 1.4.10, reflujo).
  - Los flujos principales se pueden hacer solo con el teclado.
"""
import json

import pytest

from conftest import cargar_respuesta

PANTALLAS = ["index-ingresado.html", "mis-registros.html", "alimentos.html", "progreso.html", "avatar.html", "emociones.html"]
ANCHOS = {"1280": 1280, "zoom200": 640, "320": 320}

# Todo lo que el teclado puede alcanzar con Tab (visible y no desactivado)
TABULABLES = """() => {
    const visible = (e) => { const r = e.getBoundingClientRect(), c = getComputedStyle(e);
        return c.visibility !== 'hidden' && c.display !== 'none' && (r.width > 0 || r.height > 0 || e.classList.contains('solo-lector')) };
    const lista = [...document.querySelectorAll('a[href], button, input, select, textarea, [tabindex]')]
        .filter((e) => !e.disabled && e.type !== 'hidden' && e.tabIndex >= 0 && !e.closest('[hidden]') && visible(e));
    // de un grupo de radios solo uno entra con Tab (las flechas hacen el resto)
    const vistos = new Set();
    return lista.filter((e) => { if (e.type !== 'radio') return true;
        const k = e.name; if (vistos.has(k)) return false; vistos.add(k); return true }).length }"""

# Qué está enfocado ahora y si se ve el foco (en el elemento, en su etiqueta si el control está escondido, o en su botón)
FOCO = """() => {
    const e = document.activeElement;
    if (!e || e === document.body) return null;
    const visibleIndicador = (el) => { const c = getComputedStyle(el);
        return (c.outlineStyle !== 'none' && parseFloat(c.outlineWidth) >= 2) || c.boxShadow !== 'none' };
    const duenio = e.classList.contains('solo-lector') || e.type === 'radio' ? (e.closest('label') || e) : e;
    return { clave: [e.tagName, e.id || e.name || '', e.getAttribute('href') || '', e.getAttribute('aria-label') || e.textContent.trim().slice(0, 24), e.value || ''].join('|'),
             visible: visibleIndicador(duenio), enPantalla: (() => { const r = duenio.getBoundingClientRect(); return r.bottom > 0 && r.top < innerHeight })() }
}"""


def abrir(pagina, backend, nombre, ancho=1280):
    cuerpo = cargar_respuesta("progreso")
    cuerpo["progreso"]["avatar"]["estado_animo_hoy"] = None            # sin check-in hoy: así se ven todos los controles
    backend.poner("GET", "/progreso", cuerpo)
    backend.poner("GET", "/estado-animo", {"success": True, "cantidad": 0, "historial": []})
    pagina.set_viewport_size({"width": ancho, "height": 800})
    pagina.goto(f"{pagina.servidor}/{nombre}")
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(300)


# ---------- Teclado: se llega a todo, no hay trampas y el foco se ve ----------

@pytest.mark.parametrize("ancho", ["1280", "320"])
@pytest.mark.parametrize("nombre", PANTALLAS)
def test_con_tab_se_recorre_toda_la_pantalla_y_el_foco_siempre_se_ve(pagina, backend, nombre, ancho):
    abrir(pagina, backend, nombre, ANCHOS[ancho])
    esperados = pagina.evaluate(TABULABLES)
    assert esperados >= 6                                                              # al menos el menú
    paradas = []
    for _ in range(esperados + 2):
        pagina.keyboard.press("Tab")
        foco = pagina.evaluate(FOCO)
        if foco is None:                                                               # el foco salió de la página: terminó el recorrido
            break
        paradas.append(foco)
    claves = [p["clave"] for p in paradas]
    assert len(claves) >= esperados                                                    # no hay trampa de teclado: se avanza hasta el final
    assert len(set(claves)) >= esperados - 1                                           # y cada parada es un control distinto
    sin_foco = [p["clave"] for p in paradas if not p["visible"]]
    assert sin_foco == [], f"controles sin foco visible: {sin_foco}"
    fuera = [p["clave"] for p in paradas if not p["enPantalla"]]
    assert fuera == [], f"el foco quedó fuera de la pantalla: {fuera}"


@pytest.mark.parametrize("nombre", PANTALLAS)
def test_lo_primero_que_se_alcanza_con_tab_es_el_menu_en_su_orden(pagina, backend, nombre):
    abrir(pagina, backend, nombre)
    nombres = []
    for _ in range(5):
        pagina.keyboard.press("Tab")
        nombres.append(pagina.evaluate("document.activeElement.getAttribute('aria-label')"))
    assert nombres == ["Inicio", "Mis registros", "Registrar", "Progreso", "Avatar"]


@pytest.mark.parametrize("nombre", PANTALLAS)
def test_shift_tab_vuelve_atras_sin_perderse(pagina, backend, nombre):
    abrir(pagina, backend, nombre)
    for _ in range(3):
        pagina.keyboard.press("Tab")
    ahora = pagina.evaluate("document.activeElement.getAttribute('aria-label')")
    pagina.keyboard.press("Tab")
    pagina.keyboard.press("Shift+Tab")
    assert pagina.evaluate("document.activeElement.getAttribute('aria-label')") == ahora


# ---------- Reflujo: 200 % de zoom y 320 px sin barra horizontal ----------

@pytest.mark.parametrize("ancho", ["zoom200", "320"])
@pytest.mark.parametrize("nombre", PANTALLAS)
def test_sin_barra_horizontal_a_200_por_ciento_de_zoom_y_a_320_px(pagina, backend, nombre, ancho):
    abrir(pagina, backend, nombre, ANCHOS[ancho])
    assert pagina.evaluate("document.documentElement.scrollWidth") <= ANCHOS[ancho]
    # y nada importante queda cortado a la derecha: ningún control se sale del ancho
    sale = pagina.evaluate("""(w) => [...document.querySelectorAll('a, button, input, h1, h2, img.marca')]
        .filter((e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.right > w + 1 && !e.classList.contains('solo-lector') })
        .map((e) => e.tagName + '.' + e.className)""", ANCHOS[ancho])
    assert sale == []


@pytest.mark.parametrize("ancho", ["zoom200", "320"])
def test_registrar_con_un_resultado_largo_y_tres_sellos_cabe_a_320_px(pagina, backend, foto, ancho):
    respuesta = cargar_respuesta("predecir_segura") | {"sellos_advertencia": ["sodio", "azucares", "grasas_saturadas"],
                                                        "alimento_app": "Arepa paisa de maíz precocido con sal y mantequilla"}
    backend.poner("POST", "/predecir", respuesta)
    pagina.set_viewport_size({"width": ANCHOS[ancho], "height": 800})
    pagina.goto(f"{pagina.servidor}/alimentos.html")
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#resultado[data-estado]:not([data-estado=''])").wait_for()
    assert pagina.evaluate("document.documentElement.scrollWidth") <= ANCHOS[ancho]


@pytest.mark.parametrize("ancho", ["zoom200", "320"])
def test_mis_registros_con_sellos_y_nombres_largos_cabe(pagina, backend, ancho):
    registro = cargar_respuesta("historial")["historial"][2] | {"alimento_detectado": "Coca-Cola Original de medio litro, en botella retornable"}
    backend.poner("GET", "/historial", {"success": True, "cantidad_registros": 1, "historial": [registro]})
    pagina.set_viewport_size({"width": ANCHOS[ancho], "height": 800})
    pagina.goto(f"{pagina.servidor}/mis-registros.html")
    pagina.locator("#listaRegistros > li").first.wait_for()
    assert pagina.evaluate("document.documentElement.scrollWidth") <= ANCHOS[ancho]


def test_la_tarjeta_de_colores_y_caras_cabe_a_320_px(pagina, backend):
    abrir(pagina, backend, "index-ingresado.html", 320)
    assert pagina.locator("#card-colores").is_visible()
    assert pagina.evaluate("document.documentElement.scrollWidth") <= 320


# ---------- Los flujos principales, solo con el teclado ----------

def test_el_checkin_de_inicio_se_hace_solo_con_el_teclado(pagina, backend):
    abrir(pagina, backend, "index-ingresado.html")
    pagina.evaluate("LumeaCelebrar.tiempos.xp = 300; LumeaCelebrar.tiempos.salida = 60;")
    despues = cargar_respuesta("progreso")
    despues["progreso"]["avatar"]["estado_animo_hoy"] = "neutral"
    pagina.get_by_role("button", name="Neutral", exact=True).focus()
    pagina.keyboard.press("Space")                                                       # elegir la cara
    assert pagina.get_by_role("button", name="Neutral", exact=True).get_attribute("aria-pressed") == "true"
    backend.poner("GET", "/progreso", despues)
    guardar = pagina.get_by_role("button", name="Guardar mi ánimo")
    assert guardar.is_enabled()
    guardar.focus()
    pagina.keyboard.press("Enter")                                                       # guardar
    pagina.locator(".celebracion__chip").first.wait_for()
    envio = next(c for m, u, c in backend.peticiones if m == "POST" and u.endswith("/estado-animo"))
    assert json.loads(envio) == {"email": "prueba@lumea.test", "estado": "neutral"}


def test_el_menu_se_usa_con_el_teclado(pagina, backend):
    abrir(pagina, backend, "index-ingresado.html")
    pagina.get_by_role("link", name="Mis registros").focus()
    pagina.keyboard.press("Enter")
    pagina.wait_for_url("**/mis-registros.html")


def test_la_tarjeta_de_colores_se_cierra_con_el_teclado_y_el_foco_pasa_a_la_accion_principal(pagina, backend):
    abrir(pagina, backend, "index-ingresado.html")
    pagina.get_by_role("button", name="Listo").focus()
    pagina.keyboard.press("Enter")
    assert not pagina.locator("#card-colores").is_visible()
    assert pagina.evaluate("document.activeElement.hasAttribute('data-accion-principal')")          # el foco no se pierde


def test_cerrar_sesion_se_alcanza_y_se_activa_con_el_teclado(pagina, backend):
    abrir(pagina, backend, "avatar.html")
    pagina.locator("nav.nav-app [data-cerrar-sesion]").focus()
    pagina.keyboard.press("Enter")
    pagina.wait_for_url("**/index.html")


# ---------- Nada se comunica solo con color ----------

def test_la_cara_elegida_y_la_paleta_elegida_se_distinguen_sin_el_color(pagina, backend):
    """aria-pressed / radio marcado (lo oye el lector de pantalla) y un borde más grueso (lo ve quien no distingue colores)."""
    abrir(pagina, backend, "index-ingresado.html")
    boton = pagina.get_by_role("button", name="Bien", exact=True)
    boton.click()
    assert boton.get_attribute("aria-pressed") == "true"
    borde = boton.evaluate("e => parseFloat(getComputedStyle(e).borderTopWidth)")
    otro = pagina.get_by_role("button", name="Mal", exact=True).evaluate("e => parseFloat(getComputedStyle(e).borderTopWidth)")
    assert borde > otro
    pagina.locator("#card-colores").get_by_label("Neblina", exact=True).check(force=True)
    assert pagina.locator("#card-colores input[value=neblina]").is_checked()
