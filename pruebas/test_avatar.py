"""avatar.html: el avatar, las pestañas (misiones, armario, calcomanías) y equipar/quitar."""
import pytest

from conftest import avatar_estado, cargar_respuesta


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
    return pagina.locator(".prenda", has_text=nombre)


# ---------- La vitrina ----------
def test_muestra_nivel_cara_y_barra(pagina, backend):
    abrir(pagina, backend)
    assert texto(pagina, "#avatar-nivel") == "Nivel 2"
    assert texto(pagina, "#avatar-faltan") == "Te faltan 35 XP para el nivel 3"
    assert pagina.locator("#avatar-riel").get_attribute("aria-valuenow") == "13"
    assert "mouth=smile" in pagina.locator("#avatar-figura img").get_attribute("src")        # el ánimo de hoy: «bien»
    assert pagina.locator("#avatar-figura").get_attribute("aria-label") == "Tu avatar, tu ánimo de hoy: Bien"
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
    assert misiones.nth(0).inner_text().split("\n")[0] == "Registra una fruta"
    assert "+10 XP" in misiones.nth(0).inner_text() and "Cumplida hoy" in misiones.nth(0).inner_text()
    assert "Para hoy" in misiones.nth(1).inner_text() and "Para hoy" in misiones.nth(2).inner_text()


def test_la_mision_cumplida_lleva_su_calcomania(pagina, backend):
    abrir(pagina, backend)
    misiones = pagina.locator("#misiones-lista > li")
    assert misiones.nth(0).locator(".pegatina").count() == 1                    # la fruta ya está ganada en el álbum
    assert misiones.nth(1).locator(".pegatina").count() == 0
    assert "Calcomanía: Fruta del día" in misiones.nth(0).inner_text()


# ---------- Armario ----------
def test_el_armario_agrupa_ropa_y_accesorios(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#armario")
    assert pagina.locator(".armario__titulo").all_inner_texts() == ["Ropa", "Accesorios"]
    assert pagina.locator(".prenda").count() == 6
    assert "Disponible" in prenda(pagina, "Buzo verde").inner_text()


def test_lo_bloqueado_dice_el_nivel_y_no_hace_nada(pagina, backend):
    abrir(pagina, backend, ruta="avatar.html#armario")
    camiseta = prenda(pagina, "Camiseta Lumea")
    assert "Se abre en el nivel 3" in camiseta.inner_text()
    boton = camiseta.get_by_role("button")
    assert boton.get_attribute("aria-disabled") == "true"
    assert boton.get_attribute("aria-label") == "Camiseta Lumea, se abre en el nivel 3"
    boton.click(force=True)            # Playwright lo considera «no habilitado» por aria-disabled
    pagina.wait_for_timeout(150)
    assert ("POST", "/avatar/equipar") not in backend.llamadas


def test_ponerse_algo_guarda_y_lo_dice(pagina, backend):
    backend.poner("POST", "/avatar/equipar", avatar_estado(2, ropa="buzo_verde"))
    abrir(pagina, backend, ruta="avatar.html#armario")
    prenda(pagina, "Buzo verde").get_by_role("button", name="Ponerme Buzo verde").click()
    pagina.locator(".prenda--puesta").wait_for()
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
    pagina.locator(".prenda--puesta").wait_for(state="detached")
    assert backend.cuerpo_enviado("POST", "/avatar/quitar") == {"email": "prueba@lumea.test", "tipo": "accesorio"}
    assert texto(pagina, "#avatar-aviso") == "Te quitaste Gafas."
    assert texto(pagina, "#avatar-puesto") == "Todavía no te pusiste nada."


def test_equipar_con_el_teclado(pagina, backend):
    backend.poner("POST", "/avatar/equipar", avatar_estado(2, ropa="buzo_verde"))
    abrir(pagina, backend, ruta="avatar.html#armario")
    prenda(pagina, "Buzo verde").get_by_role("button").focus()
    pagina.keyboard.press("Enter")
    pagina.locator(".prenda--puesta").wait_for()


def test_si_el_backend_dice_que_esta_bloqueado(pagina, backend):
    backend.poner("POST", "/avatar/equipar", {"error": "bloqueado", "nivel_maximo": 2, "nivel_requerido": 3, "niveles_faltantes": 1}, estado=403)
    abrir(pagina, backend, ruta="avatar.html#armario")
    prenda(pagina, "Buzo verde").get_by_role("button").click()
    pagina.locator("#avatar-aviso", has_text="Todavía no se abre").wait_for()
    assert texto(pagina, "#avatar-aviso") == "Todavía no se abre: te falta 1 nivel."
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
    ganada = pagina.locator(".album__item--ganada", has_text="Primera foto")
    assert "Registraste tu primera comida." in ganada.inner_text() and "Ganada el 3 de octubre" in ganada.inner_text()
    vacia = pagina.locator(".album__item--vacia", has_text="Una semana")
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
    assert pagina.locator(".prenda").count() == 6


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
    assert texto(pagina, "#avatar-nivel") == "Nivel 2"


def test_el_texto_del_servidor_nunca_es_html(pagina, backend):
    malo = '<img src=x onerror="window.hackeado=1">'
    cuerpo = avatar_estado(2)
    cuerpo["objetos"]["ropa"][0]["nombre"] = malo
    abrir(pagina, backend, ruta="avatar.html#armario", avatar=cuerpo)
    assert pagina.locator(".prenda__nombre", has_text="onerror").count() == 1
    assert pagina.locator(".prenda img").count() == 0
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
