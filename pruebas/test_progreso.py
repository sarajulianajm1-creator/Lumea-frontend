"""progreso.html: nivel, racha, comidas y ánimo de la semana, bienvenida y estados."""
from datetime import datetime

import pytest

from conftest import cargar_respuesta

# El «hoy» de las pruebas: miércoles 7 de octubre de 2026 (la semana va del lunes 5 al domingo 11)
HOY = datetime(2026, 10, 7, 12, 0)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Todas estas pruebas corren en hora de Colombia (UTC-5): ahí se nota si una fecha se lee mal."""
    return {**browser_context_args, "timezone_id": "America/Bogota", "locale": "es-CO"}


def fecha(dia):
    """La fecha como la manda el backend: medianoche en UTC, «Mon, 05 Oct 2026 00:00:00 GMT»."""
    nombres = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    d = datetime(2026, 10, dia)
    return f"{nombres[d.weekday()]}, {dia:02d} Oct 2026 00:00:00 GMT"


def registro(id_, dia, codigo="arepa", fruta=False):
    return {"id": id_, "alimento_codigo": codigo, "alimento_detectado": codigo, "balanceado": 1, "calorias_aprox": 100,
            "certeza_ia": 90.0, "fecha": fecha(dia), "sellos_advertencia": [], "es_fruta": fruta}


def abrir(pagina, backend, progreso=None, historial=None, animo=None):
    pagina.clock.set_fixed_time(HOY)
    if progreso is not None:
        cuerpo = cargar_respuesta("progreso")
        cuerpo["progreso"].update(progreso)
        backend.poner("GET", "/progreso", cuerpo)
    if historial is not None:
        backend.poner("GET", "/historial", {"success": True, "cantidad_registros": len(historial), "historial": historial})
    if animo is not None:
        backend.poner("GET", "/estado-animo", {"success": True, "cantidad": len(animo), "historial": animo})
    pagina.goto(f"{pagina.servidor}/progreso.html")
    pagina.locator("#progreso-contenido").wait_for()


def texto(pagina, selector):
    return pagina.locator(selector).inner_text().strip()


def test_muestra_el_nivel_y_la_racha(pagina, backend):
    abrir(pagina, backend)
    assert texto(pagina, "#nivel-titulo") == "Nivel 2"
    assert texto(pagina, "#nivel-faltan") == "Te faltan 35 XP para el nivel 3"
    assert pagina.locator("#nivel-riel").get_attribute("aria-valuenow") == "13"        # (20-15)/(55-15)
    assert texto(pagina, "#racha-actual") == "3 días"
    assert texto(pagina, "#racha-mejor") == "5 días"
    assert texto(pagina, "#meta-hoy") == "Meta cumplida"
    assert texto(pagina, "#album-enlace") == "Mi álbum: 3 de 10 calcomanías"
    assert pagina.locator("#album-enlace").get_attribute("href") == "avatar.html#calcomanias"
    assert pagina.errores == []


def test_un_solo_h1_y_la_navegacion_marca_progreso(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("h1").count() == 1
    assert pagina.locator("nav a[aria-current=page]").inner_text().strip() == "Progreso"
    assert pagina.locator("nav a").all_inner_texts() != []


@pytest.mark.parametrize("racha,cifra", [(1, "1 día"), (2, "2 días"), (0, "0 días")])
def test_el_plural_de_la_racha(pagina, backend, racha, cifra):
    abrir(pagina, backend, progreso={"racha_actual": racha})
    assert texto(pagina, "#racha-actual") == cifra


def test_sin_racha_invita_sin_reproche(pagina, backend):
    abrir(pagina, backend, progreso={"racha_actual": 0, "racha_maxima": 0})
    nota = texto(pagina, "#racha-nota")
    assert nota == "Registra algo hoy para empezar una racha"
    contenido = pagina.locator("main").inner_text().lower()
    assert "perdiste" not in contenido and "perdido" not in contenido


def test_nivel_maximo(pagina, backend):
    abrir(pagina, backend, progreso={"nivel": 10, "xp_total": 1600, "xp_inicio_nivel": 1500,
                                     "xp_siguiente_nivel": None, "xp_faltante_siguiente_nivel": None})
    assert texto(pagina, "#nivel-faltan") == "Llegaste al nivel máximo"
    assert pagina.locator("#nivel-riel").get_attribute("aria-valuenow") == "100"


def test_la_barra_no_baja_de_cero_si_se_perdio_xp(pagina, backend):
    # Después de perder XP, el XP puede quedar por debajo del inicio del nivel
    abrir(pagina, backend, progreso={"xp_total": 10, "xp_inicio_nivel": 15, "xp_siguiente_nivel": 55, "xp_faltante_siguiente_nivel": 45})
    assert pagina.locator("#nivel-riel").get_attribute("aria-valuenow") == "0"


def test_meta_sin_cumplir_dice_cuanto_lleva(pagina, backend):
    abrir(pagina, backend, progreso={"meta_diaria": {"xp_hoy": 10, "meta": 15, "cumplida": False}})
    assert texto(pagina, "#meta-hoy") == "10 de 15 XP"


def test_el_mensaje_de_regreso_es_una_bienvenida(pagina, backend):
    mensaje = "¡Te extrañamos! Tu nivel y todo lo que desbloqueaste siguen siendo tuyos."
    abrir(pagina, backend, progreso={"mensaje_regreso": mensaje, "xp_perdido_desde_ultima_visita": 15})
    assert texto(pagina, "#bienvenida") == mensaje
    assert "perdiste" not in pagina.locator("main").inner_text().lower()


def test_sin_mensaje_de_regreso_no_hay_bienvenida(pagina, backend):
    abrir(pagina, backend)
    assert not pagina.locator("#bienvenida").is_visible()


def test_comidas_de_la_semana_con_fruta(pagina, backend):
    historial = [registro(1, 7, "banano", fruta=True), registro(2, 7), registro(3, 5), registro(4, 4)]   # el 4 es de la semana pasada
    abrir(pagina, backend, historial=historial)
    dias = pagina.locator("#semana-comidas li")
    assert dias.count() == 7
    lectores = [t.strip() for t in dias.locator(".solo-lector").all_inner_texts()]
    assert lectores == [
        "Lunes: 1 comida", "Martes: 0 comidas", "Miércoles: 2 comidas, con fruta",
        "Jueves: todavía no llega", "Viernes: todavía no llega", "Sábado: todavía no llega", "Domingo: todavía no llega"]
    # La fruta se marca con un ícono (no solo con color), y hoy está señalado
    assert dias.nth(2).locator("svg.semana__fruta").count() == 1
    assert dias.locator("svg.semana__fruta").count() == 1
    assert pagina.locator("#semana-comidas li[aria-current=date]").count() == 1
    assert dias.nth(2).get_attribute("aria-current") == "date"


def test_las_fechas_del_servidor_se_leen_en_utc(pagina, backend):
    # «Wed, 07 Oct 2026 00:00:00 GMT» es el miércoles 7 aunque en Colombia sean las 7 p. m. del martes
    pagina.context.set_default_timeout(5000)
    abrir(pagina, backend, historial=[registro(1, 7)])
    assert "Miércoles: 1 comida" in pagina.locator("#semana-comidas").inner_text()


def test_animo_de_la_semana_con_las_caras_del_avatar(pagina, backend):
    animo = [{"id": 3, "estado": "bien", "fecha": fecha(7)}, {"id": 2, "estado": "mal", "fecha": fecha(7)},    # el último del día manda
             {"id": 1, "estado": "neutral", "fecha": fecha(5)}]
    abrir(pagina, backend, animo=animo)
    lectores = [t.strip() for t in pagina.locator("#semana-animo .solo-lector").all_inner_texts()]
    assert lectores[:3] == ["Lunes: Neutral", "Martes: sin check-in", "Miércoles: Bien"]
    assert pagina.locator("#semana-animo img").count() == 2          # una cara por día con check-in
    src = pagina.locator("#semana-animo img").last.get_attribute("src")
    assert "mouth=smile" in src                                       # la cara de «bien» del avatar


def test_sin_internet_para_las_caras_queda_el_nombre(pagina, backend):
    abrir(pagina, backend, animo=[{"id": 1, "estado": "bien", "fecha": fecha(7)}])
    pagina.evaluate("document.querySelectorAll('#semana-animo img').forEach(i => i.dispatchEvent(new Event('error')))")
    assert pagina.locator("#semana-animo img").count() == 0
    assert "Bien" in pagina.locator("#semana-animo").inner_text()


def test_si_faltan_los_campos_nuevos_la_pantalla_funciona(pagina, backend):
    cuerpo = cargar_respuesta("progreso")
    del cuerpo["progreso"]["calcomanias"]
    backend.poner("GET", "/progreso", cuerpo)
    backend.poner("GET", "/historial", {"success": False, "error": "x"}, estado=500)
    backend.poner("GET", "/estado-animo", {"success": False, "error": "x"}, estado=500)
    pagina.clock.set_fixed_time(HOY)
    pagina.goto(f"{pagina.servidor}/progreso.html")
    pagina.locator("#progreso-contenido").wait_for()
    assert not pagina.locator("#album-enlace").is_visible()
    assert not pagina.locator("#semana-comidas-caja").is_visible()
    assert not pagina.locator("#semana-animo-caja").is_visible()
    assert texto(pagina, "#nivel-titulo") == "Nivel 2"


def test_sin_sesion_pide_iniciar_sesion(pagina):
    pagina.add_init_script("localStorage.clear()")
    pagina.goto(f"{pagina.servidor}/progreso.html")
    pagina.locator("#sin-sesion").wait_for()
    assert not pagina.locator("#progreso-contenido").is_visible()
    assert pagina.get_by_role("link", name="Iniciar sesión").get_attribute("href") == "iniciar-sesion.html"


def test_error_de_conexion_se_puede_reintentar(pagina, backend):
    backend.poner("GET", "/progreso", {"success": False, "error": "x"}, estado=500)
    pagina.goto(f"{pagina.servidor}/progreso.html")
    pagina.locator("#estado-error").wait_for()
    assert not pagina.locator("#progreso-contenido").is_visible()
    backend.respuestas.clear()                                         # el backend vuelve
    pagina.get_by_role("button", name="Intentar otra vez").click()
    pagina.locator("#progreso-contenido").wait_for()
    assert texto(pagina, "#nivel-titulo") == "Nivel 2"


def test_no_hay_calorias_ni_comparaciones(pagina, backend):
    abrir(pagina, backend, historial=[registro(1, 7)])
    contenido = pagina.locator("main").inner_text().lower()
    for prohibido in ("kcal", "caloría", "ranking", "otros usuarios", "mejor que"):
        assert prohibido not in contenido


def test_a_375px_no_se_desborda(pagina, backend):
    pagina.set_viewport_size({"width": 375, "height": 800})
    abrir(pagina, backend, historial=[registro(i, 5 + i % 3) for i in range(1, 10)],
          animo=[{"id": 1, "estado": "muy_bien", "fecha": fecha(7)}])
    assert pagina.evaluate("document.documentElement.scrollWidth") <= 375
