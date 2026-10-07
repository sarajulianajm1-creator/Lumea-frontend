"""Pone el MISMO menú en las seis pantallas privadas: el armazón `.nav-app` de componentes.css.

Uso, desde la carpeta del proyecto:  python3 herramientas/menu_privado.py
Es idempotente: reescribe lo que hay entre las marcas `menu-privado:nav` de cada página, así
las seis no se desvían. El menú sale de la plantilla de abajo; para cambiarlo, cambia esta
herramienta y vuelve a correrla, no cada página.

Los cinco destinos son la navegación B (decisión de Isabella): Inicio, Mis registros,
Registrar, Progreso y Avatar. Ánimo NO está en el menú: se abre desde Inicio y desde Progreso.

Es UN solo <nav>: en el computador es una barra lateral de 248 px (logo arriba, destinos, y
abajo el nombre, el nivel y «Cerrar sesión»); en el celular (<= 720 px) el mismo <nav> es una
barra inferior con Registrar al centro. Qué es lateral y qué es inferior lo decide el CSS
(componentes.css y app.css), no hay dos menús que mantener.

El logo es UNA imagen: img/logo.svg. Si llega el logo de Isabella en PNG, se cambia la ruta
en LOGO (abajo) y se vuelve a correr la herramienta; las páginas públicas usan la misma ruta.
"""
import pathlib
import re

LOGO = "img/logo.svg"

DESTINOS = [  # (nombre, archivo, ícono de Bootstrap Icons, rótulo corto para la barra del celular)
    ("Inicio", "index-ingresado.html", "bi-house-door-fill", "Inicio"),
    ("Mis registros", "mis-registros.html", "bi-journal-text", "Registros"),
    ("Registrar", "alimentos.html", "bi-camera-fill", "Registrar"),
    ("Progreso", "progreso.html", "bi-bar-chart-line-fill", "Progreso"),
    ("Avatar", "avatar.html", "bi-person-badge-fill", "Avatar"),
]

# página -> (destino marcado, ¿lleva nombre y nivel?)
# El nombre y el nivel los llena lumea-ui.js: solo están donde la página carga lumea-state.js.
PAGINAS = {
    "index-ingresado.html": ("Inicio", True),
    "mis-registros.html": ("Mis registros", False),
    "alimentos.html": ("Registrar", False),
    "progreso.html": ("Progreso", True),
    "avatar.html": ("Avatar", False),
    "emociones.html": (None, True),            # Ánimo no es un destino del menú
}

USUARIO = """      <div class="nav-app__usuario">
        <p class="nav-app__nombre lumea-bind-nombre">Cargando...</p>
        <p class="nav-app__nivel lumea-bind-nivel">Nivel --</p>
      </div>
"""


def menu(activo, con_usuario):
    enlaces = []
    for nombre, archivo, icono, corto in DESTINOS:
        actual = ' aria-current="page"' if nombre == activo else ""
        clase = "nav-app__enlace nav-app__enlace--registrar" if nombre == "Registrar" else "nav-app__enlace"
        # En el celular el rótulo largo no cabe («Mis registros»): se muestra el corto. El nombre
        # accesible es siempre el largo (aria-label).
        if corto != nombre:
            texto = f'<span class="nav-app__largo">{nombre}</span><span class="nav-app__corto" aria-hidden="true">{corto}</span>'
        else:
            texto = f"<span>{nombre}</span>"
        enlaces.append(f'      <a class="{clase}" href="{archivo}" aria-label="{nombre}"{actual}>'
                       f'<i class="bi {icono}" aria-hidden="true"></i>{texto}</a>')
    return f"""<!-- menu-privado:nav (lo genera herramientas/menu_privado.py; no lo edites a mano) -->
    <nav class="nav-app" aria-label="Principal">
      <div class="nav-app__marca"><img class="marca" src="{LOGO}" alt="Lumea"></div>
{chr(10).join(enlaces)}
      <div class="nav-app__pie">
{USUARIO if con_usuario else ""}        <button type="button" class="nav-app__salir" data-cerrar-sesion><i class="bi bi-box-arrow-right" aria-hidden="true"></i> Cerrar sesión</button>
      </div>
    </nav>
    <!-- /menu-privado:nav -->"""


MARCAS = re.compile(r"<!-- menu-privado:nav.*?<!-- /menu-privado:nav -->", re.S)

for nombre, (activo, usuario) in PAGINAS.items():
    p = pathlib.Path(nombre)
    s = p.read_text(encoding="utf-8")
    assert MARCAS.search(s), f"{nombre}: no tiene las marcas menu-privado:nav (la página debe tener el armazón .app)"
    s = MARCAS.sub(lambda m: menu(activo, usuario), s)
    if "menu-privado.js" not in s:
        s = s.replace("</body>", '  <script src="menu-privado.js"></script>\n</body>', 1)
    p.write_text(s, encoding="utf-8")
    print(f"{nombre}: menú escrito ({activo or 'ningún destino marcado'})")
