"""Camino del cuidado, K1: lo que se ve dice «semillas» (no XP) y «etapa» (no nivel).

Las claves del contrato (xp_total, nivel, xp_siguiente_nivel…) NO cambian; cambia solo el texto en pantalla,
incluidos los aria-label. Los nombres de las misiones y de las calcomanías vienen del backend y no se tocan.
"""
import re

import pytest

from conftest import cargar_respuesta

PANTALLAS = ["index-ingresado.html", "progreso.html", "avatar.html", "avatar.html#armario", "avatar.html#calcomanias",
             "emociones.html", "alimentos.html", "mis-registros.html"]
TEXTOS_Y_ETIQUETAS = """() => {
    const textos = [], w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
        acceptNode: (n) => /^(SCRIPT|STYLE|NOSCRIPT)$/.test(n.parentElement.tagName) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
    while (w.nextNode()) if (w.currentNode.textContent.trim()) textos.push(w.currentNode.textContent.trim());
    document.querySelectorAll('[aria-label], [title], [alt]').forEach((e) => ['aria-label', 'title', 'alt'].forEach((a) => e.getAttribute(a) && textos.push(e.getAttribute(a))));
    return textos }"""
VIEJO = re.compile(r"\bXP\b|\bniveles?\b", re.IGNORECASE)


def formato(pagina, expresion, *args):
    pagina.goto(f"{pagina.servidor}/progreso.html")
    return pagina.evaluate(expresion, *args) if args else pagina.evaluate(expresion)


# ---------- formato.js: los plurales ----------

@pytest.mark.parametrize("n,esperado", [(0, "0 semillas"), (1, "1 semilla"), (2, "2 semillas"), (5, "5 semillas"), (35, "35 semillas")])
def test_semillas_va_en_singular_solo_con_una(pagina, n, esperado):
    assert formato(pagina, "n => LumeaFormato.semillas(n)", n) == esperado


def test_te_faltan_las_semillas_para_la_etapa_siguiente_con_su_plural(pagina):
    p = {"xp_siguiente_nivel": 80, "xp_inicio_nivel": 30, "xp_total": 45, "nivel": 2, "xp_faltante_siguiente_nivel": 35}
    assert formato(pagina, "p => LumeaFormato.textoNivel(p)", p) == "Te faltan 35 semillas para la etapa 3"
    assert pagina.evaluate("p => LumeaFormato.textoNivel({ ...p, xp_faltante_siguiente_nivel: 1 })", p) == "Te falta 1 semilla para la etapa 3"
    assert pagina.evaluate("LumeaFormato.textoNivel({ xp_siguiente_nivel: null, nivel: 10 })") == "Llegaste a la etapa máxima"


def test_la_meta_del_dia_dice_semillas_con_su_plural(pagina):
    assert formato(pagina, "LumeaFormato.textoMeta({ xp_hoy: 10, meta: 15, cumplida: false })") == "10 de 15 semillas hoy"
    assert pagina.evaluate("LumeaFormato.textoMeta({ xp_hoy: 20, meta: 15, cumplida: true })") == "Meta cumplida: 20 semillas hoy"
    assert pagina.evaluate("LumeaFormato.textoMeta({ xp_hoy: 1, meta: 15, cumplida: false })") == "1 de 15 semillas hoy"
    assert pagina.evaluate("LumeaFormato.textoMeta({ xp_hoy: 1, meta: 15, cumplida: true })") == "Meta cumplida: 1 semilla hoy"
    assert pagina.evaluate("LumeaFormato.textoMeta({ xp_hoy: 0, meta: 1, cumplida: false })") == "0 de 1 semilla hoy"


# ---------- Ninguna pantalla dice XP ni nivel ----------

@pytest.mark.parametrize("ruta", PANTALLAS)
def test_ninguna_pantalla_privada_dice_xp_ni_nivel(pagina, ruta):
    pagina.goto(f"{pagina.servidor}/{ruta}")
    pagina.wait_for_load_state("networkidle")
    pagina.wait_for_timeout(300)                                        # lo que llega del backend simulado
    malos = [t for t in pagina.evaluate(TEXTOS_Y_ETIQUETAS) if VIEJO.search(t)]
    assert malos == []


def test_las_barras_y_los_chips_dicen_etapa_tambien_en_el_aria_label(pagina):
    pagina.goto(f"{pagina.servidor}/progreso.html")
    pagina.locator("main .lumea-bind-nivel", has_text="Etapa 2").first.wait_for()
    assert pagina.locator("main [role=progressbar]").first.get_attribute("aria-label") == "Avance hacia la etapa 3"
    pagina.goto(f"{pagina.servidor}/avatar.html")
    pagina.locator("#avatar-nivel", has_text="Etapa 2").wait_for()
    assert pagina.locator("#avatar-riel").get_attribute("aria-label") == "Avance hacia la etapa 3"


def test_en_la_etapa_maxima_la_barra_dice_etapa_maxima(pagina, backend):
    p = cargar_respuesta("progreso")
    p["progreso"].update({"nivel": 10, "xp_siguiente_nivel": None, "xp_faltante_siguiente_nivel": None})
    backend.poner("GET", "/progreso", p)
    pagina.goto(f"{pagina.servidor}/progreso.html")
    pagina.locator("main .lumea-bind-nivel", has_text="Etapa 10").first.wait_for()
    assert pagina.locator("main [role=progressbar]").first.get_attribute("aria-label") == "Etapa máxima"


def test_la_carga_dice_semillas_y_no_xp(pagina, backend):
    pagina.goto(f"{pagina.servidor}/progreso.html")
    for nombre in ("progreso.html", "index-ingresado.html"):                                  # el texto de espera, antes de que llegue el backend
        html = pagina.evaluate("n => fetch(n).then(r => r.text())", nombre)
        assert "Cargando semillas..." in html and "Cargando XP" not in html


def test_el_resultado_de_registrar_y_la_celebracion_dicen_semillas_y_etapa(pagina, backend, foto):
    r = cargar_respuesta("confirmar")
    r["gamificacion"].update({"xp_ganado": 1, "nivel": 4, "subio_de_nivel": True, "misiones_cumplidas": [], "calcomanias_nuevas": []})
    backend.poner("POST", "/predecir", cargar_respuesta("predecir_segura") | {"gamificacion": r["gamificacion"]})
    pagina.goto(f"{pagina.servidor}/alimentos.html")
    pagina.set_input_files("input[type=file]", str(foto))
    pagina.locator("#backend-logros li", has_text="Llegaste a la etapa 4").wait_for()
    assert pagina.locator("#backend-logros").inner_text().split("\n")[0] == "+1 semilla"          # el singular
    assert pagina.locator(".celebracion__chip").first.inner_text() == "+1 semilla"                # el chip va primero y se va solo
    pagina.locator("dialog.celebracion__nivel").wait_for()
    assert "Llegaste a la etapa 4" in pagina.locator("dialog.celebracion__nivel").inner_text()


def test_los_nombres_de_misiones_y_calcomanias_son_los_del_backend(pagina, backend):
    p = cargar_respuesta("progreso")
    p["progreso"]["misiones"][0]["nombre"] = "Un nombre que escribe Isabella en el backend"
    backend.poner("GET", "/progreso", p)
    pagina.goto(f"{pagina.servidor}/avatar.html")
    pagina.locator(".mision__nombre", has_text="Un nombre que escribe Isabella en el backend").wait_for()
