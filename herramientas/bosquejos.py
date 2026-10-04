"""
LUMEA · bosquejos.py
Dibuja bosquejos de BAJA fidelidad (grises, sin color de marca) de las
pantallas de Lumea. Son un punto de partida para que Isabella diseñe en
Figma, no un diseño: por eso todo es gris y las cajas dicen QUÉ va, no
CÓMO se ve. Cada SVG se puede arrastrar a Figma y queda editable.

Uso: python3 herramientas/bosquejos.py   ->  bosquejos/*.svg
"""
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "bosquejos")

TINTA, SUAVE, LINEA, CAJA, CAJA2, FONDO = "#2B2F33", "#6B7177", "#B9BEC4", "#ECEEF0", "#DADDE1", "#FFFFFF"
WOW = "#E0A100"          # único color: marca el momento Wow
FUENTE = "Helvetica, Arial, sans-serif"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Lienzo:
    def __init__(self, ancho, alto):
        self.w, self.h, self.el = ancho, alto, []

    def add(self, s):
        self.el.append(s)

    def rect(self, x, y, w, h, r=12, fill=CAJA, stroke=LINEA, dash=None, sw=1.5):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def circ(self, cx, cy, r, fill=CAJA2, stroke=LINEA, sw=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def texto(self, x, y, t, size=14, peso=400, color=TINTA, ancla="start"):
        self.add(f'<text x="{x}" y="{y}" font-family="{FUENTE}" font-size="{size}" font-weight="{peso}" fill="{color}" text-anchor="{ancla}">{esc(t)}</text>')

    def linea(self, x1, y1, x2, y2, color=LINEA, sw=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}/>')

    def path(self, d, fill=CAJA2, stroke=LINEA, sw=1.5):
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def marca(self, n, x, y):
        """Número de nota sobre el bosquejo."""
        self.circ(x, y, 13, fill=TINTA, stroke=TINTA)
        self.texto(x, y + 5, str(n), 14, 700, "#FFFFFF", "middle")

    def wow(self, x, y, w, h):
        self.rect(x - 6, y - 6, w + 12, h + 12, 18, fill="none", stroke=WOW, dash="7 5", sw=2.5)
        self.rect(x + w - 44, y - 18, 50, 22, 11, fill=WOW, stroke=WOW)
        self.texto(x + w - 19, y - 3, "Wow", 13, 700, "#FFFFFF", "middle")

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}">'
                f'<rect width="{self.w}" height="{self.h}" fill="#F7F7F5"/>' + "".join(self.el) + "</svg>")


# ---------------------------------------------------------------- piezas
def telefono(L, x, y):
    L.rect(x, y, 390, 844, 46, fill=FONDO, stroke="#8E949A", sw=2.5)
    L.texto(x + 30, y + 30, "9:41", 13, 700, SUAVE)
    L.rect(x + 145, y + 12, 100, 28, 14, fill="#8E949A", stroke="#8E949A")


def barra_nav(L, x, y, etiquetas=("Inicio", "Mis comidas", "", "Progreso", "Avatar"), activa=0):
    L.rect(x + 16, y + 744, 358, 68, 34, fill="#5F656B", stroke="#5F656B")
    xs = [x + 52, x + 120, x + 195, x + 270, x + 338]
    for i, (cx, t) in enumerate(zip(xs, etiquetas)):
        if i == 2:
            continue
        L.circ(cx, y + 768, 9, fill="#FFFFFF" if i == activa else "#9AA0A6", stroke="none")
        L.texto(cx, y + 796, t, 10.5, 700 if i == activa else 400, "#FFFFFF", "middle")
    L.circ(x + 195, y + 750, 34, fill="#FFFFFF", stroke="#5F656B", sw=3)
    L.texto(x + 195, y + 755, "Cámara", 11, 700, TINTA, "middle")


def notas(L, x, y, titulo, items, ancho=380):
    L.texto(x, y, titulo, 20, 700)
    yy = y + 36
    for i, (n, texto) in enumerate(items):
        if n:
            L.marca(n, x + 13, yy - 5)
        else:
            L.circ(x + 13, yy - 5, 4, fill=SUAVE, stroke=SUAVE)
        # partir en líneas de ~44 caracteres
        palabras, linea, lineas = texto.split(), "", []
        for p in palabras:
            if len(linea) + len(p) + 1 > 42:
                lineas.append(linea)
                linea = p
            else:
                linea = (linea + " " + p).strip()
        lineas.append(linea)
        for j, l in enumerate(lineas):
            L.texto(x + 36, yy + j * 21, l, 15, 400, TINTA)
        yy += 21 * len(lineas) + 16
    return yy


