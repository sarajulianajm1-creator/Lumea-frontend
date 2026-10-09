"""avatar.html: el avatar, las pestañas (misiones, armario, calcomanías) y equipar/quitar."""
import pytest

from urllib.parse import parse_qs, urlparse

from conftest import CORREO_PRUEBA, avatar_estado, avatares_estado, cargar_respuesta, companero


def abrir(pagina, backend, ruta="avatar.html", avatar=None, progreso=None, calcomanias=None):
    if avatar is not None:
        backend.poner("GET", "/avatar", avatar)
    if progreso is not None:
        cuerpo = cargar_respuesta("progreso")
        cuerpo["progreso"].update(progreso)
        backend.poner("GET", "/progreso", cuerpo)
    if calcomanias is not None:
        backend.poner("GET", "/calcomanias", calcomanias[0], estado=calcomanias[1])
    pagina.goto(f"{pagina.servidor}/{ruta}")
    pagina.locator("#avatar-contenido").wait_for()


def persona_dibujada(pagina):
    """La persona grande de la vitrina, ya dibujada (la dirección data: del navegador, sin pedir nada afuera)."""
    pagina.locator("#avatar-figura img.avatar-figura__persona-img[src^='data:image/svg+xml']").wait_for()
    return pagina.locator("#avatar-figura img.avatar-figura__persona-img")


def svg_de(img):
    """El SVG de una <img> con dirección data: (para mirar si lleva animación)."""
    from urllib.parse import unquote
    return unquote(img.get_attribute("src").split(",", 1)[1])


def texto(pagina, selector):
    return pagina.locator(selector).inner_text().strip()


def prenda(pagina, nombre):
    return pagina.locator("#armario-lista .prenda", has_text=nombre)


# ---------- La vitrina ----------
def test_muestra_nivel_persona_compañero_y_barra(pagina, backend):
    abrir(pagina, backend)
    persona_dibujada(pagina)
    assert texto(pagina, "#avatar-nivel") == "Etapa 2"
    assert texto(pagina, "#avatar-faltan") == "Te faltan 35 semillas para la etapa 3: Gafas redondas"       # lo que se abre en la etapa que viene
    assert pagina.locator("#avatar-riel").get_attribute("aria-valuenow") == "30"
    assert "eyesVariant=happy" in pagina.locator("#avatar-figura img.avatar-figura__companero").get_attribute("data-fuente")    # el ánimo de hoy: «bien»
    assert pagina.locator("#avatar-figura").get_attribute("aria-label") == "Tu avatar y tu compañero Sol, tu ánimo de hoy: Bien"
    assert texto(pagina, "#avatar-puesto") == "Puesto: Camiseta lisa"
    assert pagina.errores == []


