"""alimentos.html (la cámara): sin sesión, IA segura, IA duda y confirmar."""
import json

import pytest


def abrir(pagina, sesion=True):
    if not sesion:
        pagina.add_init_script("localStorage.removeItem('lumea_email')")
    pagina.goto(f"{pagina.servidor}/alimentos.html")


def test_sin_sesion_se_ve_el_aviso(pagina):
    pagina.add_init_script("localStorage.clear()")   # corre después y borra la sesión de prueba
    abrir(pagina, sesion=False)
    assert pagina.locator("#sin-sesion").is_visible()
    assert pagina.locator("#flujo-registro").get_attribute("hidden") is not None   # ver nota abajo


@pytest.mark.xfail(reason="error real: .lumea-dashboard-screen (style.css) anula [hidden] y la cámara se ve sin sesión",
                   strict=True)
def test_sin_sesion_la_camara_no_se_ve(pagina):
    pagina.add_init_script("localStorage.clear()")
    abrir(pagina, sesion=False)
    assert not pagina.locator("#flujo-registro").is_visible()


def test_ia_segura_muestra_logros(pagina, foto):
    abrir(pagina)
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#backend-alimento", has_text="Arepa").wait_for()
    assert "94% seguridad" in pagina.locator("#backend-precision").inner_text()
    assert "+10 XP" in pagina.locator("#backend-logros").inner_text()
    assert "Guardado en tu historial" in pagina.locator("#backend-mensaje").inner_text()


def test_ia_duda_agrupa_las_opciones(pagina, backend, foto):
    backend.poner("POST", "/predecir", json.loads(
        (__import__("pathlib").Path(__file__).parent / "respuestas/predecir_duda.json").read_text()))
    abrir(pagina)
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#backend-opciones button").first.wait_for()
    assert pagina.locator("#backend-alimento").inner_text() == "¿Cuál de estos es?"
    assert pagina.locator("#backend-opciones button").all_inner_texts() == ["Ajiaco", "Sancocho"]


def test_confirmar_guarda_y_celebra(pagina, backend, foto):
    backend.poner("POST", "/predecir", json.loads(
        (__import__("pathlib").Path(__file__).parent / "respuestas/predecir_duda.json").read_text()))
    abrir(pagina)
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.get_by_role("button", name="Ajiaco").click()
    pagina.locator("#backend-logros li", has_text="Misión cumplida").wait_for()
    assert ("POST", "/confirmar-alimento") in backend.llamadas
    textos = pagina.locator("#backend-logros").inner_text()
    assert "+20 XP" in textos and "Subiste al nivel 3" in textos
