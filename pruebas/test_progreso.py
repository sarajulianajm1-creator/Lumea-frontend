"""progreso.html (rediseño R6, conectado por api.js): nivel, racha, comidas y ánimo de la semana, el álbum, la bienvenida y los estados."""
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
    return pagina.locator(selector).first.inner_text().strip()


def test_muestra_el_nivel_y_la_racha(pagina, backend):
    abrir(pagina, backend)
    assert texto(pagina, "main .lumea-bind-nivel") == "Etapa 2"
    assert texto(pagina, "main .progreso-faltan") == "Te faltan 35 semillas para la etapa 3"
    assert pagina.locator("main [role=progressbar]").get_attribute("aria-valuenow") == "30"        # (45-30)/(80-30)
    assert texto(pagina, "main .lumea-bind-racha") == "3 días"
    assert texto(pagina, "main .lumea-bind-mejor-racha") == "5 días"
    assert texto(pagina, "#meta-hoy-chip") == "Meta cumplida: 20 semillas hoy"
    assert texto(pagina, "#album-enlace") == "Mi álbum: 3 de 10 calcomanías"
    assert pagina.locator("#album-enlace").get_attribute("href") == "avatar.html#calcomanias"
    assert pagina.errores == []


def test_el_menu_lateral_muestra_nombre_y_nivel(pagina, backend):
    # Rediseño R1: la zona de usuario del menú es delgada (nombre, nivel y «Cerrar sesión»); la racha
    # ya no va ahí, está en esta pantalla (ver test_muestra_el_nivel_y_la_racha) y en Inicio.
    abrir(pagina, backend)
    pagina.locator(".nav-app__nivel", has_text="Etapa 2").wait_for()
    usuario = pagina.locator(".nav-app__usuario")
    assert "Ana" in usuario.inner_text() and "Etapa 2" in usuario.inner_text()


