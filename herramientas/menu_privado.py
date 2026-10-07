"""Pone el MISMO menú en las pantallas privadas: el lateral de Sara con los cinco destinos.

Uso, desde la carpeta del proyecto:  python3 herramientas/menu_privado.py
Es idempotente: si el menú ya está, solo lo vuelve a escribir igual (así las cinco páginas
no se desvían). El menú sale de las plantillas de abajo; para cambiarlo, cambia esta
herramienta y vuelve a correrla, no cada página.

Los cinco destinos son la navegación B (decisión de Isabella): Inicio, Mis registros,
Registrar, Progreso y Avatar. Ánimo NO está en el menú: se abre desde Inicio y desde Progreso.

En computador (>= 992 px) el menú es la barra lateral de Sara; en celular, su barra inferior
con la cámara al centro. La tarjeta con el nombre y el nivel solo está en las pantallas que
cargan lumea-state.js (Inicio, Progreso y Ánimo).
"""
import pathlib
import re

DESTINOS = [  # (nombre, archivo, ícono de Bootstrap Icons, rótulo corto para el celular)
    ("Inicio", "index-ingresado.html", "bi-house-door-fill", "Inicio"),
    ("Mis registros", "mis-registros.html", "bi-journal-text", "Registros"),
    ("Registrar", "alimentos.html", "bi-camera-fill", "Registrar"),
    ("Progreso", "progreso.html", "bi-bar-chart-line-fill", "Progreso"),
    ("Avatar", "avatar.html", "bi-person-badge-fill", "Avatar"),
]

# página -> (destino marcado, ¿lleva la tarjeta del usuario?, ¿ya tiene el armazón de Sara?)
PAGINAS = {
    "index-ingresado.html": ("Inicio", True, True),
    "progreso.html": ("Progreso", True, True),
    "emociones.html": (None, True, True),            # Ánimo no es un destino del menú
    "mis-registros.html": ("Mis registros", False, False),
    "alimentos.html": ("Registrar", False, False),
    "avatar.html": ("Avatar", False, False),
}

TARJETA = """      <div class="sidebar-user-card">
        <div class="sidebar-user-avatar"><span class="lumea-cara" data-cara="hoy"></span></div>
        <div class="flex-grow-1 overflow-hidden">
          <p class="mb-0 fw-bold text-truncate lumea-bind-nombre">Cargando...</p>
          <small class="text-muted d-block fw-semibold"><span class="lumea-bind-nivel">Nivel --</span> &bull; <i class="bi bi-fire" aria-hidden="true"></i> <span class="lumea-bind-racha">--</span></small>
        </div>
        <a href="avatar.html" class="btn btn-sm btn-light rounded-circle shadow-sm" aria-label="Editar mi avatar"><i class="bi bi-gear" aria-hidden="true"></i></a>
      </div>
"""


def lateral(activo, con_tarjeta):
    items = []
    for nombre, archivo, icono, _ in DESTINOS:
        marca = ' class="active" aria-current="page"' if nombre == activo else ""
        items.append(f'          <li class="sidebar-nav-item"><a href="{archivo}"{marca}>'
                     f'<i class="bi {icono} fs-5" aria-hidden="true"></i><span>{nombre}</span></a></li>')
    return f"""<!-- menu-privado:lateral (lo genera herramientas/menu_privado.py; no lo edites a mano) -->
    <aside class="lumea-desktop-sidebar d-none d-lg-flex">
      <div>
        <a href="index-ingresado.html" class="sidebar-logo"><i class="bi bi-flower2" aria-hidden="true"></i> LUMEA</a>
        <nav aria-label="Principal">
          <ul class="sidebar-nav-list">
{chr(10).join(items)}
          </ul>
        </nav>
      </div>
      <div class="menu-pie">
{TARJETA if con_tarjeta else ""}        <button type="button" class="menu-pie__salir" data-cerrar-sesion><i class="bi bi-box-arrow-right" aria-hidden="true"></i> Cerrar sesión</button>
      </div>
    </aside>
    <!-- /menu-privado:lateral -->"""


