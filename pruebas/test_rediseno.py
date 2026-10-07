"""Rediseño (R1): las reglas visuales, medidas en el navegador sobre las seis pantallas privadas.

Mide lo que MARCA.md y la misión del rediseño prometen, a 1280 y a 390 px:
  - ningún texto visible por debajo de 12,8 px (--t-xs);
  - todo border-radius es uno de los cuatro tokens (o 50 % en círculos);
  - ningún text-transform: uppercase (salvo el sello de la Res. 810, que es oficial);
  - el fondo cubre toda la altura de la ventana;
  - los enlaces del menú y la acción principal miden al menos 44 x 44 px.
Y que las seis pantallas ya no cargan los estilos de Sara ni tienen lo que se quitó.
"""
import re

import pytest

PANTALLAS = ["index-ingresado.html", "mis-registros.html", "alimentos.html",
             "progreso.html", "avatar.html", "emociones.html"]
TAMANOS = {"1280": (1280, 800), "390": (390, 844)}
COMBINACIONES = [(p, t) for p in PANTALLAS for t in TAMANOS]
ids = [f"{p[:-5]}-{t}" for p, t in COMBINACIONES]


def abrir(pagina, nombre, tamano):
    ancho, alto = TAMANOS[tamano]
    pagina.set_viewport_size({"width": ancho, "height": alto})
    pagina.goto(f"{pagina.servidor}/{nombre}")
    pagina.wait_for_load_state("networkidle")


@pytest.mark.parametrize("nombre,tamano", COMBINACIONES, ids=ids)
def test_ningun_texto_visible_por_debajo_de_12_8_px(pagina, nombre, tamano):
    abrir(pagina, nombre, tamano)
    chicos = pagina.evaluate("""() => {
        const minimo = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--t-xs')) * 16;   // 0.8rem = 12,8 px
        const visible = (el) => {
            const r = el.getBoundingClientRect(), c = getComputedStyle(el);
            return r.width > 2 && r.height > 2 && c.visibility !== 'hidden' && c.display !== 'none' && Number(c.opacity) > 0;
        };
        const malos = [];
        const recorrido = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        while (recorrido.nextNode()) {
            const nodo = recorrido.currentNode, el = nodo.parentElement;
            if (!nodo.textContent.trim() || ['SCRIPT', 'STYLE'].includes(el.tagName) || !visible(el)) continue;
            const tam = parseFloat(getComputedStyle(el).fontSize);
            if (tam < minimo - 0.01) malos.push(`${tam}px: ${el.tagName.toLowerCase()}.${el.className} «${nodo.textContent.trim().slice(0, 30)}»`);
        }
        return malos;
    }""")
    assert chicos == []


@pytest.mark.parametrize("nombre,tamano", COMBINACIONES, ids=ids)
def test_todo_border_radius_es_uno_de_los_cuatro_tokens(pagina, nombre, tamano):
    abrir(pagina, nombre, tamano)
    fuera = pagina.evaluate("""() => {
        const raiz = getComputedStyle(document.documentElement);
        const permitidos = new Set(['0px', '50%',
            ...['--r-control', '--r-tarjeta', '--r-panel', '--r-pildora'].map((t) => raiz.getPropertyValue(t).trim())]);
        const malos = [];
        for (const el of document.querySelectorAll('body, body *')) {
            const c = getComputedStyle(el);
            for (const esquina of ['TopLeft', 'TopRight', 'BottomRight', 'BottomLeft']) {
                for (const valor of c['border' + esquina + 'Radius'].split(' ')) {
                    if (!permitidos.has(valor)) malos.push(`${valor}: ${el.tagName.toLowerCase()}.${el.className}`);
                }
            }
        }
        return [...new Set(malos)];
    }""")
    assert fuera == []


@pytest.mark.parametrize("nombre,tamano", COMBINACIONES, ids=ids)
def test_ningun_text_transform_uppercase_salvo_el_sello(pagina, nombre, tamano):
    abrir(pagina, nombre, tamano)
    mayusculas = pagina.evaluate("""() => [...document.querySelectorAll('body *')]
        .filter((el) => getComputedStyle(el).textTransform === 'uppercase' && !el.closest('.sello, .sello-mini'))
        .map((el) => el.tagName.toLowerCase() + '.' + el.className)""")
    assert mayusculas == []


@pytest.mark.parametrize("nombre,tamano", COMBINACIONES, ids=ids)
def test_el_fondo_cubre_toda_la_altura(pagina, nombre, tamano):
    abrir(pagina, nombre, tamano)
    medidas = pagina.evaluate("""() => ({
        ventana: window.innerHeight,
        cuerpo: document.body.getBoundingClientRect().height,
        fondoHtml: getComputedStyle(document.documentElement).backgroundColor,
        fondoCuerpo: getComputedStyle(document.body).backgroundColor,
    })""")
    assert medidas["cuerpo"] >= medidas["ventana"]
    assert medidas["fondoHtml"] != "rgba(0, 0, 0, 0)"         # el fondo es del <html>: llega hasta abajo aunque sobre pantalla
    assert medidas["fondoCuerpo"] == medidas["fondoHtml"]


