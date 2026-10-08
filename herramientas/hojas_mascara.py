#!/usr/bin/env python3
"""
LUMEA · hojas_mascara.py — saca de Lumen.png (el fondo de hojas de Sara) solo las hojas, las formas y los destellos.

Para qué: en las páginas públicas el fondo es BLANCO (decisión de Isabella) y el color de la paleta va solo en los
adornos. Lumen.png trae un fondo crema, así que no se puede teñir tal cual. Este script lo convierte en una máscara:
un PNG blanco cuyo ALPHA es «cuánto se aparta cada punto del crema del fondo». Con esa máscara el CSS pinta los
adornos de UN color plano de la paleta (estilos/publico.css, `mask-image`), con la misma composición que Sara
dibujó y sin mezclar colores: bajar o subir el adorno es cambiar una opacidad.

Se corre una vez, o cuando cambie Lumen.png:
    python3 herramientas/hojas_mascara.py
Necesita Pillow y numpy. Escribe img/hojas-mascara.png.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "Lumen.png"
SALIDA = RAIZ / "img" / "hojas-mascara.png"

ANCHO = 1152            # el fondo se estira con `cover`; no hace falta la resolución original (1536 px)
RUIDO = 5.0             # lo que se aparta del crema por simple textura de papel: no cuenta como adorno
GAMMA = 0.7             # < 1 sube las formas suaves y los destellos finos para que no se pierdan


def main():
    img = Image.open(ENTRADA).convert("RGB")
    alto = round(img.height * ANCHO / img.width)
    img = img.resize((ANCHO, alto), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))
    datos = np.asarray(img, dtype=np.float32)

    # El crema del fondo: la mediana de una franja del centro, donde no hay adornos
    centro = datos[alto // 4: alto // 2, ANCHO // 3: 2 * ANCHO // 3].reshape(-1, 3)
    crema = np.median(centro, axis=0)

    # Qué tanto se aparta cada punto del crema (distancia entre colores) -> 0 a 1
    distancia = np.sqrt(((datos - crema) ** 2).sum(axis=2))
    tope = np.percentile(distancia, 99.7)
    alpha = np.clip((distancia - RUIDO) / (tope - RUIDO), 0, 1) ** GAMMA

    mascara = np.zeros((alto, ANCHO, 4), dtype=np.uint8)
    mascara[..., :3] = 255
    mascara[..., 3] = (alpha * 255).round().astype(np.uint8)
    Image.fromarray(mascara, "RGBA").save(SALIDA, optimize=True)
    print(f"{SALIDA.relative_to(RAIZ)}: {ANCHO}x{alto}, crema {crema.round().astype(int).tolist()}, "
          f"{SALIDA.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
