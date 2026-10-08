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
    assert "+10 semillas" in pagina.locator("#backend-logros").inner_text()
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
    assert "+20 semillas" in textos and "Llegaste a la etapa 3" in textos
    assert "Calcomanía nueva: Un día completo" in textos


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
    # los cinco botones llevan su ícono (K0.5: «Encender cámara» pasó al visor vacío) y el visor vacío trae el suyo
    assert pagina.locator("main .controles .bi, main .visor__vacio button .bi").count() == 5
    assert pagina.locator("main .bi[aria-hidden=true]").count() == 6


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


# ---------- Camino del cuidado, K0.5: consejos en el resultado ----------
# El backend agrega r.consejo a /predecir y /confirmar-alimento. Las respuestas simuladas
# (predecir_banano, predecir_gaseosa y predecir_bandeja_paisa) los traen; predecir_segura no (backend viejo).

TITULOS = "#backend-consejos .consejo__titulo, #titulo-dato:not([hidden])"


def titulos(pagina):
    """Los títulos de los bloques que se ven, de arriba abajo."""
    return pagina.eval_on_selector_all(TITULOS, "es => es.map(e => e.textContent)")


def texto_de(pagina, titulo):
    return pagina.locator(f".consejo:has(> h3:text-is('{titulo}')) > p").inner_text()


def test_los_consejos_salen_en_el_orden_de_la_mision_y_son_cuatro_como_maximo(pagina, backend, foto):
    analizar(pagina, foto, backend, cargar_respuesta("predecir_bandeja_paisa"))
    assert titulos(pagina) == ["Lo que aporta", "Para completar tu plato", "A tener en cuenta", "¿Sabías que…?"]
    assert pagina.locator("#backend-consejos .consejo").count() == 3          # el cuarto es el dato curioso
    assert texto_de(pagina, "Para completar tu plato") == cargar_respuesta("predecir_bandeja_paisa")["consejo"]["para_completar"]
    # van debajo del nombre, los sellos y las calorías
    orden = pagina.evaluate("""() => ['backend-alimento', 'backend-energia', 'backend-sellos', 'backend-consejos', 'backend-dato']
        .map(id => document.getElementById(id).getBoundingClientRect().top)""")
    assert orden == sorted(orden)


def test_sin_para_completar_sale_la_idea_del_primer_sello(pagina, backend, foto):
    # el contrato real: la gaseosa trae para_completar null (no es un plato) y un sello de azúcares
    analizar(pagina, foto, backend, cargar_respuesta("predecir_gaseosa"))
    consejo = cargar_respuesta("predecir_gaseosa")["consejo"]
    assert consejo["para_completar"] is None
    assert titulos(pagina) == ["Lo que aporta", "Una idea", "A tener en cuenta", "¿Sabías que…?"]
    assert texto_de(pagina, "Una idea") == consejo["sellos"][0]["idea"]
    assert texto_de(pagina, "A tener en cuenta") == consejo["a_tener_en_cuenta"]            # el texto propio gana al dato del sello


def test_sin_a_tener_en_cuenta_sale_el_dato_del_primer_sello(pagina, backend, foto):
    r = cargar_respuesta("predecir_gaseosa")
    r["consejo"]["a_tener_en_cuenta"] = None
    analizar(pagina, foto, backend, r)
    assert titulos(pagina) == ["Lo que aporta", "Una idea", "A tener en cuenta", "¿Sabías que…?"]
    assert texto_de(pagina, "A tener en cuenta") == r["consejo"]["sellos"][0]["dato"]


