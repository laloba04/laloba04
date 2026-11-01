#!/usr/bin/env python3
"""Genera todo el perfil: assets/<idioma>/*.svg, assets/<idioma>/mobile/*.svg, README.md y README.en.md.

Uso:  python gen/build.py
Lee:  data/profile.json (textos, proyectos, inventario) y data/live.json (datos de GitHub, opcional)
No necesita dependencias externas.
"""
import json
import re
import shutil
import sys

import sections as S
from pixel import ROOT, WIDTH
from readme import readme

ASSETS = ROOT / "assets"


def load_live():
    p = ROOT / "data" / "live.json"
    if not p.exists():
        return None
    live = json.loads(p.read_text(encoding="utf-8"))
    return live if live.get("updated") else None


def cv_link(cfg, lang="es"):
    """URL del CV del idioma, o None si es una ruta del repo que aún no existe (así el botón no aparece roto)."""
    cv = cfg["links"].get("cv")
    if isinstance(cv, dict):
        cv = cv.get(lang)
    if not cv:
        return None
    if cv.startswith("http"):
        return cv
    if (ROOT / cv).exists():
        return f'https://github.com/{cfg["user"]}/{cfg["user"]}/blob/main/{cv}'
    return None


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build():
    cfg = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
    live = load_live()
    if ASSETS.exists():
        shutil.rmtree(ASSETS)
    count = 0
    for lang, d in cfg["lang"].items():
        base = ASSETS / lang
        # botones: tamaño fijo, valen para PC y móvil
        write(base / "btn-lang.svg", S.button(d["lang_btn"], "lang"))
        for key in d["btn"]:
            if key == "cv" and not cv_link(cfg, lang):
                continue
            write(base / f"btn-{key}.svg", S.button(d["btn"][key], key))
            count += 1
        count += 1
        stats_alt = ""
        for mode in WIDTH:
            folder = base if mode == "desktop" else base / "mobile"
            files = {
                "hero.svg": S.hero(d, lang, mode, cfg),
                "sheet.svg": S.sheet(d, lang, mode, cfg, live),
                "achievements.svg": S.achievements(d, lang, mode, cfg, live),
                "inventory.svg": S.inventory(d, lang, mode, cfg),
                "quests-title.svg": S.quests_title(d, lang, mode, cfg),
                "quests-more.svg": S.quests_more(d, lang, mode, cfg),
                "night.svg": S.night(d, lang, mode, cfg),
                "start.svg": S.start(d, lang, mode, cfg),
            }
            if mode == "desktop":  # las tarjetas de misión valen igual para PC y móvil
                for q in [q for q in cfg["quests"] if q.get("show", True)]:
                    files[f'quest-{q["slug"]}.svg'] = S.quest(d, lang, mode, cfg, q)
            for name, content in files.items():
                write(folder / name, content)
            count += len(files)
        import html
        write(ROOT / ("README.md" if lang == "es" else "README.en.md"),
              readme(cfg, lang, False, "", cv_link(cfg, lang)))
    print(f"{count} SVG generados" + ("" if live else " (sin datos vivos: data/live.json vacío)"))
    for lang in cfg["lang"]:
        if not cv_link(cfg, lang):
            print(f"Aviso: no hay CV para '{lang}'; su botón no se muestra")


if __name__ == "__main__":
    sys.exit(build())
