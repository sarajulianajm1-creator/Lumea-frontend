"""index-ingresado.html (Inicio, rediseño R2): Tu día, el check-in, la misión de hoy y el nivel con la racha."""
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
    pagina.locator("main .lumea-bind-nivel", has_text="Etapa").first.wait_for()
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
    assert texto(pagina, ".inicio__dia .lumea-bind-xp-valor") == "Meta cumplida: 20 semillas hoy"


def test_meta_sin_cumplir_dice_cuanto_lleva(pagina, backend):
    abrir(pagina, backend, meta_diaria={"xp_hoy": 10, "meta": 15, "cumplida": False})
    assert texto(pagina, ".inicio__dia .lumea-bind-xp-valor") == "10 de 15 semillas hoy"


def test_tu_dia_no_muestra_el_xp_total_del_nivel(pagina, backend):
    abrir(pagina, backend)
    assert "/55" not in pagina.locator(".inicio__dia").inner_text()          # antes decía «210/250 XP del día»


def test_las_comidas_son_de_tres_no_de_quince(pagina, backend):
    abrir(pagina, backend)                                                  # un banano registrado el 5 de oct
    assert texto(pagina, ".inicio__dia .lumea-bind-comidas-count") == "1 de 3"
    assert texto(pagina, ".inicio__cifra") == "1 de 3 comidas"
    assert "de 15" not in pagina.locator("main").inner_text()
    barra = pagina.locator(".lumea-bind-comidas-bar")                       # la barra de la meta de comidas: 1 de 3
    assert barra.get_attribute("aria-valuenow") == "33" and barra.get_attribute("aria-label") == "Comidas registradas hoy"


def test_la_mision_de_hoy_es_la_proxima_con_su_chip_de_10_semillas(pagina, backend):
    abrir(pagina, backend)                                                  # solo la fruta está cumplida
    assert texto(pagina, ".inicio__franja[aria-labelledby=titulo-mision] .inicio__rotulo") == "Misión de hoy"
    assert texto(pagina, "#proxima-mision-titulo") == "Cuida de ti en tus tres comidas"
    assert texto(pagina, "#proxima-mision-xp") == "+10 semillas"                 # antes decía +20


def test_con_las_tres_misiones_cumplidas_se_celebra_sin_pedir_mas(pagina, backend):
    misiones = [{"id": i, "nombre": n, "xp": 10, "cumplida": True}
                for i, n in (("fruta", "Agradece y disfruta una fruta de la creación"), ("tres_comidas", "Cuida de ti en tus tres comidas"), ("check_in_animo", "Haz una pausa y escucha cómo te sientes"))]
    abrir(pagina, backend, misiones=misiones)
    assert texto(pagina, "#proxima-mision-titulo") == "Hoy cumpliste tus tres misiones"
    assert not pagina.locator("#proxima-mision-xp").is_visible()            # no hay recompensa que pedir


def test_nivel_y_cuanto_falta_con_el_numero_escrito(pagina, backend):
    abrir(pagina, backend)
    assert texto(pagina, ".inicio__nivel .lumea-bind-xp-text") == "Te faltan 35 semillas para la etapa 3"
    assert texto(pagina, ".inicio__nivel .lumea-bind-racha") == "3 días"
    assert pagina.locator(".inicio__nivel [role=progressbar]").get_attribute("aria-valuenow") == "30"
    assert pagina.locator("a.inicio__nivel").get_attribute("href") == "progreso.html"       # la franja enlaza a Progreso


def test_si_ya_hizo_el_checkin_hoy_se_ve_su_estado_y_no_se_puede_cambiar(pagina, backend):
    abrir(pagina, backend)                                                  # progreso.json trae «bien» como ánimo de hoy
    assert "Bien" in texto(pagina, "#checkin-confirmado")
    elegida = pagina.locator(".animo-cara[aria-pressed=true]")
    assert elegida.count() == 1 and elegida.inner_text().strip() == "Bien"
    assert pagina.locator(".animo-cara:enabled").count() == 1               # los otros cuatro quedan en reposo
    assert not pagina.locator("#btn-guardar-animo-inicio").is_visible()


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


def test_el_checkin_tiene_cinco_estados_con_su_palabra_y_sin_xp(pagina, backend):
    abrir(pagina, backend, avatar=sin_animo_hoy(backend))
    botones = pagina.locator(".inicio__animo .animo-cara")
    assert [b.locator(".animo-cara__nombre").inner_text() for b in botones.all()] == ["Muy mal", "Mal", "Neutral", "Bien", "Muy bien"]
    # el nombre accesible es la palabra, y ningún botón promete XP (regla 4 de la misión)
    for boton in botones.all():
        assert "XP" not in boton.inner_text()
        assert boton.get_attribute("aria-pressed") == "false"
    # cada botón lleva la cara de tu compañero (a fondo, en test_caras_checkin.py); la palabra siempre está
    assert botones.locator("img").count() == 5
    assert botones.locator("[data-cara-checkin]").count() == 5
    assert pagina.locator(".animo-cara [data-cara]").count() == 0           # ya no usan data-cara: lumea-ui.js no les pinta la cara del avatar


