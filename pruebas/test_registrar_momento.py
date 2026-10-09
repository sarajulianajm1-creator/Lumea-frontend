"""P11 · 2: Registrar, el momento de la verdad. La línea de luz mientras espera, el resultado por partes (60 ms), los sellos con
fundido y escala de 0,96 a 1 sin rebote, las opciones escalonadas y todo instantáneo con prefers-reduced-motion."""
import json

import pytest

from conftest import cargar_respuesta


def abrir(pagina):
    pagina.goto(f"{pagina.servidor}/alimentos.html")
    pagina.locator("#btn-subir").wait_for()


def subir_y_esperar(pagina, foto, respuesta):
    """Sube la foto y deja la respuesta del backend en espera; devuelve una función que la libera."""
    pendientes = []
    pagina.route("**/predecir", lambda ruta: pendientes.append(ruta))
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator(".visor[data-mirando]").wait_for()
    return lambda: pendientes[0].fulfill(status=200, content_type="application/json", body=json.dumps(respuesta))


def test_mientras_espera_una_linea_de_luz_recorre_la_foto_y_dice_mirando_tu_plato(pagina, foto):
    abrir(pagina)
    liberar = subir_y_esperar(pagina, foto, cargar_respuesta("predecir_gaseosa"))
    luz = pagina.locator(".visor__luz")
    d = luz.evaluate("e => { const c = getComputedStyle(e); return [c.display, c.animationName, c.animationIterationCount, c.backgroundColor] }")
    marca = pagina.evaluate("(() => { const i = document.createElement('i'); i.style.backgroundColor = 'var(--c-marca)'; document.body.appendChild(i); const c = getComputedStyle(i).backgroundColor; i.remove(); return c })()")
    assert d[:3] == ["block", "linea-de-luz", "infinite"] and d[3] == marca                       # color marca, recorre la foto mientras dura la espera
    assert luz.get_attribute("aria-hidden") == "true"
    assert pagina.locator(".visor__mirando").inner_text() == "Mirando tu plato…" and pagina.locator(".visor__mirando").is_visible()
    assert pagina.locator("#backend-estado").inner_text() == "Mirando tu plato…"
    antes = luz.evaluate("e => e.getBoundingClientRect().top")
    pagina.wait_for_timeout(300)
    assert luz.evaluate("e => e.getBoundingClientRect().top") > antes                              # y baja
    liberar()
    pagina.locator("#backend-alimento", has_text="Gaseosa").wait_for()
    assert pagina.locator(".visor[data-mirando]").count() == 0 and not pagina.locator(".visor__luz").is_visible()   # solo mientras dura la espera


def test_si_el_servidor_falla_la_linea_de_luz_tambien_se_va(pagina, foto):
    abrir(pagina)
    pagina.route("**/predecir", lambda ruta: ruta.abort())
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#backend-estado", has_text="No se pudo analizar").wait_for()
    assert pagina.locator(".visor[data-mirando]").count() == 0


def test_el_resultado_aparece_por_partes_60_ms_una_tras_otra(pagina, foto, backend):
    backend.poner("POST", "/predecir", cargar_respuesta("predecir_gaseosa"))
    abrir(pagina)
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#backend-alimento", has_text="Gaseosa").wait_for()
    r = pagina.evaluate("""() => { const d = (s) => { const e = document.querySelector(s); return [parseFloat(getComputedStyle(e).animationDelay) * 1000, getComputedStyle(e).animationName, getComputedStyle(e).animationDuration] };
        return { nombre: d('#backend-alimento'), certeza: d('.etiqueta__certeza'), sellos: d('.resultado__rotulo'), consejo: d('#backend-consejos'), dato: d('#consejo-dato') } }""")
    assert [r[k][0] for k in ("nombre", "certeza", "sellos", "consejo")] == [0, 60, 120, 180]        # nombre, certeza y kcal, sellos, consejo
    assert all(v[1] == "resultado-parte" and v[2] == "0.22s" for v in r.values())                      # --m-base


def test_las_kcal_aparecen_sin_conteo_animado(pagina, foto, backend):
    backend.poner("POST", "/predecir", cargar_respuesta("predecir_gaseosa"))
    pagina.add_init_script("window.__textos = []; new MutationObserver(() => { const e = document.querySelector('#backend-energia'); if (e && e.textContent) window.__textos.push(e.textContent) }).observe(document, { subtree: true, childList: true, characterData: true });")
    abrir(pagina)
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#backend-alimento", has_text="Gaseosa").wait_for()
    pagina.wait_for_timeout(500)
    textos = pagina.evaluate("window.__textos")
    assert len(set(textos)) <= 1                                                                        # el texto llega entero, una sola vez


def test_los_sellos_entran_con_fundido_y_escala_de_096_a_1_en_220_ms_sin_rebote(pagina, foto, backend):
    backend.poner("POST", "/predecir", cargar_respuesta("predecir_gaseosa"))
    abrir(pagina)
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#backend-sellos .sello").first.wait_for()
    d = pagina.locator("#backend-sellos .sello").first.evaluate("""e => { const c = getComputedStyle(e), a = e.getAnimations()[0];
        return [c.animationName, c.animationDuration, c.animationTimingFunction, a.effect.getKeyframes().map(k => [k.opacity, k.transform])] }""")
    assert d[0] == "sello-entra" and d[1] == "0.22s"
    assert d[3] == [["0", "scale(0.96)"], ["1", "none"]]
    assert "1.56" not in d[2] and d[2].startswith("cubic-bezier(0.2, 0.8, 0.2, 1)")                      # frena suave: sin rebote (nada pasa de 1)


def test_si_la_ia_duda_las_opciones_entran_escalonadas(pagina, foto, backend):
    backend.poner("POST", "/predecir", cargar_respuesta("predecir_duda"))
    abrir(pagina)
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#backend-opciones .opciones__boton").first.wait_for()
    retardos = pagina.locator("#backend-opciones .opciones__boton").evaluate_all("e => e.map(x => Math.round(parseFloat(getComputedStyle(x).animationDelay) * 1000))")
    assert len(retardos) >= 2 and retardos == sorted(retardos) and len(set(retardos)) == len(retardos)
    assert {b - a for a, b in zip(retardos, retardos[1:])} == {60}


def test_con_movimiento_reducido_todo_es_instantaneo(pagina, foto):
    pagina.emulate_media(reduced_motion="reduce")
    abrir(pagina)
    liberar = subir_y_esperar(pagina, foto, cargar_respuesta("predecir_gaseosa"))
    assert not pagina.locator(".visor__luz").is_visible()                                                 # sin línea que se mueva (queda el texto)
    assert pagina.locator(".visor__mirando").is_visible()
    liberar()
    pagina.locator("#backend-sellos .sello").first.wait_for()
    animaciones = pagina.locator("#resultado *").evaluate_all("e => e.map(x => getComputedStyle(x).animationName).filter(n => n !== 'none')")
    assert animaciones == []