def test_un_bloque_vacio_no_se_dibuja(pagina, backend, foto):
    analizar(pagina, foto, backend, cargar_respuesta("predecir_banano"))      # el contrato real: sin para_completar (es una fruta) y sin sellos
    assert titulos(pagina) == ["Lo que aporta", "A tener en cuenta", "¿Sabías que…?"]
    assert pagina.locator("#backend-consejos .consejo").count() == 2
    # sin aporta, sin dato curioso y con espacios en blanco: tampoco se dibujan ni dejan un título suelto
    r = cargar_respuesta("predecir_banano")
    r["consejo"] = {"aporta": "   ", "para_completar": "", "a_tener_en_cuenta": None, "sellos": []}
    r["dato_curioso"] = ""
    backend.poner("POST", "/predecir", r)
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#backend-consejos").wait_for(state="attached")
    pagina.wait_for_function("document.getElementById('backend-alimento').textContent === 'Banano'")
    assert titulos(pagina) == []
    assert pagina.locator("#consejo-dato").is_hidden()


def test_sin_consejo_la_pantalla_queda_como_antes(pagina, backend, foto):
    analizar(pagina, foto, backend, cargar_respuesta("predecir_segura"))          # backend viejo: sin «consejo»
    assert titulos(pagina) == []
    assert pagina.locator("#backend-consejos .consejo").count() == 0
    assert pagina.locator("#backend-dato").inner_text() == "La arepa es de maíz."
    assert pagina.locator("#titulo-dato").is_hidden()


def test_mientras_la_ia_duda_no_se_aconseja_sobre_una_suposicion(pagina, backend, foto):
    r = cargar_respuesta("predecir_grupo") | {"consejo": cargar_respuesta("predecir_banano")["consejo"]}
    analizar(pagina, foto, backend, r)
    assert titulos(pagina) == []
    # al confirmar el plato sí aparecen (también /confirmar-alimento trae «consejo»)
    backend.poner("POST", "/confirmar-alimento", cargar_respuesta("confirmar") | {"consejo": cargar_respuesta("predecir_gaseosa")["consejo"]})
    pagina.get_by_role("button", name="Ajiaco").click()
    pagina.locator("#backend-consejos .consejo").first.wait_for()
    assert titulos(pagina)[0] == "Lo que aporta"


def test_el_texto_de_un_consejo_nunca_es_html(pagina, backend, foto):
    malo = "<b>negrita</b><img src=x onerror=\"window.__roto = 1\">"
    r = cargar_respuesta("predecir_banano")
    r["consejo"] = {"aporta": malo, "para_completar": malo, "a_tener_en_cuenta": malo, "sellos": [{"sello": "sodio", "dato": malo, "idea": malo}]}
    analizar(pagina, foto, backend, r)
    assert pagina.locator("#backend-consejos .consejo__texto").first.inner_text() == malo
    assert pagina.locator("#backend-consejos b, #backend-consejos img").count() == 0
    assert pagina.evaluate("window.__roto") is None


def test_los_consejos_no_llevan_color_de_alerta_ni_iconos_de_advertencia(pagina, backend, foto):
    analizar(pagina, foto, backend, cargar_respuesta("predecir_bandeja_paisa"))
    assert pagina.locator("#backend-consejos .bi, #backend-consejos svg, #backend-consejos img, #backend-consejos [role=alert], #backend-consejos .alert").count() == 0
    tinta = variable_en_rgb(pagina, "--c-tinta")
    tinta_suave = variable_en_rgb(pagina, "--c-tinta-suave")
    assert pagina.locator("#backend-consejos .consejo__texto").first.evaluate("e => getComputedStyle(e).color") == tinta
    assert pagina.locator("#backend-consejos .consejo__titulo").first.evaluate("e => getComputedStyle(e).color") == tinta_suave
    fondos = pagina.eval_on_selector_all("#backend-consejos, #backend-consejos .consejo, #consejo-dato",
                                         "es => es.map(e => getComputedStyle(e).backgroundColor)")
    assert set(fondos) == {"rgba(0, 0, 0, 0)"}                                       # sin recuadro de aviso
    assert "advertencia" not in pagina.locator("#backend-consejos").inner_text().lower()


