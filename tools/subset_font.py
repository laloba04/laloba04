#!/usr/bin/env python3
"""Recorta la fuente pixel a los caracteres que usa el perfil.

Lee fonts/VT323-Regular.woff2 y escribe:
  - fonts/vt323-pixel.woff2   (subconjunto que se incrusta en cada SVG)
  - fonts/vt323-pixel.chars   (caracteres que contiene; el resto usa la fuente de reserva)

Solo hace falta volver a ejecutarlo si añades textos con letras nuevas.
Requiere: pip install fonttools brotli
"""
import json
import pathlib
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "fonts" / "VT323-Regular.woff2"
OUT = ROOT / "fonts" / "vt323-pixel.woff2"
CHARS = ROOT / "fonts" / "vt323-pixel.chars"


def wanted_chars():
    text = (ROOT / "data" / "profile.json").read_text(encoding="utf-8")
    # ASCII imprimible + todo lo que aparece en los textos + dígitos/separadores de los datos vivos
    base = "".join(chr(c) for c in range(32, 127))
    return set(base + json.loads(json.dumps(text)) + "0123456789.,%·→")


def main():
    font = TTFont(SRC)
    cmap = font.getBestCmap()
    chars = sorted(c for c in wanted_chars() if ord(c) in cmap)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = []
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=[ord(c) for c in chars])
    sub.subset(font)
    font.flavor = "woff2"
    font.save(OUT)
    CHARS.write_text("".join(chars), encoding="utf-8")
    print(f"{OUT.name}: {OUT.stat().st_size} bytes, {len(chars)} caracteres")


if __name__ == "__main__":
    sys.exit(main())
