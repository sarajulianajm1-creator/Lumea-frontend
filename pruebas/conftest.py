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
    ("GET", "/avatares"): "avatares.json",
    ("POST", "/avatar"): "avatar_elegir.json",
    ("POST", "/avatar/equipar"): "avatar_equipar.json",
    ("POST", "/avatar/quitar"): "avatar_quitar.json",
    ("GET", "/calcomanias"): "calcomanias.json",
    ("GET", "/alimentos"): "alimentos.json",
    ("POST", "/predecir"): "predecir_segura.json",
    ("POST", "/confirmar-alimento"): "confirmar.json",
}


def cargar_respuesta(nombre):
    """El JSON de pruebas/respuestas/<nombre>.json, para modificarlo en un test."""
    return json.loads((RESPUESTAS / f"{nombre}.json").read_text(encoding="utf-8"))


# La persona (voxel-art) y el armario por etapas: `objetos_avatar.json` y `rasgos_disponibles.json` salen de la
# configuración real del backend (gamificacion_config.OBJETOS_AVATAR y gamificacion.rasgos_disponibles(), 9 oct 2026).


# ---------- Los seis compañeros (Camino del cuidado): DiceBear 10.x «gaze», como los manda el backend ----------
# Los valores salen de Backend/gamificacion_config.py (AVATARES y EXPRESION_POR_ESTADO) y las URL, de
# Backend/docs/CONTRATO_GAMIFICACION.md. Las URL son QUIETAS: la animación (animationVariant) la agrega el frontend.
COMPANEROS = [  # (id, nombre, forma, color, nivel_requerido)
    ("sol", "Sol", "circle", "F6B73C", 1), ("luna", "Luna", "arch", "C9C3F0", 1), ("rio", "Río", "pill", "52DCD8", 3),
    ("montana", "Montaña", "triangle", "8FBF7A", 5), ("orquidea", "Orquídea", "diamond", "E89BC4", 7), ("colibri", "Colibrí", "egg", "3FB6A8", 9),
]
OJOS_POR_ESTADO = {"muy_mal": "bars", "mal": "small", "neutral": "dots", "bien": "happy", "muy_bien": "grin"}
OJOS_NEUTROS = "dots"


def url_companero(id_, ojos=OJOS_NEUTROS):
    _, _, forma, color, _ = next(c for c in COMPANEROS if c[0] == id_)
    return f"https://api.dicebear.com/10.x/gaze/svg?seed=lumea-{id_}&shapeVariant={forma}&bodyColor={color}&eyesVariant={ojos}"


def companero_basico(id_):
    """El compañero como lo manda `POST /avatar` y `respaldo_dicebear`: id, nombre, forma, color y la URL quieta (ojos neutros)."""
    _, nombre, forma, color, _ = next(c for c in COMPANEROS if c[0] == id_)
    return {"id": id_, "nombre": nombre, "forma": forma, "color": color, "url": url_companero(id_)}


def companero(id_="sol", estado_hoy="bien"):
    """`progreso.avatar` de GET /progreso: el compañero con sus cinco caras (`urls_por_estado`) y la del ánimo de hoy."""
    c = companero_basico(id_)
    c["estado_animo_hoy"] = estado_hoy
    c["url_con_animo"] = url_companero(id_, OJOS_POR_ESTADO[estado_hoy]) if estado_hoy else c["url"]
    c["urls_por_estado"] = {e: url_companero(id_, o) for e, o in OJOS_POR_ESTADO.items()}
    return c


def avatares_estado(nivel=2, actual="sol", xp_total=45):
    """El cuerpo de GET /avatares: los seis compañeros con lo que la persona ya abrió (por nivel máximo)."""
    lista = []
    for id_, nombre, forma, color, requerido in COMPANEROS:
        lista.append({"id": id_, "nombre": nombre, "forma": forma, "color": color, "url": url_companero(id_),
                      "nivel_requerido": requerido, "desbloqueado": nivel >= requerido, "niveles_faltantes": max(0, requerido - nivel),
                      "seleccionado": id_ == actual})
    return {"success": True, "avatar_actual": actual, "nivel_maximo": nivel, "xp_total": xp_total, "avatares": lista}