def celular(activo):
    enlaces = []
    for nombre, archivo, icono, corto in DESTINOS:
        actual = ' aria-current="page"' if nombre == activo else ""
        if nombre == "Registrar":        # la cámara va al centro, grande y cerca del pulgar
            enlaces.append(f'      <a href="{archivo}" class="nav-camera-fab" aria-label="{nombre}"{actual}>'
                           f'<i class="bi {icono}" aria-hidden="true"></i><span>{corto}</span></a>')
        else:
            clase = "nav-link-item active" if nombre == activo else "nav-link-item"
            enlaces.append(f'      <a href="{archivo}" class="{clase}" aria-label="{nombre}"{actual}>'
                           f'<i class="bi {icono}" aria-hidden="true"></i><span>{corto}</span></a>')
    return f"""<!-- menu-privado:celular (lo genera herramientas/menu_privado.py; no lo edites a mano) -->
  <div class="lumea-bottom-nav-container d-lg-none">
    <nav class="lumea-pill-nav" aria-label="Principal en celular">
{chr(10).join(enlaces)}
    </nav>
  </div>
  <!-- /menu-privado:celular -->"""


MARCAS_LATERAL = re.compile(r"<!-- menu-privado:lateral.*?<!-- /menu-privado:lateral -->", re.S)
MARCAS_CELULAR = re.compile(r"<!-- menu-privado:celular.*?<!-- /menu-privado:celular -->", re.S)
ASIDE_DE_SARA = re.compile(r'<aside class="lumea-desktop-sidebar.*?</aside>', re.S)
CELULAR_DE_SARA = re.compile(r'<div class="lumea-bottom-nav-container.*?</nav>\s*</div>', re.S)
BARRA_VIEJA = re.compile(r'[ \t]*<!-- Barra de Navegación Global[^>]*-->\s*<header>\s*<div class="container fixed-bottom.*?</header>\s*', re.S)
ESPACIO = re.compile(r'[ \t]*<div class="espacio-barra-inferior" aria-hidden="true"></div>\s*')


def armar_armazon(texto, nombre):
    """Páginas que todavía no tienen el armazón de Sara: lo crea alrededor de su <main>."""
    texto, n = BARRA_VIEJA.subn("@@LATERAL@@\n", texto, count=1)
    assert n == 1, f"{nombre}: no encontré la barra de navegación vieja"
    texto = ESPACIO.sub("", texto)
    texto = re.sub(r"<body[^>]*>", '<body class="lumea-screen-wrapper">\n<div class="lumea-desktop-layout">', texto, count=1)
    texto = texto.replace("@@LATERAL@@", "    @@LATERAL@@\n    <div class=\"lumea-main-area\">", 1)
    # el contenido (<main> y, si lo hay, el pie) queda dentro de lumea-main-area; se cierra antes de los <script>
    primero = re.search(r"\n\s*(<!-- Bootstrap[^\n]*-->\s*)?<script", texto[texto.index("lumea-main-area"):])
    assert primero, f"{nombre}: no encontré dónde cierra el contenido"
    corte = texto.index("lumea-main-area") + primero.start()
    return texto[:corte] + "\n    </div>\n  </div>\n  @@CELULAR@@\n" + texto[corte:]


for nombre, (activo, tarjeta, con_armazon) in PAGINAS.items():
    p = pathlib.Path(nombre)
    s = p.read_text(encoding="utf-8")
    if con_armazon:
        if MARCAS_LATERAL.search(s):
            s = MARCAS_LATERAL.sub(lambda m: lateral(activo, tarjeta), s)
            s = MARCAS_CELULAR.sub(lambda m: celular(activo), s)
        else:
            s, a = ASIDE_DE_SARA.subn(lambda m: lateral(activo, tarjeta), s, count=1)
            s, b = CELULAR_DE_SARA.subn(lambda m: celular(activo), s, count=1)
            assert a == 1 and b == 1, f"{nombre}: no encontré el menú de Sara"
    elif MARCAS_LATERAL.search(s):
        s = MARCAS_LATERAL.sub(lambda m: lateral(activo, tarjeta), s)
        s = MARCAS_CELULAR.sub(lambda m: celular(activo), s)
    else:
        s = armar_armazon(s, nombre)
        s = s.replace("@@LATERAL@@", lateral(activo, tarjeta)).replace("@@CELULAR@@", celular(activo))
    if "menu-privado.js" not in s:
        s = s.replace("</body>", '  <script src="menu-privado.js"></script>\n</body>', 1)
    if "pantallas-sara.css" not in s:
        s = re.sub(r'([ \t]*)(<link rel="stylesheet" href="estilos/puente-sara.css">)',
                   r'\1\2\n\1<link rel="stylesheet" href="estilos/pantallas-sara.css">', s, count=1)
    p.write_text(s, encoding="utf-8")
    print(f"{nombre}: menú escrito ({activo or 'ningún destino marcado'})")