def test_un_solo_h1_sin_version_ni_emojis_de_icono(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("h1").count() == 1 and texto(pagina, "h1") == "Tu progreso"
    contenido = pagina.locator("body").inner_text()
    assert "Versión" not in contenido
    for emoji in ("🔥", "⭐", "🍎", "💛", "🙂", "😄"):
        assert emoji not in contenido


@pytest.mark.parametrize("racha,cifra", [(0, "0 días"), (1, "1 día"), (3, "3 días")])
def test_el_plural_de_la_racha(pagina, backend, racha, cifra):
    abrir(pagina, backend, progreso={"racha_actual": racha})
    assert texto(pagina, "main .lumea-bind-racha") == cifra


def test_sin_racha_invita_sin_reproche(pagina, backend):
    abrir(pagina, backend, progreso={"racha_actual": 0})
    nota = texto(pagina, "main .lumea-bind-racha-nota")
    assert nota == "Registra algo hoy para empezar una racha"


def test_nivel_maximo(pagina, backend):
    abrir(pagina, backend, progreso={"nivel": 10, "xp_siguiente_nivel": None, "xp_faltante_siguiente_nivel": None})
    assert texto(pagina, "main .progreso-faltan") == "Llegaste a la etapa máxima"
    assert pagina.locator("main [role=progressbar]").get_attribute("aria-valuenow") == "100"


def test_la_barra_no_baja_de_cero_si_se_perdio_xp(pagina, backend):
    abrir(pagina, backend, progreso={"xp_total": 10, "xp_inicio_nivel": 15, "xp_faltante_siguiente_nivel": 45})
    assert pagina.locator("main [role=progressbar]").get_attribute("aria-valuenow") == "0"


def test_la_meta_es_de_semillas_no_de_comidas_ni_semillas_de_la_etapa(pagina, backend):
    abrir(pagina, backend, progreso={"meta_diaria": {"xp_hoy": 10, "meta": 15, "cumplida": False}})
    assert texto(pagina, "#meta-hoy-chip") == "10 de 15 semillas hoy"
    contenido = pagina.locator("main").inner_text()
    assert "de 15 comidas" not in contenido and "/55 semillas" not in contenido


def test_el_mensaje_de_regreso_es_una_bienvenida(pagina, backend):
    mensaje = "¡Te extrañamos! Tu nivel y todo lo que desbloqueaste siguen siendo tuyos."
    abrir(pagina, backend, progreso={"mensaje_regreso": mensaje, "xp_perdido_desde_ultima_visita": 15})
    assert pagina.locator("#aviso-regreso").is_visible()
    assert texto(pagina, "#aviso-regreso") == mensaje
    assert "perdiste" not in pagina.locator("main").inner_text().lower()
    assert "no te penaliza" not in pagina.locator("main").inner_text().lower()      # no se promete lo que el backend no hace


def test_sin_mensaje_de_regreso_no_hay_bienvenida(pagina, backend):
    abrir(pagina, backend)
    assert not pagina.locator("#aviso-regreso").is_visible()


def test_comidas_de_la_semana_con_fruta(pagina, backend):
    historial = [registro(1, 7, "banano", fruta=True), registro(2, 7), registro(3, 5), registro(4, 4)]   # el 4 es de la semana pasada
    abrir(pagina, backend, historial=historial)
    dias = pagina.locator("#grafica-barras-semana .bar-col-item")
    assert dias.count() == 7
    lectores = [t.strip() for t in dias.locator(".solo-lector").all_inner_texts()]
    assert lectores == [
        "Lunes: 1 comida", "Martes: 0 comidas", "Miércoles (hoy): 2 comidas, con fruta",
        "Jueves: todavía no llega", "Viernes: todavía no llega", "Sábado: todavía no llega", "Domingo: todavía no llega"]
    # La fruta se marca con un ícono (no solo con color), y hoy está señalado
    assert dias.nth(2).locator(".bar-fruit-floating-icon").count() == 1
    assert dias.locator(".bar-fruit-floating-icon").count() == 1
    assert pagina.locator("#grafica-barras-semana [aria-current=date]").count() == 1
    assert dias.nth(2).get_attribute("aria-current") == "date"


def test_las_fechas_del_servidor_se_leen_en_utc(pagina, backend):
    # «Wed, 07 Oct 2026 00:00:00 GMT» es el miércoles 7 aunque en Colombia sean las 7 p. m. del martes
    pagina.context.set_default_timeout(5000)
    abrir(pagina, backend, historial=[registro(1, 7)])
    assert "Miércoles (hoy): 1 comida" in pagina.locator("#grafica-barras-semana").inner_text()


def test_la_semana_de_animo_va_quieta_y_es_la_cara_de_cada_estado_del_companero(pagina, backend):
    """K4: [data-cara]/dibujarSemanaAnimo ya usan urls_por_estado; ninguna se anima, ni en Progreso hay nada con movimiento."""
    animo = [{"id": 4, "estado": "bien", "fecha": fecha(7)}, {"id": 3, "estado": "muy_mal", "fecha": fecha(6)},
             {"id": 2, "estado": "neutral", "fecha": fecha(5)}]
    abrir(pagina, backend, animo=animo)
    imgs = pagina.locator("#animo-semana-fila img")
    assert imgs.count() == 3
    src = imgs.evaluate_all("e => e.map(i => i.src)")
    assert [s.split("eyesVariant=")[1] for s in src] == ["dots", "bars", "happy"]       # lunes, martes, miércoles
    assert all("animationVariant" not in s and "/10.x/gaze/" in s and "seed=lumea-sol" in s for s in src)   # quietas, del compañero
    assert imgs.evaluate_all("e => e.every(i => i.alt === '')")
    assert pagina.locator('img[src*="animationVariant=slow"], img[src*="animationVariant=medium"]').count() == 0


def test_animo_de_la_semana_con_las_caras_del_avatar(pagina, backend):
    animo = [{"id": 3, "estado": "bien", "fecha": fecha(7)}, {"id": 2, "estado": "mal", "fecha": fecha(7)},    # el último del día manda
             {"id": 1, "estado": "neutral", "fecha": fecha(5)}]
    abrir(pagina, backend, animo=animo)
    lectores = [t.strip() for t in pagina.locator("#animo-semana-fila .solo-lector").all_inner_texts()]
    assert lectores[:3] == ["Lunes: Neutral", "Martes: sin check-in", "Miércoles (hoy): Bien"]
    assert pagina.locator("#animo-semana-fila img").count() == 2          # una cara por día con check-in
    src = pagina.locator("#animo-semana-fila img").last.get_attribute("src")
    assert "eyesVariant=happy" in src                                           # la cara de «bien» del avatar


def test_sin_internet_para_las_caras_queda_el_nombre(pagina, backend):
    abrir(pagina, backend, animo=[{"id": 1, "estado": "bien", "fecha": fecha(7)}])
    pagina.evaluate("document.querySelectorAll('#animo-semana-fila img').forEach(i => i.dispatchEvent(new Event('error')))")
    assert pagina.locator("#animo-semana-fila img").count() == 0
    assert "Bien" in pagina.locator("#animo-semana-fila").inner_text()


def test_el_enlace_al_checkin_dice_si_ya_se_hizo(pagina, backend):
    abrir(pagina, backend)                                                 # la respuesta de prueba trae el ánimo de hoy
    assert texto(pagina, "#checkin-enlace-texto") == "Ver mi check-in de hoy"
    cuerpo = cargar_respuesta("progreso")
    cuerpo["progreso"]["avatar"]["estado_animo_hoy"] = None
    backend.poner("GET", "/progreso", cuerpo)
    pagina.reload()
    pagina.locator("#progreso-contenido").wait_for()
    assert texto(pagina, "#checkin-enlace-texto") == "Hacer mi check-in de hoy"


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
    assert texto(pagina, "main .lumea-bind-nivel") == "Etapa 2"


def test_sin_sesion_lleva_a_iniciar_sesion(pagina):
    pagina.add_init_script("localStorage.clear()")
    pagina.goto(f"{pagina.servidor}/progreso.html")
    pagina.wait_for_url("**/iniciar-sesion.html")


def test_error_de_conexion_se_puede_reintentar(pagina, backend):
    backend.poner("GET", "/progreso", {"success": False, "error": "x"}, estado=500)
    pagina.goto(f"{pagina.servidor}/progreso.html")
    pagina.locator("#estado-error").wait_for()
    assert not pagina.locator("#progreso-contenido").is_visible()
    backend.respuestas.clear()                                         # el backend vuelve
    pagina.get_by_role("button", name="Intentar otra vez").click()
    pagina.locator("#progreso-contenido").wait_for()
    assert texto(pagina, "main .lumea-bind-nivel") == "Etapa 2"


def test_no_hay_calorias_ni_comparaciones(pagina, backend):
    abrir(pagina, backend, historial=[registro(1, 7)])
    contenido = pagina.locator("main").inner_text().lower()
    for prohibido in ("kcal", "caloría", "ranking", "otros usuarios", "mejor que"):
        assert prohibido not in contenido


def test_sin_mayusculas_decorativas(pagina, backend):
    abrir(pagina, backend, historial=[registro(1, 7)])
    transformaciones = pagina.evaluate("""[...document.querySelectorAll('main *')]
        .filter(e => e.textContent.trim() && getComputedStyle(e).textTransform === 'uppercase').map(e => e.className)""")
    assert transformaciones == []


def test_a_375px_no_se_desborda(pagina, backend):
    pagina.set_viewport_size({"width": 375, "height": 800})
    abrir(pagina, backend, historial=[registro(i, 5 + i % 3) for i in range(1, 10)],
          animo=[{"id": 1, "estado": "muy_bien", "fecha": fecha(7)}])
    assert pagina.evaluate("document.documentElement.scrollWidth") <= 375


# ---------- Rediseño R6: cinco superficies, sin flecha y sin Bootstrap ----------

def test_cinco_superficies_como_maximo(pagina, backend):
    abrir(pagina, backend)
    tarjetas = pagina.locator("main .tarjeta")
    assert tarjeta_nombres(tarjetas) == ["Nivel", "Racha", "Comidas de la semana", "Tu ánimo de la semana"]      # nivel, racha, comidas, ánimo
    assert pagina.locator("#album-enlace").is_visible()                                                         # y el enlace al álbum
    assert tarjetas.count() + pagina.locator("#album-enlace").count() <= 5
    assert pagina.locator("#album-enlace.tarjeta").count() == 0                                                 # el álbum es una franja plana


def tarjeta_nombres(tarjetas):
    """Cada tarjeta se nombra por su título (el h2 de su aria-labelledby); la del nivel lo tiene dinámico."""
    nombres = []
    for t in tarjetas.all():
        titulo = t.locator("h2").first.inner_text().strip()
        nombres.append("Nivel" if "semilla" in titulo or "etapa" in titulo.lower() else titulo)
    return nombres


def test_no_hay_flecha_de_volver_ni_el_boton_del_avatar_de_arriba(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("main .bi-arrow-left").count() == 0
    assert pagina.get_by_role("link", name="Volver a Inicio").count() == 0
    assert pagina.locator("main .avatar-header-btn").count() == 0                                               # el menú ya lleva a Avatar


def test_progreso_ya_no_carga_bootstrap_ni_los_estilos_de_sara(pagina, backend):
    abrir(pagina, backend)
    hojas = pagina.eval_on_selector_all("link[rel=stylesheet]", "e => e.map(x => x.getAttribute('href'))")
    assert not any("bootstrap.min.css" in h or h.endswith("style.css") or "sara" in h for h in hojas)
    assert pagina.locator("[class*='btn-'], .card, .rounded-4, .shadow-sm, .bg-white").count() == 0               # ni una clase de Bootstrap


def test_la_jerarquia_es_titulo_seccion_y_cuerpo(pagina, backend):
    abrir(pagina, backend)
    tam = lambda sel: pagina.locator(sel).first.evaluate("e => parseFloat(getComputedStyle(e).fontSize)")
    assert tam("h1") == pytest.approx(31.25, abs=0.1)            # --t-2xl: el título de la pantalla
    assert tam("#titulo-comidas") == 20                          # --t-l: una sección
    assert tam("#titulo-nivel") == 20


def test_la_racha_es_una_sola_superficie_con_la_actual_y_la_mejor(pagina, backend):
    abrir(pagina, backend)
    racha = pagina.locator("section[aria-labelledby=titulo-racha]")
    assert racha.locator(".progreso__racha").count() == 2
    assert "Racha actual" in racha.inner_text() and "Mejor racha" in racha.inner_text()
    assert racha.locator("i.bi-fire, i.bi-star-fill").count() == 2                                              # Bootstrap Icons, no emojis


def test_el_enlace_al_checkin_es_secundario_y_la_pantalla_no_tiene_boton_relleno(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("main .boton:not(.boton--secundario):not(.boton--fantasma)").count() == 0
    assert pagina.get_by_role("link", name="Ver mi check-in de hoy").get_attribute("class") == "boton boton--secundario"
    assert pagina.get_by_role("link", name="Ver mi armario").get_attribute("href") == "avatar.html#armario"


def test_progreso_en_celular_cabe_y_apila(pagina, backend):
    pagina.set_viewport_size({"width": 390, "height": 844})
    abrir(pagina, backend, historial=[registro(i, 5 + i % 3) for i in range(1, 8)])
    assert pagina.evaluate("document.documentElement.scrollWidth") <= 390
    tops = pagina.evaluate("[...document.querySelectorAll('main .tarjeta')].map(e => e.getBoundingClientRect().top)")
    assert tops == sorted(tops) and len(set(tops)) == len(tops)                                                 # una debajo de otra
