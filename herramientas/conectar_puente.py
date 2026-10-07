"""Conecta las páginas de Sara al sistema de diseño (tokens, paletas y puente).

Uso, desde la carpeta del proyecto:  python3 herramientas/conectar_puente.py
Es idempotente: si una página ya está conectada, no la toca.
"""
import pathlib
import re

PAGINAS = ["index.html", "conocenos.html", "guialumea.html", "terminos.html",
           "iniciar-sesion.html", "crear-cuenta.html", "index-ingresado.html",
           "mis-registros.html", "alimentos.html", "progreso.html", "emociones.html", "avatar.html"]

# Bootstrap y sus íconos se sirven desde vendor/ (la demo y el video funcionan sin internet)
CDN_A_VENDOR = [
    ("https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css", "vendor/bootstrap/bootstrap.min.css"),
    ("https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js", "vendor/bootstrap/bootstrap.bundle.min.js"),
    ("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css", "vendor/bootstrap-icons/bootstrap-icons.min.css"),
]

for nombre in PAGINAS:
    p = pathlib.Path(nombre)
    s = p.read_text(encoding="utf-8")
    for cdn, local in CDN_A_VENDOR:
        s = s.replace(cdn, local)
    if "estilos/puente-sara.css" in s:
        p.write_text(s, encoding="utf-8")
        print(f"{nombre}: ya estaba conectada")
        continue

    # 1. tema.js va primero y sin defer: pone paleta, modo y piel antes de pintar
    s, n1 = re.subn(r'^([ \t]*)(<meta name="viewport"[^>]*>)[ \t]*\n',
                    r'\1\2\n\1<!-- Paleta, modo y piel (?piel=sara muestra el original) -->\n\1<script src="tema.js"></script>\n',
                    s, count=1, flags=re.M)
    # 2. Tokens y paletas antes de style.css; el puente después, para ganarle
    s, n2 = re.subn(r'^([ \t]*)(<link rel="stylesheet" href="style\.css"\s*/?>)[ \t]*\n',
                    r'\1<link rel="stylesheet" href="estilos/tokens.css">\n'
                    r'\1<link rel="stylesheet" href="estilos/paletas.css">\n'
                    r'\1\2\n'
                    r'\1<!-- Piel de Lumea sobre el diseño de Sara (no cambia style.css) -->\n'
                    r'\1<link rel="stylesheet" href="estilos/puente-sara.css">\n',
                    s, count=1, flags=re.M)
    assert n1 == 1 and n2 == 1, f"{nombre}: no encontré el viewport o style.css"
    p.write_text(s, encoding="utf-8")
    print(f"{nombre}: conectada")
