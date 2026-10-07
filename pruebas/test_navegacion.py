"""La navegación privada es la misma en las cinco pantallas, con aria-current en la actual."""
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


@pytest.mark.parametrize("pagina_nombre,actual", list(PANTALLAS.items()))
def test_los_cinco_destinos_y_la_actual_marcada(pagina, pagina_nombre, actual):
    pagina.goto(f"{pagina.servidor}/{pagina_nombre}")
    nav = pagina.locator("nav[aria-label=Principal]")
    enlaces = nav.locator("a")
    assert [(e.inner_text().strip(), e.get_attribute("href")) for e in enlaces.all()] == DESTINOS
    marcados = nav.locator("a[aria-current=page]")
    assert marcados.count() == 1
    assert marcados.inner_text().strip() == actual


@pytest.mark.parametrize("pagina_nombre", list(PANTALLAS))
def test_cada_destino_privado_existe_y_abre(pagina, pagina_nombre):
    respuesta = pagina.goto(f"{pagina.servidor}/{pagina_nombre}")
    assert respuesta.status == 200
