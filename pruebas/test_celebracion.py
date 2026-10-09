"""celebracion.js: los cuatro momentos (XP, misión, calcomanía, nivel), en cola y de a uno."""
import pytest

from conftest import cargar_respuesta

# Los momentos que se van solos duran milisegundos en las pruebas (en la app, 3 s)
CORTO = "LumeaCelebrar.tiempos.xp = 250; LumeaCelebrar.tiempos.mision = 250; LumeaCelebrar.tiempos.salida = 60;"


def abrir(pagina):
    pagina.goto(f"{pagina.servidor}/alimentos.html")
    pagina.evaluate(CORTO)


def celebrar(pagina, g):
    pagina.evaluate("g => LumeaCelebrar(g)", g)


def gamificacion(**cambios):
    g = {"xp_ganado": 0, "misiones_cumplidas": [], "subio_de_nivel": False, "nivel": 2, "nivel_anterior": 2,
         "desbloqueos": [], "calcomanias_nuevas": [], "meta_diaria": {"recien_cumplida": False}}
    g.update(cambios)
    return g


def test_sin_nada_que_celebrar_no_aparece_nada(pagina):
    abrir(pagina)
    celebrar(pagina, None)
    celebrar(pagina, gamificacion())
    pagina.wait_for_timeout(300)
    assert pagina.locator(".celebracion > *").count() == 0
    assert pagina.locator("dialog").count() == 0


def test_el_xp_aparece_y_se_va_solo(pagina):
    abrir(pagina)
    celebrar(pagina, gamificacion(xp_ganado=10, meta_diaria={"recien_cumplida": True}))
    chip = pagina.locator(".celebracion__chip").first
    chip.wait_for()
    assert chip.inner_text() == "+10 semillas"
    assert pagina.locator(".celebracion__chip--meta").inner_text() == "Meta de hoy cumplida"
    pagina.locator(".celebracion__chip").first.wait_for(state="detached")


def test_la_region_anuncia_sin_interrumpir(pagina):
    abrir(pagina)
    celebrar(pagina, gamificacion(xp_ganado=10))
    pagina.locator(".celebracion").wait_for(state="attached")
    region = pagina.locator(".celebracion")
    assert region.get_attribute("aria-live") == "polite" and region.get_attribute("role") == "status"


def test_los_momentos_van_de_a_uno_y_en_orden(pagina):
    abrir(pagina)
    g = cargar_respuesta("confirmar")["gamificacion"]
    celebrar(pagina, g)
    orden = []
    for _ in range(3):
        # XP -> misión (con su calcomanía) -> calcomanía suelta
        pagina.locator(".celebracion > *").first.wait_for()
        assert pagina.locator(".celebracion > *").count() == 1, "dos momentos a la vez"
        momento = pagina.locator(".celebracion > *").first.element_handle()
        texto = momento.inner_text()
        orden.append(texto.split("\n")[0])
        if "Inteligencia humana al rescate" in texto:
            break
        pagina.wait_for_function("e => !e.isConnected", arg=momento)    # ese momento en concreto ya se fue
    assert orden[0] == "+20 semillas"
    assert orden[1] == "Misión cumplida: Cuida de ti en tus tres comidas"
    assert orden[2] == "Calcomanía nueva: Inteligencia humana al rescate"


def test_la_calcomania_de_mision_se_pega_con_su_mision(pagina):
    abrir(pagina)
    celebrar(pagina, gamificacion(
        misiones_cumplidas=[{"id": "fruta", "nombre": "Registra una fruta", "xp": 10}],
        calcomanias_nuevas=[{"id": "fruta", "nombre": "Fruta del día", "descripcion": "Registraste una fruta.", "rol": "mision"}]))
    tarjeta = pagina.locator(".celebracion__tarjeta--mision")
    tarjeta.wait_for()
    assert "Misión cumplida: Registra una fruta" in tarjeta.inner_text()
    assert "Calcomanía nueva: Fruta del día" in tarjeta.inner_text()
    assert tarjeta.locator(".pegatina--mision.pegatina--pegandose").count() == 1


def test_calcomania_nueva_se_cierra_con_el_teclado_y_lleva_al_album(pagina):
    abrir(pagina)
    celebrar(pagina, gamificacion(calcomanias_nuevas=[
        {"id": "como_llegas", "nombre": "Cómo llegas", "descripcion": "Hiciste tu primer check-in de ánimo.", "rol": "emocion"}]))
    tarjeta = pagina.locator(".celebracion__tarjeta--emocion")
    tarjeta.wait_for()
    assert tarjeta.get_by_role("link", name="Ver mi álbum").get_attribute("href") == "avatar.html#calcomanias"
    # No se va sola (tiene botones): espera a que la persona toque «Seguir»
    pagina.wait_for_timeout(600)
    assert tarjeta.is_visible()
    tarjeta.get_by_role("button", name="Seguir").focus()
    pagina.keyboard.press("Enter")
    tarjeta.wait_for(state="detached")


def test_esc_cierra_la_calcomania(pagina):
    abrir(pagina)
    celebrar(pagina, gamificacion(calcomanias_nuevas=[
        {"id": "racha_3", "nombre": "Tres días seguidos", "descripcion": "x", "rol": "logro"}]))
    tarjeta = pagina.locator(".celebracion__tarjeta--logro")
    tarjeta.wait_for()
    pagina.keyboard.press("Escape")
    tarjeta.wait_for(state="detached")


