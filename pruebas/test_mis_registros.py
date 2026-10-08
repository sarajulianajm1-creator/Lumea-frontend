"""mis-registros.html (rediseño R6): el historial como una lista de filas, con el texto del servidor como texto (no como HTML)."""
import pytest

from conftest import cargar_respuesta

HISTORIAL = cargar_respuesta("historial")["historial"]


def abrir(pagina, backend, historial=None):
    if historial is not None:
        backend.poner("GET", "/historial", {"success": True, "cantidad_registros": len(historial), "historial": historial})
    pagina.goto(f"{pagina.servidor}/mis-registros.html")
    pagina.locator("#listaRegistros > li.registro").first.wait_for()


def test_cada_registro_es_una_fila_de_una_lista_y_no_una_tarjeta(pagina, backend):
    abrir(pagina, backend)
    lista = pagina.locator("ul#listaRegistros")
    assert lista.count() == 1
    assert lista.locator("> li.registro").count() == 3
    assert pagina.locator("main .tarjeta:visible").count() == 0            # «las tarjetas pasan a filas de lista»
    sombras = pagina.locator("#listaRegistros > li").evaluate_all("e => e.map(x => getComputedStyle(x).boxShadow)")
    assert set(sombras) == {"none"}                                        # sin sombra: la fila se separa con una línea


def test_la_fila_muestra_lo_mismo_que_la_tarjeta_de_antes(pagina, backend):
    """Los datos de cada registro son los de siempre; cambió cómo se ven, no qué se ve."""
    abrir(pagina, backend)
    esperado = [
        ("Banano", "5 de octubre de 2026", "89 kcal aprox.", "Certeza IA: 97.0%"),
        ("Arepa", "4 de octubre de 2026", "120 kcal aprox.", "Certeza IA: 91.0%"),
        ("Coca-Cola Original", "3 de octubre de 2026", "30 kcal aprox.", "Certeza IA: 100.0%"),
    ]
    for i, (nombre, fecha, kcal, certeza) in enumerate(esperado):
        fila = pagina.locator("#listaRegistros > li.registro").nth(i)
        assert fila.locator("h3").inner_text() == nombre
        datos = [p.inner_text().strip() for p in fila.locator(".registro__dato").all()]
        assert datos == [fecha, kcal, certeza], f"registro {i}"


def test_los_datos_van_con_su_icono_de_bootstrap_icons(pagina, backend):
    abrir(pagina, backend)
    fila = pagina.locator("#listaRegistros > li.registro").first
    assert [i.get_attribute("class") for i in fila.locator(".registro__dato i").all()] == ["bi bi-calendar3", "bi bi-fire", "bi bi-bullseye"]
    assert all(i.get_attribute("aria-hidden") == "true" for i in fila.locator(".registro__dato i").all())


def test_sin_sellos_conocidos_no_pinta_nada_de_sellos(pagina, backend):
    registro = HISTORIAL[0] | {"sellos_advertencia": None}
    abrir(pagina, backend, historial=[registro])
    fila = pagina.locator("#listaRegistros > li.registro").first
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
    assert pagina.locator("#sinRegistros a").inner_text() == "Registra tu primera comida"
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