@pytest.mark.parametrize("ancho", [375, 1280])
def test_los_consejos_se_leen_bien_y_no_desbordan(pagina, backend, foto, ancho):
    pagina.set_viewport_size({"width": ancho, "height": 800})
    analizar(pagina, foto, backend, cargar_respuesta("predecir_bandeja_paisa"))
    assert pagina.evaluate("document.documentElement.scrollWidth") <= ancho
    chicos = pagina.evaluate("""() => [...document.querySelectorAll('#backend-consejos *, #consejo-dato *')]
        .filter(e => e.textContent.trim() && e.getBoundingClientRect().width > 1 && parseFloat(getComputedStyle(e).fontSize) < 12.79)
        .map(e => e.className)""")
    assert chicos == []
    # el título es menor que el texto y es un h3 dentro de la sección «Lo que reconoció Lumea»
    assert pagina.locator("#resultado h3").count() == 4


# ---------- Camino del cuidado, K0.5: Registrar sigue a ejemplo-camara.html ----------
# Se adoptan el subtítulo, el visor vacío y «Lumea cree que es…»; donde choca, gana R5 (certeza en palabras y número,
# nada de «+10 XP» en los botones, «Tomar foto» como única acción principal).

def test_el_titulo_trae_el_subtitulo_de_la_referencia(pagina):
    abrir(pagina)
    assert pagina.get_by_role("heading", level=1).inner_text() == "Registrar comida"
    assert pagina.locator("main header .contenido__subtitulo").inner_text().startswith("Toma una foto de lo que vas a comer.")


def test_con_la_camara_apagada_el_visor_dice_que_esta_apagada_y_ofrece_encenderla(pagina):
    abrir(pagina)
    vacio = pagina.locator("#visor-vacio")
    assert vacio.is_visible() and "La cámara está apagada" in vacio.inner_text()
    encender = vacio.get_by_role("button", name="Encender cámara")
    assert encender.is_visible() and encender.is_enabled()
    assert encender.get_attribute("class").split() == ["boton", "boton--secundario"]            # R5: «Tomar foto» sigue siendo la única acción principal
    # el visor vacío cubre el visor entero, sin empujar nada
    cajas = pagina.evaluate("[document.querySelector('.visor'), document.querySelector('#visor-vacio')].map(e => e.getBoundingClientRect().toJSON())")
    assert cajas[0]["width"] == cajas[1]["width"] and cajas[0]["height"] == cajas[1]["height"]


def test_el_visor_vacio_se_esconde_con_una_foto_y_vuelve_con_otra_foto(pagina, foto):
    abrir(pagina)
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#backend-foto").wait_for(state="visible")
    assert not pagina.locator("#visor-vacio").is_visible()
    pagina.locator("#backend-alimento", has_text="Arepa").wait_for()
    pagina.get_by_role("button", name="Otra foto").click()
    assert pagina.locator("#visor-vacio").is_visible()


def test_el_visor_vacio_se_esconde_con_la_camara_encendida(pagina):
    pagina.add_init_script("""navigator.mediaDevices.getUserMedia = async () => {
        const c = Object.assign(document.createElement('canvas'), { width: 64, height: 48 });
        c.getContext('2d').fillRect(0, 0, 64, 48); return c.captureStream(5); };""")
    abrir(pagina)
    pagina.get_by_role("button", name="Encender cámara").click()
    pagina.locator("#btn-tomar:enabled").wait_for()
    assert not pagina.locator("#visor-vacio").is_visible()
    pagina.get_by_role("button", name="Apagar").click()
    assert pagina.locator("#visor-vacio").is_visible()


