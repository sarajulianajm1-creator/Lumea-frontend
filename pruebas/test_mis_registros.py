"""mis-registros.html: el texto del servidor se escribe como texto (no como HTML) y el diseño no cambió."""
import re

from conftest import cargar_respuesta

# La plantilla que usaba la página ANTES (con innerHTML): sirve de referencia para comprobar
# que armar las tarjetas con createElement no cambió ni una clase ni un texto.
PLANTILLA_ANTERIOR = """
  (registro) => `
    <div class="col">
      <div class="card h-100 rounded-4 shadow-sm p-3">
        <h3 class="h6 fw-bold hero-title mb-1">${registro.alimento_detectado ?? "Alimento"}</h3>
        <p class="small text-secondary mb-1"><i class="bi bi-calendar3 me-1"></i>${formatearFecha(registro.fecha)}</p>
        ${htmlSellos(registro.sellos_advertencia)}
        <p class="small text-secondary mb-1"><i class="bi bi-fire me-1"></i>${registro.calorias_aprox ?? "—"} kcal aprox.</p>
        <p class="small text-secondary mb-0"><i class="bi bi-bullseye me-1"></i>Certeza IA: ${Number(registro.certeza_ia ?? 0).toFixed(1)}%</p>
      </div>
    </div>
  `
"""
HTML_SELLOS_ANTERIOR = """
  (sellos) => {
    if (sellos === null || sellos === undefined) return "";
    if (sellos.length === 0) return '<p class="small text-secondary mb-1">Sin sellos de advertencia</p>';
    return `<div class="d-flex flex-wrap gap-1 mb-1">${sellos.map((s) => `<span class="sello-mini">${TEXTO_SELLO[s] ?? s}</span>`).join("")}</div>`;
  }
"""


def abrir(pagina, backend, historial=None):
    if historial is not None:
        backend.poner("GET", "/historial", {"success": True, "cantidad_registros": len(historial), "historial": historial})
    pagina.goto(f"{pagina.servidor}/mis-registros.html")
    pagina.locator("#listaRegistros > .col").first.wait_for()


def normalizar(html):
    return re.sub(r">\s+<", "><", re.sub(r"\s+", " ", html)).strip()


def test_la_tarjeta_es_igual_a_la_de_antes(pagina, backend):
    abrir(pagina, backend)
    for i in range(3):          # banano (sin sellos), arepa (sin sellos) y gaseosa (con dos sellos)
        nuevo = pagina.locator("#listaRegistros > .col").nth(i).evaluate("e => e.outerHTML")
        registro = cargar_respuesta("historial")["historial"][i]
        antes = pagina.evaluate(
            f"""([registro]) => {{
                const htmlSellos = {HTML_SELLOS_ANTERIOR};
                const plantilla = {PLANTILLA_ANTERIOR};
                const caja = document.createElement('div');
                caja.innerHTML = plantilla(registro);
                return caja.firstElementChild.outerHTML;
            }}""", [registro])
        assert normalizar(nuevo) == normalizar(antes), f"registro {i}"


def test_sin_sellos_conocidos_no_pinta_nada_de_sellos(pagina, backend):
    registro = cargar_respuesta("historial")["historial"][0] | {"sellos_advertencia": None}
    abrir(pagina, backend, historial=[registro])
    tarjeta = pagina.locator("#listaRegistros > .col").first
    assert tarjeta.locator(".sello-mini, p:has-text('Sin sellos')").count() == 0


def test_los_sellos_se_leen_como_octagonos(pagina, backend):
    abrir(pagina, backend)
    assert pagina.locator(".sello-mini").all_inner_texts() == ["EXCESO EN AZÚCARES", "CONTIENE EDULCORANTES"]
    assert pagina.locator("#listaRegistros p", has_text="Sin sellos de advertencia").count() == 2


def test_el_texto_del_servidor_nunca_es_html(pagina, backend):
    malo = '<img src=x onerror="window.hackeado=1"><b>negrita</b>'
    registro = cargar_respuesta("historial")["historial"][0] | {"alimento_detectado": malo, "sellos_advertencia": ["<i>raro</i>"]}
    abrir(pagina, backend, historial=[registro])
    assert pagina.locator("#listaRegistros img, #listaRegistros b, #listaRegistros i.raro").count() == 0
    assert malo in pagina.locator("#listaRegistros h3").inner_text()
    # text_content y no inner_text: el sello va en mayúsculas por CSS (Res. 810) y inner_text devuelve lo que se ve
    assert "<i>raro</i>" in pagina.locator(".sello-mini").text_content()
    assert pagina.evaluate("window.hackeado") is None


def test_sin_registros_invita_a_registrar(pagina, backend):
    backend.poner("GET", "/historial", {"success": True, "cantidad_registros": 0, "historial": []})
    pagina.goto(f"{pagina.servidor}/mis-registros.html")
    pagina.locator("#sinRegistros").wait_for()
    assert pagina.locator("#sinRegistros a").get_attribute("href") == "alimentos.html"


def test_si_el_servidor_no_responde_se_avisa(pagina, backend):
    pagina.route("http://127.0.0.1:5002/**", lambda ruta: ruta.abort())
    pagina.goto(f"{pagina.servidor}/mis-registros.html")
    pagina.locator(".alert-danger").wait_for()
    assert "No se pudo conectar con el servidor" in pagina.locator(".alert-danger").inner_text()
