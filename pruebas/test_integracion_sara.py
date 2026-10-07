"""La unión con las pantallas de Sara: una sola conexión (api.js, puerto 5002), una sola sesión,
sin fetch escritos a mano y sin innerHTML con texto del servidor."""
from pathlib import Path

import pytest

from conftest import RAIZ, sin_sesion

PAGINAS_DE_SARA = ["index-ingresado.html", "progreso.html", "emociones.html", "crear-cuenta.html", "iniciar-sesion.html"]
SCRIPTS_DE_SARA = ["lumea-state.js", "lumea-ui.js", "indexx.js", "progreso.js", "emociones.js", "formato.js", "menu-privado.js"]


def leer(nombre):
    return (Path(RAIZ) / nombre).read_text(encoding="utf-8")


@pytest.mark.parametrize("nombre", SCRIPTS_DE_SARA + PAGINAS_DE_SARA)
def test_no_hay_direcciones_ni_fetch_escritos_a_mano(nombre):
    texto = leer(nombre)
    for prohibido in ("fetch(", "127.0.0.1", "localhost", "LUMEA_BACKEND_URLS", "5001", "5000", "?email=", "urlParams"):
        assert prohibido not in texto, f"{nombre} tiene «{prohibido}»: la conexión es solo api.js"


def test_api_js_es_el_unico_lugar_con_la_direccion_del_backend():
    asi = [n for n in sorted(p.name for p in Path(RAIZ).glob("*.js")) if "5002" in leer(n)]
    assert asi == ["api.js"]


@pytest.mark.parametrize("nombre", SCRIPTS_DE_SARA)
def test_el_texto_del_servidor_nunca_es_html(nombre):
    assert "innerHTML" not in leer(nombre), f"{nombre} escribe con innerHTML"


@pytest.mark.parametrize("nombre", ["index-ingresado.html", "progreso.html", "emociones.html"])
def test_ninguna_pantalla_pide_a_otro_puerto(pagina, backend, nombre):
    pedidas = []
    pagina.on("request", lambda r: pedidas.append(r.url))
    pagina.goto(f"{pagina.servidor}/{nombre}")
    pagina.wait_for_load_state("networkidle")
    assert [u for u in pedidas if ":5001" in u or ":5000" in u or "localhost" in u] == []
    assert any(":5002/progreso" in u for u in pedidas)
    assert pagina.errores == []


def correos_pedidos(backend, ruta="/progreso"):
    return {u.split("email=")[1].split("&")[0].replace("%40", "@") for m, u, _ in backend.peticiones if m == "GET" and ruta in u and "email=" in u}


def test_el_correo_de_la_url_se_ignora(pagina, backend):
    pagina.goto(f"{pagina.servidor}/progreso.html?email=intruso@lumea.test")
    pagina.locator("#progreso-contenido").wait_for()
    assert correos_pedidos(backend) == {"prueba@lumea.test"}


def test_la_clave_vieja_de_sara_tambien_es_la_sesion(pagina, backend):
    pagina.add_init_script("localStorage.removeItem('lumea_email'); localStorage.setItem('lumea_usuario_email', 'sara@lumea.test')")
    pagina.goto(f"{pagina.servidor}/progreso.html")
    pagina.locator("#progreso-contenido").wait_for()
    assert correos_pedidos(backend) == {"sara@lumea.test"}


def test_guardar_sesion_deja_una_sola_clave(pagina):
    pagina.goto(f"{pagina.servidor}/iniciar-sesion.html")
    claves = pagina.evaluate("""() => { localStorage.setItem('lumea_usuario_email', 'vieja@lumea.test');
        guardarSesion('nueva@lumea.test');
        return [localStorage.getItem('lumea_email'), localStorage.getItem('lumea_usuario_email'), obtenerSesion()]; }""")
    assert claves == ["nueva@lumea.test", None, "nueva@lumea.test"]


def test_iniciar_sesion_guarda_la_sesion_y_lleva_a_inicio(pagina, backend):
    backend.poner("POST", "/login", {"success": True, "perfil": {"nombre": "Ana", "email": "ana@lumea.test"}})
    sin_sesion(pagina)
    pagina.goto(f"{pagina.servidor}/iniciar-sesion.html")
    pagina.fill("#correo", "ana@lumea.test")
    pagina.fill("#contrasena", "clave-de-prueba")
    pagina.get_by_role("button", name="Entrar a LUMEA").click()
    pagina.wait_for_url("**/index-ingresado.html")
    assert pagina.evaluate("localStorage.getItem('lumea_email')") == "ana@lumea.test"
    assert ("POST", "/login") in backend.llamadas


def test_el_formulario_de_login_no_manda_la_contrasena_por_la_url(pagina):
    pagina.goto(f"{pagina.servidor}/iniciar-sesion.html")
    assert pagina.locator("#loginForm").get_attribute("method").lower() == "post"


def test_crear_cuenta_manda_la_contrasena_a_la_api_y_entra(pagina, backend):
    backend.poner("POST", "/perfil", {"success": True, "mensaje": "Perfil guardado."})
    sin_sesion(pagina)
    pagina.goto(f"{pagina.servidor}/crear-cuenta.html")
    pagina.fill("#nombre", "Ana")
    pagina.fill("#email", "ana@lumea.test")
    pagina.fill("#edad", "15")
    pagina.select_option("#genero", "otro")
    pagina.fill("#peso", "55")
    pagina.fill("#altura", "165")
    pagina.fill("#contrasena", "clave-de-prueba")
    pagina.locator("input[name=objetivo]").first.check(force=True)
    pagina.locator("#terminosCheck").check()
    pagina.locator("#btnSubmit").click()
    pagina.wait_for_url("**/index-ingresado.html")
    cuerpo = next(c for m, u, c in backend.peticiones if m == "POST" and u.endswith("/perfil"))
    assert '"contraseña":"clave-de-prueba"' in cuerpo.replace(" ", "")
    assert pagina.evaluate("localStorage.getItem('lumea_email')") == "ana@lumea.test"


def test_el_error_del_servidor_en_el_registro_se_escribe_como_texto(pagina, backend):
    backend.poner("POST", "/perfil", {"success": False, "error": "<img src=x onerror=window.__roto=1>"}, estado=400)
    pagina.add_init_script("localStorage.clear()")
    pagina.goto(f"{pagina.servidor}/crear-cuenta.html")
    for campo, valor in (("nombre", "Ana"), ("email", "ana@lumea.test"), ("edad", "15"), ("peso", "55"), ("altura", "165"), ("contrasena", "clave-de-prueba")):
        pagina.fill(f"#{campo}", valor)
    pagina.select_option("#genero", "otro")
    pagina.locator("input[name=objetivo]").first.check(force=True)
    pagina.locator("#terminosCheck").check()
    pagina.locator("#btnSubmit").click()
    pagina.locator("#alertFeedback").get_by_text("onerror").wait_for()
    assert pagina.locator("#alertFeedback img").count() == 0
    assert pagina.evaluate("window.__roto") is None
