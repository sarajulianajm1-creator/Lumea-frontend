"""Movimiento (rediseño R8): una entrada por pantalla, la celebración y las respuestas a lo que la persona hace.

Nada más se mueve, todo dura 420 ms o menos, y con prefers-reduced-motion las cosas solo aparecen.
(La celebración, las caras elegidas y el saltico del armario tienen sus propias pruebas en test_celebracion.py,
test_caras_checkin.py y test_avatar.py.)
"""
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
PRIVADAS = ["index-ingresado.html", "mis-registros.html", "alimentos.html", "progreso.html", "avatar.html", "emociones.html"]

# Anota todo lo que empieza a moverse mientras se abre la pantalla (antes de que cargue cualquier script)
ESPIA = """window.__animaciones = []; window.__transiciones = [];
document.addEventListener('animationstart', (e) => window.__animaciones.push(e.animationName), true);
document.addEventListener('transitionrun', (e) => window.__transiciones.push(e.propertyName), true);"""
# Propiedades que MUEVEN algo de lugar o de tamaño (un cambio de color al pasar el cursor no cuenta como movimiento)
MOVIMIENTO = {"transform", "width", "height", "top", "left", "right", "bottom", "margin", "padding", "translate", "scale", "rotate"}


def abrir(pagina, nombre, espiar=True):
    if espiar:
        pagina.add_init_script(ESPIA)
    pagina.goto(f"{pagina.servidor}/{nombre}")
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(500)


# ---------- Una sola entrada por pantalla ----------

@pytest.mark.parametrize("nombre", PRIVADAS)
def test_al_abrir_la_pantalla_se_mueve_una_sola_cosa_la_entrada(pagina, nombre):
    abrir(pagina, nombre)
    assert pagina.evaluate("window.__animaciones") == ["entrada"]
    movimientos = [p for p in pagina.evaluate("window.__transiciones") if p in MOVIMIENTO]
    assert set(movimientos) <= {"width"}                                      # solo las barras se llenan (una vez, P6); nada más se corre solo


@pytest.mark.parametrize("nombre", PRIVADAS)
def test_la_entrada_hace_aparecer_y_subir_un_poco_el_contenido_una_vez_en_220_ms(pagina, nombre):
    abrir(pagina, nombre)
    datos = pagina.locator("main.contenido").evaluate("""e => { const c = getComputedStyle(e); const a = e.getAnimations()[0];
        return { nombre: c.animationName, duracion: c.animationDuration, repeticion: c.animationIterationCount,
                 relleno: c.animationFillMode, cuadros: a.effect.getKeyframes().map(k => [k.opacity, k.transform]) } }""")
    assert datos["nombre"] == "entrada" and datos["duracion"] == "0.22s"          # --m-base
    assert datos["repeticion"] == "1" and datos["relleno"] == "both"               # una sola vez
    assert datos["cuadros"][0] == ["0", "translateY(8px)"]                         # sube un poco (--e-2)…
    assert datos["cuadros"][1] == ["1", "none"]                                    # …y termina quieto


@pytest.mark.parametrize("nombre", PRIVADAS)
def test_con_movimiento_reducido_nada_se_mueve_las_cosas_solo_aparecen(pagina, nombre):
    pagina.emulate_media(reduced_motion="reduce")
    abrir(pagina, nombre)
    assert pagina.evaluate("window.__animaciones") == []
    assert pagina.locator("main.contenido").evaluate("e => getComputedStyle(e).animationName") == "none"
    assert pagina.locator("main.contenido").evaluate("e => getComputedStyle(e).opacity") == "1"          # y se ve de una vez
    duraciones = pagina.evaluate("""[...new Set([...document.querySelectorAll('*')].flatMap(e => getComputedStyle(e).transitionDuration.split(', ')))]""")
    assert set(duraciones) <= {"0s"}                                                                       # ninguna transición dura nada


# ---------- Todo dura 420 ms o menos, y nada tiene la duración escrita a mano ----------

def segundos(texto):
    return [float(v[:-2]) / 1000 if v.endswith("ms") else float(v[:-1]) for v in texto.split(", ") if v]