@pytest.mark.parametrize("nombre,tamano", COMBINACIONES, ids=ids)
def test_el_menu_y_la_accion_principal_miden_al_menos_44_por_44(pagina, nombre, tamano):
    abrir(pagina, nombre, tamano)
    enlaces = pagina.locator("nav.nav-app a.nav-app__enlace")
    assert enlaces.count() == 5
    for i in range(5):
        caja = enlaces.nth(i).bounding_box()
        assert caja["width"] >= 44 and caja["height"] >= 44, enlaces.nth(i).get_attribute("aria-label")
    for principal in pagina.locator("[data-accion-principal]:visible").all():
        caja = principal.bounding_box()
        assert caja["width"] >= 44 and caja["height"] >= 44


# ---------- El armazón único ----------

@pytest.mark.parametrize("nombre", PANTALLAS)
def test_las_seis_pantallas_usan_un_solo_armazon_y_no_cargan_los_estilos_de_sara(pagina, nombre):
    pagina.goto(f"{pagina.servidor}/{nombre}")
    hojas = pagina.eval_on_selector_all("link[rel=stylesheet]", "e => e.map(x => x.getAttribute('href'))")
    for vieja in ("style.css", "estilos/puente-sara.css", "estilos/pantallas-sara.css"):
        assert vieja not in hojas, f"{nombre} todavía carga {vieja}"
    assert "estilos/app.css" in hojas
    assert pagina.locator(".app > nav.nav-app").count() == 1
    assert pagina.locator("nav").count() == 1                    # un solo <nav>: en celular es la barra de abajo
    assert pagina.locator("nav.nav-app img.marca[src='img/logo.svg'][alt=Lumea]").count() == 1
    assert re.search(r"\bLUMEA\b", pagina.locator("body").inner_text()) is None      # el nombre ya no se escribe en mayúsculas


@pytest.mark.parametrize("tamano", list(TAMANOS))
def test_el_menu_es_lateral_en_computador_y_barra_inferior_en_celular(pagina, tamano):
    abrir(pagina, "index-ingresado.html", tamano)
    caja = pagina.locator("nav.nav-app").bounding_box()
    ancho, alto = TAMANOS[tamano]
    if tamano == "1280":
        assert caja["x"] == 0 and caja["width"] == 248 and caja["height"] >= alto
    else:
        assert caja["width"] == ancho and caja["y"] + caja["height"] == alto      # pegada abajo
        centro = pagina.locator("nav.nav-app a").nth(2)                            # Registrar, al centro
        assert centro.get_attribute("aria-label") == "Registrar"


def test_la_zona_de_usuario_del_menu_muestra_nombre_y_nivel(pagina):
    abrir(pagina, "index-ingresado.html", "1280")
    pagina.locator(".nav-app__nivel", has_text="Nivel 2").wait_for()
    usuario = pagina.locator(".nav-app__usuario").inner_text()
    assert "Ana" in usuario and "Nivel 2" in usuario
    assert pagina.locator(".nav-app__salir").is_visible()


# ---------- Lo que se quitó ----------

def test_inicio_ya_no_muestra_la_hora(pagina):
    abrir(pagina, "index-ingresado.html", "1280")
    pagina.locator(".lumea-bind-fecha", has_text="octubre").wait_for()
    assert pagina.locator(".lumea-bind-hora").count() == 0
    assert re.search(r"\b\d{1,2}:\d{2}\b", pagina.locator("body").inner_text()) is None


@pytest.mark.parametrize("nombre", ["progreso.html", "emociones.html"])
def test_progreso_y_animo_no_tienen_flecha_de_volver(pagina, nombre):
    pagina.goto(f"{pagina.servidor}/{nombre}")
    assert pagina.locator("main .bi-arrow-left").count() == 0
    assert pagina.get_by_role("link", name="Volver a Inicio").count() == 0


@pytest.mark.parametrize("tamano", list(TAMANOS))
def test_cerrar_sesion_siempre_tiene_donde_estar(pagina, tamano):
    """En el computador está en el menú; en el celular, al final de Avatar."""
    abrir(pagina, "avatar.html", tamano)
    visibles = pagina.locator("[data-cerrar-sesion]:visible")
    assert visibles.count() == 1
    assert visibles.first.inner_text().strip() == "Cerrar sesión"
    if tamano == "390":
        assert pagina.locator("nav.nav-app [data-cerrar-sesion]").is_visible() is False
