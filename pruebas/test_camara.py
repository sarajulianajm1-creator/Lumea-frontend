"""alimentos.html (la cámara): sin sesión, IA segura, IA duda y confirmar. Rediseño R5: una sola acción
principal, «Lo que reconoció Lumea», calorías en una línea, sellos con nombre accesible."""
import json
import re
from pathlib import Path

import pytest

from conftest import cargar_respuesta

RAIZ = Path(__file__).resolve().parent.parent


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
    assert pagina.locator("#backend-precision").inner_text() == "La IA está segura: 94 %"      # la certeza, en palabras y en número
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


# ---------- Rediseño R5: el aspecto ----------

def analizar(pagina, foto, backend=None, respuesta=None):
    if respuesta is not None:
        backend.poner("POST", "/predecir", respuesta)
    abrir(pagina)
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#resultado[data-estado]:not([data-estado=''])").wait_for()


def color(pagina, selector):
    return pagina.locator(selector).first.evaluate("e => getComputedStyle(e).color")


def variable_en_rgb(pagina, variable, propiedad="color"):
    """El valor de un token (--c-…) como lo calcula el navegador, para compararlo con un color calculado."""
    return pagina.evaluate("""([v, p]) => { const e = document.createElement('i'); e.style[p] = `var(${v})`;
        document.body.appendChild(e); const c = getComputedStyle(e)[p]; e.remove(); return c }""", [variable, propiedad])


def test_antes_de_la_foto_solo_hay_la_invitacion_y_ningun_resultado(pagina):
    abrir(pagina)
    assert pagina.locator("#resultado").get_attribute("data-estado") == ""
    assert pagina.get_by_role("heading", name="Lo que reconoció Lumea").is_visible()
    assert "Toma una foto de tu plato" in pagina.locator("#resultado").inner_text()
    assert not pagina.locator("#backend-alimento").is_visible()
    assert not pagina.locator("#backend-sellos").is_visible()


def test_tomar_foto_es_la_unica_accion_principal(pagina):
    abrir(pagina)
    rellenos = pagina.locator("main .boton:visible:not(.boton--secundario):not(.boton--fantasma)")
    assert rellenos.count() == 1 and rellenos.get_attribute("id") == "btn-tomar"
    assert rellenos.inner_text().strip() == "Tomar foto"
    assert pagina.get_by_role("button", name="Tomar foto").get_attribute("aria-keyshortcuts") == "Space"
    # antes eran cinco botones iguales: ahora los demás son secundarios o de texto
    assert pagina.locator("#btn-encender").get_attribute("class").split() == ["boton", "boton--secundario"]
    for id_ in ("btn-subir", "btn-otra", "btn-apagar"):
        assert "boton--fantasma" in pagina.locator(f"#{id_}").get_attribute("class")


def test_los_iconos_son_de_bootstrap_icons_y_no_hay_svg_a_mano(pagina):
    abrir(pagina)
    assert pagina.locator("main svg").count() == 0
    assert pagina.locator("main .controles .bi").count() == 5
    assert pagina.locator("main .bi[aria-hidden=true]").count() == 5


def test_el_resultado_seguro_dice_lo_que_reconocio_con_el_nombre_en_grande(pagina, foto):
    analizar(pagina, foto)
    resultado = pagina.locator("#resultado")
    assert resultado.get_attribute("data-estado") == "segura"
    assert resultado.get_by_role("heading", name="Lo que reconoció Lumea").is_visible()
    assert not pagina.get_by_text("Detectamos").count()
    tam = lambda sel: pagina.locator(sel).evaluate("e => parseFloat(getComputedStyle(e).fontSize)")
    assert tam("#backend-alimento") == pytest.approx(48.83, abs=0.1)              # --t-3xl
    assert tam("#backend-precision") == 16                                          # la certeza, al tamaño del cuerpo (antes 10 px)
    assert pagina.locator("#backend-alimento").inner_text() == "Arepa"
    assert "Toma una foto de tu plato" not in pagina.locator("#resultado").inner_text()