def hoja(L, x, y, s=1.0):      # hoja = comida
    L.path(f"M{x} {y+60*s} C{x} {y+10*s} {x+40*s} {y-20*s} {x+95*s} {y} C{x+90*s} {y+55*s} {x+50*s} {y+95*s} {x} {y+60*s} Z")


def estrella(L, cx, cy, r):    # estrella = logro
    import math
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.5
        pts.append(f"{cx + rr*math.cos(a):.1f},{cy - rr*math.sin(a):.1f}")
    L.add(f'<polygon points="{" ".join(pts)}" fill="{CAJA2}" stroke="{LINEA}" stroke-width="1.5"/>')


def bandera(L, x, y):          # bandera = misión
    L.path(f"M{x} {y} L{x+110} {y} L{x+85} {y+40} L{x+110} {y+80} L{x} {y+80} Z")
    L.linea(x, y, x, y + 120, TINTA, 2)


def cara(L, cx, cy, r, fill=CAJA2):   # cara = emoción
    L.circ(cx, cy, r, fill=fill)
    L.circ(cx - r * .3, cy - r * .15, r * .08, fill=SUAVE, stroke="none")
    L.circ(cx + r * .3, cy - r * .15, r * .08, fill=SUAVE, stroke="none")
    L.add(f'<path d="M{cx-r*.35} {cy+r*.25} Q{cx} {cy+r*.55} {cx+r*.35} {cy+r*.25}" fill="none" stroke="{SUAVE}" stroke-width="2"/>')


def boton(L, x, y, w, t, primario=True, h=48):
    L.rect(x, y, w, h, h / 2, fill="#5F656B" if primario else FONDO, stroke="#5F656B")
    L.texto(x + w / 2, y + h / 2 + 5, t, 14, 700, "#FFFFFF" if primario else TINTA, "middle")


def cabecera(L, nombre, variante, explicacion):
    L.texto(40, 50, nombre, 28, 700)
    L.texto(40, 80, variante, 17, 700, SUAVE)
    L.texto(40, 104, explicacion, 15, 400, SUAVE)


# ---------------------------------------------------------------- pantallas
def inicio_a():
    L = Lienzo(900, 1010); cabecera(L, "Inicio", "Variante A · La canasta", "Un vistazo juguetón a tu día: cada forma es un dato.")
    x, y = 40, 140; telefono(L, x, y)
    L.texto(x + 24, y + 92, "Hola, Ana", 28, 700); L.texto(x + 24, y + 116, "Domingo 4 de octubre", 13, 400, SUAVE)
    cara(L, x + 340, y + 96, 24); L.marca(1, x + 372, y + 70)
    L.rect(x + 16, y + 140, 358, 110, 20); L.texto(x + 32, y + 168, "¿Cómo llegas hoy?", 16, 700); L.texto(x + 358, y + 168, "+5 XP", 12, 700, SUAVE, "end")
    for i in range(5):
        cara(L, x + 60 + i * 67, y + 212, 22, fill=FONDO)
    L.marca(2, x + 372, y + 140)
    L.texto(x + 24, y + 288, "Tu canasta de hoy", 18, 700)
    hoja(L, x + 40, y + 330, 1.6); L.texto(x + 110, y + 410, "2 de 3", 18, 700, TINTA, "middle"); L.texto(x + 110, y + 430, "comidas", 12, 400, SUAVE, "middle")
    estrella(L, x + 285, y + 370, 70); L.texto(x + 285, y + 378, "35/50", 16, 700, TINTA, "middle"); L.texto(x + 285, y + 396, "XP", 11, 400, SUAVE, "middle")
    bandera(L, x + 70, y + 470); L.texto(x + 112, y + 515, "1 de 3", 15, 700, TINTA, "middle"); L.texto(x + 112, y + 532, "misiones", 11, 400, SUAVE, "middle")
    cara(L, x + 285, y + 530, 58); L.texto(x + 285, y + 612, "ánimo: bien", 12, 400, SUAVE, "middle")
    L.wow(x + 24, y + 300, 342, 330); L.marca(3, x + 30, y + 296)
    L.rect(x + 16, y + 650, 358, 78, 20)
    L.texto(x + 32, y + 680, "Próxima misión", 12, 400, SUAVE); L.texto(x + 32, y + 702, "Registra una fruta", 15, 700); L.texto(x + 32, y + 720, "+10 XP", 11.5, 400, SUAVE)
    boton(L, x + 240, y + 666, 120, "Abrir cámara", h=44); L.marca(4, x + 372, y + 650)
    barra_nav(L, x, y); L.marca(5, x + 240, y + 742)
    notas(L, 470, 160, "Qué hace cada parte", [
        (1, "Tu avatar con la cara de tu ánimo de hoy. Al tocarlo abres Perfil y apariencia."),
        (2, "El check-in de ánimo. Desaparece cuando ya lo hiciste. Las caras son las de tu propio avatar (urls_por_estado) y todas dan el mismo XP."),
        (3, "La canasta: hoja = comidas, estrella = XP del día, bandera = misiones, cara = ánimo. Tocar una forma abre su pantalla. Wow: al registrar algo, su forma se llena con un rebote."),
        (4, "Siempre una sola misión sugerida: la más cercana a cumplirse."),
        (5, "La cámara al centro: es la acción más frecuente, así que es la más grande y la más cercana al pulgar (ley de Fitts)."),
        (0, "Datos: GET /progreso (xp, meta, racha, misiones, avatar) y GET /estado-animo."),
    ])
    return L


