"""index-ingresado.html (Inicio, el diseño es de Sara): la canasta, la meta, las misiones y el check-in rápido."""
import json
from datetime import datetime

import pytest

from conftest import cargar_respuesta

HOY = datetime(2026, 10, 5, 12, 0)        # el lunes 5 de oct: en historial.json hay un banano ese día
CORTO = "LumeaCelebrar.tiempos.xp = 300; LumeaCelebrar.tiempos.mision = 300; LumeaCelebrar.tiempos.salida = 60;"


def abrir(pagina, backend, **cambios):
    cuerpo = cargar_respuesta("progreso")
    cuerpo["progreso"].update(cambios)
    backend.poner("GET", "/progreso", cuerpo)
    pagina.clock.set_fixed_time(HOY)
    pagina.goto(f"{pagina.servidor}/index-ingresado.html")
    pagina.locator("main .nivel-badge", has_text="Nivel").wait_for()
    pagina.evaluate(CORTO)


def texto(pagina, selector):
    return pagina.locator(selector).first.inner_text().strip()


def test_el_saludo_es_el_unico_h1_con_el_nombre(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("h1").count() == 1
    assert texto(pagina, "h1") == "Hola, Ana"


@pytest.mark.parametrize("racha,cifra", [(0, "0 días"), (1, "1 día"), (3, "3 días")])
def test_el_plural_de_la_racha(pagina, backend, racha, cifra):
    abrir(pagina, backend, racha_actual=racha)
    assert texto(pagina, "main .lumea-bind-racha") == cifra


def test_meta_cumplida_no_dice_20_de_15(pagina, backend):
    abrir(pagina, backend, meta_diaria={"xp_hoy": 20, "meta": 15, "cumplida": True})
    assert texto(pagina, "#shape-xp .lumea-bind-xp-valor") == "Meta cumplida: 20 XP hoy"


def test_meta_sin_cumplir_dice_cuanto_lleva(pagina, backend):
    abrir(pagina, backend, meta_diaria={"xp_hoy": 10, "meta": 15, "cumplida": False})
    assert texto(pagina, "#shape-xp .lumea-bind-xp-valor") == "10 de 15 XP hoy"


def test_la_forma_de_xp_no_muestra_el_xp_total_del_nivel(pagina, backend):
    abrir(pagina, backend)
    assert "/55" not in pagina.locator("#shape-xp").inner_text()          # antes decía «210/250 XP del día»


def test_las_comidas_son_de_tres_no_de_quince(pagina, backend):
    abrir(pagina, backend)                                                  # un banano registrado el 5 de oct
    assert texto(pagina, "#shape-comidas .lumea-bind-comidas-count") == "1 de 3"
    assert "de 15" not in pagina.locator("main").inner_text()


def test_misiones_listas_y_proxima_mision_con_10_xp(pagina, backend):
    abrir(pagina, backend)                                                  # solo la fruta está cumplida
    assert texto(pagina, "#shape-misiones .lumea-bind-misiones-count") == "1 de 3"
    assert texto(pagina, "#proxima-mision-titulo") == "Registra 3 comidas"
    assert texto(pagina, "#proxima-mision-xp").startswith("+10 XP")        # antes decía +20


def test_con_las_tres_misiones_cumplidas_se_celebra_sin_pedir_mas(pagina, backend):
    misiones = [{"id": i, "nombre": n, "xp": 10, "cumplida": True}
                for i, n in (("fruta", "Registra una fruta"), ("tres_comidas", "Registra 3 comidas"), ("check_in_animo", "Haz tu check-in de ánimo"))]
    abrir(pagina, backend, misiones=misiones)
    assert texto(pagina, "#proxima-mision-titulo") == "Hoy cumpliste tus tres misiones"
    assert texto(pagina, "#shape-misiones .lumea-bind-misiones-count") == "3 de 3"


def test_nivel_y_cuanto_falta_con_el_numero_escrito(pagina, backend):
    abrir(pagina, backend)
    assert texto(pagina, ".card-racha-nivel .lumea-bind-xp-text") == "Te faltan 35 XP para el nivel 3"
    assert pagina.locator(".card-racha-nivel .progress-bar").get_attribute("aria-valuenow") == "13"


def test_el_animo_de_hoy_dice_su_nombre_y_muestra_la_cara_del_avatar(pagina, backend):
    abrir(pagina, backend)
    assert texto(pagina, "#shape-animo .lumea-bind-animo-hoy") == "Bien"
    assert pagina.locator("#shape-animo img").count() == 1
    assert "mouth=smile" in pagina.locator("#shape-animo img").get_attribute("src")


def test_sin_ver_aviso_de_regreso_es_la_bienvenida_del_backend(pagina, backend):
    mensaje = "¡Te extrañamos! Tu nivel y todo lo que desbloqueaste siguen siendo tuyos."
    abrir(pagina, backend, mensaje_regreso=mensaje)
    assert texto(pagina, "#aviso-regreso") == mensaje
    pagina.get_by_role("button", name="Cerrar el mensaje").click()
    assert not pagina.locator("#aviso-regreso").is_visible()
    assert "perdiste" not in pagina.locator("main").inner_text().lower()


def test_sin_mensaje_no_hay_aviso(pagina, backend):
    abrir(pagina, backend)
    assert not pagina.locator("#aviso-regreso").is_visible()


# ---------- Check-in rápido ----------

def sin_animo_hoy(backend):
    """Nadie ha hecho el check-in hoy: ni el avatar trae estado de hoy ni hay registros de ánimo."""
    cuerpo = cargar_respuesta("progreso")
    cuerpo["progreso"]["avatar"]["estado_animo_hoy"] = None
    backend.poner("GET", "/progreso", cuerpo)
    backend.poner("GET", "/estado-animo", {"success": True, "cantidad": 0, "historial": []})
    return cuerpo["progreso"]["avatar"]


def test_el_checkin_rapido_usa_las_caras_del_avatar_y_cinco_estados(pagina, backend):
    abrir(pagina, backend, avatar=sin_animo_hoy(backend))
    botones = pagina.locator(".card-animo-checkin .btn-face-mood")
    assert [b.locator(".face-name-label").inner_text() for b in botones.all()] == ["Muy mal", "Mal", "Neutral", "Bien", "Muy bien"]
    assert botones.locator("img").count() == 5
    assert botones.locator("img").nth(0).get_attribute("src") != botones.locator("img").nth(4).get_attribute("src")


def test_el_checkin_rapido_guarda_celebra_y_queda_registrado(pagina, backend):
    abrir(pagina, backend, avatar=sin_animo_hoy(backend))
    # tras guardar, el backend ya trae el ánimo de hoy
    despues = cargar_respuesta("progreso")
    despues["progreso"]["avatar"]["estado_animo_hoy"] = "mal"
    backend.poner("GET", "/progreso", despues)
    backend.respuestas.pop(("GET", "/estado-animo"))
    pagina.locator(".card-animo-checkin .btn-face-mood", has=pagina.get_by_text("Mal", exact=True)).click()
    pagina.locator(".celebracion__chip").first.wait_for()
    assert pagina.locator(".celebracion__chip").first.inner_text() == "+5 XP"
    envio = next(c for m, u, c in backend.peticiones if m == "POST" and u.endswith("/estado-animo"))
    assert json.loads(envio) == {"email": "prueba@lumea.test", "estado": "mal"}
    pagina.locator("#checkin-confirmado").wait_for()
    assert "Mal" in pagina.locator("#checkin-confirmado").inner_text()
    assert pagina.locator(".card-animo-checkin .btn-face-mood:enabled").count() == 1       # solo queda el elegido


def test_el_rebote_de_la_canasta_respeta_el_movimiento_reducido(pagina, backend):
    pagina.emulate_media(reduced_motion="reduce")
    abrir(pagina, backend)
    duracion = pagina.evaluate("""() => { const e = document.getElementById('shape-animo'); e.classList.add('animate-shape-bounce');
        return getComputedStyle(e).animationName; }""")
    assert duracion == "none"


# ---------- Foto directa ----------

def test_foto_directa_pasa_a_la_camara_y_se_analiza(pagina, backend, foto):
    abrir(pagina, backend)
    pagina.set_input_files("#input-foto-directa-home", str(foto))
    pagina.wait_for_url("**/alimentos.html")
    pagina.locator("#backend-alimento", has_text="Arepa").wait_for()
    assert ("POST", "/predecir") in backend.llamadas
    assert pagina.evaluate("sessionStorage.getItem('lumea_foto_temporal')") is None      # la foto no se queda guardada


# ---------- Forma ----------

def test_no_hay_emojis_de_icono_ni_mayusculas_decorativas(pagina, backend):
    abrir(pagina, backend)
    for emoji in ("🔥", "⭐", "🧺", "🍃", "🚩", "💛", "✨", "🌿", "🙂"):
        assert emoji not in pagina.locator("body").inner_text()
    mayusculas = pagina.evaluate("""[...document.querySelectorAll('main *')]
        .filter(e => e.textContent.trim() && getComputedStyle(e).textTransform === 'uppercase').map(e => e.className)""")
    assert mayusculas == []


def test_a_375px_no_se_desborda(pagina, backend):
    pagina.set_viewport_size({"width": 375, "height": 800})
    abrir(pagina, backend)
    assert pagina.evaluate("document.documentElement.scrollWidth") <= 375
