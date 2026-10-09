"""Crear cuenta (decisiones de Isabella, 8 de octubre): sin peso ni altura, edad mínima de 11 años
y casilla para menores de 18 que se envía como `acudiente_sabe: true`."""
import json

MENSAJE_EDAD = "Lumea es para personas de 11 años en adelante."


def llenar(pagina, edad):
    pagina.add_init_script("localStorage.clear()")
    pagina.goto(f"{pagina.servidor}/crear-cuenta.html")
    pagina.fill("#nombre", "Ana")
    pagina.fill("#email", "ana@lumea.test")
    pagina.fill("#edad", str(edad))
    pagina.select_option("#genero", "otro")
    pagina.fill("#contrasena", "clave-de-prueba")
    pagina.locator("input[name=objetivo]").first.check(force=True)
    pagina.locator("#terminosCheck").check()


def perfiles_enviados(backend):
    return [json.loads(c) for m, u, c in backend.peticiones if m == "POST" and u.endswith("/perfil")]


def test_el_formulario_ya_no_pide_peso_ni_altura(pagina):
    pagina.goto(f"{pagina.servidor}/crear-cuenta.html")
    assert pagina.locator("#peso, #altura, [name=peso], [name=altura]").count() == 0
    assert pagina.get_by_text("Peso", exact=False).count() == 0 and pagina.get_by_text("Altura", exact=False).count() == 0


def test_el_payload_no_lleva_peso_ni_altura(pagina, backend):
    backend.poner("POST", "/perfil", {"success": True, "mensaje": "Perfil guardado."})
    llenar(pagina, 20)
    pagina.locator("#btnSubmit").click()
    pagina.wait_for_url("**/index-ingresado.html")
    (perfil,) = perfiles_enviados(backend)
    assert "peso" not in perfil and "altura" not in perfil and "acudiente_sabe" not in perfil


def test_con_10_anos_no_se_envia_y_el_error_esta_conectado(pagina, backend):
    llenar(pagina, 10)
    pagina.locator("#btnSubmit").click()
    assert perfiles_enviados(backend) == []
    assert pagina.locator("#edad").get_attribute("min") == "11"
    error = pagina.locator("#edad-error")
    assert error.is_visible() and error.inner_text() == MENSAJE_EDAD
    assert "edad-error" in pagina.locator("#edad").get_attribute("aria-describedby")


def test_con_15_anos_sin_la_casilla_no_se_envia_y_con_ella_si(pagina, backend):
    backend.poner("POST", "/perfil", {"success": True, "mensaje": "Perfil guardado."})
    llenar(pagina, 15)
    bloque = pagina.locator("#acudiente-bloque")
    assert bloque.is_visible()
    assert pagina.get_by_label("Mi madre, padre o acudiente sabe que uso Lumea").is_visible()
    assert pagina.locator("#acudiente").get_attribute("required") is not None
    pagina.locator("#btnSubmit").click()
    assert perfiles_enviados(backend) == []
    assert pagina.locator("#acudiente-error").is_visible()
    assert "acudiente-error" in pagina.locator("#acudiente").get_attribute("aria-describedby")
    pagina.locator("#acudiente").check()
    pagina.locator("#btnSubmit").click()
    pagina.wait_for_url("**/index-ingresado.html")
    (perfil,) = perfiles_enviados(backend)
    assert perfil["acudiente_sabe"] is True and perfil["edad"] == 15


def test_con_20_anos_la_casilla_no_aparece_ni_es_obligatoria(pagina, backend):
    llenar(pagina, 20)
    assert pagina.locator("#acudiente-bloque").is_hidden()
    assert pagina.locator("#acudiente").get_attribute("required") is None


def test_si_la_edad_sube_a_18_la_casilla_marcada_no_se_envia(pagina, backend):
    backend.poner("POST", "/perfil", {"success": True, "mensaje": "Perfil guardado."})
    llenar(pagina, 15)
    pagina.locator("#acudiente").check()
    pagina.fill("#edad", "18")
    assert pagina.locator("#acudiente-bloque").is_hidden()
    pagina.locator("#btnSubmit").click()
    pagina.wait_for_url("**/index-ingresado.html")
    assert "acudiente_sabe" not in perfiles_enviados(backend)[0]