def inicio_b():
    L = Lienzo(900, 1010); cabecera(L, "Inicio", "Variante B · El día", "Tu día ordenado por momentos, como una agenda.")
    x, y = 40, 140; telefono(L, x, y)
    L.circ(x + 60, y + 100, 36); L.texto(x + 60, y + 98, "Nivel", 11, 400, SUAVE, "middle"); L.texto(x + 60, y + 116, "2", 18, 700, TINTA, "middle")
    L.texto(x + 110, y + 92, "Hola, Ana", 24, 700); L.rect(x + 110, y + 104, 120, 26, 13, fill=CAJA2); L.texto(x + 170, y + 122, "Racha 3 días", 12, 700, TINTA, "middle")
    L.marca(1, x + 30, y + 64)
    L.texto(x + 24, y + 170, "35 de 50 XP hoy", 14, 700); L.rect(x + 24, y + 182, 342, 12, 6, fill=CAJA2); L.rect(x + 24, y + 182, 240, 12, 6, fill="#9AA0A6", stroke="#9AA0A6")
    L.marca(2, x + 372, y + 180)
    momentos = [("Desayuno", "Arepa con queso", True), ("Media mañana", "Registrar", False), ("Almuerzo", "Registrar", False), ("Algo de fruta", "Registrar", False)]
    for i, (m, t, hecho) in enumerate(momentos):
        yy = y + 222 + i * 92
        L.texto(x + 24, yy + 18, m, 12, 700, SUAVE)
        L.rect(x + 24, yy + 26, 342, 56, 16, fill=CAJA if hecho else FONDO, stroke=LINEA, dash=None if hecho else "6 5")
        L.texto(x + 44, yy + 60, ("✓  " if hecho else "+  ") + t, 15, 700 if hecho else 400, TINTA if hecho else SUAVE)
    L.marca(3, x + 372, y + 222)
    L.texto(x + 24, y + 610, "Misiones", 16, 700)
    for i, t in enumerate(["Fruta", "3 comidas", "Ánimo"]):
        L.rect(x + 24 + i * 116, y + 624, 106, 80, 18); L.texto(x + 77 + i * 116, y + 670, t, 13, 700, TINTA, "middle")
    L.wow(x + 24, y + 624, 338, 80); L.marca(4, x + 30, y + 620)
    barra_nav(L, x, y)
    notas(L, 470, 160, "Qué hace cada parte", [
        (1, "Nivel y racha arriba, siempre visibles."),
        (2, "La meta del día en una barra. Debe decir el número además de la barra."),
        (3, "Los momentos del día. Los vacíos invitan a registrar. Ojo: el backend no guarda si fue desayuno o almuerzo; habría que deducirlo de la hora."),
        (4, "Wow: la misión cumplida se voltea y aparece su calcomanía."),
        (0, "A es más juguetona y visual; B es más clara para crear rutina. ¿Cuál se parece más a 'divertido y fluido'? También puedes combinarlas."),
    ])
    return L


