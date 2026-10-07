"""alimentos.html (la cámara): sin sesión, IA segura, IA duda y confirmar."""
from conftest import cargar_respuesta


def abrir(pagina, sesion=True):
    if not sesion:
        pagina.add_init_script("localStorage.removeItem('lumea_email')")
    pagina.goto(f"{pagina.servidor}/alimentos.html")


def test_sin_sesion_se_ve_el_aviso(pagina):
    pagina.add_init_script("localStorage.clear()")   # corre después y borra la sesión de prueba
    abrir(pagina, sesion=False)
    assert pagina.locator("#sin-sesion").is_visible()
    assert pagina.locator("#flujo-registro").get_attribute("hidden") is not None


def test_sin_sesion_la_camara_no_se_ve(pagina):
    # Antes era un error real: .lumea-dashboard-screen (style.css) anulaba [hidden].
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


def test_ia_duda_en_un_grupo_agrupa_las_opciones(pagina, backend, foto):
    backend.poner("POST", "/predecir", cargar_respuesta("predecir_grupo"))
    abrir(pagina)
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#backend-opciones button").first.wait_for()
    assert pagina.locator("#backend-alimento").inner_text() == "¿Cuál de estos es?"
    assert pagina.locator("#backend-opciones button").all_inner_texts() == ["Ajiaco", "Sancocho"]


def test_ia_duda_con_cualquier_plato_ofrece_tres_opciones(pagina, backend, foto):
    # Contrato del 5 oct: certeza baja -> hasta 3 opciones con grupo null y nombres largos.
    backend.poner("POST", "/predecir", cargar_respuesta("predecir_duda"))
    abrir(pagina)
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#backend-opciones button").first.wait_for()
    assert pagina.locator("#backend-alimento").inner_text() == "¿Cuál de estos es?"
    assert pagina.locator("#backend-opciones button").all_inner_texts() == [
        "Arepa paisa (de maíz precocido, con sal)", "Huevo de gallina, entero, cocido", "Llapingachos (sin relleno)"]
    # Sin grupos no hay títulos de grupo, y el mensaje es amable (no el texto técnico del backend)
    assert pagina.locator(".opciones__grupo").count() == 0
    mensaje = pagina.locator("#backend-mensaje").inner_text()
    assert "La IA no está segura" in mensaje and "certeza" not in mensaje


def test_los_botones_de_nombre_largo_no_se_salen_en_375px(pagina, backend, foto):
    pagina.set_viewport_size({"width": 375, "height": 800})
    respuesta = cargar_respuesta("predecir_duda")
    respuesta["opciones_detalle"][0]["nombre"] = "Arepa paisa de maíz precocido con sal y mantequilla, rellena de queso campesino y hogao"
    backend.poner("POST", "/predecir", respuesta)
    abrir(pagina)
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#backend-opciones button").first.wait_for()
    # Ningún botón se sale del ancho de la pantalla, y la página no se desborda de lado
    cajas = pagina.eval_on_selector_all("#backend-opciones button", "e => e.map(b => b.getBoundingClientRect())")
    assert all(c["left"] >= 0 and c["right"] <= 375 for c in cajas)
    assert pagina.evaluate("document.documentElement.scrollWidth") <= 375


def test_confirmar_guarda_y_celebra(pagina, backend, foto):
    backend.poner("POST", "/predecir", cargar_respuesta("predecir_grupo"))
    abrir(pagina)
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.get_by_role("button", name="Ajiaco").click()
    pagina.locator("#backend-logros li", has_text="Misión cumplida").wait_for()
    assert ("POST", "/confirmar-alimento") in backend.llamadas
    textos = pagina.locator("#backend-logros").inner_text()
    assert "+20 XP" in textos and "Subiste al nivel 3" in textos
    assert "Calcomanía nueva: Tres al día" in textos
