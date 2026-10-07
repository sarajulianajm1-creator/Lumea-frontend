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