def registrar(duda=False):
    L = Lienzo(900, 1010)
    cabecera(L, "Registrar comida", "Variante B · La IA tiene dudas" if duda else "Variante A · La IA está segura",
             "Ya existe en código (ejemplo-camara.html); aquí se piensa el celular.")
    x, y = 40, 140; telefono(L, x, y)
    L.texto(x + 24, y + 86, "Registrar comida", 22, 700)
    L.rect(x + 16, y + 104, 358, 300, 28, fill="#5F656B", stroke="#5F656B"); L.texto(x + 195, y + 260, "Visor de la cámara", 14, 400, "#FFFFFF", "middle")
    L.marca(1, x + 372, y + 104)
    # hoja inferior = etiqueta
    L.rect(x + 8, y + 430, 374, 300, 30, fill=FONDO, stroke="#8E949A", sw=2)
    L.circ(x + 40, y + 466, 8, fill=CAJA2); L.linea(x + 62, y + 446, x + 62, y + 714, LINEA, 1.5, "5 5")
    if not duda:
        L.texto(x + 80, y + 466, "Lumea cree que es", 13, 400, SUAVE); L.texto(x + 80, y + 512, "Banano", 40, 700)
        L.rect(x + 80, y + 528, 120, 8, 4, fill=CAJA2); L.texto(x + 212, y + 537, "Segura al 94 %", 12, 400, SUAVE)
        L.texto(x + 80, y + 580, "89 kcal  por cada 100 g", 16, 700)
        L.texto(x + 80, y + 610, "Su potasio ayuda a tus músculos.", 13, 400, SUAVE)
        boton(L, x + 80, y + 638, 190, "Sí, es esto  +10 XP"); L.texto(x + 280, y + 668, "No, es otra", 13, 400, SUAVE)
        L.wow(x + 14, y + 436, 362, 288)
        notas(L, 470, 160, "Qué hace cada parte", [
            (1, "Visor grande arriba; la foto ocupa lo que más se mira."),
            (0, "La etiqueta sube como hoja desde abajo y queda al alcance del pulgar. En computador va al lado del visor (ya está hecho)."),
            (0, "Wow: la etiqueta entra colgando y se balancea una sola vez. Al confirmar, salta la calcomanía de XP."),
            (0, "Si el alimento tiene sellos, van entre el nombre y las calorías, en negro como dice la norma."),
            (0, "Datos: POST /predecir y POST /confirmar-alimento (api.js)."),
        ])
    else:
        L.texto(x + 80, y + 470, "?  Tengo dudas con esta foto.", 15, 700); L.texto(x + 80, y + 492, "¿Me ayudas a confirmarla?", 13, 400, SUAVE)
        for i, t in enumerate(["Ajiaco", "Sancocho", "Mondongo"]):
            L.rect(x + 80, y + 512 + i * 58, 280, 48, 14, fill=FONDO); L.texto(x + 98, y + 542 + i * 58, t, 15, 700)
        L.texto(x + 80, y + 700, "Ninguno, lo escribo yo", 13, 400, SUAVE)
        L.marca(2, x + 372, y + 512)
        notas(L, 470, 160, "Qué hace cada parte", [
            (2, "Cuando la IA duda, no adivina: ofrece opciones como botones. Pide ayuda, no alarma (color mango + signo de pregunta)."),
            (0, "Hoy el backend ya manda opciones para los grupos que se confunden (sopas, dulces...). Mostrar el top-3 general en cualquier foto es un cambio pequeño en /predecir: en la prueba de campo la respuesta correcta estuvo en el top-3 en 13 de 13 fotos."),
            (0, "'Ninguno, lo escribo yo' abre un buscador sobre GET /alimentos."),
        ])
    barra_nav(L, x, y, activa=-1)
    return L


