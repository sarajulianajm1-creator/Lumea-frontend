"""Lumea dibuja a la persona y a los compañeros en el navegador (vendor/dicebear/): ninguna página le pide nada a DiceBear."""
import pytest

PAGINAS_PRIVADAS = ["index-ingresado.html", "alimentos.html", "emociones.html", "progreso.html", "avatar.html", "mis-registros.html"]


@pytest.mark.parametrize("nombre", PAGINAS_PRIVADAS)
def test_ninguna_pagina_pide_nada_a_dicebear(pagina, nombre):
    pagina.goto(f"{pagina.servidor}/{nombre}")
    pagina.wait_for_load_state("networkidle")
    if nombre in ("index-ingresado.html", "emociones.html"):
        pagina.wait_for_function("document.querySelectorAll('.animo-caras img[src^=\"data:image/svg+xml\"]').length === 5")
    if nombre == "avatar.html":
        pagina.locator("#avatar-figura img.avatar-figura__persona-img[src^='data:image/svg+xml']").wait_for()
    assert [u for u in pagina.peticiones_externas if "dicebear" in u] == []
    assert pagina.peticiones_externas == []


def test_el_compañero_y_la_persona_llevan_su_dibujo_en_la_propia_imagen(pagina):
    pagina.goto(f"{pagina.servidor}/avatar.html")
    pagina.locator("#avatar-figura img.avatar-figura__companero[src^='data:image/svg+xml']").wait_for()
    pagina.locator("#avatar-figura img.avatar-figura__persona-img[src^='data:image/svg+xml']").wait_for()
    # (el SVG trae el crédito de DiceBear como texto adentro; lo que cuenta es que ninguna imagen apunte a una dirección de afuera)
    assert pagina.evaluate("[...document.images].filter(i => (i.currentSrc || i.src) && !(i.currentSrc || i.src).startsWith('data:') && /dicebear/.test(i.currentSrc || i.src)).length") == 0
