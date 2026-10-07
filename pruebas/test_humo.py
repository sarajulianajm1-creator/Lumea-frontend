"""Prueba de humo: cada página de la raíz abre y cumple lo básico."""
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
PAGINAS = sorted(p.name for p in RAIZ.glob("*.html"))

# Páginas que todavía no existen (ya no queda ninguna: Progreso y Avatar se construyeron en F3 y F4).
VACIAS = {}
# Reglas que fallan hoy en páginas de Sara (se reportan, no se arreglan aquí).
XFAIL = {
    ("inicio.html", "errores"): "borrador de Isabella: enlaza estilos/___.css, que aún no existen",
}


def abrir(pagina, nombre):
    if nombre in VACIAS:
        pytest.xfail(f"página vacía: {VACIAS[nombre]}")
    archivos_404 = []
    pagina.on("response", lambda r: r.status >= 400 and r.url.startswith(pagina.servidor)
              and archivos_404.append(f"{r.status} {r.url}"))
    pagina.goto(f"{pagina.servidor}/{nombre}")
    pagina.wait_for_load_state("networkidle")
    pagina.archivos_404 = archivos_404


def marcar(nombre, regla):
    if (nombre, regla) in XFAIL:
        pytest.xfail(XFAIL[(nombre, regla)])


@pytest.mark.parametrize("nombre", PAGINAS)
def test_sin_errores_ni_404(pagina, nombre):
    abrir(pagina, nombre)
    marcar(nombre, "errores")
    assert pagina.errores == []
    assert pagina.archivos_404 == []


@pytest.mark.parametrize("nombre", PAGINAS)
def test_idioma_y_un_solo_h1(pagina, nombre):
    abrir(pagina, nombre)
    marcar(nombre, "estructura")
    assert pagina.locator("html").get_attribute("lang") == "es"
    assert pagina.locator("h1:visible").count() == 1


@pytest.mark.parametrize("nombre", PAGINAS)
def test_imagenes_con_alt_y_botones_con_nombre(pagina, nombre):
    abrir(pagina, nombre)
    marcar(nombre, "accesibilidad")
    sin_alt = pagina.eval_on_selector_all("img:not([alt])", "e => e.map(x => x.outerHTML.slice(0, 80))")
    sin_nombre = pagina.eval_on_selector_all(
        "button, [role=button]",
        """e => e.filter(b => !(b.textContent.trim() || b.getAttribute('aria-label')
                              || b.getAttribute('aria-labelledby') || b.title))
                .map(b => b.outerHTML.slice(0, 80))""")
    assert sin_alt == []
    assert sin_nombre == []