def avatar_a():
    L = Lienzo(900, 1010); cabecera(L, "Avatar y misiones", "Variante A · La vitrina", "Tu avatar en grande; misiones y armario en pestañas.")
    x, y = 40, 140; telefono(L, x, y)
    L.texto(x + 24, y + 86, "Tu avatar", 22, 700); L.rect(x + 280, y + 66, 86, 28, 14, fill=CAJA2); L.texto(x + 323, y + 85, "Nivel 2", 12, 700, TINTA, "middle")
    L.rect(x + 16, y + 106, 358, 270, 30)
    L.circ(x + 195, y + 190, 50); L.rect(x + 140, y + 240, 110, 120, 40, fill=CAJA2)
    L.wow(x + 16, y + 106, 358, 270); L.marca(1, x + 26, y + 102)
    L.texto(x + 24, y + 404, "60 XP para el nivel 3", 13, 700); L.rect(x + 24, y + 414, 342, 10, 5, fill=CAJA2)
    L.rect(x + 24, y + 440, 342, 44, 22, fill=CAJA); L.rect(x + 28, y + 444, 167, 36, 18, fill=FONDO)
    L.texto(x + 111, y + 467, "Misiones", 14, 700, TINTA, "middle"); L.texto(x + 280, y + 467, "Armario", 14, 400, SUAVE, "middle"); L.marca(2, x + 372, y + 440)
    for i, (t, ok) in enumerate([("Registra una fruta", True), ("Registra 3 comidas", False), ("Haz tu check-in de ánimo", False)]):
        yy = y + 500 + i * 76
        L.rect(x + 24, yy, 342, 64, 18, fill=CAJA if ok else FONDO)
        L.texto(x + 44, yy + 30, t, 15, 700 if ok else 400); L.texto(x + 44, yy + 50, "+10 XP", 12, 400, SUAVE)
        if ok:
            estrella(L, x + 330, yy + 32, 22)
    L.marca(3, x + 372, y + 500)
    barra_nav(L, x, y, activa=4)
    notas(L, 470, 160, "Qué hace cada parte", [
        (1, "El avatar por capas de Laura (base, ropa, accesorio) con la cara de tu ánimo. Wow: al ponerte algo nuevo, el avatar da un saltico."),
        (2, "Pestañas: Misiones | Armario. El armario muestra ropa y accesorios; lo bloqueado lleva candado y 'Nivel 8'."),
        (3, "Las tres misiones diarias del backend. La cumplida lleva su calcomanía."),
        (0, "Datos: GET /avatar, POST /avatar/equipar y /quitar, y misiones de GET /progreso. Si las imágenes de Laura no llegan, el backend tiene el avatar DiceBear de respaldo."),
    ])
    return L


def avatar_b():
    L = Lienzo(900, 1010); cabecera(L, "Avatar y misiones", "Variante B · El tablero", "Las misiones mandan; el avatar acompaña.")
    x, y = 40, 140; telefono(L, x, y)
    L.circ(x + 60, y + 100, 34); L.texto(x + 110, y + 94, "Ana", 22, 700); L.texto(x + 110, y + 116, "Nivel 2 · 60 XP para el 3", 13, 400, SUAVE)
    L.marca(1, x + 372, y + 70)
    L.texto(x + 24, y + 172, "Misiones de hoy", 20, 700)
    hoja(L, x + 36, y + 210, 1.45); L.texto(x + 104, y + 290, "Fruta", 14, 700, TINTA, "middle")
    L.rect(x + 210, y + 196, 150, 150, 40); L.texto(x + 285, y + 276, "3 comidas", 14, 700, TINTA, "middle"); L.texto(x + 285, y + 296, "2 de 3", 12, 400, SUAVE, "middle")
    cara(L, x + 195, y + 430, 66); L.texto(x + 195, y + 520, "Check-in de ánimo", 13, 700, TINTA, "middle")
    L.wow(x + 24, y + 190, 342, 344); L.marca(2, x + 30, y + 186)
    L.texto(x + 24, y + 572, "Armario", 18, 700); L.texto(x + 366, y + 572, "Ver todo", 13, 400, SUAVE, "end")
    for i, t in enumerate(["Buzo", "Gafas", "Nivel 3", "Nivel 4"]):
        L.rect(x + 24 + i * 88, y + 588, 78, 100, 18, fill=CAJA if i < 2 else FONDO, dash=None if i < 2 else "6 5")
        L.texto(x + 63 + i * 88, y + 676, t, 11.5, 700 if i < 2 else 400, TINTA if i < 2 else SUAVE, "middle")
    L.marca(3, x + 372, y + 588)
    barra_nav(L, x, y, activa=4)
    notas(L, 470, 160, "Qué hace cada parte", [
        (1, "Avatar pequeño y tu nivel. Tocarlo abre el armario completo."),
        (2, "Las misiones como formas grandes, igual que la canasta de Inicio: misma gramática visual en toda la app. Wow: al cumplirse, la forma se llena y gira."),
        (3, "Un adelanto del armario: lo que ya tienes y lo que viene, con el nivel que falta."),
        (0, "A presume el avatar; B empuja a cumplir misiones. Tú dijiste que esta pantalla es 'donde estarán las misiones': B lo toma literal."),
    ])
    return L