def test_lumea_cree_que_es_abre_la_tarjeta_con_la_ia_segura_y_no_cuando_duda(pagina, backend, foto):
    abrir(pagina)
    assert not pagina.get_by_text("Lumea cree que es…").is_visible()                  # antes de la foto solo está la invitación
    analizar(pagina, foto)
    pregunta = pagina.get_by_text("Lumea cree que es…")
    assert pregunta.is_visible()
    # va antes del nombre, y el título de la sección sigue ahí para el lector de pantalla
    assert pagina.evaluate("document.querySelector('.etiqueta__pregunta').getBoundingClientRect().bottom <= document.getElementById('backend-alimento').getBoundingClientRect().top")
    assert pagina.locator("#resultado").get_by_role("heading", name="Lo que reconoció Lumea").count() == 1
    # con la IA en duda el nombre ya es la pregunta («¿Cuál de estos es?»): no se afirma nada
    backend.poner("POST", "/predecir", cargar_respuesta("predecir_duda"))
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#backend-opciones button").first.wait_for()
    assert not pregunta.is_visible()


def test_la_certeza_sigue_en_palabras_y_numero_y_el_medidor_la_acompana(pagina, backend, foto):
    analizar(pagina, foto)                                                           # certeza 94
    assert pagina.locator("#backend-precision").inner_text() == "La IA está segura: 94 %"
    medidor = pagina.locator("#backend-medidor")
    assert medidor.get_attribute("aria-hidden") == "true" and medidor.inner_text() == ""
    assert medidor.evaluate("e => e.style.getPropertyValue('--certeza')") == "94%"
    assert medidor.evaluate("e => parseFloat(getComputedStyle(e, '::after').width) / parseFloat(getComputedStyle(e).width)") == pytest.approx(0.94, abs=0.02)
    # sin dato de certeza no queda un medidor suelto
    backend.poner("POST", "/predecir", cargar_respuesta("predecir_segura") | {"certeza": None})
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.wait_for_function("!document.getElementById('backend-precision').textContent")
    assert not pagina.locator(".etiqueta__certeza").is_visible()


def test_ningun_boton_del_resultado_ni_del_visor_promete_xp(pagina, backend, foto):
    analizar(pagina, foto, backend, cargar_respuesta("predecir_grupo"))
    botones = pagina.locator("main button").all_inner_texts()
    assert botones and not [b for b in botones if "XP" in b or "semilla" in b]                          # R5: la referencia trae «+10 XP» en «Sí, es esto»; aquí no


# ---------- Camino del cuidado, K0.5: el dato curioso largo ----------
# Isabella reescribió los datos curiosos: miden entre 500 y 860 caracteres. Líneas de unos 65 caracteres, buen
# interlineado y, si pasa de cuatro líneas, un «Leer más» con aria-expanded y sin animación.

DATO_860 = ("La papa criolla es de las primeras papas que se cultivaron en los Andes, mucho antes de que existieran los mercados "
            "de hoy. Las comunidades indígenas de la cordillera la sembraban en terrazas, la guardaban secándola al sol y la "
            "cocinaban en sopas y guisos que alimentaban a familias enteras durante las épocas frías. Su color amarillo viene "
            "de pigmentos naturales parecidos a los de otros alimentos amarillos y anaranjados, y su cáscara es tan fina que "
            "casi no hace falta pelarla. Cuando llegó a otros continentes cambió la manera de comer de muchos pueblos, y hoy "
            "sigue siendo protagonista del ajiaco, de la bandeja y de muchas mesas de domingo. Cada papa guarda así una parte "
            "de la historia de quienes la cultivaron, la cuidaron y la compartieron en las veredas y en las plazas de mercado. "
            "Por eso vale la pena probarla despacio y con curiosidad.")


def con_dato(texto):
    return cargar_respuesta("predecir_segura") | {"dato_curioso": texto}


def estado_dato(pagina):
    return pagina.evaluate("""() => { const p = document.getElementById('backend-dato'), b = document.getElementById('btn-dato-mas');
        const lh = parseFloat(getComputedStyle(p).lineHeight);
        return { lineas: Math.round(p.clientHeight / lh), todas: Math.round(p.scrollHeight / lh), visible: !b.hidden,
                 expandido: b.getAttribute('aria-expanded'), etiqueta: b.textContent.trim(), cortado: p.scrollHeight > p.clientHeight + 1 } }""")


