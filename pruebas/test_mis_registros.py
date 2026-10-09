"""mis-registros.html: el historial en una tarjeta por día (con una fila por registro), con el texto del servidor como texto (no como HTML)."""
from datetime import date, timedelta

import pytest

from conftest import cargar_respuesta

HISTORIAL = cargar_respuesta("historial")["historial"]


def abrir(pagina, backend, historial=None):
    if historial is not None:
        backend.poner("GET", "/historial", {"success": True, "cantidad_registros": len(historial), "historial": historial})
    pagina.goto(f"{pagina.servidor}/mis-registros.html")
    pagina.locator("#listaRegistros li.registro").first.wait_for()


def fecha_http(dias_atras):
    """La fecha como la manda el backend: medianoche en UTC («Mon, 05 Oct 2026 00:00:00 GMT»), de hace `dias_atras` días."""
    return (date.today() - timedelta(days=dias_atras)).strftime("%a, %d %b %Y 00:00:00 GMT")


def test_cada_registro_es_una_fila_dentro_de_la_tarjeta_de_su_dia(pagina, backend):
    abrir(pagina, backend)
    dias = pagina.locator("ul#listaRegistros > li.dia")
    assert dias.count() == 3                                               # tres días distintos en el historial de prueba
    assert pagina.locator("#listaRegistros li.registro").count() == 3
    assert all("tarjeta" in c for c in dias.evaluate_all("e => e.map(x => x.className)"))
    sombras = pagina.locator("#listaRegistros .registro").evaluate_all("e => e.map(x => getComputedStyle(x).boxShadow)")
    assert set(sombras) == {"none"}                                        # las filas se separan con una línea


def test_los_dias_van_del_mas_reciente_al_mas_viejo_con_hoy_y_ayer(pagina, backend):
    historial = [
        HISTORIAL[0] | {"id": 9, "fecha": fecha_http(0)},
        HISTORIAL[1] | {"id": 8, "fecha": fecha_http(1)},
        HISTORIAL[0] | {"id": 7, "fecha": fecha_http(1), "alimento_detectado": "Mango"},
        HISTORIAL[2] | {"id": 6, "fecha": "Tue, 06 Oct 2026 00:00:00 GMT"},
        HISTORIAL[1] | {"id": 5, "fecha": "Sat, 03 Oct 2026 00:00:00 GMT"},
    ]
    abrir(pagina, backend, historial=historial[::-1])                      # aunque lleguen desordenados
    assert pagina.locator("#listaRegistros > li > h2").all_inner_texts() == ["Hoy", "Ayer", "martes 6 de octubre", "sábado 3 de octubre"]
    assert pagina.locator("#listaRegistros > li").nth(1).locator("li.registro").count() == 2
    assert "3 comidas" not in pagina.locator("#listaRegistros").inner_text()
    assert pagina.locator("#listaRegistros > li").nth(1).locator(".dia__cuantas").inner_text() == "2 comidas"
    assert pagina.locator("#listaRegistros > li").first.locator(".dia__cuantas").inner_text() == "1 comida"


def test_la_tarjeta_de_hoy_lleva_la_forma_decorativa_y_las_demas_no(pagina, backend):
    abrir(pagina, backend, historial=[HISTORIAL[0] | {"fecha": fecha_http(0)}, HISTORIAL[1] | {"fecha": fecha_http(3)}])
    hoy, otro = pagina.locator("#listaRegistros > li").all()
    assert "con-forma" in hoy.get_attribute("class") and "con-forma--sol" in hoy.get_attribute("class")
    assert "con-forma" not in otro.get_attribute("class")


def test_el_resumen_del_dia_marca_los_grupos_que_aparecieron_sin_decir_te_faltan(pagina, backend):
    abrir(pagina, backend, historial=[HISTORIAL[0] | {"fecha": fecha_http(2)}, HISTORIAL[1] | {"fecha": fecha_http(2)}])
    resumen = pagina.locator(".dia__resumen").first
    assert resumen.locator(".marca-grupo").count() == 6                    # los seis grupos del plato del ICBF
    assert resumen.locator(".marca-grupo--llena").count() == 2             # frutas y verduras, y cereales
    assert "Grupos del plato que aparecieron: Cereales, Frutas y verduras" in resumen.text_content()
    assert resumen.locator(".marcas-grupos").get_attribute("aria-hidden") == "true"
    contenido = pagina.locator("main").inner_text().lower()
    assert "te faltan" not in contenido and "te falta" not in contenido