def crear_cuenta():
    L = Lienzo(900, 1010); cabecera(L, "Crear cuenta", "Paso 3 de 4 · Elige tu paleta", "El formulario de Sara, dividido en pasos.")
    x, y = 40, 140; telefono(L, x, y)
    for i in range(4):
        L.rect(x + 24 + i * 87, y + 70, 79, 8, 4, fill="#5F656B" if i < 3 else CAJA2, stroke="none")
    L.marca(1, x + 372, y + 62)
    L.texto(x + 24, y + 124, "Elige cómo se ve tu Lumea", 22, 700); L.texto(x + 24, y + 148, "Puedes cambiarla cuando quieras.", 13, 400, SUAVE)
    for i, t in enumerate(["Laguna Verde", "Neblina", "Carnaval", "Colibrí", "Cosecha"]):
        yy = y + 172 + i * 84
        L.rect(x + 24, yy, 342, 72, 18, fill=CAJA if i == 0 else FONDO, sw=2.5 if i == 0 else 1.5, stroke="#5F656B" if i == 0 else LINEA)
        L.texto(x + 44, yy + 32, t, 16, 700)
        for k in range(5):
            L.circ(x + 52 + k * 26, yy + 52, 9)
    L.wow(x + 24, y + 172, 342, 408); L.marca(2, x + 30, y + 168)
    boton(L, x + 24, y + 640, 342, "Seguir")
    notas(L, 470, 160, "Qué hace cada parte", [
        (1, "Cuatro pasos: 1 tu nombre y correo, 2 tu objetivo (las cinco tarjetas de Sara), 3 tu paleta, 4 tu contraseña."),
        (2, "Wow: al tocar una paleta, TODA la pantalla cambia a esos colores al instante. Es el primer momento de autonomía en la app."),
        (0, "Pregunta abierta: el formulario de Sara pide sexo (masculino, femenino, otro). ¿El backend lo usa para algo? Si no, quítalo: con menores de edad se piden los datos mínimos (Ley 1581 de 2012). Y nunca se usa para elegir colores."),
        (0, "La contraseña va al final: primero se gana el interés, después se pide el esfuerzo."),
    ])
    return L


def bienvenida():
    L = Lienzo(1320, 680); cabecera(L, "Bienvenida (computador)", "index.html de Sara, con nueva piel", "Lo primero que ve el jurado.")
    x, y, s = 40, 140, 0.62
    W, H = 1280 * s, 800 * s
    L.rect(x, y, W, H, 18, fill=FONDO, stroke="#8E949A", sw=2.5)
    L.rect(x + 24, y + 22, 90, 26, 8, fill=CAJA2); L.texto(x + 69, y + 40, "logo", 12, 700, TINTA, "middle")
    for i, t in enumerate(["Conócenos", "Guía"]):
        L.texto(x + 160 + i * 90, y + 40, t, 12, 400, SUAVE)
    boton(L, x + W - 230, y + 18, 90, "Entrar", False, 34); boton(L, x + W - 130, y + 18, 110, "Crear cuenta", True, 34)
    L.texto(x + 40, y + 140, "Tu titular aquí:", 14, 400, SUAVE)
    L.texto(x + 40, y + 176, "Una frase que diga qué hace", 24, 700); L.texto(x + 40, y + 206, "Lumea y por qué no prohíbe", 24, 700)
    L.rect(x + 40, y + 226, 340, 12, 6, fill=CAJA2); L.rect(x + 40, y + 246, 280, 12, 6, fill=CAJA2)
    boton(L, x + 40, y + 280, 150, "Crear cuenta"); boton(L, x + 204, y + 280, 150, "Ya tengo cuenta", False)
    L.marca(1, x + 30, y + 120)
    L.rect(x + 480, y + 80, 240, 300, 30, fill="#5F656B", stroke="#5F656B"); L.texto(x + 600, y + 120, "foto de comida real", 12, 400, "#FFFFFF", "middle")
    L.rect(x + 520, y + 200, 200, 150, 18, fill=FONDO); L.circ(x + 540, y + 222, 6); L.texto(x + 560, y + 270, "Banano", 26, 700); L.texto(x + 560, y + 300, "89 kcal", 14, 700)
    L.wow(x + 480, y + 80, 260, 300); L.marca(2, x + 470, y + 70)
    for i, t in enumerate(["Captura y reconoce", "Información nutricional", "Enfoque educativo"]):
        L.rect(x + 40 + i * 250, y + 410, 230, 70, 16); L.texto(x + 56 + i * 250, y + 450, t, 13, 700)
    L.marca(3, x + 30, y + 405)
    notas(L, 880, 160, "Qué hace cada parte", [
        (1, "El titular es tuyo: una frase que diga qué hace Lumea sin prometer milagros. Botón principal: Crear cuenta."),
        (2, "Wow: en vez de la imagen de hojas, una foto real de comida y la etiqueta de plaza entrando colgada. Muestra el producto en dos segundos."),
        (3, "Las tres tarjetas de Sara, con sus textos."),
        (0, "En celular todo va en una columna: titular, botón, la foto con la etiqueta y las tarjetas."),
    ], ancho=400)
    return L


