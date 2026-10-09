"""La navegación privada es la misma en las cinco pantallas (un solo <nav>), con aria-current en la actual.

Rediseño R1: ya no hay un menú lateral y otro de celular. Es UN <nav class="nav-app"> que el CSS
convierte en barra lateral (computador) o en barra inferior (celular)."""
import pytest

PANTALLAS = {                      # página -> el destino que debe quedar marcado
    "index-ingresado.html": "Inicio",
    "mis-registros.html": "Mis registros",
    "alimentos.html": "Registrar",
    "progreso.html": "Progreso",
    "avatar.html": "Avatar",
}
DESTINOS = [("Inicio", "index-ingresado.html"), ("Mis registros", "mis-registros.html"),
            ("Registrar", "alimentos.html"), ("Progreso", "progreso.html"), ("Avatar", "avatar.html")]
CON_MENU = list(PANTALLAS) + ["emociones.html"]      # Ánimo tiene menú pero ningún destino marcado


@pytest.mark.parametrize("pagina_nombre,actual", list(PANTALLAS.items()))
def test_los_cinco_destinos_y_la_actual_marcada(pagina, pagina_nombre, actual):
    pagina.goto(f"{pagina.servidor}/{pagina_nombre}")
    nav = pagina.locator("nav[aria-label=Principal]")
    enlaces = nav.locator("a")
    assert [(e.inner_text().strip(), e.get_attribute("href")) for e in enlaces.all()] == DESTINOS
    marcados = nav.locator("a[aria-current=page]")
    assert marcados.count() == 1
    assert marcados.inner_text().strip() == actual


@pytest.mark.parametrize("pagina_nombre,actual", list(PANTALLAS.items()))
def test_el_menu_del_celular_tiene_los_mismos_cinco_destinos(pagina, pagina_nombre, actual):
    pagina.set_viewport_size({"width": 375, "height": 812})
    pagina.goto(f"{pagina.servidor}/{pagina_nombre}")
    nav = pagina.locator("nav[aria-label=Principal]")          # el MISMO nav, ahora pegado abajo
    assert nav.is_visible()
    assert pagina.locator("nav").count() == 1
    caja = nav.bounding_box()
    assert caja["y"] + caja["height"] == 812
    enlaces = nav.locator("a")
    assert [(e.get_attribute("aria-label"), e.get_attribute("href")) for e in enlaces.all()] == DESTINOS
    marcados = nav.locator("a[aria-current=page]")
    assert marcados.count() == 1 and marcados.get_attribute("aria-label") == actual
    assert pagina.evaluate("document.documentElement.scrollWidth") <= 375


def test_animo_no_esta_en_el_menu_pero_se_abre_desde_inicio_y_progreso(pagina):
    pagina.goto(f"{pagina.servidor}/emociones.html")
    nav = pagina.locator("nav[aria-label=Principal]")
    assert [e.inner_text().strip() for e in nav.locator("a").all()] == [d for d, _ in DESTINOS]
    assert nav.locator("a[aria-current=page]").count() == 0          # ningún destino del menú es Ánimo
    for origen in ("index-ingresado.html", "progreso.html"):
        pagina.goto(f"{pagina.servidor}/{origen}")
        assert pagina.locator("main a[href='emociones.html']").count() >= 1, origen


@pytest.mark.parametrize("pagina_nombre", CON_MENU)
def test_cada_pantalla_con_menu_abre(pagina, pagina_nombre):
    respuesta = pagina.goto(f"{pagina.servidor}/{pagina_nombre}")
    assert respuesta.status == 200


@pytest.mark.parametrize("pagina_nombre", CON_MENU)
def test_cerrar_sesion_borra_las_dos_claves_y_vuelve_a_la_portada(pagina, pagina_nombre):
    # la clave vieja de Sara se siembra una sola vez (el script de inicio corre en cada página)
    pagina.add_init_script("""if (!sessionStorage.getItem('sembrado')) {
        sessionStorage.setItem('sembrado', '1'); localStorage.setItem('lumea_usuario_email', 'vieja@lumea.test'); }""")
    pagina.goto(f"{pagina.servidor}/{pagina_nombre}")
    pagina.get_by_role("button", name="Cerrar sesión").click()
    pagina.wait_for_url("**/index.html")
    assert pagina.evaluate("[localStorage.getItem('lumea_email'), localStorage.getItem('lumea_usuario_email')]") == [None, None]


# ---------- P9: el menú lateral ocupa todo el alto ----------

import pytest as _pytest


@_pytest.mark.parametrize("nombre", ["progreso.html", "avatar.html", "mis-registros.html"])
def test_el_fondo_del_menu_lateral_ocupa_todo_el_alto_de_la_pagina(pagina, nombre):
    pagina.set_viewport_size({"width": 1280, "height": 720})
    pagina.goto(f"{pagina.servidor}/{nombre}")
    pagina.wait_for_load_state("networkidle")
    # un alto de página mayor que la ventana: se alarga con un bloque alto al final
    pagina.evaluate("(() => { const d = document.createElement('div'); d.style.height = '2400px'; document.querySelector('main').appendChild(d); })()")
    datos = pagina.evaluate("""() => { const a = getComputedStyle(document.querySelector('.app'), '::before'), r = document.querySelector('.app').getBoundingClientRect();
        return { alto: parseFloat(a.height), pagina: r.height, fondo: a.backgroundColor, ancho: parseFloat(a.width) } }""")
    assert datos["alto"] >= datos["pagina"] - 1 and datos["pagina"] > 2400            # el fondo llega hasta abajo, no se corta a 720 px
    assert datos["fondo"] != "rgba(0, 0, 0, 0)" and 240 <= datos["ancho"] <= 260
    assert pagina.locator(".nav-app").evaluate("e => getComputedStyle(e).position") == "sticky"      # el menú sigue pegado arriba al bajar


def test_en_el_celular_el_menu_sigue_siendo_la_barra_de_abajo(pagina):
    pagina.set_viewport_size({"width": 390, "height": 844})
    pagina.goto(f"{pagina.servidor}/avatar.html")
    assert pagina.locator(".nav-app").evaluate("e => getComputedStyle(e).position") == "fixed"
    assert pagina.evaluate("getComputedStyle(document.querySelector('.app'), '::before').display") == "none"