def test_el_nivel_es_modal_con_lo_que_se_abrio(pagina):
    abrir(pagina)
    g = cargar_respuesta("confirmar")["gamificacion"]
    g["xp_ganado"] = 0
    g["misiones_cumplidas"] = []
    g["calcomanias_nuevas"] = []
    celebrar(pagina, g)
    dialogo = pagina.locator("dialog.celebracion__nivel")
    dialogo.wait_for()
    assert dialogo.get_attribute("open") is not None
    assert pagina.evaluate("document.querySelector('dialog.celebracion__nivel').matches(':modal')")
    texto = dialogo.inner_text()
    assert "Llegaste a la etapa 3" in texto
    assert "Camiseta Lumea" in texto and "Compañero nuevo" in texto and "Río" in texto
    assert dialogo.get_attribute("aria-labelledby") == "celebracion-nivel-titulo"
    assert dialogo.get_by_role("link", name="Ponérmelo").get_attribute("href") == "avatar.html#armario"


def test_esc_cierra_el_nivel_y_el_foco_vuelve(pagina):
    abrir(pagina)
    pagina.locator("#btn-subir").focus()
    g = gamificacion(subio_de_nivel=True, nivel=4, nivel_anterior=3,
                     desbloqueos=[{"tipo": "accesorio", "id": "audifonos", "nombre": "Audífonos", "nivel_requerido": 4}])
    celebrar(pagina, g)
    dialogo = pagina.locator("dialog.celebracion__nivel")
    dialogo.wait_for()
    pagina.keyboard.press("Escape")
    dialogo.wait_for(state="detached")
    assert pagina.evaluate("document.activeElement.id") == "btn-subir"


def test_nivel_sin_desbloqueos_no_ofrece_ponerselo(pagina):
    abrir(pagina)
    celebrar(pagina, gamificacion(subio_de_nivel=True, nivel=2))
    dialogo = pagina.locator("dialog.celebracion__nivel")
    dialogo.wait_for()
    assert dialogo.get_by_role("link", name="Ponérmelo").count() == 0
    dialogo.get_by_role("button", name="Seguir").click()
    dialogo.wait_for(state="detached")


def test_el_texto_del_servidor_nunca_es_html(pagina):
    abrir(pagina)
    malo = '<img src=x onerror="window.hackeado=1">'
    celebrar(pagina, gamificacion(
        misiones_cumplidas=[{"id": "x", "nombre": malo, "xp": 1}],
        calcomanias_nuevas=[{"id": "y", "nombre": malo, "descripcion": malo, "rol": "logro"}]))
    pagina.locator(".celebracion__tarjeta").first.wait_for()
    assert pagina.locator(".celebracion img").count() == 0
    assert pagina.evaluate("window.hackeado") is None


def test_con_movimiento_reducido_nada_se_anima(pagina):
    pagina.emulate_media(reduced_motion="reduce")
    abrir(pagina)
    celebrar(pagina, gamificacion(xp_ganado=10, calcomanias_nuevas=[
        {"id": "racha_3", "nombre": "Tres días seguidos", "descripcion": "x", "rol": "logro"}]))
    pagina.locator(".celebracion__chip").wait_for()
    assert pagina.evaluate("getComputedStyle(document.querySelector('.celebracion__chip')).animationName") == "none"
    pagina.locator(".pegatina").wait_for()
    assert pagina.evaluate("getComputedStyle(document.querySelector('.pegatina')).animationName") == "none"


@pytest.mark.parametrize("paleta", ["laguna", "neblina", "carnaval", "colibri", "cosecha"])
@pytest.mark.parametrize("modo", ["claro", "oscuro"])
def test_el_texto_de_los_momentos_tiene_contraste(pagina, paleta, modo):
    from axe_playwright_python.sync_playwright import Axe
    pagina.add_init_script(f"localStorage.setItem('lumea-paleta', '{paleta}'); localStorage.setItem('lumea-modo', '{modo}')")
    abrir(pagina)
    pagina.evaluate("LumeaCelebrar.tiempos.xp = 60000")
    celebrar(pagina, gamificacion(xp_ganado=10, meta_diaria={"recien_cumplida": True}))
    pagina.locator(".celebracion__chip").first.wait_for()
    pagina.wait_for_timeout(500)           # que termine de entrar
    errores = Axe().run(pagina, options={"runOnly": ["color-contrast"], "include": [[".celebracion"]]}).response["violations"]
    assert errores == [], f"{paleta}/{modo}: {[n['html'] for v in errores for n in v['nodes']]}"


def test_una_prenda_nueva_se_celebra_con_la_persona_puesta_esa_prenda(pagina, backend):
    from conftest import avatar_estado
    backend.poner("GET", "/avatar", avatar_estado(4, ropa="camiseta_lisa"))
    abrir(pagina)
    celebrar(pagina, gamificacion(subio_de_nivel=True, nivel=4, nivel_anterior=3, desbloqueos=[
        {"tipo": "ropa", "id": "overol", "nombre": "Overol de jardín", "nivel_requerido": 4, "parametros": {"outfitVariant": "overalls"}}]))
    dialogo = pagina.locator("dialog.celebracion__nivel")
    dialogo.wait_for()
    assert "Prenda nueva: Overol de jardín" in dialogo.inner_text()
    img = dialogo.locator("img.celebracion__persona-img")
    img.wait_for()
    assert img.get_attribute("src").startswith("data:image/svg+xml") and img.get_attribute("alt") == ""        # dibujada en el navegador
    assert dialogo.get_by_role("link", name="Ponérmelo").get_attribute("href") == "avatar.html#armario"
    assert pagina.peticiones_externas == []