def test_ia_duda_usa_el_contenedor_del_rol_duda_y_el_mango_no_es_texto(pagina, backend, foto):
    analizar(pagina, foto, backend, cargar_respuesta("predecir_duda"))
    assert pagina.locator("#resultado").get_attribute("data-estado") == "duda"
    fondo = pagina.locator("#resultado").evaluate("e => getComputedStyle(e).backgroundColor")
    assert fondo == variable_en_rgb(pagina, "--c-duda-contenedor", "backgroundColor")
    mango = variable_en_rgb(pagina, "--c-duda")
    colores = pagina.locator("#resultado *").evaluate_all("e => e.filter(x => x.childNodes.length && [...x.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())).map(x => getComputedStyle(x).color)")
    assert colores and mango not in colores                                         # ningún texto va en mango
    assert pagina.locator("#backend-precision").inner_text() == "La IA no está segura: 65 %"
    # mientras duda no se afirma nada de la comida: ni calorías ni sellos de una suposición
    assert not pagina.locator("#backend-energia").is_visible()
    assert not pagina.locator("#backend-sellos").is_visible()


def test_las_calorias_van_en_una_sola_linea_secundaria_sin_color_de_alerta(pagina, foto):
    analizar(pagina, foto)
    linea = pagina.locator("#backend-energia")
    assert linea.is_visible()
    assert linea.inner_text() == "Calorías aproximadas: 120 kcal por 100 g"           # arepa: 120 en pruebas/respuestas/alimentos.json
    assert pagina.locator("#resultado :text('kcal')").count() == 1                  # una sola vez, no en una tarjeta aparte
    assert linea.evaluate("e => getComputedStyle(e).color") == variable_en_rgb(pagina, "--c-tinta-suave")
    assert linea.evaluate("e => parseFloat(getComputedStyle(e).fontSize)") == 14      # secundaria: --t-s


def test_el_interruptor_de_las_calorias_esta_arriba_del_archivo_con_su_comentario():
    texto = (RAIZ / "lumea-camara.js").read_text(encoding="utf-8")
    assert texto.startswith("// Decisión de Isabella, 7 oct 2026: se muestran.")
    assert "const MOSTRAR_CALORIAS = true;" in texto.split("(function ()")[0]


def test_con_mostrar_calorias_en_false_no_se_dibujan(pagina, foto):
    codigo = (RAIZ / "lumea-camara.js").read_text(encoding="utf-8").replace("const MOSTRAR_CALORIAS = true;", "const MOSTRAR_CALORIAS = false;")
    pagina.route("**/lumea-camara.js", lambda ruta: ruta.fulfill(status=200, content_type="text/javascript", body=codigo))
    analizar(pagina, foto)
    assert not pagina.locator("#backend-energia").is_visible()
    assert pagina.locator("#backend-energia").inner_text() == ""
    assert "kcal" not in pagina.locator("#resultado").inner_text()


def test_sin_dato_de_calorias_la_linea_no_se_dibuja(pagina, backend, foto):
    backend.poner("GET", "/alimentos", {"alimentos": []})
    analizar(pagina, foto)
    assert not pagina.locator("#backend-energia").is_visible()


def test_los_sellos_son_oficiales_negros_con_nombre_accesible_y_texto_legible(pagina, backend, foto):
    respuesta = cargar_respuesta("predecir_segura") | {"sellos_advertencia": ["azucares", "grasas_saturadas", "edulcorantes"]}
    analizar(pagina, foto, backend, respuesta)
    sellos = pagina.locator("#backend-sellos .sello")
    assert sellos.count() == 3
    assert [s.get_attribute("aria-label") for s in sellos.all()] == ["Exceso en azúcares", "Exceso en grasas saturadas", "Contiene edulcorantes"]
    for s in sellos.all():
        assert s.get_attribute("role") == "img"
        assert s.evaluate("e => parseFloat(getComputedStyle(e).fontSize)") >= 12.8       # el texto del sello llega al mínimo de la app
        assert s.evaluate("e => getComputedStyle(e).textTransform") == "uppercase"       # el sello oficial va en mayúsculas (Res. 810)
        assert s.evaluate("e => e.scrollWidth <= e.clientWidth + 1 && e.scrollHeight <= e.clientHeight + 1")   # el texto cabe en el octágono
        assert s.evaluate("e => getComputedStyle(e).backgroundColor") == variable_en_rgb(pagina, "--c-sello", "backgroundColor")   # siempre negro
    assert pagina.get_by_role("img", name="Exceso en azúcares").count() == 1