@pytest.mark.parametrize("nombre", PRIVADAS)
def test_ninguna_transicion_ni_animacion_pasa_de_420_ms(pagina, nombre):
    abrir(pagina, nombre)
    duraciones = pagina.evaluate("""[...document.querySelectorAll('body *, body')].flatMap(e => { const c = getComputedStyle(e);
        return [c.transitionDuration, c.animationDuration] })""")
    todas = [d for texto in duraciones for d in segundos(texto)]
    assert todas and max(todas) <= 0.42 + 1e-9


def test_ninguna_hoja_escribe_una_duracion_a_mano():
    """Las duraciones salen de tokens.css (--m-rapido, --m-base y --m-lento): ninguna hoja las escribe con números."""
    hojas = [p for p in (RAIZ / "estilos").glob("*.css") if p.name not in {"tokens.css", "paletas.css", "inicio.css", "puente-sara.css", "pantallas-sara.css"}]
    assert {h.name for h in hojas} >= {"app.css", "componentes.css", "avatar.css", "celebracion.css", "pegatinas.css", "publico.css"}
    for hoja in hojas:
        texto = re.sub(r"/\*.*?\*/", "", hoja.read_text(encoding="utf-8"), flags=re.S)
        for declaracion in re.findall(r"(?:transition|animation)[a-z-]*\s*:[^;{}]+", texto):
            sin_variables = re.sub(r"var\([^)]*\)", "", declaracion)
            assert not re.search(r"\b\d*\.?\d+m?s\b", sin_variables), f"{hoja.name}: {declaracion.strip()}"


def test_entre_pantallas_hay_un_fundido_corto_solo_con_movimiento():
    """P6: @view-transition vive dentro de prefers-reduced-motion: no-preference, con la duración del token --m-base."""
    css = re.sub(r"/\*.*?\*/", "", (RAIZ / "estilos" / "app.css").read_text(encoding="utf-8"), flags=re.S)
    bloque = css[css.index("@media (prefers-reduced-motion: no-preference)"):]
    assert "@view-transition" in bloque and "navigation: auto" in bloque
    assert "animation-duration: var(--m-base)" in bloque
    for hoja in (RAIZ / "estilos").glob("*.css"):
        if hoja.name in ("inicio.css", "app.css"):                            # inicio.css: el ejercicio de Isabella; app.css: arriba
            continue
        assert "@view-transition" not in re.sub(r"/\*.*?\*/", "", hoja.read_text(encoding="utf-8"), flags=re.S), hoja.name


@pytest.mark.parametrize("nombre", PRIVADAS)
def test_el_menu_y_el_logo_llevan_su_nombre_de_transicion(pagina, nombre):
    abrir(pagina, nombre, espiar=False)
    nombres = pagina.evaluate("[document.querySelector('.nav-app'), document.querySelector('.nav-app__marca')].map(e => getComputedStyle(e).viewTransitionName)")
    assert nombres == ["menu", "logo"]


def test_con_movimiento_reducido_no_hay_fundido_entre_pantallas(pagina):
    pagina.emulate_media(reduced_motion="reduce")
    abrir(pagina, "avatar.html", espiar=False)
    nombres = pagina.evaluate("[document.querySelector('.nav-app'), document.querySelector('.nav-app__marca')].map(e => getComputedStyle(e).viewTransitionName)")
    assert nombres == ["none", "none"]


@pytest.mark.parametrize("selector", [".boton", ".pestana", ".animo-cara", ".prenda__mosaico", ".nav-app__enlace"])
def test_al_presionar_la_respuesta_es_inmediata_menos_de_0_1_s(pagina, selector):
    abrir(pagina, {".animo-cara": "emociones.html", ".boton": "index-ingresado.html"}.get(selector, "avatar.html"), espiar=False)
    elemento = pagina.locator(f"{selector}:visible").first
    elemento.wait_for()
    caja = elemento.bounding_box()
    pagina.mouse.move(caja["x"] + caja["width"] / 2, caja["y"] + caja["height"] / 2)
    pagina.mouse.down()
    try:
        assert elemento.evaluate("e => getComputedStyle(e).transitionDuration") .split(", ")[0] == "0s"
    finally:
        pagina.mouse.up()


# ---------- Responder a lo que la persona hace: 120 ms ----------

