#!/usr/bin/env python3
"""Hace capturas del perfil tal y como se vería en PC y en móvil (con las animaciones terminadas).

Uso:  python tools/preview.py [es|en]
Guarda previews/<idioma>-desktop.png y previews/<idioma>-mobile.png (carpeta ignorada por git).
Requiere: pip install playwright && playwright install chromium
"""
import pathlib
import re
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "previews"


def page_html(lang):
    readme = (ROOT / ("README.md" if lang == "es" else "README.en.md")).read_text(encoding="utf-8")
    # apunta las imágenes a los archivos locales en vez de a github.com
    readme = re.sub(r"https://github\.com/[^/]+/[^/]+/raw/main/", (ROOT.as_uri() + "/"), readme)
    readme = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", readme)
    readme = re.sub(r"^<!--.*?-->\n", "", readme)
    return ("<!doctype html><meta charset=utf-8><style>body{background:#0d1117;color:#e6edf3;"
            "font-family:sans-serif;margin:0 auto;max-width:900px;padding:16px}img{max-width:100%}"
            "picture img{display:block;margin:8px 0}</style>" + readme)


def main():
    langs = sys.argv[1:] or ["es", "en"]
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for lang in langs:
            html = OUT / f"{lang}.html"
            html.write_text(page_html(lang), encoding="utf-8")
            for mode, width in (("desktop", 960), ("mobile", 400)):
                pg = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=1)
                pg.goto(html.as_uri())
                pg.wait_for_timeout(9000)  # deja que la terminal termine de escribirse
                pg.screenshot(path=str(OUT / f"{lang}-{mode}.png"), full_page=True)
                pg.close()
                print(f"previews/{lang}-{mode}.png")
        browser.close()


if __name__ == "__main__":
    sys.exit(main())