def test_un_solo_h1_y_la_navegacion_marca_avatar(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("h1").count() == 1
    assert pagina.locator("nav a[aria-current=page]").inner_text().strip() == "Avatar"


def test_la_persona_se_dibuja_en_el_navegador_grande_y_animada_con_el_companero_pequeno_y_quieto(pagina, backend):
    abrir(pagina, backend)
    persona = persona_dibujada(pagina)
    assert persona.get_attribute("alt") == ""
    assert "@keyframes" in svg_de(persona)                                            # la persona se mueve (slow)
    cajas = pagina.evaluate("""() => ({ persona: document.querySelector('.avatar-figura__persona-img').getBoundingClientRect().toJSON(),
                                      companero: document.querySelector('.avatar-figura__companero').getBoundingClientRect().toJSON() })""")
    assert cajas["persona"]["width"] >= 200                                           # grande
    assert cajas["companero"]["left"] >= cajas["persona"]["right"] - 1                # el compañero a su lado, no encima
    assert cajas["companero"]["width"] < cajas["persona"]["width"] / 2                # y más pequeño
    assert "animationVariant" not in pagina.locator("#avatar-figura img.avatar-figura__companero").get_attribute("data-fuente")   # quieto
    assert pagina.locator(ANIMADAS).count() == 0                                      # el compañero no pide movimiento


def test_con_movimiento_reducido_ni_la_persona_ni_el_companero_se_mueven(pagina, backend):
    pagina.emulate_media(reduced_motion="reduce")
    abrir(pagina, backend)
    assert "@keyframes" not in svg_de(persona_dibujada(pagina))
    assert pagina.locator(ANIMADAS).count() == 0


def test_si_el_backend_no_manda_la_persona_el_companero_es_la_figura_principal(pagina, backend):
    cuerpo = avatar_estado(2)
    cuerpo.pop("persona")
    abrir(pagina, backend, avatar=cuerpo)
    pagina.locator("#avatar-figura img.avatar-figura__cara").wait_for()
    assert pagina.locator("#avatar-figura").get_attribute("aria-label") == "Tu compañero Sol, tu ánimo de hoy: Bien"
    assert "animationVariant=slow" in pagina.locator("#avatar-figura img").get_attribute("data-fuente")


def test_sin_poder_dibujar_la_cara_queda_en_silueta(pagina, backend):
    cuerpo = avatar_estado(2)
    cuerpo.pop("persona")
    abrir(pagina, backend, avatar=cuerpo)
    pagina.locator("#avatar-figura img.avatar-figura__cara").wait_for()
    pagina.evaluate("document.querySelector('#avatar-figura img').dispatchEvent(new Event('error'))")
    assert pagina.locator("#avatar-figura img").count() == 0
    assert pagina.locator(".avatar-figura__silueta svg").count() == 1


# ---------- Pestañas ----------
def test_las_pestanas_siguen_el_patron_aria(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("[role=tablist] [role=tab]").all_inner_texts() == ["Mi armario", "Cómo me veo", "Misiones", "Calcomanías", "Compañero"]
    assert pagina.locator("#pestana-armario").get_attribute("aria-selected") == "true"      # el armario es la acción principal
    assert pagina.locator("#pestana-misiones").get_attribute("tabindex") == "-1"
    assert pagina.locator("#panel-armario").is_visible() and not pagina.locator("#panel-misiones").is_visible()
    assert pagina.locator("#panel-misiones").get_attribute("aria-labelledby") == "pestana-misiones"
    assert pagina.locator("#pestana-misiones").get_attribute("aria-controls") == "panel-misiones"


def test_las_flechas_cambian_de_pestana(pagina, backend):
    abrir(pagina, backend)
    pagina.locator("#pestana-armario").focus()
    pagina.keyboard.press("ArrowRight")
    assert pagina.evaluate("document.activeElement.id") == "pestana-como-me-veo"
    assert pagina.locator("#panel-como-me-veo").is_visible()
    pagina.keyboard.press("End")
    assert pagina.evaluate("document.activeElement.id") == "pestana-companero"
    pagina.keyboard.press("ArrowRight")                                         # da la vuelta
    assert pagina.evaluate("document.activeElement.id") == "pestana-armario"
    pagina.keyboard.press("ArrowLeft")
    assert pagina.evaluate("document.activeElement.id") == "pestana-companero"
    pagina.keyboard.press("Home")
    assert pagina.evaluate("document.activeElement.id") == "pestana-armario"


@pytest.mark.parametrize("ancla,panel", [("armario", "armario"), ("como-me-veo", "como-me-veo"), ("misiones", "misiones"), ("calcomanias", "calcomanias"), ("companero", "companero")])
def test_se_abre_en_la_pestana_del_ancla(pagina, backend, ancla, panel):
    abrir(pagina, backend, ruta=f"avatar.html#{ancla}")
    assert pagina.locator(f"#panel-{panel}").is_visible()
    assert pagina.locator(f"#pestana-{panel}").get_attribute("aria-selected") == "true"
    assert pagina.locator("[role=tabpanel]:visible").count() == 1


def test_un_ancla_que_no_existe_abre_el_armario(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#cualquier-cosa")
    assert pagina.locator("#panel-armario").is_visible()


def test_tocar_una_pestana_actualiza_el_ancla(pagina, backend):
    abrir(pagina, backend)
    pagina.locator("#pestana-calcomanias").click()
    assert pagina.evaluate("location.hash") == "#calcomanias"
    pagina.evaluate("location.hash = '#misiones'")
    assert pagina.locator("#panel-misiones").is_visible()


# ---------- Misiones ----------
def test_las_tres_misiones_con_su_xp(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#misiones")
    misiones = pagina.locator("#misiones-lista > li")
    assert misiones.count() == 3
    assert misiones.nth(0).inner_text().split("\n")[0] == "Agradece y disfruta una fruta de la creación"
    assert "+10 semillas" in misiones.nth(0).inner_text() and "Cumplida hoy" in misiones.nth(0).inner_text()
    assert "Para hoy" in misiones.nth(1).inner_text() and "Para hoy" in misiones.nth(2).inner_text()


def test_la_mision_cumplida_lleva_su_calcomania(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#misiones")
    misiones = pagina.locator("#misiones-lista > li")
    assert misiones.nth(0).locator(".pegatina").count() == 1                    # la fruta ya está ganada en el álbum
    assert misiones.nth(1).locator(".pegatina").count() == 0
    assert "Calcomanía: Una fruta para alegrar tu día" in misiones.nth(0).inner_text()


# ---------- Mi armario ----------
def test_el_armario_es_una_cuadricula_de_mosaicos_con_la_persona_puesta_cada_prenda(pagina, backend):
    abrir(pagina, backend)
    mosaicos = pagina.locator("#armario-lista .prenda")
    assert mosaicos.count() == 10                                                       # una por etapa, de la 1 a la 10
    assert [m.locator(".prenda__nombre").inner_text() for m in mosaicos.all()][:5] == [
        "Camiseta lisa", "Camiseta de rayas", "Gafas redondas", "Overol de jardín", "Camisa de cuadros"]
    pagina.wait_for_function("[...document.querySelectorAll('#armario-lista img.prenda__persona')].every(i => i.src.startsWith('data:image/svg+xml'))")
    # cada mosaico dibuja a la persona con SUS rasgos y esa prenda: los dibujos son distintos entre sí
    assert len(set(pagina.eval_on_selector_all("#armario-lista img.prenda__persona", "e => e.map(i => i.src)"))) == 10
    assert "Disponible" in prenda(pagina, "Camiseta de rayas").inner_text() and "Puesto" in prenda(pagina, "Camiseta lisa").inner_text()
    assert pagina.errores == []


def test_lo_bloqueado_dice_la_etapa_lleva_candado_y_no_hace_nada(pagina, backend):
    abrir(pagina, backend)
    gafas = prenda(pagina, "Gafas de sol")
    assert "Etapa 7" in gafas.inner_text() and gafas.locator(".prenda__candado").count() == 1
    assert "prenda--bloqueada" in gafas.get_attribute("class")
    boton = gafas.get_by_role("button")
    assert boton.get_attribute("aria-disabled") == "true"
    assert boton.get_attribute("aria-label") == "Gafas de sol, se abre en la etapa 7"
    assert boton.get_attribute("aria-pressed") is None
    boton.click(force=True)            # Playwright lo considera «no habilitado» por aria-disabled
    pagina.wait_for_timeout(150)
    assert ("POST", "/avatar/equipar") not in backend.llamadas
    assert "Puesto" not in gafas.inner_text()


def test_ponerse_algo_guarda_cambia_la_persona_de_la_vitrina_y_lo_dice(pagina, backend):
    backend.poner("POST", "/avatar/equipar", avatar_estado(2, ropa="camiseta_rayas"))
    abrir(pagina, backend)
    antes = persona_dibujada(pagina).get_attribute("src")
    boton = prenda(pagina, "Camiseta de rayas").get_by_role("button", name="Camiseta de rayas")
    assert boton.get_attribute("aria-pressed") == "false"
    boton.click()
    pagina.locator("#armario-lista .prenda--puesta", has_text="Camiseta de rayas").wait_for()
    assert backend.cuerpo_enviado("POST", "/avatar/equipar") == {"email": "prueba@lumea.test", "tipo": "ropa", "item_id": "camiseta_rayas"}
    assert prenda(pagina, "Camiseta de rayas").get_by_role("button").get_attribute("aria-pressed") == "true"
    assert "Puesto" in prenda(pagina, "Camiseta de rayas").inner_text()
    assert texto(pagina, "#avatar-puesto") == "Puesto: Camiseta de rayas"
    assert texto(pagina, "#avatar-aviso") == "Te pusiste Camiseta de rayas."
    pagina.wait_for_function("(a) => document.querySelector('.avatar-figura__persona-img').src !== a", arg=antes)      # la vitrina cambió
    # el avatar dio su saltico (un solo movimiento) y el foco sigue en el mismo botón
    assert pagina.evaluate("document.activeElement.dataset.objeto") == "camiseta_rayas"


def test_el_avatar_da_un_saltico_al_ponerse_algo(pagina, backend):
    backend.poner("POST", "/avatar/equipar", avatar_estado(3, accesorio="gafas_redondas"))
    backend.poner("GET", "/avatar", avatar_estado(3))
    abrir(pagina, backend)
    prenda(pagina, "Gafas redondas").get_by_role("button").click()
    pagina.locator("#avatar-figura.avatar-figura--saltico").wait_for()
    pagina.locator("#avatar-figura.avatar-figura--saltico").wait_for(state="detached")     # una sola vez


def test_tocar_la_prenda_puesta_se_la_quita_y_la_ropa_vuelve_a_la_camiseta_lisa(pagina, backend):
    backend.poner("GET", "/avatar", avatar_estado(4, ropa="overol", accesorio="gafas_redondas"))
    backend.poner("POST", "/avatar/quitar", avatar_estado(4, ropa="camiseta_lisa", accesorio="gafas_redondas"))
    abrir(pagina, backend)
    assert texto(pagina, "#avatar-puesto") == "Puesto: Overol de jardín y Gafas redondas"
    prenda(pagina, "Overol de jardín").get_by_role("button").click()
    pagina.locator("#armario-lista .prenda--puesta", has_text="Camiseta lisa").wait_for()
    assert backend.cuerpo_enviado("POST", "/avatar/quitar") == {"email": "prueba@lumea.test", "tipo": "ropa"}
    assert texto(pagina, "#avatar-aviso") == "Te quitaste Overol de jardín."
    assert texto(pagina, "#avatar-puesto") == "Puesto: Camiseta lisa y Gafas redondas"
    assert pagina.locator("#armario-lista .prenda--puesta").count() == 2


def test_equipar_con_el_teclado(pagina, backend):
    backend.poner("POST", "/avatar/equipar", avatar_estado(2, ropa="camiseta_rayas"))
    abrir(pagina, backend)
    prenda(pagina, "Camiseta de rayas").get_by_role("button").focus()
    pagina.keyboard.press("Enter")
    pagina.locator("#armario-lista .prenda--puesta", has_text="Camiseta de rayas").wait_for()


def test_si_el_backend_dice_que_esta_bloqueado(pagina, backend):
    # El servidor manda 403 aunque el mosaico estuviera abierto (la etapa se verifica allá)
    backend.poner("POST", "/avatar/equipar", {"error": "El objeto \"camiseta_rayas\" todavía está bloqueado.", "nivel_maximo": 1,
                                               "nivel_requerido": 2, "niveles_faltantes": 1}, estado=403)
    abrir(pagina, backend)
    prenda(pagina, "Camiseta de rayas").get_by_role("button").click()
    pagina.locator("#avatar-aviso", has_text="Todavía no se abre").wait_for()
    assert texto(pagina, "#avatar-aviso") == "Todavía no se abre: te falta 1 etapa."
    assert "Puesto" not in prenda(pagina, "Camiseta de rayas").inner_text()


def test_si_falla_el_guardado_no_cambia_nada(pagina, backend):
    backend.poner("POST", "/avatar/equipar", {"error": "x"}, estado=500)
    abrir(pagina, backend)
    prenda(pagina, "Camiseta de rayas").get_by_role("button").click()
    pagina.locator("#avatar-aviso", has_text="No se pudo guardar").wait_for()
    assert texto(pagina, "#avatar-puesto") == "Puesto: Camiseta lisa"


# ---------- Cómo me veo: los rasgos son libres ----------
RASGOS_ENVIABLES = {"skinColor", "topVariant", "hairColor", "eyesVariant", "mouthVariant", "cheeksVariant", "beardVariant", "shirtColor",
                    "eyebrowsVariant", "noseVariant", "pantsColor", "shoesColor", "backgroundColor"}


def test_los_rasgos_nunca_se_bloquean_y_van_en_secciones_con_subtitulo(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#como-me-veo")
    assert pagina.locator("#rasgos-form .rasgos-seccion__titulo").all_inner_texts() == ["Cara", "Pelo", "Ropa", "Fondo"]
    leyendas = pagina.locator("#rasgos-form legend").all_inner_texts()
    assert leyendas == ["Tono de piel", "Ojos", "Cejas", "Nariz", "Boca", "Mejillas", "Barba",
                        "Peinado", "Color de pelo", "Color de la camiseta", "Color del pantalón", "Color de los zapatos", "Fondo"]
    assert pagina.locator("#rasgos-form fieldset").count() == 13
    assert pagina.locator("#rasgos-form input[type=radio]:disabled").count() == 0
    assert pagina.locator("#rasgos-form [aria-disabled=true]").count() == 0
    assert pagina.locator("#rasgos-form .prenda--bloqueada, #rasgos-form .prenda__candado").count() == 0


def test_si_el_backend_aun_no_manda_los_rasgos_nuevos_no_se_dibujan(pagina, backend):
    cuerpo = avatar_estado(2)
    for k in ("eyebrowsVariant", "noseVariant", "pantsColor", "shoesColor", "backgroundColor"):
        cuerpo["rasgos_disponibles"].pop(k)
        cuerpo["persona"]["rasgos"].pop(k)
    abrir(pagina, backend, ruta="avatar.html#como-me-veo", avatar=cuerpo)
    assert pagina.locator("#rasgos-form fieldset").count() == 8
    assert pagina.locator("#rasgos-form .rasgos-seccion__titulo").all_inner_texts() == ["Cara", "Pelo", "Ropa"]        # «Fondo» queda sin nada y no se dibuja
    persona_dibujada(pagina)


def test_sin_fondo_es_una_opcion_que_se_guarda_como_null(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#como-me-veo")
    assert pagina.get_by_role("radio", name="Sin fondo").is_checked()
    pagina.get_by_role("radio", name="Celeste").check(force=True)
    backend.poner("POST", "/avatar/rasgos", avatar_estado(2, rasgos={"backgroundColor": "b6e3f4"}))
    pagina.get_by_role("button", name="Guardar cómo me veo").click()
    pagina.locator("#avatar-aviso", has_text="Guardamos cómo te ves.").wait_for()
    assert backend.cuerpo_enviado("POST", "/avatar/rasgos")["rasgos"]["backgroundColor"] == "b6e3f4"
    pagina.get_by_role("radio", name="Sin fondo").check(force=True)
    backend.poner("POST", "/avatar/rasgos", avatar_estado(2))
    pagina.get_by_role("button", name="Guardar cómo me veo").click()
    pagina.wait_for_function("(window.__n = (window.__n || 0) + 1) > 3 && document.getElementById('avatar-aviso').textContent === 'Guardamos cómo te ves.'")
    assert backend.cuerpo_enviado("POST", "/avatar/rasgos")["rasgos"]["backgroundColor"] is None


def test_los_mosaicos_son_una_cuadricula_del_mismo_tamano_con_nombre_de_dos_lineas(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#como-me-veo")
    pagina.wait_for_function("[...document.querySelectorAll('#rasgos-form img[data-rasgo]')].every(i => i.src.startsWith('data:image/svg+xml'))")
    minis = pagina.locator("#rasgos-form .rasgo--mosaico .rasgo__mini").evaluate_all("e => e.map(x => { const r = x.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)] })")
    assert len({tuple(m) for m in minis}) == 1 and minis[0][0] >= 80                          # todos iguales y de 88 px o más
    cols = pagina.locator("#rasgos-form .rasgo--eyesVariant .rasgo__opciones").evaluate("e => getComputedStyle(e).gridTemplateColumns.split(' ').length")
    assert cols >= 3
    alto = pagina.locator("#rasgos-form .rasgo__texto").evaluate_all("e => [...new Set(e.map(x => Math.round(x.getBoundingClientRect().height)))]")
    assert all(a >= 2 * 1.25 * 12 for a in alto)                                              # espacio fijo para dos líneas


def test_los_mosaicos_de_la_cara_se_acercan_a_ella(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#como-me-veo")
    pagina.wait_for_function("[...document.querySelectorAll('#rasgos-form img[data-rasgo]')].every(i => i.src.startsWith('data:image/svg+xml'))")
    from urllib.parse import unquote
    def caja_de(clave):
        svg = unquote(pagina.locator(f"#rasgos-form img[data-rasgo={clave}]").first.get_attribute("src").split(",", 1)[1])
        return svg.split('viewBox="')[1].split('"')[0].split()
    for clave in ("eyesVariant", "eyebrowsVariant", "noseVariant", "mouthVariant", "cheeksVariant", "beardVariant"):
        assert float(caja_de(clave)[2]) < 128, clave                                          # un recorte del lienzo de 128
    assert caja_de("topVariant") == ["0", "0", "128", "128"]                                  # el peinado se ve con todo el cuerpo


def test_los_8_tonos_de_piel_van_en_4_por_2_en_el_celular_y_en_una_fila_en_pantalla_ancha(pagina, backend):
    pagina.set_viewport_size({"width": 390, "height": 844})
    abrir(pagina, backend, ruta="avatar.html#como-me-veo")
    def filas():
        return pagina.locator(".rasgo--skinColor .rasgo__muestra").evaluate_all("e => [...new Set(e.map(x => Math.round(x.getBoundingClientRect().top)))].length")
    assert filas() == 2
    assert pagina.locator(".rasgo--skinColor .rasgo__muestra").evaluate_all("e => [...new Set(e.slice(0, 4).map(x => Math.round(x.getBoundingClientRect().top)))].length") == 1
    pagina.set_viewport_size({"width": 1280, "height": 800})
    assert filas() == 1


def test_en_el_celular_una_vista_previa_pequena_y_fija_acompana_la_edicion(pagina, backend):
    pagina.set_viewport_size({"width": 390, "height": 844})
    abrir(pagina, backend, ruta="avatar.html#como-me-veo")
    pagina.locator("#rasgos-vista-img[src^='data:image/svg+xml']").wait_for()
    assert pagina.locator(".rasgos-vista").evaluate("e => getComputedStyle(e).position") == "sticky"
    pagina.evaluate("window.scrollTo(0, document.querySelector('#rasgos-form').getBoundingClientRect().top + scrollY + 500)")
    pagina.wait_for_timeout(200)
    assert pagina.evaluate("scrollY") > 600
    caja = pagina.locator(".rasgos-vista").bounding_box()
    assert 0 <= caja["y"] < 40 and caja["width"] <= 100                                       # sigue a la vista y es pequeña
    pagina.set_viewport_size({"width": 1280, "height": 800})
    assert not pagina.locator(".rasgos-vista").is_visible()                                   # en el computador la vitrina ya está al lado


def test_las_pestanas_van_en_una_sola_fila_dentro_de_su_contenedor(pagina, backend):
    for ancho in (390, 1280):
        pagina.set_viewport_size({"width": ancho, "height": 844})
        abrir(pagina, backend, ruta="avatar.html")
        pagina.reload()
        pagina.locator("#avatar-contenido").wait_for()
        tops = pagina.locator(".pestana").evaluate_all("e => [...new Set(e.map(x => Math.round(x.getBoundingClientRect().top)))].length")
        assert tops == 1, f"{ancho}: las pestañas se parten en filas"
        caja = pagina.locator("#pestanas").bounding_box()
        assert caja["x"] + caja["width"] <= ancho + 1
        assert pagina.evaluate("document.documentElement.scrollWidth") <= ancho
    # en el celular no caben todas: la fila se desliza de lado (con imán), sin partirse
    pagina.set_viewport_size({"width": 390, "height": 844})
    pagina.reload()
    pagina.locator("#avatar-contenido").wait_for()
    datos = pagina.locator("#pestanas").evaluate("e => [getComputedStyle(e).overflowX, getComputedStyle(e).scrollSnapType, e.scrollWidth > e.clientWidth]")
    assert datos[0] == "auto" and datos[1].startswith("x") and datos[2] is True
    pagina.locator("#pestana-companero").click()                                              # elegir la última la deja a la vista
    assert pagina.locator("#pestana-companero").evaluate("e => { const f = e.parentElement.getBoundingClientRect(), r = e.getBoundingClientRect(); return r.left >= f.left - 1 && r.right <= f.right + 1 }")
    assert pagina.locator("[role=tab]").count() == 5 and pagina.evaluate("location.hash") == "#companero"


def test_los_tonos_de_piel_se_llaman_tono_1_a_tono_8_y_hay_un_radio_con_etiqueta_por_opcion(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#como-me-veo")
    piel = pagina.locator("#rasgos-form fieldset", has=pagina.locator("legend", has_text="Tono de piel"))
    assert [t.inner_text() for t in piel.locator(".solo-lector").all()] == [f"Tono {n}" for n in range(1, 9)]
    assert piel.locator("input[type=radio]").count() == 8
    assert piel.locator("input[type=radio]:checked").get_attribute("value") == "c99062"          # el de ahora (Tono 4)
    # cada radio está dentro de su <label> y el grupo trae su <legend>
    assert pagina.locator("#rasgos-form label.rasgo__opcion > input[type=radio]").count() == pagina.locator("#rasgos-form input[type=radio]").count()
    assert pagina.get_by_role("radio", name="Tono 5").count() == 1


def test_mejillas_y_barba_traen_ninguno_y_se_guarda_como_null(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#como-me-veo")
    assert pagina.get_by_role("radio", name="Ninguno").is_checked() and pagina.get_by_role("radio", name="Ninguna").is_checked()
    pagina.get_by_role("radio", name="Pecas").check(force=True)
    backend.poner("POST", "/avatar/rasgos", avatar_estado(2, rasgos={"cheeksVariant": "freckles"}))
    pagina.get_by_role("button", name="Guardar cómo me veo").click()
    pagina.locator("#avatar-aviso", has_text="Guardamos cómo te ves.").wait_for()
    enviado = backend.cuerpo_enviado("POST", "/avatar/rasgos")
    assert enviado["rasgos"]["cheeksVariant"] == "freckles" and enviado["rasgos"]["beardVariant"] is None
    pagina.get_by_role("radio", name="Ninguno").check(force=True)            # «Ninguno» vuelve a null
    backend.poner("POST", "/avatar/rasgos", avatar_estado(2))
    pagina.get_by_role("button", name="Guardar cómo me veo").click()
    pagina.wait_for_function("document.getElementById('avatar-aviso').textContent === 'Guardamos cómo te ves.'")
    assert backend.cuerpo_enviado("POST", "/avatar/rasgos")["rasgos"]["cheeksVariant"] is None


def test_cambiar_un_rasgo_cambia_la_vista_previa_al_instante_y_guardar_envia_solo_claves_permitidas(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#como-me-veo")
    antes = persona_dibujada(pagina).get_attribute("src")
    pagina.get_by_role("radio", name="Trenzas").check(force=True)
    pagina.wait_for_function("(a) => document.querySelector('.avatar-figura__persona-img').src !== a", arg=antes)
    backend.poner("POST", "/avatar/rasgos", avatar_estado(2, rasgos={"topVariant": "braids", "skinColor": "b07347"}))
    pagina.get_by_role("radio", name="Tono 5").check(force=True)
    pagina.get_by_role("button", name="Guardar cómo me veo").click()
    pagina.locator("#avatar-aviso", has_text="Guardamos cómo te ves.").wait_for()
    enviado = backend.cuerpo_enviado("POST", "/avatar/rasgos")
    assert enviado["email"] == "prueba@lumea.test"
    assert set(enviado["rasgos"]) <= RASGOS_ENVIABLES and enviado["rasgos"]["topVariant"] == "braids" and enviado["rasgos"]["skinColor"] == "b07347"
    assert all(isinstance(v, str) or v is None for v in enviado["rasgos"].values())


def test_si_guardar_los_rasgos_falla_se_avisa(pagina, backend):
    backend.poner("POST", "/avatar/rasgos", {"error": "El valor de \"topVariant\" no es válido."}, estado=400)
    abrir(pagina, backend, ruta="avatar.html#como-me-veo")
    pagina.get_by_role("radio", name="Trenzas").check(force=True)
    pagina.get_by_role("button", name="Guardar cómo me veo").click()
    pagina.locator("#avatar-aviso", has_text="No se pudo guardar").wait_for()


def test_los_mosaicos_de_peinado_ojos_y_boca_se_dibujan_en_el_navegador(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#como-me-veo")
    pagina.wait_for_function("[...document.querySelectorAll('#rasgos-form img[data-rasgo]')].every(i => i.src.startsWith('data:image/svg+xml'))")
    assert pagina.locator("#rasgos-form img[data-rasgo=topVariant]").count() == 17          # sin gorras, gorros ni orejas
    assert pagina.locator("#rasgos-form img[data-rasgo=eyesVariant]").count() == 8
    assert pagina.locator("#rasgos-form img[data-rasgo=mouthVariant]").count() == 10


# ---------- Álbum ----------
def test_el_album_muestra_ganadas_y_por_ganar(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#calcomanias")
    assert texto(pagina, "#album-resumen") == "3 de 10 calcomanías"
    assert pagina.locator(".album__item").count() == 10
    assert pagina.locator(".album__item--ganada").count() == 3
    ganada = pagina.locator(".album__item--ganada", has_text="Primer paso")
    assert "Has dado el primer paso en el camino del cuidado." in ganada.inner_text() and "Ganada el 3 de octubre" in ganada.inner_text()
    vacia = pagina.locator(".album__item--vacia", has_text="Siete días caminando juntos")
    assert "Cómo se gana: Llega a una racha de 7 días." in vacia.inner_text()
    assert vacia.locator(".pegatina--vacia").count() == 1 and ganada.locator(".pegatina--vacia").count() == 0


def test_cada_calcomania_toma_el_color_de_su_rol(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#calcomanias")
    roles = pagina.eval_on_selector_all(".album__item .pegatina", "e => e.map(p => p.className.match(/pegatina--(comida|logro|mision|emocion|duda)/)[1])")
    assert roles == ["comida", "comida", "mision", "mision", "emocion", "duda", "logro", "logro", "logro", "logro"]


def test_si_no_carga_el_album_lo_demas_funciona(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#calcomanias", calcomanias=({"error": "x"}, 500))
    assert pagina.locator("#album-error").is_visible()
    assert pagina.locator(".album__item").count() == 0
    pagina.locator("#pestana-armario").click()
    assert pagina.locator("#armario-lista .prenda").count() == 10


# ---------- Estados, seguridad y tamaño ----------
def test_sin_sesion_pide_iniciar_sesion(pagina):
    pagina.add_init_script("localStorage.clear()")
    pagina.goto(f"{pagina.servidor}/avatar.html")
    pagina.locator("#sin-sesion").wait_for()
    assert not pagina.locator("#avatar-contenido").is_visible()


def test_error_de_conexion_se_puede_reintentar(pagina, backend):
    backend.poner("GET", "/avatar", {"error": "x"}, estado=500)
    pagina.goto(f"{pagina.servidor}/avatar.html")
    pagina.locator("#estado-error").wait_for()
    backend.respuestas.clear()
    pagina.get_by_role("button", name="Intentar otra vez").click()
    pagina.locator("#avatar-contenido").wait_for()
    assert texto(pagina, "#avatar-nivel") == "Etapa 2"


def test_el_texto_del_servidor_nunca_es_html(pagina, backend):
    malo = '<img src=x onerror="window.hackeado=1">'
    cuerpo = avatar_estado(2)
    cuerpo["objetos"]["ropa"][0]["nombre"] = malo
    cuerpo["rasgos_disponibles"]["topVariant"]["opciones"]["short"] = malo
    abrir(pagina, backend, ruta="avatar.html#armario", avatar=cuerpo)
    assert pagina.locator(".prenda__nombre", has_text="onerror").count() == 1
    pagina.locator("#pestana-como-me-veo").click()
    assert pagina.locator("#rasgos-form .rasgo__texto", has_text="onerror").count() == 1
    assert pagina.locator("#armario-lista .prenda img:not(.prenda__persona), #rasgos-form img:not([data-rasgo])").count() == 0
    assert pagina.evaluate("window.hackeado") is None


def test_no_hay_calorias_ni_comparaciones(pagina, backend):
    abrir(pagina, backend)
    for ruta in ("armario", "como-me-veo", "misiones", "calcomanias", "companero"):
        pagina.locator(f"#pestana-{ruta}").click()
    contenido = pagina.locator("main").inner_text().lower()
    for prohibido in ("kcal", "caloría", "ranking", "otros usuarios", "perdiste"):
        assert prohibido not in contenido


@pytest.mark.parametrize("ancla", ["armario", "como-me-veo", "misiones", "calcomanias", "companero"])
def test_a_375px_no_se_desborda(pagina, backend, ancla):
    pagina.set_viewport_size({"width": 375, "height": 800})
    abrir(pagina, backend, ruta=f"avatar.html#{ancla}")
    assert pagina.evaluate("document.documentElement.scrollWidth") <= 375


def test_la_celebracion_lleva_al_armario_y_al_album(pagina, backend):
    # Los botones «Ponérmelo» y «Ver mi álbum» de la celebración apuntan a estas anclas
    abrir(pagina, backend, ruta="avatar.html#armario")
    assert pagina.locator("#pestana-armario").get_attribute("aria-selected") == "true"
    abrir(pagina, backend, ruta="avatar.html#calcomanias")
    assert pagina.locator("#pestana-calcomanias").get_attribute("aria-selected") == "true"


# ---------- Tu compañero (Camino del cuidado, K2) ----------

NOMBRES = ["Sol", "Luna", "Río", "Montaña", "Orquídea", "Colibrí"]
ETAPAS = {"Río": 3, "Montaña": 5, "Orquídea": 7, "Colibrí": 9}


ANIMADAS = 'img[data-fuente*="animationVariant=slow"], img[data-fuente*="animationVariant=medium"]'      # lo que pide movimiento (none no)


def tarjeta_de(pagina, nombre):
    return pagina.locator("#companeros-lista .prenda", has=pagina.locator(".prenda__nombre", has_text=nombre))


def parametros(src):
    return {k: v[0] for k, v in parse_qs(urlparse(src).query).items()}


def test_la_seccion_tu_companero_muestra_los_seis_con_su_nombre_y_su_etapa(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#companero")
    assert pagina.get_by_role("heading", name="Tu compañero", level=2).count() == 1
    tarjetas = pagina.locator("#companeros-lista .prenda")
    assert [t.locator(".prenda__nombre").inner_text() for t in tarjetas.all()] == NOMBRES
    assert tarjeta_de(pagina, "Sol").locator(".prenda__estado").inner_text() == "Tu compañero"
    assert tarjeta_de(pagina, "Luna").locator(".prenda__estado").inner_text() == "Disponible"
    for nombre, etapa in ETAPAS.items():
        assert tarjeta_de(pagina, nombre).locator(".prenda__estado").inner_text() == f"Se abre en la etapa {etapa}"
    assert pagina.errores == []


def test_los_bloqueados_llevan_candado_etapa_y_aria_disabled_y_no_hacen_nada(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#companero")
    for nombre, etapa in ETAPAS.items():
        tarjeta = tarjeta_de(pagina, nombre)
        assert "prenda--bloqueada" in tarjeta.get_attribute("class")
        assert tarjeta.locator(".prenda__candado").count() == 1                       # el candado, que es un dibujo, no un emoji
        boton = tarjeta.get_by_role("button")
        assert boton.inner_text() == f"Etapa {etapa}"
        assert boton.get_attribute("aria-disabled") == "true"
        assert boton.get_attribute("aria-label") == f"{nombre}, se abre en la etapa {etapa}"
        boton.click(force=True)                                                       # aria-disabled: se puede tocar, no hace nada
    assert ("POST", "/avatar") not in backend.llamadas
    # Los dos primeros (Sol y Luna) y el elegido no llevan candado
    assert tarjeta_de(pagina, "Luna").locator(".prenda__candado").count() == 0
    assert tarjeta_de(pagina, "Sol").locator(".prenda__candado").count() == 0


def test_los_seis_van_quietos_sin_datos_de_la_persona_y_con_alt_vacio(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#companero")
    imagenes = pagina.locator("#companeros-lista img")
    assert imagenes.count() == 6
    for img in imagenes.all():
        src = img.get_attribute("data-fuente")
        datos = parametros(src)
        assert src.startswith("https://api.dicebear.com/10.x/gaze/svg?")
        assert "animationVariant" not in datos                                        # quietos
        assert datos["seed"].startswith("lumea-") and set(datos) <= {"seed", "shapeVariant", "bodyColor", "eyesVariant"}
        assert CORREO_PRUEBA.split("@")[0] not in src and "@" not in src
        assert img.get_attribute("alt") == ""
    assert pagina.locator("#companeros-lista .prenda__imagen").evaluate_all("e => e.every(x => x.getAttribute('aria-hidden') === 'true')")


def test_elegir_un_companero_lo_guarda_lo_marca_y_el_foco_se_queda(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#companero")
    backend.poner("GET", "/progreso", _progreso_con(companero("luna", "bien")))        # lo que el backend dirá después de elegir
    boton = tarjeta_de(pagina, "Luna").get_by_role("button")
    assert boton.inner_text() == "Elegir" and boton.get_attribute("aria-label") == "Elegir a Luna"
    boton.click()
    pagina.locator("#companeros-lista .prenda--puesta .prenda__nombre", has_text="Luna").wait_for()
    assert backend.cuerpo_enviado("POST", "/avatar") == {"email": CORREO_PRUEBA, "avatar_id": "luna"}
    assert tarjeta_de(pagina, "Luna").get_by_role("button").inner_text() == "Elegido"
    assert tarjeta_de(pagina, "Luna").get_by_role("button").get_attribute("aria-label") == "Elegido: Luna"
    assert tarjeta_de(pagina, "Sol").get_by_role("button").inner_text() == "Elegir"
    assert pagina.locator("#companeros-lista .prenda--puesta").count() == 1
    assert pagina.evaluate("document.activeElement.dataset.companero") == "luna"        # el foco no se pierde
    assert texto(pagina, "#avatar-aviso") == "Tu compañero ahora es Luna."
    # la figura grande ya es Luna, con los ojos del ánimo de hoy
    pagina.wait_for_function("document.querySelector('#avatar-figura img.avatar-figura__companero') && document.querySelector('#avatar-figura img.avatar-figura__companero').dataset.fuente.includes('seed=lumea-luna')")
    assert "eyesVariant=happy" in pagina.locator("#avatar-figura img.avatar-figura__companero").get_attribute("data-fuente")
    assert pagina.locator("#avatar-figura").get_attribute("aria-label") == "Tu avatar y tu compañero Luna, tu ánimo de hoy: Bien"


def _progreso_con(avatar):
    cuerpo = cargar_respuesta("progreso")
    cuerpo["progreso"]["avatar"] = avatar
    return cuerpo


def test_elegir_un_companero_con_el_teclado(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#companero")
    backend.poner("GET", "/progreso", _progreso_con(companero("luna", "bien")))
    tarjeta_de(pagina, "Luna").get_by_role("button").focus()
    pagina.keyboard.press("Enter")
    pagina.locator("#companeros-lista .prenda--puesta .prenda__nombre", has_text="Luna").wait_for()
    assert backend.cuerpo_enviado("POST", "/avatar")["avatar_id"] == "luna"


def test_si_el_backend_dice_que_el_companero_esta_bloqueado(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#companero")
    backend.poner("POST", "/avatar", {"error": "El avatar \"luna\" todavía está bloqueado.", "nivel_maximo": 1,
                                       "nivel_requerido": 3, "niveles_faltantes": 2}, estado=403)
    tarjeta_de(pagina, "Luna").get_by_role("button").click()
    pagina.wait_for_function("document.getElementById('avatar-aviso').textContent !== ''")
    assert texto(pagina, "#avatar-aviso") == "Todavía no se abre: te faltan 2 etapas."
    assert tarjeta_de(pagina, "Sol").locator(".prenda__estado").inner_text() == "Tu compañero"       # nada cambió


def test_si_falla_la_conexion_al_elegir_no_cambia_nada(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#companero")
    backend.poner("POST", "/avatar", {"success": False}, estado=500)
    tarjeta_de(pagina, "Luna").get_by_role("button").click()
    pagina.wait_for_function("document.getElementById('avatar-aviso').textContent !== ''")
    assert texto(pagina, "#avatar-aviso") == "No se pudo guardar el cambio."
    assert tarjeta_de(pagina, "Sol").locator(".prenda__estado").inner_text() == "Tu compañero"


def test_con_un_compañero_mas_adelante_se_desbloquean_mas(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#companero")
    backend.poner("GET", "/avatares", avatares_estado(nivel=5, actual="luna"))
    pagina.reload()
    pagina.locator("#avatar-contenido").wait_for()
    assert tarjeta_de(pagina, "Luna").locator(".prenda__estado").inner_text() == "Tu compañero"
    assert tarjeta_de(pagina, "Río").get_by_role("button").inner_text() == "Elegir"
    assert tarjeta_de(pagina, "Montaña").get_by_role("button").inner_text() == "Elegir"
    assert tarjeta_de(pagina, "Orquídea").get_by_role("button").inner_text() == "Etapa 7"


def test_sin_internet_los_companeros_quedan_en_silueta_con_su_nombre(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#companero")
    pagina.evaluate("document.querySelectorAll('#companeros-lista img').forEach(i => i.dispatchEvent(new Event('error')))")
    assert pagina.locator("#companeros-lista img").count() == 0
    assert pagina.locator("#companeros-lista .prenda__imagen svg").count() == 6
    assert [t.locator(".prenda__nombre").inner_text() for t in pagina.locator("#companeros-lista .prenda").all()] == NOMBRES


def test_si_no_cargan_los_companeros_lo_demas_funciona(pagina, backend):
    backend.poner("GET", "/avatares", {"success": False, "error": "sin perfil"}, estado=404)
    abrir(pagina, backend, ruta="avatar.html#companero")
    assert pagina.locator("#companeros-error").is_visible()
    assert pagina.locator("#companeros-lista .prenda").count() == 0
    assert texto(pagina, "#avatar-nivel") == "Etapa 2"
    persona_dibujada(pagina)


def test_el_nombre_del_companero_nunca_es_html(pagina, backend):
    cuerpo = avatares_estado()
    cuerpo["avatares"][1]["nombre"] = '<img src=x onerror="window.hackeado=1">'
    backend.poner("GET", "/avatares", cuerpo)
    abrir(pagina, backend, ruta="avatar.html#companero")
    assert pagina.locator("#companeros-lista .prenda__nombre", has_text="onerror").count() == 1
    assert pagina.evaluate("window.hackeado") is None


@pytest.mark.parametrize("ancho", [375, 1280])
def test_la_seccion_de_companeros_no_desborda(pagina, backend, ancho):
    pagina.set_viewport_size({"width": ancho, "height": 900})
    abrir(pagina, backend, ruta="avatar.html#companero")
    assert pagina.evaluate("document.documentElement.scrollWidth") <= ancho
    caja = pagina.locator("#panel-companero").bounding_box()
    assert caja["x"] + caja["width"] <= ancho


def test_la_accion_principal_de_avatar_es_el_armario_y_nada_queda_debajo_de_la_vitrina(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("#pestana-armario").get_attribute("aria-selected") == "true"
    # los botones de los compañeros son secundarios; el armario es la pestaña con la que se abre
    pagina.set_viewport_size({"width": 1280, "height": 800})
    pagina.locator("#panel-companero").evaluate("e => e.hidden = false")
    vitrina = pagina.locator(".avatar-vitrina").bounding_box()
    for selector in ("#panel-armario", "#panel-companero", ".avatar-panel"):
        caja = pagina.locator(selector).bounding_box()
        assert caja["x"] >= vitrina["x"] + vitrina["width"] - 1 or caja["y"] + caja["height"] <= vitrina["y"] + 1