@pytest.mark.parametrize("nombre,selectores", [
    ("index-ingresado.html", [".boton", ".nav-app__enlace", ".nav-app__salir", ".animo-cara", ".selector__opcion"]),
    ("avatar.html", [".pestana", ".boton", ".selector__opcion"]),
    ("emociones.html", [".animo-cara", ".boton"]),
    ("alimentos.html", [".boton", ".nav-app__enlace"]),
])
def test_pasar_el_cursor_o_enfocar_responde_en_120_ms(pagina, nombre, selectores):
    abrir(pagina, nombre, espiar=False)
    if nombre == "index-ingresado.html":
        pagina.locator(".selector__opcion").first.wait_for()
    for selector in selectores:
        elementos = pagina.locator(selector)
        assert elementos.count() > 0, selector
        duraciones = elementos.first.evaluate("e => getComputedStyle(e).transitionDuration")
        assert set(segundos(duraciones)) == {0.12}, f"{selector}: {duraciones}"           # --m-rapido


# ---------- El cambio de paleta: fondo y texto, 220 ms ----------

def test_la_transicion_del_cambio_de_paleta_es_solo_del_fondo_y_el_texto_de_la_pagina(pagina):
    abrir(pagina, "index-ingresado.html", espiar=False)
    for selector in ("html", "body"):
        datos = pagina.locator(selector).evaluate("e => [getComputedStyle(e).transitionProperty, getComputedStyle(e).transitionDuration]")
        assert datos == ["background-color, color", "0.22s, 0.22s"], selector
    # y no hay ningún «transition: all» que mueva cada elemento (el valor de fábrica es «all» con duración 0 s: no hace nada)
    con_todo = pagina.evaluate("""[...document.querySelectorAll('*')].filter(e => { const c = getComputedStyle(e);
        return c.transitionProperty.split(', ').includes('all') && c.transitionDuration.split(', ').some(d => parseFloat(d) > 0) }).length""")
    assert con_todo == 0


def test_al_cambiar_de_paleta_el_fondo_y_el_texto_se_transicionan(pagina):
    abrir(pagina, "index-ingresado.html", espiar=False)
    transiciones = pagina.evaluate("""() => {
        LumeaTema.ponerPaleta('colibri');                                      // una paleta con otro fondo que el neutro
        getComputedStyle(document.body).backgroundColor;                      // fuerza el cálculo: aquí arrancan las transiciones
        return [document.documentElement, document.body].flatMap(e => e.getAnimations().filter(a => a instanceof CSSTransition)
            .map(a => [e.tagName, a.transitionProperty, a.effect.getTiming().duration])) }""")
    assert ["BODY", "background-color", 220] in transiciones and ["BODY", "color", 220] in transiciones
    assert all(duracion == 220 for _, _, duracion in transiciones)


def test_con_movimiento_reducido_el_cambio_de_paleta_es_instantaneo(pagina):
    pagina.emulate_media(reduced_motion="reduce")
    abrir(pagina, "index-ingresado.html", espiar=False)
    transiciones = pagina.evaluate("""() => { LumeaTema.ponerPaleta('carnaval'); getComputedStyle(document.body).backgroundColor;
        return document.body.getAnimations().filter(a => a instanceof CSSTransition && a.effect.getTiming().duration > 0).length }""")
    assert transiciones == 0


# ---------- Lo que dejó de moverse ----------

def test_el_esqueleto_de_carga_esta_quieto_y_es_de_un_solo_color(pagina):
    abrir(pagina, "avatar.html", espiar=False)
    datos = pagina.evaluate("""() => { const e = document.createElement('div'); e.className = 'esqueleto'; document.body.appendChild(e);
        const c = getComputedStyle(e); const r = [c.animationName, c.backgroundImage]; e.remove(); return r }""")
    assert datos == ["none", "none"]                                          # sin destello que se repita sin parar y sin degradado


def test_la_barra_se_llena_una_vez_al_cargar(pagina):
    """P6: el ancho de la barra pasa de 0 a su valor cuando llegan los datos (--m-lento); con movimiento reducido, de golpe."""
    abrir(pagina, "index-ingresado.html", espiar=False)
    datos = pagina.locator(".barra-xp__relleno").first.evaluate("e => [getComputedStyle(e).transitionProperty, getComputedStyle(e).transitionDuration]")
    assert datos == ["width", "0.42s"]


def test_con_movimiento_reducido_la_barra_se_llena_de_golpe(pagina):
    pagina.emulate_media(reduced_motion="reduce")
    abrir(pagina, "index-ingresado.html", espiar=False)
    assert pagina.locator(".barra-xp__relleno").first.evaluate("e => getComputedStyle(e).transitionDuration") == "0s"
