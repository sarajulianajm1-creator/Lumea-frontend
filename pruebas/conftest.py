"""Piezas compartidas de las pruebas: servidor local y backend simulado.

- `servidor`: sirve la carpeta del proyecto en un puerto libre.
- `backend`: responde a http://127.0.0.1:5002 con los JSON de `respuestas/`.
  Un test puede cambiar una respuesta con `backend.poner("GET", "/progreso", {...})`.
- `pagina`: una página de Playwright con todo lo anterior conectado y la
  sesión de prueba iniciada.
"""
import json
import struct
import threading
import zlib
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
RESPUESTAS = Path(__file__).resolve().parent / "respuestas"
CORREO_PRUEBA = "prueba@lumea.test"

# (método, ruta) -> archivo en pruebas/respuestas/
RUTAS = {
    ("GET", "/perfil"): "perfil.json",
    ("GET", "/progreso"): "progreso.json",
    ("GET", "/historial"): "historial.json",
    ("GET", "/estado-animo"): "estado_animo.json",
    ("POST", "/estado-animo"): "estado_animo_guardado.json",
    ("GET", "/avatar"): "avatar.json",
    ("POST", "/avatar/equipar"): "avatar_equipar.json",
    ("POST", "/avatar/quitar"): "avatar_quitar.json",
    ("GET", "/calcomanias"): "calcomanias.json",
    ("GET", "/alimentos"): "alimentos.json",
    ("POST", "/predecir"): "predecir_segura.json",
    ("POST", "/confirmar-alimento"): "confirmar.json",
}


class _Silencioso(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture(scope="session")
def servidor():
    http = ThreadingHTTPServer(("127.0.0.1", 0), partial(_Silencioso, directory=str(RAIZ)))
    threading.Thread(target=http.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{http.server_address[1]}"
    http.shutdown()


class Backend:
    """El backend de mentira: guarda qué se le pidió para poder comprobarlo."""

    def __init__(self):
        self.respuestas = {}
        self.llamadas = []

    def poner(self, metodo, ruta, cuerpo, estado=200):
        self.respuestas[(metodo, ruta)] = (estado, cuerpo)

    def _responder(self, route):
        pet = route.request
        ruta = pet.url.split("5002", 1)[1].split("?")[0]
        self.llamadas.append((pet.method, ruta))
        if pet.method == "OPTIONS":
            return route.fulfill(status=204, headers=_CORS)
        if (pet.method, ruta) in self.respuestas:
            estado, cuerpo = self.respuestas[(pet.method, ruta)]
        elif (pet.method, ruta) in RUTAS:
            estado = 200
            cuerpo = json.loads((RESPUESTAS / RUTAS[(pet.method, ruta)]).read_text(encoding="utf-8"))
        else:
            estado, cuerpo = 404, {"success": False, "error": "ruta sin simular"}
        route.fulfill(status=estado, headers=_CORS, content_type="application/json",
                      body=json.dumps(cuerpo))


_CORS = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*"}
_TIPOS = {".css": "text/css", ".js": "text/javascript", ".woff2": "font/woff2", ".woff": "font/woff"}


@pytest.fixture
def backend():
    return Backend()


@pytest.fixture
def pagina(page, backend, servidor):
    """Página con backend simulado, sin internet y con sesión iniciada."""
    page.route("http://127.0.0.1:5002/**", backend._responder)

    def sin_internet(route):                      # CDN de Bootstrap, Google Fonts, DiceBear…
        ruta = route.request.url.split("?")[0]
        sufijo = Path(ruta).suffix
        if route.request.resource_type == "image":
            return route.fulfill(status=200, content_type="image/svg+xml",
                                 body='<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>')
        # De todo Bootstrap solo se conserva lo que las páginas usan para ocultar cosas
        cuerpo = ".d-none{display:none!important}" if "bootstrap.min.css" in ruta else ""
        route.fulfill(status=200, content_type=_TIPOS.get(sufijo, "text/css"), body=cuerpo)
    page.route(lambda url: not url.startswith(("http://127.0.0.1", "data:", "blob:")), sin_internet)

    page.add_init_script(f"localStorage.setItem('lumea_email', '{CORREO_PRUEBA}')")
    page.servidor = servidor
    page.errores = []
    page.on("console", lambda m: m.type == "error" and page.errores.append(m.text))
    page.on("pageerror", lambda e: page.errores.append(str(e)))
    return page


def foto_de_prueba(tmp_path):
    """Un PNG de 8x8 color liso (sin personas) para subir como foto."""
    ancho = alto = 8
    filas = b"".join(b"\x00" + b"\xc8\x8a\x3c" * ancho for _ in range(alto))

    def trozo(tipo, datos):
        c = struct.pack(">I", len(datos)) + tipo + datos
        return c + struct.pack(">I", zlib.crc32(tipo + datos))
    png = (b"\x89PNG\r\n\x1a\n" + trozo(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0))
           + trozo(b"IDAT", zlib.compress(filas)) + trozo(b"IEND", b""))
    ruta = tmp_path / "plato.png"
    ruta.write_bytes(png)
    return ruta


@pytest.fixture
def foto(tmp_path):
    return foto_de_prueba(tmp_path)