def avatar_estado(nivel=2, ropa="camiseta_lisa", accesorio=None, rasgos=None):
    """El cuerpo de GET /avatar (y de equipar, quitar y rasgos, que responden igual) como lo arma el backend real
    (CONTRATO_GAMIFICACION.md, «La persona»): `persona` con los 8 rasgos y lo puesto, `rasgos_disponibles`, y una
    prenda o accesorio por cada una de las 10 etapas, abiertos por nivel máximo. Lo viejo (base, capas) sigue, en desuso."""
    datos = cargar_respuesta("objetos_avatar")
    objetos = {"ropa": [], "accesorio": []}
    for o in datos["objetos"]:
        objetos[o["tipo"]].append({**o, "desbloqueado": nivel >= o["nivel_requerido"],
                                   "niveles_faltantes": max(0, o["nivel_requerido"] - nivel), "puesto": o["id"] in (ropa, accesorio)})
    puesto = {"ropa": None, "accesorio": None}
    for tipo, id_ in (("ropa", ropa), ("accesorio", accesorio)):
        if id_:
            o = next(x for x in objetos[tipo] if x["id"] == id_)
            puesto[tipo] = {k: o[k] for k in ("id", "nombre", "parametros")}
    return {
        "success": True, "nivel_maximo": nivel,
        "persona": {"estilo": "voxel-art", "rasgos": {**datos["rasgos_por_defecto"], **(rasgos or {})}, "puesto": puesto},
        "rasgos_disponibles": cargar_respuesta("rasgos_disponibles"),
        "objetos": objetos, "puesto": puesto,
        "imagenes_listas": False,                                                        # EN DESUSO
        "base": {"id": "base_1", "nombre": "Base 1", "archivo": "base_1.png", "imagen_lista": False,
                 "url": "http://127.0.0.1:5002/static/avatar/base_1.png"},
        "bases": [], "capas": [],
        "respaldo_dicebear": companero_basico("sol"),
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
        self.peticiones = []          # (método, dirección completa, cuerpo): para ver con qué correo se pidió
        self.cuerpos = {}                 # (método, ruta) -> el último cuerpo que se le mandó

    def poner(self, metodo, ruta, cuerpo, estado=200):
        self.respuestas[(metodo, ruta)] = (estado, cuerpo)

    def cuerpo_enviado(self, metodo, ruta):
        """El JSON que la página mandó en la última llamada, o None si no hubo."""
        enviado = self.cuerpos.get((metodo, ruta))
        return json.loads(enviado) if enviado else None

    def _responder(self, route):
        pet = route.request
        ruta = pet.url.split("5002", 1)[1].split("?")[0]
        self.llamadas.append((pet.method, ruta))
        cuerpo = pet.post_data_buffer
        self.peticiones.append((pet.method, pet.url, cuerpo.decode('utf-8', 'replace') if cuerpo else None))   # fotos: bytes que no son texto
        self.cuerpos[(pet.method, ruta)] = cuerpo.decode('utf-8', 'replace') if cuerpo else None
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
    # Todo lo que la página pide fuera de esta máquina (para comprobar que no le pide nada a DiceBear)
    page.peticiones_externas = []
    page.on("request", lambda r: None if r.url.startswith(("http://127.0.0.1", "data:", "blob:")) else page.peticiones_externas.append(r.url))

    def sin_internet(route):                      # Google Fonts, DiceBear…
        ruta = route.request.url.split("?")[0]
        sufijo = Path(ruta).suffix
        if route.request.resource_type == "image":
            return route.fulfill(status=200, content_type="image/svg+xml",
                                 body='<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>')
        # Bootstrap y Bootstrap Icons ya viven en vendor/ (se sirven desde el proyecto):
        # lo que llega aquí es lo que queda afuera, como las fuentes de Google.
        route.fulfill(status=200, content_type=_TIPOS.get(sufijo, "text/css"), body="")
    page.route(lambda url: not url.startswith(("http://127.0.0.1", "data:", "blob:")), sin_internet)

    # La sesión se siembra UNA vez por pestaña (este script corre en cada página): así lo que la
    # app haga después, como cerrar sesión, no se deshace al cambiar de página.
    page.add_init_script(f"""if (!sessionStorage.getItem('sesion-sembrada')) {{
        sessionStorage.setItem('sesion-sembrada', '1'); localStorage.setItem('lumea_email', '{CORREO_PRUEBA}'); }}""")
    page.servidor = servidor
    page.errores = []
    page.on("console", lambda m: m.type == "error" and page.errores.append(m.text))
    page.on("pageerror", lambda e: page.errores.append(str(e)))
    return page


def sin_sesion(pagina):
    """Quita la sesión de prueba SOLO en la primera página: si la prueba navega (por ejemplo, tras
    iniciar sesión), lo que la app guarde después no se borra otra vez."""
    pagina.add_init_script("""if (!sessionStorage.getItem('sesion-quitada')) {
        sessionStorage.setItem('sesion-quitada', '1'); localStorage.clear(); }""")


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