def test_el_dato_de_860_caracteres_es_exactamente_el_que_prueba_el_largo(pagina):
    assert 840 <= len(DATO_860) <= 870


@pytest.mark.parametrize("ancho", [375, 1280])
def test_un_dato_largo_se_corta_a_cuatro_lineas_con_leer_mas_y_se_abre_y_se_cierra(pagina, backend, foto, ancho):
    pagina.set_viewport_size({"width": ancho, "height": 900})
    analizar(pagina, foto, backend, con_dato(DATO_860))
    e = estado_dato(pagina)
    assert e["visible"] and e["lineas"] == 4 and e["todas"] > 4 and e["cortado"]
    assert (e["expandido"], e["etiqueta"]) == ("false", "Leer más")
    boton = pagina.get_by_role("button", name="Leer más")
    assert boton.get_attribute("aria-controls") == "backend-dato"
    boton.click()
    e = estado_dato(pagina)
    assert e["expandido"] == "true" and e["etiqueta"] == "Leer menos" and not e["cortado"] and e["lineas"] == e["todas"]
    assert pagina.locator("#backend-dato").inner_text().replace("\n", " ").strip() == DATO_860                   # el texto completo
    pagina.get_by_role("button", name="Leer menos").click()
    e = estado_dato(pagina)
    assert e["expandido"] == "false" and e["lineas"] == 4 and e["cortado"]
    assert pagina.evaluate("document.documentElement.scrollWidth") <= ancho


def test_un_dato_corto_no_lleva_boton(pagina, backend, foto):
    analizar(pagina, foto, backend, con_dato("La arepa es de maíz y se come en todo el país desde hace siglos."))
    e = estado_dato(pagina)
    assert not e["visible"] and not e["cortado"]
    assert pagina.get_by_role("button", name="Leer más").count() == 0


def test_cuatro_lineas_justas_no_llevan_boton_y_la_quinta_si(pagina, backend, foto):
    # el límite: lo que cabe en cuatro líneas se ve entero; con una línea más aparece «Leer más»
    pagina.set_viewport_size({"width": 1280, "height": 900})
    analizar(pagina, foto, backend, con_dato("Palabra " * 20))
    cortos = estado_dato(pagina)["todas"]
    assert cortos <= 4
    backend.poner("POST", "/predecir", con_dato(" ".join(["Palabra"] * 60)))
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.wait_for_function("document.getElementById('backend-dato').textContent.split(' ').length > 50")
    assert estado_dato(pagina)["visible"]


def test_el_dato_largo_tiene_lineas_de_65_caracteres_como_maximo_y_buen_interlineado(pagina, backend, foto):
    pagina.set_viewport_size({"width": 900, "height": 900})                              # una columna: la tarjeta es ancha
    analizar(pagina, foto, backend, con_dato(DATO_860))
    pagina.get_by_role("button", name="Leer más").click()
    medidas = pagina.evaluate("""() => { const p = document.getElementById('backend-dato'), cs = getComputedStyle(p);
        const sonda = Object.assign(document.createElement('span'), { style: 'width:1ch;position:absolute;visibility:hidden' });
        p.appendChild(sonda); const ch = sonda.getBoundingClientRect().width; sonda.remove();
        return { ancho: p.getBoundingClientRect().width, ch, lh: parseFloat(cs.lineHeight), fs: parseFloat(cs.fontSize) } }""")
    assert medidas["ancho"] <= 65 * medidas["ch"] + 1
    assert medidas["lh"] >= 1.5 * medidas["fs"] - 0.1