def test_en_modo_oscuro_los_sellos_llevan_su_placa_clara(pagina, backend, foto):
    pagina.emulate_media(color_scheme="dark")
    respuesta = cargar_respuesta("predecir_segura") | {"sellos_advertencia": ["sodio"]}
    analizar(pagina, foto, backend, respuesta)
    placa = variable_en_rgb(pagina, "--c-sello-placa", "backgroundColor")
    filtro = pagina.locator("#backend-sellos .sellos").evaluate("e => getComputedStyle(e).filter")
    assert "drop-shadow" in filtro and placa in filtro                              # sin la placa el negro se pierde sobre el fondo oscuro


def test_sin_sellos_dice_sin_sellos_de_advertencia_y_no_afirma_que_sea_saludable(pagina, foto):
    analizar(pagina, foto)
    assert pagina.locator("#backend-sellos").inner_text() == "Sin sellos de advertencia"
    assert "saludable" not in pagina.locator("main").inner_text().lower()


def test_nada_en_mayusculas_salvo_el_sello_en_el_resultado(pagina, backend, foto):
    respuesta = cargar_respuesta("predecir_segura") | {"sellos_advertencia": ["sodio"]}
    analizar(pagina, foto, backend, respuesta)
    fuera = pagina.evaluate("""[...document.querySelectorAll('main *')]
        .filter(e => getComputedStyle(e).textTransform === 'uppercase' && !e.closest('.sello')).map(e => e.className)""")
    assert fuera == []
    texto = pagina.locator("main").evaluate("""e => { const c = e.cloneNode(true); c.querySelectorAll('.sello').forEach(s => s.remove()); return c.innerText }""")
    assert not re.search(r"\b[A-ZÁÉÍÓÚÑ]{4,}\b", texto), texto                      # ningún título escrito en mayúsculas sostenidas


def test_todo_el_texto_del_resultado_mide_12_8_px_o_mas(pagina, backend, foto):
    respuesta = cargar_respuesta("predecir_segura") | {"sellos_advertencia": ["sodio", "azucares"]}
    analizar(pagina, foto, backend, respuesta)
    chicos = pagina.evaluate("""() => {
        const malos = [], w = document.createTreeWalker(document.querySelector('main'), NodeFilter.SHOW_TEXT);
        while (w.nextNode()) { const n = w.currentNode, e = n.parentElement;
            if (!n.textContent.trim() || e.getBoundingClientRect().width < 2) continue;
            const t = parseFloat(getComputedStyle(e).fontSize); if (t < 12.79) malos.push(t + 'px ' + n.textContent.trim().slice(0, 30)); }
        return malos }""")
    assert chicos == []


@pytest.mark.parametrize("ancho", [375, 1280])
def test_el_resultado_no_desborda_la_pagina(pagina, backend, foto, ancho):
    pagina.set_viewport_size({"width": ancho, "height": 800})
    respuesta = cargar_respuesta("predecir_segura") | {"sellos_advertencia": ["sodio", "azucares", "grasas_saturadas"],
                                                        "alimento_app": "Arepa paisa de maíz precocido con sal y mantequilla"}
    analizar(pagina, foto, backend, respuesta)
    assert pagina.evaluate("document.documentElement.scrollWidth") <= ancho


def test_en_computador_la_camara_y_el_resultado_van_lado_a_lado_y_en_celular_apilados(pagina):
    abrir(pagina)
    lado = pagina.evaluate("[document.querySelector('.registro__camara').getBoundingClientRect().top, document.querySelector('#resultado').getBoundingClientRect().top]")
    assert abs(lado[0] - lado[1]) < 4                                                # a la misma altura
    pagina.set_viewport_size({"width": 390, "height": 800})
    apilado = pagina.evaluate("[document.querySelector('.registro__camara').getBoundingClientRect().bottom, document.querySelector('#resultado').getBoundingClientRect().top]")
    assert apilado[1] >= apilado[0]
