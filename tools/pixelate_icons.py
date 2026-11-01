#!/usr/bin/env python3
"""Convierte los logotipos vectoriales de gen/icons/*.svg en sprites pixel art.

Cada logo se rasteriza a una cuadrícula pequeña, se reduce a pocos colores y se guarda
como gen/icons/pixel/<nombre>.json  ->  {"size": N, "palette": {"a": "#hex"}, "rows": [...]}
El generador lee esos JSON, así que solo hace falta ejecutar esto si cambias un logo.

Requiere: rsvg-convert (librsvg) y Pillow.
"""
import io
import json
import pathlib
import string
import subprocess
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "gen" / "icons"
OUT = SRC / "pixel"

SIZE = 16          # celdas por lado
MAX_COLORS = 5     # colores por icono (sin contar transparente)
ALPHA_CUT = 70     # por debajo, el píxel se considera transparente
# Algunos logos se leen mejor con un poco más de resolución
SIZE_OVERRIDE = {"java": 18, "githubactions": 18, "postgresql": 18, "docker": 18}
# Umbral de transparencia propio para logos de trazo muy fino o muy grueso
ALPHA_OVERRIDE = {"react": 120, "ionic": 130, "sonarqube": 40}


def render(svg_path, size):
    # se renderiza grande y se reduce con 'box' para que cada celda sea la media de su zona
    png = subprocess.run(["rsvg-convert", "-w", str(size * 16), "-h", str(size * 16), str(svg_path)],
                         check=True, capture_output=True).stdout
    img = Image.open(io.BytesIO(png)).convert("RGBa")  # alfa premultiplicado: los bordes no se oscurecen
    return img.resize((size, size), Image.BOX).convert("RGBA")


def pixelate(name):
    size = SIZE_OVERRIDE.get(name, SIZE)
    img = render(SRC / f"{name}.svg", size)
    alpha = img.getchannel("A")
    rgb = img.convert("RGB")  # color real de cada celda, sin mezclar con el fondo
    q = rgb.quantize(colors=MAX_COLORS + 1, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    letters = iter(string.ascii_letters)
    used, rows = {}, []
    for y in range(size):
        row = ""
        for x in range(size):
            if alpha.getpixel((x, y)) < ALPHA_OVERRIDE.get(name, ALPHA_CUT):
                row += "."
                continue
            idx = q.getpixel((x, y))
            hexc = "#{:02x}{:02x}{:02x}".format(*pal[idx * 3: idx * 3 + 3])
            if hexc not in used:
                used[hexc] = next(letters)
            row += used[hexc]
        rows.append(row)
    return {"size": size, "palette": {v: k for k, v in used.items()}, "rows": rows}


# Logos con partes oscuras que no se verían sobre el fondo: los colores muy oscuros pasan a claro
LIGHTEN_DARK = {"amazonwebservices", "flask"}


def lighten_dark(data):
    for k, hexc in data["palette"].items():
        r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
        if 0.2126 * r + 0.7152 * g + 0.0722 * b < 90:
            data["palette"][k] = "#e6edf3"
    return data


# Sprites dibujados a mano para logos que pierden la forma al reducirlos
HAND = {
    "docker": {"size": 16, "palette": {"b": "#2496ed", "e": "#0d1117"}, "rows": [
        "................",
        "................",
        "..........bb....",
        "..........bb....",
        "....bb.bb.bb....",
        "....bb.bb.bb....",
        ".bb.bb.bb.bb.bb.",
        ".bb.bb.bb.bb.bb.",
        "..............b.",
        "bbbbbbbbbbbbbbbb",
        "bbebbbbbbbbbbbb.",
        "bbbbbbbbbbbbbb..",
        ".bbbbbbbbbbbb...",
        "..bbbbbbbbbb....",
        "....bbbbbb......",
        "................",
    ]},
}


def ionic():
    """Anillo abierto + círculo central + punto, como el logo de Ionic."""
    import math
    rows = []
    for y in range(16):
        row = ""
        for x in range(16):
            dx, dy = x + 0.5 - 8, y + 0.5 - 8
            r = math.hypot(dx, dy)
            ang = math.degrees(math.atan2(-dy, dx))
            dot = math.hypot(x + 0.5 - 12.6, y + 0.5 - 3.4) < 1.9
            if r < 3.3 or dot:
                row += "b"
            elif 5.6 < r < 7.3 and not (20 < ang < 70):
                row += "b"
            else:
                row += "."
        rows.append(row)
    return {"size": 16, "palette": {"b": "#4e8ef7"}, "rows": rows}


def main():
    OUT.mkdir(exist_ok=True)
    HAND["ionic"] = ionic()
    for svg in sorted(SRC.glob("*.svg")):
        data = HAND.get(svg.stem) or pixelate(svg.stem)
        if svg.stem in LIGHTEN_DARK:
            data = lighten_dark(data)
        (OUT / f"{svg.stem}.json").write_text(json.dumps(data, indent=0), encoding="utf-8")
        print(f"{svg.stem}: {data['size']}x{data['size']}, {len(data['palette'])} colores")


if __name__ == "__main__":
    sys.exit(main())
