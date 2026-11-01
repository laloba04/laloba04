"""Tests del generador. Ejecutar con:  pytest -q"""
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gen"))
sys.path.insert(0, str(ROOT / "tools"))

import fetch_live  # noqa: E402
import pixel  # noqa: E402
import validate  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def built():
    subprocess.run([sys.executable, str(ROOT / "gen" / "build.py")], check=True)


def test_validator_passes():
    assert validate.check() == []


def test_both_languages_have_same_structure():
    cfg = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
    es, en = cfg["lang"]["es"], cfg["lang"]["en"]
    assert set(es) == set(en)
    for key in ("sheet", "ach", "stats_labels"):
        assert len(es[key]) == len(en[key]), key
    for q in cfg["quests"]:
        assert q["es"] and q["en"], q["slug"]


def test_every_inventory_icon_has_pixel_sprite():
    cfg = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
    for _name, icon, _color in cfg["inventory"]:
        sprite = json.loads((ROOT / "gen" / "icons" / "pixel" / f"{icon}.json").read_text())
        assert len(sprite["rows"]) == sprite["size"]
        used = set("".join(sprite["rows"])) - {"."}
        assert used <= set(sprite["palette"]), icon


def test_mobile_lines_fit():
    """En móvil ninguna línea de la terminal se sale del marco."""
    cfg = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
    for lang, d in cfg["lang"].items():
        for _p, line in d["term"]["mobile"]:
            assert len(line) <= 36, (lang, line)


def test_wrap():
    assert pixel.wrap("uno dos tres cuatro", 8) == ["uno dos", "tres", "cuatro"]


def test_number_format():
    assert pixel.fmt_int(5022, "es") == "5.022"
    assert pixel.fmt_int(5022, "en") == "5,022"


def test_text_runs_split_symbols_from_pixel_font():
    runs = pixel._runs("★ Hola")
    assert runs[0] == ("★", False)
    assert runs[-1][1] is True


def test_streaks():
    days = [("2026-01-01", 1), ("2026-01-02", 2), ("2026-01-03", 0),
            ("2026-01-04", 3), ("2026-01-05", 1), ("2026-01-06", 0)]
    # hoy (06) aún sin contribuciones: la racha actual cuenta hasta ayer
    assert fetch_live.streaks(days, "2026-01-06") == (2, 2, 4)
    assert fetch_live.streaks(days[:3], "2026-01-03") == (2, 2, 2)


def test_languages_skip_profile_repo():
    repos = [
        {"name": "laloba04", "languages": {"edges": [{"size": 999, "node": {"name": "Python", "color": "#3572A5"}}]}},
        {"name": "app", "languages": {"edges": [{"size": 75, "node": {"name": "Java", "color": "#b07219"}},
                                                {"size": 25, "node": {"name": "CSS", "color": None}}]}},
    ]
    langs = fetch_live.languages(repos, skip="laloba04")
    assert [l_["name"] for l_ in langs] == ["Java", "CSS"]
    assert langs[0]["pct"] == 75.0
    assert langs[1]["color"] == "#8b949e"
