"""P11 · 5: esqueletos de carga con la forma final (dato del día, «Tu semana» y Mis registros): quietos y sin que nada salte."""
import json

import pytest

from conftest import cargar_respuesta


def retener(pagina, patron):
    """Deja pendiente la respuesta de una ruta y devuelve cómo liberarla."""
    pendientes = []
    pagina.route(patron, lambda ruta: pendientes.append(ruta))
    return lambda cuerpo, estado=200: pendientes[0].fulfill(status=estado, content_type="application/json", body=json.dumps(cuerpo))


def esqueletos_quietos(pagina, selector):
    return pagina.locator(selector).evaluate("""e => [...e.querySelectorAll('.esqueleto')].every(x => { const c = getComputedStyle(x);
        return c.animationName === 'none' && c.backgroundImage === 'none' })""")


def test_inicio_muestra_esqueletos_del_dato_y_de_la_semana_mientras_llegan_y_luego_no_saltan(pagina, backend):
    liberar_dato = retener(pagina, "**/dato-del-dia")
    liberar_semana = retener(pagina, "**/estado-animo**")
    pagina.set_viewport_size({"width": 390, "height": 900})
    pagina.goto(f"{pagina.servidor}/index-ingresado.html")
    pagina.locator("#esqueleto-dato").wait_for()
    assert pagina.locator("#esqueleto-dato").is_visible() and pagina.locator("#esqueleto-semana").count() in (0, 1)
    assert not pagina.locator("#card-dato-dia").is_visible()
    assert pagina.locator("#esqueleto-dato").get_attribute("aria-hidden") == "true"
    assert esqueletos_quietos(pagina, "#esqueleto-dato")                                       # quietos, sin brillo ni degradado
    antes = pagina.locator("#esqueleto-dato").bounding_box()
    liberar_dato(cargar_respuesta("dato_del_dia"))
    pagina.locator("#card-dato-dia").wait_for(state="visible")
    despues = pagina.locator("#card-dato-dia").bounding_box()
    assert pagina.locator("#esqueleto-dato").count() == 0
    assert abs(antes["y"] - despues["y"]) < 1 and abs(antes["x"] - despues["x"]) < 1 and abs(antes["width"] - despues["width"]) < 1   # ocupa el mismo sitio
    liberar_semana({"success": True, "cantidad": 0, "historial": []})


def test_si_el_dato_del_dia_falla_el_esqueleto_se_va(pagina, backend):
    backend.poner("GET", "/dato-del-dia", {"success": False}, estado=500)
    pagina.goto(f"{pagina.servidor}/index-ingresado.html")
    pagina.locator("main .lumea-bind-nivel", has_text="Etapa").first.wait_for()
    pagina.wait_for_timeout(300)
    assert pagina.locator("#esqueleto-dato").count() == 0 and not pagina.locator("#card-dato-dia").is_visible()


def test_la_semana_de_inicio_tiene_su_esqueleto_hasta_que_llegan_los_datos(pagina, backend):
    liberar = retener(pagina, "**/progreso**")
    pagina.goto(f"{pagina.servidor}/index-ingresado.html")
    pagina.locator("#esqueleto-semana").wait_for()
    assert pagina.locator("#esqueleto-semana").is_visible() and not pagina.locator("#franja-semana").is_visible()
    assert esqueletos_quietos(pagina, "#esqueleto-semana")
    antes = pagina.locator("#esqueleto-semana").bounding_box()
    liberar(cargar_respuesta("progreso"))
    pagina.locator("#franja-semana").wait_for(state="visible")
    assert pagina.locator("#esqueleto-semana").count() == 0
    despues = pagina.locator("#franja-semana").bounding_box()
    assert abs(antes["height"] - despues["height"]) < 40 and antes["width"] == despues["width"]           # casi el mismo alto y el mismo ancho (lo de arriba también espera /progreso)


def test_mis_registros_muestra_una_tarjeta_de_bloques_mientras_llega_el_historial(pagina, backend):
    liberar = retener(pagina, "**/historial**")
    pagina.goto(f"{pagina.servidor}/mis-registros.html")
    pagina.locator("#cargando .esqueleto-tarjeta").wait_for()
    assert pagina.locator("#cargando").get_attribute("role") == "status"
    assert pagina.locator("#cargando .solo-lector").inner_text() == "Cargando tu historial…"             # el lector de pantalla oye el aviso
    assert pagina.locator("#cargando ul").get_attribute("aria-hidden") == "true"
    assert pagina.locator("#cargando .esqueleto").count() >= 5 and esqueletos_quietos(pagina, "#cargando .esqueleto-tarjeta")
    liberar(cargar_respuesta("historial"))
    pagina.locator("#listaRegistros > li").first.wait_for()
    assert not pagina.locator("#cargando").is_visible()


def test_con_movimiento_reducido_los_esqueletos_siguen_quietos(pagina, backend):
    pagina.emulate_media(reduced_motion="reduce")
    liberar = retener(pagina, "**/historial**")
    pagina.goto(f"{pagina.servidor}/mis-registros.html")
    pagina.locator("#cargando .esqueleto-tarjeta").wait_for()
    assert esqueletos_quietos(pagina, "#cargando .esqueleto-tarjeta")
    assert pagina.locator("#cargando .esqueleto-tarjeta").evaluate("e => e.getAnimations({ subtree: true }).length") == 0
