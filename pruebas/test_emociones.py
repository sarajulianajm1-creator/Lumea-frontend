"""emociones.html (Ánimo, el diseño es de Sara): las caras del avatar cambian en vivo y guardar celebra."""
import json

import pytest

from conftest import cargar_respuesta

ESTADOS = ["Muy mal", "Mal", "Neutral", "Bien", "Muy bien"]
CORTO = "LumeaCelebrar.tiempos.xp = 300; LumeaCelebrar.tiempos.mision = 300; LumeaCelebrar.tiempos.salida = 60;"


def boton(pagina, nombre):
    """El botón de un estado por su nombre exacto («Mal» no es «Muy mal»)."""
    return pagina.locator(".btn-face-mood").filter(has=pagina.get_by_text(nombre, exact=True))


def sin_animo_hoy(backend):
    cuerpo = cargar_respuesta("progreso")
    cuerpo["progreso"]["avatar"]["estado_animo_hoy"] = None
    backend.poner("GET", "/progreso", cuerpo)


def abrir(pagina, backend=None, registrado=False):
    if backend is not None and not registrado:
        sin_animo_hoy(backend)
    pagina.goto(f"{pagina.servidor}/emociones.html")
    pagina.locator(".btn-face-mood").first.wait_for()
    pagina.locator(".btn-face-mood img").first.wait_for()
    pagina.evaluate(CORTO)


def test_los_cinco_estados_con_nombre_y_la_cara_del_avatar(pagina, backend):
    abrir(pagina, backend)
    botones = pagina.locator(".btn-face-mood")
    assert [b.locator(".face-name-label").inner_text() for b in botones.all()] == ESTADOS
    assert botones.locator("img").count() == 5
    assert "mouth=sad" in botones.nth(0).locator("img").get_attribute("src")
    assert "twinkle" in botones.nth(4).locator("img").get_attribute("src")
    assert pagina.errores == []                       # ni «suscribir is not a function» ni «null.style»


def test_sin_emojis_ni_version_en_la_pantalla(pagina, backend):
    abrir(pagina, backend)
    contenido = pagina.locator("body").inner_text()
    assert "Versión" not in contenido
    for emoji in ("😢", "🙁", "😐", "🙂", "😄", "🌿", "✓"):
        assert emoji not in contenido


def test_la_cara_grande_cambia_en_vivo_al_elegir(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("#btn-guardar-animo").is_disabled()          # sin elegir no se guarda
    boton(pagina, "Mal").click()
    assert "mouth=concerned" in pagina.locator("#cara-grande img").get_attribute("src")
    assert pagina.locator("#texto-estado-seleccionado").inner_text() == "Me siento mal"
    boton(pagina, "Muy bien").click()
    assert "twinkle" in pagina.locator("#cara-grande img").get_attribute("src")
    assert pagina.locator("#texto-estado-seleccionado").inner_text() == "Me siento muy bien"
    pulsados = pagina.locator(".btn-face-mood[aria-pressed=true]")
    assert pulsados.count() == 1 and "Muy bien" in pulsados.inner_text()
    assert pagina.locator("#btn-guardar-animo").is_enabled()


def test_los_textos_no_tienen_genero(pagina, backend):
    abrir(pagina, backend)
    textos = []
    for nombre in ESTADOS:
        boton(pagina, nombre).click()
        textos.append(pagina.locator("#subtexto-estado").inner_text())
    for t in textos:
        assert not any(p in t for p in ("valiosa", "Tranquila", "Receptiva"))


def test_guardar_registra_celebra_y_queda_registrado(pagina, backend):
    abrir(pagina, backend)
    boton(pagina, "Mal").click()
    # el backend, ya con el ánimo de hoy, para la lectura que sigue a guardar
    cuerpo = cargar_respuesta("progreso")
    cuerpo["progreso"]["avatar"]["estado_animo_hoy"] = "mal"
    backend.poner("GET", "/progreso", cuerpo)
    pagina.get_by_role("button", name="Guardar mi ánimo (+5 XP)").click()
    pagina.locator(".celebracion__chip").first.wait_for()
    assert pagina.locator(".celebracion__chip").first.inner_text() == "+5 XP"
    envio = next(c for m, u, c in backend.peticiones if m == "POST" and u.endswith("/estado-animo"))
    assert json.loads(envio) == {"email": "prueba@lumea.test", "estado": "mal"}
    guardar = pagina.locator("#btn-guardar-animo")
    pagina.wait_for_function("document.getElementById('btn-guardar-animo').textContent.includes('ya está registrado')")
    assert guardar.is_disabled()
    assert pagina.locator("#confirmacion-animo").is_visible()


def test_si_ya_hizo_el_checkin_hoy_no_se_puede_repetir(pagina, backend):
    abrir(pagina, backend, registrado=True)
    pagina.locator("#btn-guardar-animo", has_text="ya está registrado").wait_for()
    assert pagina.locator("#btn-guardar-animo").is_disabled()
    assert "Bien" in pagina.locator(".btn-face-mood[aria-pressed=true]").inner_text()
    assert pagina.locator(".btn-face-mood:enabled").count() == 1


def test_si_guardar_falla_se_avisa_y_se_puede_intentar_otra_vez(pagina, backend):
    abrir(pagina, backend)
    backend.poner("POST", "/estado-animo", {"success": False, "error": "x"}, estado=500)
    boton(pagina, "Bien").click()
    pagina.locator("#btn-guardar-animo").click()
    pagina.locator(".lumea-toast-item", has_text="No se pudo guardar tu ánimo").wait_for()
    assert pagina.locator("#btn-guardar-animo").is_enabled()
    assert pagina.locator(".celebracion__chip").count() == 0


def test_esta_semana_viene_del_backend_no_de_ejemplos(pagina, backend):
    backend.poner("GET", "/estado-animo", {"success": True, "cantidad": 0, "historial": []})
    abrir(pagina, backend)
    pagina.locator("#animo-semana-fila .animo-day-pill").first.wait_for()
    lectores = pagina.locator("#animo-semana-fila .solo-lector").all_inner_texts()
    assert len(lectores) == 7 and all("sin check-in" in t or "todavía no llega" in t for t in lectores)


def test_sin_internet_para_las_caras_queda_el_nombre(pagina, backend):
    abrir(pagina, backend)
    pagina.evaluate("document.querySelectorAll('img').forEach(i => i.dispatchEvent(new Event('error')))")
    assert pagina.locator(".btn-face-mood img").count() == 0
    assert [b.locator(".face-name-label").inner_text() for b in pagina.locator(".btn-face-mood").all()] == ESTADOS


def test_sin_sesion_lleva_a_iniciar_sesion(pagina):
    pagina.add_init_script("localStorage.clear()")
    pagina.goto(f"{pagina.servidor}/emociones.html")
    pagina.wait_for_url("**/iniciar-sesion.html")


def test_la_invitacion_a_hablar_es_texto_no_un_boton_falso(pagina, backend):
    abrir(pagina, backend)
    assert "Si te sientes mal varios días, hablar con alguien ayuda." in pagina.locator("main").inner_text()
    assert pagina.get_by_role("button", name="orientación").count() == 0        # no se promete un envío que no existe


@pytest.mark.parametrize("ancho", [375, 1280])
def test_no_se_desborda(pagina, backend, ancho):
    pagina.set_viewport_size({"width": ancho, "height": 800})
    abrir(pagina, backend)
    assert pagina.evaluate("document.documentElement.scrollWidth") <= ancho