def test_leer_mas_se_alcanza_con_el_teclado_y_mide_44_px(pagina, backend, foto):
    analizar(pagina, foto, backend, con_dato(DATO_860))
    boton = pagina.get_by_role("button", name="Leer más")
    for _ in range(40):
        pagina.keyboard.press("Tab")
        if pagina.evaluate("document.activeElement.id") == "btn-dato-mas":
            break
    assert pagina.evaluate("document.activeElement.id") == "btn-dato-mas"
    aro = boton.evaluate("e => { const c = getComputedStyle(e); return [c.outlineStyle, parseFloat(c.outlineWidth)] }")
    assert aro[0] != "none" and aro[1] >= 2                                              # el foco se ve
    pagina.keyboard.press("Enter")
    assert estado_dato(pagina)["expandido"] == "true"
    assert pagina.locator("#btn-dato-mas").bounding_box()["height"] >= 44              # (ahora se llama «Leer menos»)


def test_cortar_y_abrir_el_dato_no_lleva_animacion(pagina, backend, foto):
    # sin gamificación: la celebración de XP tiene su propia animación y podría caer en medio de la medida
    analizar(pagina, foto, backend, con_dato(DATO_860) | {"gamificacion": None})
    for sel in ("#backend-dato", "#btn-dato-mas"):
        d = pagina.locator(sel).evaluate("e => { const c = getComputedStyle(e); return [c.transitionDuration, c.animationName] }")
        assert d == ["0s", "none"], (sel, d)
    # nada se anima al abrirlo: se anota todo transitionrun y animationstart mientras se abre
    pagina.evaluate("window.__mov = []; ['transitionrun', 'animationstart'].forEach(t => document.addEventListener(t, e => window.__mov.push(t + ' ' + e.target.id), true))")
    pagina.get_by_role("button", name="Leer más").click()
    assert pagina.evaluate("window.__mov") == []


def test_cada_respuesta_nueva_vuelve_a_cortar_el_dato(pagina, backend, foto):
    analizar(pagina, foto, backend, con_dato(DATO_860))
    pagina.get_by_role("button", name="Leer más").click()
    assert estado_dato(pagina)["expandido"] == "true"
    backend.poner("POST", "/predecir", con_dato(DATO_860 + " Y sigue."))
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.wait_for_function("document.getElementById('backend-dato').textContent.endsWith('Y sigue.')")
    e = estado_dato(pagina)
    assert (e["expandido"], e["etiqueta"], e["lineas"]) == ("false", "Leer más", 4)


def test_al_girar_o_cambiar_el_ancho_se_vuelve_a_medir(pagina, backend, foto):
    pagina.set_viewport_size({"width": 1280, "height": 900})
    analizar(pagina, foto, backend, con_dato("Palabra " * 45))                           # ≈ 360 caracteres: 3 líneas en ancho, más en estrecho
    ancho = estado_dato(pagina)
    pagina.set_viewport_size({"width": 340, "height": 900})
    pagina.wait_for_function("(document.getElementById('btn-dato-mas').hidden === false)")
    estrecho = estado_dato(pagina)
    assert estrecho["todas"] > ancho["todas"] and estrecho["visible"] and estrecho["lineas"] == 4
    pagina.set_viewport_size({"width": 1280, "height": 900})
    pagina.wait_for_function("document.getElementById('btn-dato-mas').hidden === (" + str(not ancho["visible"]).lower() + ")")
    assert pagina.evaluate("window.__erroresRO || 0") == 0 and not [e for e in pagina.errores if "ResizeObserver" in e]


def test_el_dato_largo_con_consejos_sigue_sin_desbordar_ni_bajar_de_12_8_px(pagina, backend, foto):
    pagina.set_viewport_size({"width": 375, "height": 900})
    analizar(pagina, foto, backend, cargar_respuesta("predecir_bandeja_paisa") | {"dato_curioso": DATO_860})
    assert pagina.evaluate("document.documentElement.scrollWidth") <= 375
    assert estado_dato(pagina)["visible"]
    assert pagina.evaluate("parseFloat(getComputedStyle(document.getElementById('btn-dato-mas')).fontSize)") >= 12.8