def inicio_pc():
    L = Lienzo(1320, 760); cabecera(L, "Inicio (computador)", "Variante A en 1280 px", "El mismo contenido del celular, en dos columnas.")
    x, y, s = 40, 140, 0.62
    W, H = 1280 * s, 800 * s
    L.rect(x, y, W, H, 18, fill=FONDO, stroke="#8E949A", sw=2.5)
    L.rect(x, y, 150, H, 18, fill=CAJA, stroke=LINEA)
    L.texto(x + 20, y + 36, "logo", 13, 700)
    for i, t in enumerate(["Inicio", "Mis comidas", "Registrar", "Progreso", "Avatar"]):
        L.rect(x + 12, y + 60 + i * 40, 126, 32, 10, fill=FONDO if i == 0 else CAJA, stroke=LINEA if i == 0 else CAJA)
        L.texto(x + 26, y + 81 + i * 40, t, 12, 700 if i == 0 else 400, TINTA if i == 0 else SUAVE)
    L.marca(1, x + 150, y + 60)
    L.texto(x + 180, y + 50, "Hola, Ana", 24, 700)
    L.rect(x + 180, y + 72, 430, 380, 20); L.texto(x + 200, y + 100, "Tu canasta de hoy", 15, 700)
    hoja(L, x + 220, y + 150, 1.5); estrella(L, x + 500, y + 200, 70); bandera(L, x + 250, y + 300); cara(L, x + 500, y + 360, 55)
    L.wow(x + 180, y + 72, 430, 380); L.marca(2, x + 186, y + 68)
    L.rect(x + 630, y + 72, 152, 120, 18); L.texto(x + 645, y + 100, "¿Cómo llegas hoy?", 12, 700)
    L.rect(x + 630, y + 206, 152, 110, 18); L.texto(x + 645, y + 234, "Próxima misión", 12, 700)
    L.rect(x + 630, y + 330, 152, 122, 18); L.texto(x + 645, y + 358, "Racha y nivel", 12, 700)
    L.marca(3, x + 782, y + 72)
    notas(L, 880, 160, "Qué cambia en 1280 px", [
        (1, "La barra inferior se vuelve menú lateral. Es el mismo HTML (ya está en componentes.css)."),
        (2, "La canasta crece y queda a la izquierda, donde empieza la lectura."),
        (3, "Lo que en celular iba arriba y abajo, aquí va en una columna a la derecha."),
        (0, "Diseña siempre las dos medidas, pero piensa primero el celular: si cabe ahí, cabe en todo."),
    ], ancho=400)
    return L


def progreso():
    L = Lienzo(900, 1010); cabecera(L, "Progreso", "Versión 1.1", "Cómo vas en la semana, sin juzgar.")
    x, y = 40, 140; telefono(L, x, y)
    L.texto(x + 24, y + 86, "Tu progreso", 22, 700)
    L.rect(x + 24, y + 104, 342, 40, 20, fill=CAJA)
    for i, t in enumerate(["Hoy", "Semana", "Todo"]):
        L.texto(x + 81 + i * 114, y + 129, t, 13, 700 if i == 1 else 400, TINTA if i == 1 else SUAVE, "middle")
    L.rect(x + 24, y + 160, 342, 110, 20); L.texto(x + 44, y + 194, "Nivel 2", 22, 700); L.texto(x + 44, y + 218, "Te faltan 60 XP para el nivel 3", 13, 400, SUAVE)
    L.rect(x + 44, y + 234, 302, 12, 6, fill=CAJA2); L.wow(x + 24, y + 160, 342, 110); L.marca(1, x + 30, y + 156)
    for i, (n, t) in enumerate([("3 días", "racha"), ("5 días", "tu mejor racha")]):
        L.rect(x + 24 + i * 177, y + 288, 165, 80, 18); L.texto(x + 44 + i * 177, y + 324, n, 18, 700); L.texto(x + 44 + i * 177, y + 346, t, 12, 400, SUAVE)
    L.texto(x + 24, y + 404, "Comidas de la semana", 15, 700)
    hs = [40, 70, 55, 90, 30, 80, 60]
    for i, h in enumerate(hs):
        L.rect(x + 34 + i * 47, y + 520 - h, 30, h, 6, fill=CAJA2); L.texto(x + 49 + i * 47, y + 540, "LMMJVSD"[i], 11, 400, SUAVE, "middle")
    L.marca(2, x + 372, y + 404)
    L.texto(x + 24, y + 582, "Tu ánimo de la semana", 15, 700)
    for i in range(7):
        cara(L, x + 46 + i * 50, y + 620, 18, fill=FONDO)
    L.marca(3, x + 372, y + 580)
    L.rect(x + 24, y + 656, 342, 70, 18, dash="6 5", fill=FONDO); L.texto(x + 44, y + 688, "¡Te extrañamos! Tu nivel sigue siendo tuyo.", 13, 400, SUAVE); L.marca(4, x + 372, y + 656)
    barra_nav(L, x, y, activa=3)
    notas(L, 470, 160, "Qué hace cada parte", [
        (1, "Nivel y XP con el número escrito. Wow: subir de nivel destapa lo que se desbloqueó en el armario."),
        (2, "Una gráfica simple de comidas por día; la fruta puede marcarse con su ícono, no solo con color."),
        (3, "El ánimo de la semana con las caras de tu avatar. Es tuyo y no se compara con nadie."),
        (4, "Cuando vuelves después de días sin usarla, el backend manda mensaje_regreso. Va como bienvenida cálida, nunca como 'perdiste XP'."),
        (0, "Datos: GET /progreso, GET /historial y GET /estado-animo."),
    ])
    return L


