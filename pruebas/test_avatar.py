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


def texto(pagina, selector):
    return pagina.locator(selector).inner_text().strip()


def prenda(pagina, nombre):
    return pagina.locator("#armario-grupos .prenda", has_text=nombre)


# ---------- La vitrina ----------
def test_muestra_nivel_cara_y_barra(pagina, backend):
    abrir(pagina, backend)
    assert texto(pagina, "#avatar-nivel") == "Etapa 2"
    assert texto(pagina, "#avatar-faltan") == "Te faltan 35 semillas para la etapa 3"
    assert pagina.locator("#avatar-riel").get_attribute("aria-valuenow") == "30"
    assert "eyesVariant=happy" in pagina.locator("#avatar-figura img").get_attribute("src")        # el ánimo de hoy: «bien»
    assert pagina.locator("#avatar-figura").get_attribute("aria-label") == "Tu compañero Sol, tu ánimo de hoy: Bien"
    assert texto(pagina, "#avatar-puesto") == "Todavía no te pusiste nada."
    assert pagina.errores == []


def test_un_solo_h1_y_la_navegacion_marca_avatar(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("h1").count() == 1
    assert pagina.locator("nav a[aria-current=page]").inner_text().strip() == "Avatar"


def test_con_las_imagenes_de_laura_se_apilan_las_capas(pagina, backend):
    abrir(pagina, backend, avatar=avatar_estado(4, ropa="camiseta_lumea", accesorio="gafas", imagenes=True))
    srcs = pagina.eval_on_selector_all("#avatar-figura img.avatar-figura__capa", "e => e.map(i => i.src.split('/').pop())")
    assert srcs == ["base_1.png", "ropa_camiseta_lumea.png", "accesorio_gafas.png"]       # de abajo hacia arriba
    assert pagina.locator("#avatar-figura img.avatar-figura__cara").count() == 0


def test_sin_internet_la_cara_queda_en_silueta(pagina, backend):
    abrir(pagina, backend)
    pagina.evaluate("document.querySelector('#avatar-figura img').dispatchEvent(new Event('error'))")
    assert pagina.locator("#avatar-figura img").count() == 0
    assert pagina.locator(".avatar-figura__silueta svg").count() == 1


# ---------- Pestañas ----------
def test_las_pestanas_siguen_el_patron_aria(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator("[role=tablist] [role=tab]").all_inner_texts() == ["Misiones", "Armario", "Calcomanías"]
    assert pagina.locator("#pestana-misiones").get_attribute("aria-selected") == "true"
    assert pagina.locator("#pestana-armario").get_attribute("tabindex") == "-1"
    assert pagina.locator("#panel-misiones").is_visible() and not pagina.locator("#panel-armario").is_visible()
    assert pagina.locator("#panel-armario").get_attribute("aria-labelledby") == "pestana-armario"
    assert pagina.locator("#pestana-armario").get_attribute("aria-controls") == "panel-armario"


def test_las_flechas_cambian_de_pestana(pagina, backend):
    abrir(pagina, backend)
    pagina.locator("#pestana-misiones").focus()
    pagina.keyboard.press("ArrowRight")
    assert pagina.evaluate("document.activeElement.id") == "pestana-armario"
    assert pagina.locator("#panel-armario").is_visible()
    pagina.keyboard.press("End")
    assert pagina.evaluate("document.activeElement.id") == "pestana-calcomanias"
    pagina.keyboard.press("ArrowRight")                                         # da la vuelta
    assert pagina.evaluate("document.activeElement.id") == "pestana-misiones"
    pagina.keyboard.press("ArrowLeft")
    assert pagina.evaluate("document.activeElement.id") == "pestana-calcomanias"
    pagina.keyboard.press("Home")
    assert pagina.evaluate("document.activeElement.id") == "pestana-misiones"


@pytest.mark.parametrize("ancla,panel", [("misiones", "misiones"), ("armario", "armario"), ("calcomanias", "calcomanias")])
def test_se_abre_en_la_pestana_del_ancla(pagina, backend, ancla, panel):
    abrir(pagina, backend, ruta=f"avatar.html#{ancla}")
    assert pagina.locator(f"#panel-{panel}").is_visible()
    assert pagina.locator(f"#pestana-{panel}").get_attribute("aria-selected") == "true"
    assert pagina.locator("[role=tabpanel]:visible").count() == 1


def test_un_ancla_que_no_existe_abre_misiones(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#cualquier-cosa")
    assert pagina.locator("#panel-misiones").is_visible()


def test_tocar_una_pestana_actualiza_el_ancla(pagina, backend):
    abrir(pagina, backend)
    pagina.locator("#pestana-calcomanias").click()
    assert pagina.evaluate("location.hash") == "#calcomanias"
    pagina.evaluate("location.hash = '#armario'")
    assert pagina.locator("#panel-armario").is_visible()


# ---------- Misiones ----------
def test_las_tres_misiones_con_su_xp(pagina, backend):
    abrir(pagina, backend)
    misiones = pagina.locator("#misiones-lista > li")
    assert misiones.count() == 3
    assert misiones.nth(0).inner_text().split("\n")[0] == "Agradece y disfruta una fruta de la creación"
    assert "+10 semillas" in misiones.nth(0).inner_text() and "Cumplida hoy" in misiones.nth(0).inner_text()
    assert "Para hoy" in misiones.nth(1).inner_text() and "Para hoy" in misiones.nth(2).inner_text()


def test_la_mision_cumplida_lleva_su_calcomania(pagina, backend):
    abrir(pagina, backend)
    misiones = pagina.locator("#misiones-lista > li")
    assert misiones.nth(0).locator(".pegatina").count() == 1                    # la fruta ya está ganada en el álbum
    assert misiones.nth(1).locator(".pegatina").count() == 0
    assert "Calcomanía: Una fruta para alegrar tu día" in misiones.nth(0).inner_text()


# ---------- Armario ----------
def test_el_armario_agrupa_ropa_y_accesorios(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#armario")
    assert pagina.locator(".armario__titulo").all_inner_texts() == ["Ropa", "Accesorios"]
    assert pagina.locator("#armario-grupos .prenda").count() == 6
    assert "Disponible" in prenda(pagina, "Buzo verde").inner_text()


def test_lo_bloqueado_dice_el_nivel_y_no_hace_nada(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#armario")
    camiseta = prenda(pagina, "Camiseta Lumea")
    assert "Se abre en la etapa 3" in camiseta.inner_text()
    boton = camiseta.get_by_role("button")
    assert boton.get_attribute("aria-disabled") == "true"
    assert boton.get_attribute("aria-label") == "Camiseta Lumea, se abre en la etapa 3"
    boton.click(force=True)            # Playwright lo considera «no habilitado» por aria-disabled
    pagina.wait_for_timeout(150)
    assert ("POST", "/avatar/equipar") not in backend.llamadas


def test_ponerse_algo_guarda_y_lo_dice(pagina, backend):
    backend.poner("POST", "/avatar/equipar", avatar_estado(2, ropa="buzo_verde"))
    abrir(pagina, backend, ruta="avatar.html#armario")
    prenda(pagina, "Buzo verde").get_by_role("button", name="Ponerme Buzo verde").click()
    pagina.locator("#armario-grupos .prenda--puesta").wait_for()
    assert backend.cuerpo_enviado("POST", "/avatar/equipar") == {"email": "prueba@lumea.test", "tipo": "ropa", "item_id": "buzo_verde"}
    assert "Puesto" in prenda(pagina, "Buzo verde").inner_text()
    assert prenda(pagina, "Buzo verde").get_by_role("button").inner_text() == "Quitar"
    assert texto(pagina, "#avatar-puesto") == "Puesto: Buzo verde"
    assert texto(pagina, "#avatar-aviso") == "Te pusiste Buzo verde."
    # El avatar dio su saltico (un solo movimiento) y el foco sigue en el mismo botón
    assert pagina.evaluate("document.activeElement.dataset.objeto") == "buzo_verde"


def test_el_avatar_da_un_saltico_al_ponerse_algo(pagina, backend):
    backend.poner("POST", "/avatar/equipar", avatar_estado(2, accesorio="gafas"))
    abrir(pagina, backend, ruta="avatar.html#armario")
    prenda(pagina, "Gafas").get_by_role("button").click()
    pagina.locator("#avatar-figura.avatar-figura--saltico").wait_for()
    pagina.locator("#avatar-figura.avatar-figura--saltico").wait_for(state="detached")     # una sola vez


def test_quitar_una_prenda(pagina, backend):
    backend.poner("GET", "/avatar", avatar_estado(2, accesorio="gafas"))
    backend.poner("POST", "/avatar/quitar", avatar_estado(2))
    abrir(pagina, backend, ruta="avatar.html#armario")
    assert texto(pagina, "#avatar-puesto") == "Puesto: Gafas"
    prenda(pagina, "Gafas").get_by_role("button", name="Quitar Gafas").click()
    pagina.locator("#armario-grupos .prenda--puesta").wait_for(state="detached")
    assert backend.cuerpo_enviado("POST", "/avatar/quitar") == {"email": "prueba@lumea.test", "tipo": "accesorio"}
    assert texto(pagina, "#avatar-aviso") == "Te quitaste Gafas."
    assert texto(pagina, "#avatar-puesto") == "Todavía no te pusiste nada."


def test_equipar_con_el_teclado(pagina, backend):
    backend.poner("POST", "/avatar/equipar", avatar_estado(2, ropa="buzo_verde"))
    abrir(pagina, backend, ruta="avatar.html#armario")
    prenda(pagina, "Buzo verde").get_by_role("button").focus()
    pagina.keyboard.press("Enter")
    pagina.locator("#armario-grupos .prenda--puesta").wait_for()


def test_si_el_backend_dice_que_esta_bloqueado(pagina, backend):
    backend.poner("POST", "/avatar/equipar", {"error": "bloqueado", "nivel_maximo": 2, "nivel_requerido": 3, "niveles_faltantes": 1}, estado=403)
    abrir(pagina, backend, ruta="avatar.html#armario")
    prenda(pagina, "Buzo verde").get_by_role("button").click()
    pagina.locator("#avatar-aviso", has_text="Todavía no se abre").wait_for()
    assert texto(pagina, "#avatar-aviso") == "Todavía no se abre: te falta 1 etapa."
    assert "Puesto" not in prenda(pagina, "Buzo verde").inner_text()


def test_si_falla_el_guardado_no_cambia_nada(pagina, backend):
    backend.poner("POST", "/avatar/equipar", {"error": "x"}, estado=500)
    abrir(pagina, backend, ruta="avatar.html#armario")
    prenda(pagina, "Buzo verde").get_by_role("button").click()
    pagina.locator("#avatar-aviso", has_text="No se pudo guardar").wait_for()
    assert texto(pagina, "#avatar-puesto") == "Todavía no te pusiste nada."


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
    assert pagina.locator("#armario-grupos .prenda").count() == 6


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
    abrir(pagina, backend, ruta="avatar.html#armario", avatar=cuerpo)
    assert pagina.locator(".prenda__nombre", has_text="onerror").count() == 1
    assert pagina.locator("#armario-grupos .prenda img").count() == 0
    assert pagina.evaluate("window.hackeado") is None


def test_no_hay_calorias_ni_comparaciones(pagina, backend):
    abrir(pagina, backend)
    for ruta in ("misiones", "armario", "calcomanias"):
        pagina.locator(f"#pestana-{ruta}").click()
    contenido = pagina.locator("main").inner_text().lower()
    for prohibido in ("kcal", "caloría", "ranking", "otros usuarios", "perdiste"):
        assert prohibido not in contenido


@pytest.mark.parametrize("ancla", ["misiones", "armario", "calcomanias"])
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


ANIMADAS = 'img[src*="animationVariant=slow"], img[src*="animationVariant=medium"]'      # lo que pide movimiento (none no)


def tarjeta_de(pagina, nombre):
    return pagina.locator("#companeros-lista .prenda", has=pagina.locator(".prenda__nombre", has_text=nombre))


def parametros(src):
    return {k: v[0] for k, v in parse_qs(urlparse(src).query).items()}


def test_la_seccion_tu_companero_muestra_los_seis_con_su_nombre_y_su_etapa(pagina, backend):
    abrir(pagina, backend)
    assert pagina.get_by_role("heading", name="Tu compañero", level=2).count() == 1
    tarjetas = pagina.locator("#companeros-lista .prenda")
    assert [t.locator(".prenda__nombre").inner_text() for t in tarjetas.all()] == NOMBRES
    assert tarjeta_de(pagina, "Sol").locator(".prenda__estado").inner_text() == "Tu compañero"
    assert tarjeta_de(pagina, "Luna").locator(".prenda__estado").inner_text() == "Disponible"
    for nombre, etapa in ETAPAS.items():
        assert tarjeta_de(pagina, nombre).locator(".prenda__estado").inner_text() == f"Se abre en la etapa {etapa}"
    assert pagina.errores == []


def test_los_bloqueados_llevan_candado_etapa_y_aria_disabled_y_no_hacen_nada(pagina, backend):
    abrir(pagina, backend)
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
    abrir(pagina, backend)
    imagenes = pagina.locator("#companeros-lista img")
    assert imagenes.count() == 6
    for img in imagenes.all():
        src = img.get_attribute("src")
        datos = parametros(src)
        assert src.startswith("https://api.dicebear.com/10.x/gaze/svg?")
        assert "animationVariant" not in datos                                        # quietos
        assert datos["seed"].startswith("lumea-") and set(datos) <= {"seed", "shapeVariant", "bodyColor", "eyesVariant"}
        assert CORREO_PRUEBA.split("@")[0] not in src and "@" not in src
        assert img.get_attribute("alt") == ""
    assert pagina.locator("#companeros-lista .prenda__imagen").evaluate_all("e => e.every(x => x.getAttribute('aria-hidden') === 'true')")


def test_elegir_un_companero_lo_guarda_lo_marca_y_el_foco_se_queda(pagina, backend):
    abrir(pagina, backend)
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
    assert "seed=lumea-luna" in pagina.locator("#avatar-figura img").get_attribute("src")
    assert "eyesVariant=happy" in pagina.locator("#avatar-figura img").get_attribute("src")
    assert pagina.locator("#avatar-figura").get_attribute("aria-label") == "Tu compañero Luna, tu ánimo de hoy: Bien"


def _progreso_con(avatar):
    cuerpo = cargar_respuesta("progreso")
    cuerpo["progreso"]["avatar"] = avatar
    return cuerpo


def test_elegir_un_companero_con_el_teclado(pagina, backend):
    abrir(pagina, backend)
    backend.poner("GET", "/progreso", _progreso_con(companero("luna", "bien")))
    tarjeta_de(pagina, "Luna").get_by_role("button").focus()
    pagina.keyboard.press("Enter")
    pagina.locator("#companeros-lista .prenda--puesta .prenda__nombre", has_text="Luna").wait_for()
    assert backend.cuerpo_enviado("POST", "/avatar")["avatar_id"] == "luna"


def test_si_el_backend_dice_que_el_companero_esta_bloqueado(pagina, backend):
    abrir(pagina, backend)
    backend.poner("POST", "/avatar", {"error": "El avatar \"luna\" todavía está bloqueado.", "nivel_maximo": 1,
                                       "nivel_requerido": 3, "niveles_faltantes": 2}, estado=403)
    tarjeta_de(pagina, "Luna").get_by_role("button").click()
    pagina.wait_for_function("document.getElementById('avatar-aviso').textContent !== ''")
    assert texto(pagina, "#avatar-aviso") == "Todavía no se abre: te faltan 2 etapas."
    assert tarjeta_de(pagina, "Sol").locator(".prenda__estado").inner_text() == "Tu compañero"       # nada cambió


def test_si_falla_la_conexion_al_elegir_no_cambia_nada(pagina, backend):
    abrir(pagina, backend)
    backend.poner("POST", "/avatar", {"success": False}, estado=500)
    tarjeta_de(pagina, "Luna").get_by_role("button").click()
    pagina.wait_for_function("document.getElementById('avatar-aviso').textContent !== ''")
    assert texto(pagina, "#avatar-aviso") == "No se pudo guardar el cambio."
    assert tarjeta_de(pagina, "Sol").locator(".prenda__estado").inner_text() == "Tu compañero"


def test_con_un_compañero_mas_adelante_se_desbloquean_mas(pagina, backend):
    abrir(pagina, backend)
    backend.poner("GET", "/avatares", avatares_estado(nivel=5, actual="luna"))
    abrir(pagina, backend)
    assert tarjeta_de(pagina, "Luna").locator(".prenda__estado").inner_text() == "Tu compañero"
    assert tarjeta_de(pagina, "Río").get_by_role("button").inner_text() == "Elegir"
    assert tarjeta_de(pagina, "Montaña").get_by_role("button").inner_text() == "Elegir"
    assert tarjeta_de(pagina, "Orquídea").get_by_role("button").inner_text() == "Etapa 7"


def test_el_compañero_grande_se_anima_despacio_y_es_lo_unico_que_se_mueve(pagina, backend):
    abrir(pagina, backend)
    grande = pagina.locator("#avatar-figura img")
    datos = parametros(grande.get_attribute("src"))
    assert datos["animationVariant"] == "slow" and datos["eyesVariant"] == "happy" and datos["seed"] == "lumea-sol"
    # en toda la pantalla, una sola imagen pide animación: nunca dos caras moviéndose
    assert pagina.locator(ANIMADAS).count() == 1


def test_con_movimiento_reducido_no_se_pide_ninguna_animacion(pagina, backend):
    pagina.emulate_media(reduced_motion="reduce")
    abrir(pagina, backend)
    assert "animationVariant" not in pagina.locator("#avatar-figura img").get_attribute("src")
    assert pagina.locator(ANIMADAS).count() == 0


def test_con_las_imagenes_de_laura_la_persona_y_el_companero_al_lado_mas_pequeño_y_quieto(pagina, backend):
    abrir(pagina, backend, avatar=avatar_estado(4, ropa="camiseta_lumea", imagenes=True))
    assert "avatar-figura--con-persona" in pagina.locator("#avatar-figura").get_attribute("class")
    assert pagina.locator("#avatar-figura .avatar-figura__persona img.avatar-figura__capa").count() == 2
    lado = pagina.locator("#avatar-figura img.avatar-figura__companero")
    assert lado.count() == 1
    src = lado.get_attribute("src")
    assert "seed=lumea-sol" in src and "animationVariant" not in src                  # el pequeño va quieto
    cajas = pagina.evaluate("""() => ({ persona: document.querySelector('.avatar-figura__persona').getBoundingClientRect().toJSON(),
                                      companero: document.querySelector('.avatar-figura__companero').getBoundingClientRect().toJSON() })""")
    assert cajas["companero"]["left"] >= cajas["persona"]["right"] - 1                 # a su lado, no encima
    assert cajas["companero"]["width"] < cajas["persona"]["width"] / 2                 # más pequeño
    assert pagina.locator("#avatar-figura").get_attribute("aria-label") == "Tu avatar y tu compañero Sol, tu ánimo de hoy: Bien"
    assert pagina.locator(ANIMADAS).count() == 0                   # con la persona, nada se anima


def test_sin_internet_los_companeros_quedan_en_silueta_con_su_nombre(pagina, backend):
    abrir(pagina, backend)
    pagina.evaluate("document.querySelectorAll('#companeros-lista img').forEach(i => i.dispatchEvent(new Event('error')))")
    assert pagina.locator("#companeros-lista img").count() == 0
    assert pagina.locator("#companeros-lista .prenda__imagen svg").count() == 6
    assert [t.locator(".prenda__nombre").inner_text() for t in pagina.locator("#companeros-lista .prenda").all()] == NOMBRES


def test_si_no_cargan_los_companeros_lo_demas_funciona(pagina, backend):
    backend.poner("GET", "/avatares", {"success": False, "error": "sin perfil"}, estado=404)
    abrir(pagina, backend)
    assert pagina.locator("#companeros-error").is_visible()
    assert pagina.locator("#companeros-lista .prenda").count() == 0
    assert texto(pagina, "#avatar-nivel") == "Etapa 2"
    assert pagina.locator("#avatar-figura img").count() == 1


def test_el_nombre_del_companero_nunca_es_html(pagina, backend):
    cuerpo = avatares_estado()
    cuerpo["avatares"][1]["nombre"] = '<img src=x onerror="window.hackeado=1">'
    backend.poner("GET", "/avatares", cuerpo)
    abrir(pagina, backend)
    assert pagina.locator("#companeros-lista .prenda__nombre", has_text="onerror").count() == 1
    assert pagina.evaluate("window.hackeado") is None


@pytest.mark.parametrize("ancho", [375, 1280])
def test_la_seccion_de_companeros_no_desborda(pagina, backend, ancho):
    pagina.set_viewport_size({"width": ancho, "height": 900})
    abrir(pagina, backend)
    assert pagina.evaluate("document.documentElement.scrollWidth") <= ancho
    caja = pagina.locator(".avatar-companeros").bounding_box()
    assert caja["x"] + caja["width"] <= ancho


def test_la_accion_principal_de_avatar_sigue_siendo_el_armario(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#armario")
    # los botones de los compañeros son secundarios: el relleno es de «Ponerme»
    assert pagina.locator("#companeros-lista .boton:not(.boton--secundario)").count() == 0
    assert pagina.locator("#armario-grupos .boton:not(.boton--secundario)").count() >= 1


# ---------- Rediseño R6: superficies tranquilas y dos columnas desde 992 px ----------

def color_de(pagina, selector, propiedad="backgroundColor"):
    return pagina.locator(selector).first.evaluate(f"e => getComputedStyle(e).{propiedad}")


def token(pagina, variable):
    return pagina.evaluate("""(v) => { const e = document.createElement('i'); e.style.backgroundColor = `var(${v})`;
        document.body.appendChild(e); const c = getComputedStyle(e).backgroundColor; e.remove(); return c }""", variable)


def test_sin_el_gran_fondo_rosado_el_avatar_va_sobre_una_superficie_tranquila(pagina, backend):
    abrir(pagina, backend)
    assert color_de(pagina, ".avatar-vitrina") == token(pagina, "--c-superficie")
    assert color_de(pagina, ".avatar-vitrina") != token(pagina, "--c-emocion-contenedor")      # antes: el rosado de «emoción»
    assert "tarjeta--emocion" not in pagina.locator(".avatar-vitrina").get_attribute("class")
    assert color_de(pagina, ".avatar-figura") == token(pagina, "--c-fondo")                    # la figura, sobre el fondo de la página
    assert pagina.locator(".avatar-vitrina").evaluate("e => getComputedStyle(e).boxShadow") == "none"


def test_las_misiones_son_tarjetas_con_borde_y_el_color_va_en_su_chip(pagina, backend):
    abrir(pagina, backend)
    assert color_de(pagina, "#misiones-lista .mision") == token(pagina, "--c-superficie")      # antes: el lila de «misión» en toda la caja
    assert "tarjeta--mision" not in pagina.locator("#misiones-lista .mision").first.get_attribute("class")
    assert color_de(pagina, "#misiones-lista .chip--mision") == token(pagina, "--c-mision-suave")   # el color, en el chip de +10 semillas


def test_en_computador_hay_dos_columnas_desde_992_px_y_debajo_una(pagina, backend):
    for ancho, dos_columnas in ((1280, True), (992, True), (991, False), (390, False)):
        pagina.set_viewport_size({"width": ancho, "height": 900})
        abrir(pagina, backend)
        cajas = pagina.evaluate("""() => ({ vitrina: document.querySelector('.avatar-vitrina').getBoundingClientRect().toJSON(),
                                          panel: document.querySelector('.avatar-panel').getBoundingClientRect().toJSON() })""")
        lado_a_lado = cajas["panel"]["left"] >= cajas["vitrina"]["right"] - 1 and abs(cajas["panel"]["top"] - cajas["vitrina"]["top"]) < 4
        assert lado_a_lado == dos_columnas, f"{ancho} px"
        if not dos_columnas:
            assert cajas["panel"]["top"] >= cajas["vitrina"]["bottom"] - 1                      # apilados: primero el avatar y su nivel
        assert pagina.evaluate("document.documentElement.scrollWidth") <= ancho


def test_avatar_ya_no_carga_bootstrap_ni_los_estilos_de_sara(pagina, backend):
    abrir(pagina, backend)
    hojas = pagina.eval_on_selector_all("link[rel=stylesheet]", "e => e.map(x => x.getAttribute('href'))")
    assert not any("bootstrap.min.css" in h or h.endswith("style.css") or "sara" in h for h in hojas)
