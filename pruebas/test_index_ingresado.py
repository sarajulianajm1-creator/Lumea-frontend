"""index-ingresado.html (Inicio de Sara): los textos de racha y meta del día."""
from conftest import cargar_respuesta


def abrir(pagina, backend, **cambios):
    cuerpo = cargar_respuesta("progreso")
    cuerpo["progreso"].update(cambios)
    backend.poner("GET", "/progreso", cuerpo)
    pagina.goto(f"{pagina.servidor}/index-ingresado.html")
    pagina.locator("#user-nivel", has_text="Nivel 2").wait_for()


def test_racha_en_singular(pagina, backend):
    abrir(pagina, backend, racha_actual=1)
    assert pagina.locator("#user-racha").inner_text() == "1 día de racha"


def test_racha_en_plural(pagina, backend):
    abrir(pagina, backend, racha_actual=3)
    assert pagina.locator("#user-racha").inner_text() == "3 días de racha"


def test_meta_cumplida_no_dice_20_de_15(pagina, backend):
    abrir(pagina, backend, meta_diaria={"xp_hoy": 20, "meta": 15, "cumplida": True})
    assert pagina.locator("#meta-texto").inner_text() == "Meta cumplida: 20 XP hoy"


def test_meta_sin_cumplir_dice_cuanto_lleva(pagina, backend):
    abrir(pagina, backend, meta_diaria={"xp_hoy": 10, "meta": 15, "cumplida": False})
    assert pagina.locator("#meta-texto").inner_text() == "10 de 15 XP hoy"