def animo():
    L = Lienzo(900, 1010); cabecera(L, "Ánimo", "Versión 1.1", "Un check-in de diez segundos; también vive en Inicio.")
    x, y = 40, 140; telefono(L, x, y)
    L.texto(x + 24, y + 86, "¿Cómo llegas hoy?", 24, 700)
    cara(L, x + 195, y + 230, 90); L.wow(x + 95, y + 130, 200, 200); L.marca(1, x + 100, y + 126)
    for i, t in enumerate(["Muy mal", "Mal", "Neutral", "Bien", "Muy bien"]):
        cara(L, x + 51 + i * 72, y + 400, 26, fill=FONDO if i != 3 else CAJA2)
        L.texto(x + 51 + i * 72, y + 446, t, 11, 700 if i == 3 else 400, TINTA if i == 3 else SUAVE, "middle")
    L.marca(2, x + 372, y + 372)
    boton(L, x + 24, y + 480, 342, "Guardar mi ánimo  +5 XP")
    L.texto(x + 24, y + 572, "Esta semana", 15, 700)
    for i in range(7):
        cara(L, x + 46 + i * 50, y + 610, 18, fill=FONDO)
    L.rect(x + 24, y + 650, 342, 76, 18, dash="6 5", fill=FONDO); L.texto(x + 44, y + 682, "Si te sientes mal varios días,", 13, 400, SUAVE); L.texto(x + 44, y + 702, "hablar con alguien ayuda.", 13, 400, SUAVE)
    L.marca(3, x + 372, y + 650)
    barra_nav(L, x, y, activa=-1)
    notas(L, 470, 160, "Qué hace cada parte", [
        (1, "Tu avatar cambia de cara mientras eliges. Wow: la cara se transforma en vivo."),
        (2, "Los cinco estados del backend (muy_mal a muy_bien). Todos dan el mismo XP: no se premia estar bien."),
        (3, "Decisión ética tuya: si alguien marca 'mal' varios días, ¿la app sugiere hablar con orientación escolar? Si lo haces, que sea una invitación, nunca un diagnóstico."),
        (0, "Con la navegación B, esta pantalla se abre desde Inicio y desde Progreso, no desde la barra."),
    ])
    return L


PANTALLAS = {
    "01-inicio-a-canasta": inicio_a, "02-inicio-b-dia": inicio_b, "03-inicio-computador": inicio_pc,
    "04-registrar-a-segura": lambda: registrar(False), "05-registrar-b-duda": lambda: registrar(True),
    "06-avatar-a-vitrina": avatar_a, "07-avatar-b-tablero": avatar_b,
    "08-crear-cuenta-paleta": crear_cuenta, "09-bienvenida-computador": bienvenida,
    "10-progreso": progreso, "11-animo": animo,
}

if __name__ == "__main__":
    os.makedirs(SALIDA, exist_ok=True)
    for nombre, f in PANTALLAS.items():
        with open(os.path.join(SALIDA, nombre + ".svg"), "w") as fh:
            fh.write(f().svg())
        print("bosquejos/" + nombre + ".svg")