def test_elegir_una_cara_la_marca_y_habilita_guardar_pero_no_guarda(pagina, backend):
    abrir(pagina, backend, avatar=sin_animo_hoy(backend))
    guardar = pagina.locator("#btn-guardar-animo-inicio")
    assert guardar.is_disabled()                                            # sin elegir no se guarda
    pagina.locator(".animo-cara", has=pagina.get_by_text("Neutral", exact=True)).click()
    assert pagina.locator(".animo-cara[aria-pressed=true]").inner_text().strip() == "Neutral"
    pagina.locator(".animo-cara", has=pagina.get_by_text("Bien", exact=True)).click()   # se puede cambiar de idea antes de guardar
    assert pagina.locator(".animo-cara[aria-pressed=true]").count() == 1
    assert pagina.locator(".animo-cara[aria-pressed=true]").inner_text().strip() == "Bien"
    assert guardar.is_enabled()
    assert ("POST", "/estado-animo") not in backend.llamadas


def test_guardar_mi_animo_guarda_celebra_y_queda_registrado(pagina, backend):
    abrir(pagina, backend, avatar=sin_animo_hoy(backend))
    # tras guardar, el backend ya trae el ánimo de hoy
    despues = cargar_respuesta("progreso")
    despues["progreso"]["avatar"]["estado_animo_hoy"] = "mal"
    backend.poner("GET", "/progreso", despues)
    backend.respuestas.pop(("GET", "/estado-animo"))
    pagina.locator(".animo-cara", has=pagina.get_by_text("Mal", exact=True)).click()
    pagina.get_by_role("button", name="Guardar mi ánimo").click()
    pagina.locator(".celebracion__chip").first.wait_for()
    assert pagina.locator(".celebracion__chip").first.inner_text() == "+5 semillas"
    envio = next(c for m, u, c in backend.peticiones if m == "POST" and u.endswith("/estado-animo"))
    assert json.loads(envio) == {"email": "prueba@lumea.test", "estado": "mal"}
    pagina.locator("#checkin-confirmado").wait_for()
    assert "Mal" in pagina.locator("#checkin-confirmado").inner_text()
    assert pagina.locator(".animo-cara:enabled").count() == 1               # solo queda el elegido
    assert not pagina.locator("#btn-guardar-animo-inicio").is_visible()


def test_si_guardar_falla_avisa_y_se_puede_intentar_otra_vez(pagina, backend):
    abrir(pagina, backend, avatar=sin_animo_hoy(backend))
    backend.poner("POST", "/estado-animo", {"success": False, "error": "falló"}, estado=500)
    pagina.locator(".animo-cara", has=pagina.get_by_text("Mal", exact=True)).click()
    pagina.get_by_role("button", name="Guardar mi ánimo").click()
    pagina.locator(".lumea-toast-item", has_text="No se pudo guardar tu ánimo").wait_for()
    assert pagina.locator("#btn-guardar-animo-inicio").is_enabled()
    assert pagina.locator(".celebracion__chip").count() == 0


def test_el_checkin_lleva_a_la_semana_de_animo(pagina, backend):
    abrir(pagina, backend)
    assert pagina.get_by_role("link", name="Ver mi semana de ánimo").get_attribute("href") == "emociones.html"


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


# ---------- El Inicio nuevo (R2) ----------

def test_cuatro_superficies_como_maximo_y_un_solo_boton_relleno(pagina, backend):
    abrir(pagina, backend)
    # sin contar la tarjeta «Elige tus colores», que desaparece una vez elegida la paleta
    superficies = pagina.locator("main .tarjeta:not(#card-colores), main .inicio__franja")
    assert superficies.count() <= 4                                         # antes eran 13 cajas
    # «una acción principal por pantalla»: solo un botón relleno, y es «Registrar comida»
    rellenos = pagina.locator("main .boton:not(.boton--secundario):not(.boton--fantasma)")
    assert rellenos.count() == 1
    assert rellenos.inner_text().strip() == "Registrar comida"
    assert rellenos.get_attribute("href") == "alimentos.html"


def test_las_semillas_aparecen_tres_veces_como_maximo(pagina, backend):
    abrir(pagina, backend)
    texto_visible = pagina.locator("main").inner_text()
    assert texto_visible.count("semilla") <= 3                                   # antes eran 11


def test_cada_bloque_es_una_seccion_con_su_titulo(pagina, backend):
    abrir(pagina, backend)
    secciones = pagina.locator("main section[aria-labelledby]:not(#card-colores)")
    assert secciones.count() == 4
    for seccion in secciones.all():
        titulo = seccion.get_attribute("aria-labelledby")
        assert pagina.locator(f"h2#{titulo}").count() == 1
    assert pagina.locator("main h1").count() == 1


def test_la_jerarquia_de_tamanos_es_titulo_seccion_y_cuerpo(pagina, backend):
    abrir(pagina, backend)
    tam = lambda selector: pagina.locator(selector).first.evaluate("e => parseFloat(getComputedStyle(e).fontSize)")
    assert tam("h1") == pytest_aprox(31.25)                                   # --t-2xl
    assert tam("h2#titulo-dia") == pytest_aprox(20)                           # --t-l
    assert tam(".inicio__acciones .boton") >= 16                              # los botones, a 16 px o más
    assert tam("#titulo-dia ~ .inicio__nota, .inicio__nota") <= 14.01         # lo secundario, en --t-s


def pytest_aprox(valor):
    return pytest.approx(valor, abs=0.1)


def test_la_fecha_va_en_un_time_con_su_fecha_y_sin_hora(pagina, backend):
    abrir(pagina, backend)
    fecha = pagina.locator("time.inicio__fecha")
    assert fecha.inner_text() == "Lunes, 5 de octubre"
    assert fecha.get_attribute("datetime") == "2026-10-05"
