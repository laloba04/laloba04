#!/usr/bin/env python3
"""Comprueba que lo generado es correcto antes de publicarlo.

- todos los SVG son XML válidos, tienen <title> y aria-label, y el ancho esperado (900 PC / 420 móvil)
- no cargan nada externo (GitHub bloquea recursos externos dentro de los SVG)
- español e inglés tienen los mismos archivos, y cada SVG de PC tiene su versión móvil
- todas las imágenes que enlazan los README existen
Sale con código 1 si encuentra algún problema.
"""
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
NS = "{http://www.w3.org/2000/svg}"
MAX_BYTES = 400_000


def check():
    errors = []
    svgs = sorted(ASSETS.rglob("*.svg"))
    if not svgs:
        return ["No hay SVG en assets/: ejecuta python gen/build.py"]
    for p in svgs:
        rel = p.relative_to(ROOT)
        text = p.read_text(encoding="utf-8")
        try:
            root = ET.fromstring(text)
        except ET.ParseError as e:
            errors.append(f"{rel}: XML inválido ({e})")
            continue
        if root.find(f"{NS}title") is None or not root.get("aria-label"):
            errors.append(f"{rel}: falta <title> o aria-label")
        w = int(float(root.get("width")))
        if p.name.startswith("btn-"):
            expected = w  # los botones miden según su texto
        elif p.name.startswith("quest-"):
            expected = 412  # tarjetas: dos por fila en PC, una en móvil
        else:
            expected = 420 if p.parent.name == "mobile" else 900
        if w != expected:
            errors.append(f"{rel}: ancho {w}, se esperaba {expected}")
        if re.search(r'(href|src)="https?://|url\((?!data:|#)', text):
            errors.append(f"{rel}: referencia externa (GitHub no la cargaría)")
        if len(text.encode()) > MAX_BYTES:
            errors.append(f"{rel}: pesa {len(text.encode())} bytes (máx. {MAX_BYTES})")

    langs = [d for d in ASSETS.iterdir() if d.is_dir()]
    sets = {d.name: {str(p.relative_to(d)) for p in d.rglob("*.svg")} for d in langs}
    names = list(sets)
    for other in names[1:]:
        diff = sets[names[0]] ^ sets[other]
        if diff:
            errors.append(f"{names[0]} y {other} no tienen los mismos archivos: {sorted(diff)}")
    for lang, files in sets.items():
        for f in files:
            if "/" not in f and not f.startswith(("btn-", "quest-")) and f"mobile/{f}" not in files:
                errors.append(f"assets/{lang}/{f}: falta la versión móvil")

    for readme in ("README.md", "README.en.md"):
        text = (ROOT / readme).read_text(encoding="utf-8")
        for m in re.findall(r'/raw/main/(assets/[^"?]+\.svg)', text):
            if not (ROOT / m).exists():
                errors.append(f"{readme}: enlaza {m}, que no existe")
    return errors


def main():
    errors = check()
    for e in errors:
        print("✗", e)
    if errors:
        return 1
    print(f"✓ {len(list(ASSETS.rglob('*.svg')))} SVG correctos y README coherentes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