def test_cada_fila_lleva_el_chip_de_su_grupo(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("#listaRegistros li.registro .registro__grupo").all_inner_texts() == ["Frutas y verduras", "Cereales", "Azúcares"]


def test_sin_grupo_en_el_backend_no_se_dibujan_ni_el_chip_ni_las_marcas(pagina, backend):
    sin_grupo = [{k: v for k, v in r.items() if k not in ("grupo", "sellos")} for r in HISTORIAL]
    abrir(pagina, backend, historial=sin_grupo)
    assert pagina.locator(".registro__grupo, .marcas-grupos").count() == 0
    assert pagina.locator(".dia__cuantas").count() == 3


def test_las_calorias_van_en_segundo_plano_con_la_clase_cifra(pagina, backend):
    abrir(pagina, backend)
    kcal = pagina.locator("#listaRegistros li.registro").first.locator(".registro__dato")
    assert kcal.inner_text().strip() == "89 kcal aprox." and "cifra" in kcal.get_attribute("class")
    assert kcal.evaluate("e => parseFloat(getComputedStyle(e).fontSize)") < pagina.locator("#listaRegistros h3").first.evaluate("e => parseFloat(getComputedStyle(e).fontSize)")


def test_en_el_computador_las_tarjetas_de_dias_se_reparten_en_columnas(pagina, backend):
    pagina.set_viewport_size({"width": 1440, "height": 900})
    abrir(pagina, backend)
    cajas = pagina.locator("#listaRegistros > li").evaluate_all("e => e.map(x => x.getBoundingClientRect().toJSON())")
    assert cajas[0]["y"] == cajas[1]["y"] and cajas[0]["x"] < cajas[1]["x"]          # dos en la misma fila
    assert pagina.evaluate("document.documentElement.scrollWidth") <= 1440


def test_los_datos_van_con_su_icono_de_bootstrap_icons(pagina, backend):
    abrir(pagina, backend)
    fila = pagina.locator("#listaRegistros li.registro").first
    assert [i.get_attribute("class") for i in fila.locator(".registro__dato i").all()] == ["bi bi-fire"]
    assert all(i.get_attribute("aria-hidden") == "true" for i in fila.locator(".registro__dato i").all())


def test_sin_sellos_conocidos_no_pinta_nada_de_sellos(pagina, backend):
    registro = HISTORIAL[0] | {"sellos_advertencia": None}
    abrir(pagina, backend, historial=[registro])
    fila = pagina.locator("#listaRegistros li.registro").first
    assert fila.locator(".sello, .sellos, p:has-text('Sin sellos')").count() == 0


def test_los_sellos_se_leen_como_octagonos_con_nombre_accesible(pagina, backend):
    abrir(pagina, backend)
    sellos = pagina.locator("#listaRegistros .sello")
    assert sellos.all_text_contents() == ["EXCESO EN AZÚCARES", "CONTIENE EDULCORANTES"]       # el sello oficial va en mayúsculas
    assert [s.get_attribute("aria-label") for s in sellos.all()] == ["Exceso en azúcares", "Contiene edulcorantes"]
    assert all(s.get_attribute("role") == "img" for s in sellos.all())
    assert pagina.get_by_role("img", name="Exceso en azúcares").count() == 1
    assert pagina.locator("#listaRegistros p", has_text="Sin sellos de advertencia").count() == 2
    for s in sellos.all():
        assert s.evaluate("e => parseFloat(getComputedStyle(e).fontSize)") >= 12.8
        assert s.evaluate("e => e.scrollWidth <= e.clientWidth + 1 && e.scrollHeight <= e.clientHeight + 1")


def test_los_sellos_van_en_una_envoltura_con_placa_para_el_modo_oscuro(pagina, backend):
    pagina.emulate_media(color_scheme="dark")
    abrir(pagina, backend)
    envoltura = pagina.locator("#listaRegistros .sellos").first
    placa = pagina.evaluate("""() => { const e = document.createElement('i'); e.style.backgroundColor = 'var(--c-sello-placa)';
        document.body.appendChild(e); const c = getComputedStyle(e).backgroundColor; e.remove(); return c }""")
    filtro = envoltura.evaluate("e => getComputedStyle(e).filter")
    assert "drop-shadow" in filtro and placa in filtro                      # sin la placa el negro se pierde sobre el fondo oscuro


def test_el_texto_del_servidor_nunca_es_html(pagina, backend):
    malo = '<img src=x onerror="window.hackeado=1"><b>negrita</b>'
    registro = HISTORIAL[0] | {"alimento_detectado": malo, "sellos_advertencia": ["<i>raro</i>"]}
    abrir(pagina, backend, historial=[registro])
    assert pagina.locator("#listaRegistros img, #listaRegistros b, #listaRegistros i.raro").count() == 0
    assert malo in pagina.locator("#listaRegistros h3").inner_text()
    # text_content y no inner_text: el sello va en mayúsculas por CSS (Res. 810) y inner_text devuelve lo que se ve
    assert "<i>raro</i>" in pagina.locator("#listaRegistros .sello").text_content()
    assert pagina.evaluate("window.hackeado") is None


def test_sin_registros_invita_a_registrar(pagina, backend):
    backend.poner("GET", "/historial", {"success": True, "cantidad_registros": 0, "historial": []})
    pagina.goto(f"{pagina.servidor}/mis-registros.html")
    pagina.locator("#sinRegistros").wait_for()
    assert pagina.locator("#sinRegistros a").get_attribute("href") == "alimentos.html"
    assert pagina.locator("#sinRegistros a").inner_text().strip() == "Registrar comida"
    assert pagina.locator("#listaRegistros > li").count() == 0


def test_si_el_servidor_no_responde_se_avisa(pagina, backend):
    pagina.route("http://127.0.0.1:5002/**", lambda ruta: ruta.abort())
    pagina.goto(f"{pagina.servidor}/mis-registros.html")
    pagina.locator("#errorHistorial").wait_for()
    assert pagina.locator("#errorHistorial").get_attribute("role") == "alert"
    assert "No se pudo conectar con el servidor" in pagina.locator("#errorHistorial").inner_text()
    assert not pagina.locator("#cargando").is_visible()


def test_sin_sesion_se_ve_el_aviso_y_no_la_lista(pagina, backend):
    pagina.add_init_script("localStorage.clear()")
    pagina.goto(f"{pagina.servidor}/mis-registros.html")
    assert pagina.locator("#sinSesion").is_visible()
    assert not pagina.locator("#conSesion").is_visible()
    assert pagina.locator("h1:visible").inner_text() == "Inicia sesión para ver tus registros"
    assert pagina.get_by_role("link", name="Iniciar Sesión").get_attribute("href") == "iniciar-sesion.html"
    assert pagina.get_by_role("link", name="Crear Cuenta").get_attribute("href") == "crear-cuenta.html"


def test_la_pantalla_usa_el_mismo_armazon_y_la_misma_escala(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("h1:visible").inner_text() == "Mis registros"
    assert pagina.locator("h1:visible").evaluate("e => parseFloat(getComputedStyle(e).fontSize)") == pytest.approx(31.25, abs=0.1)   # --t-2xl, como las demás
    hojas = pagina.eval_on_selector_all("link[rel=stylesheet]", "e => e.map(x => x.getAttribute('href'))")
    assert not any("bootstrap.min.css" in h for h in hojas)                                            # el aspecto ya no sale de Bootstrap
    assert pagina.locator("script[src*='bootstrap']").count() == 0


def test_el_pie_lleva_a_las_paginas_publicas(pagina, backend):
    abrir(pagina, backend)
    enlaces = pagina.locator(".pie-app a")
    assert [e.get_attribute("href") for e in enlaces.all()] == ["index.html", "conocenos.html", "guialumea.html", "terminos.html"]
    assert pagina.locator(".pie-app img.marca").get_attribute("src") == "img/logo.svg"
