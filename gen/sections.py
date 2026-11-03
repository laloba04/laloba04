"""Cada función devuelve el SVG de una sección del perfil para (idioma, formato)."""
import json
import random

from pixel import (AMBER, BG, BLUE, BORDER, GREEN, MOON, MUTED, NAMED, PANEL, PURPLE, ROOT, TXT,
                   WIDTH, fmt_int, frame, grid, rule, section, svg, t, wrap)
from sprites import big_text, big_width, BLINK_CSS, HOWL, MOON as MOON_SPRITE, SCENE_CSS, TWINKLE_CSS, girl_scene

CW = 0.6  # ancho de carácter en múltiplos del tamaño de diseño


# ---------- Portada ----------
PREFIX_COLOR = {"$": PURPLE, "✓": GREEN, "●": GREEN, "!": AMBER, ">": MUTED}


def _terminal(body, d, lang, mode, tx, ty, tw, th, fsize, lh):
    body.append(frame(tx, ty, tw, th, fill="#010409"))
    body.append(f'<rect x="{tx+4}" y="{ty+4}" width="{tw-8}" height="24" fill="{PANEL}"/>')
    for k, c in enumerate(["#f85149", "#d29922", GREEN]):
        body.append(f'<rect x="{tx+14+k*16}" y="{ty+12}" width="8" height="8" fill="{c}"/>')
    body.append(t(tx + tw / 2, ty + 21, "maria@dev: ~", 12, MUTED, anchor="middle"))
    cw = fsize * CW
    y = ty + 30 + lh
    delay = 0.3
    for i, (p, line) in enumerate(d["term"][mode]):
        is_cmd = p == "$"
        col = GREEN if is_cmd else (AMBER if p in ("!", "●") or (p == ">" and i == len(d["term"][mode]) - 1) else TXT)
        chars = len(line) + 2
        dur = max(0.4, chars * (0.06 if is_cmd else 0.02))
        cid = f"c{lang}{mode[0]}{i}"
        # el texto se "escribe": un recorte que crece de izquierda a derecha
        body.append(f'<clipPath id="{cid}"><rect x="{tx+14}" y="{y-fsize-2}" width="0" height="{fsize+8}">'
                    f'<animate attributeName="width" begin="{delay:.2f}s" '
                    f'dur="{dur:.2f}s" fill="freeze" calcMode="discrete" '
                    f'values="{";".join([str(round(k * cw + 2)) for k in range(chars + 2)] + [str(tw - 20)])}"/></rect></clipPath>')
        body.append(f'<g clip-path="url(#{cid})">'
                    + t(tx + 16, y, p, fsize, PREFIX_COLOR.get(p, MUTED))
                    + t(tx + 16 + 2 * cw, y, line, fsize, col) + '</g>')
        delay += dur + (0.45 if is_cmd else 0.18)
        y += lh
    body.append(f'<rect class="cur" x="{tx+16}" y="{y-fsize+2}" width="{cw:.0f}" height="{fsize+2}" '
                f'fill="{GREEN}" opacity="0"><set attributeName="opacity" to="1" begin="{delay:.2f}s"/></rect>')


def hero(d, lang, mode, cfg):
    w = WIDTH[mode]
    body = []
    if mode == "desktop":
        h = 300
        body.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
        stars = [(30, 30), (250, 22), (300, 270), (60, 270), (870, 20), (880, 280), (200, 285)]
        body.append(frame(24, 24, 264, 252))
        body.append(girl_scene(44, 84, 7))
        body.append(f'<g class="code">{t(196, 74, "</>", 18, GREEN)}</g>')
        body.append(t(156, 266, "@" + cfg["user"], 13, MUTED, anchor="middle"))
        _terminal(body, d, lang, mode, 312, 24, 564, 252, 16, 31)
    else:
        n = len(d["term"]["mobile"])
        th = 44 + n * 26 + 26
        h = 16 + 196 + 14 + th + 16
        body.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
        stars = [(20, 24), (70, 150), (360, 30), (400, 170), (330, 120), (40, 200)]
        body.append(frame((w - 196) / 2, 16, 196, 196))
        body.append(girl_scene((w - 160) / 2, 62, 5))
        body.append(f'<g class="code">{t(w/2 + 30, 50, "</>", 15, GREEN)}</g>')
        body.append(t(w / 2, 202, "@" + cfg["user"], 12, MUTED, anchor="middle"))
        _terminal(body, d, lang, mode, 12, 16 + 196 + 14, w - 24, th, 15, 26)
    stars_svg = "".join(f'<rect class="tw{i%3}" x="{sx}" y="{sy}" width="3" height="3" fill="{MOON}"/>'
                        for i, (sx, sy) in enumerate(stars))
    body.insert(1, stars_svg)
    # cabecera: nombre en letras pixel grandes + subtítulo
    name = cfg["name"].upper()
    if mode == "desktop":
        off, cell = 108, 6
        head = (big_text(name, 24, 18, cell, TXT) + t(24, 92, d["subtitle"], 16, MUTED))
    else:
        off, cell = 96, 4
        nx = (w - big_width(name, cell)) / 2
        head = (big_text(name, nx, 16, cell, TXT) + t(w / 2, 76, d["subtitle"], 13, MUTED, anchor="middle"))
    body = [f'<rect width="{w}" height="{h + off}" fill="{BG}"/>', head,
            f'<g transform="translate(0 {off})">'] + body[1:] + ['</g>']
    h += off
    css = (BLINK_CSS + TWINKLE_CSS + SCENE_CSS +
           ".cur{animation:cur 1s steps(1) infinite}@keyframes cur{50%{fill:transparent}}")
    return svg(w, h, "".join(body), d["hero_alt"], css)


# ---------- Botones ----------
# Bloques de color con contorno oscuro, sombra abajo-derecha e icono pixel (2 px por celda)
BTN_ICONS = {
    "play": ["#.......", "##......", "###.....", "####....", "###.....", "##......", "#......."],
    "linkedin": ["#########", "#.#######", "#########", "#.##..###", "#.#.##.##",
                 "#.#.##.##", "#.#.##.##", "#########"],
    "mail": ["###########", "##wwwwwww##", "#w#wwwww#w#", "#ww#www#ww#", "#www#w#www#",
             "#wwww#wwww#", "#wwwwwwwww#", "###########"],
    "download": ["....#....", "....#....", "....#....", "..#.#.#..", "...###...", "....#....",
                 ".........", "#.......#", "#########"],
}
BTN_ICONS["globe"] = ["..#####..", ".#..#..#.", "#########", "#..#.#..#", "#########",
                      "#..#.#..#", "#########", ".#..#..#.", "..#####.."]
BUTTON_STYLE = {  # clave: (relleno, sombra, icono) — colores de la paleta del perfil
    "portfolio": ("#f5a524", "#9a5f00", "play"),      # ámbar (ojos del lobo)
    "linkedin": ("#a371f7", "#5b2fa8", "linkedin"),   # lila (sudadera)
    "email": ("#f0e6c8", "#a39470", "mail"),          # luna
    "cv": ("#db61a2", "#8a2a5e", "download"),         # rosa (orejas del lobito)
    "lang": ("#c9d1d9", "#6e7681", "globe"),          # gris claro con globo
}
INK = "#0d1117"


def button(label, key):
    fill, shadow, icon = BUTTON_STYLE[key]
    rows = BTN_ICONS[icon]
    cell = 2
    iw = len(rows[0]) * cell
    tw = len(label) * 15 * CW
    bw = round(14 + iw + 10 + tw + 16)
    bh = 40
    w, h = bw + 4, bh + 4
    ih = len(rows) * cell
    body = [f'<rect x="4" y="4" width="{bw}" height="{bh}" fill="{shadow}"/>',            # sombra
            f'<rect x="0" y="0" width="{bw}" height="{bh}" fill="{INK}"/>',               # contorno
            f'<rect x="2" y="2" width="{bw-4}" height="{bh-4}" fill="{fill}"/>',
            f'<rect x="2" y="2" width="{bw-4}" height="2" fill="#ffffff" opacity=".35"/>',  # brillo
            f'<rect x="2" y="{bh-5}" width="{bw-4}" height="3" fill="{shadow}" opacity=".6"/>',
            grid(rows, {"#": INK, "w": "#ffffff"}, 14, (bh - ih) / 2 - 1, cell),
            t(14 + iw + 10, bh / 2 + 6, label, 15, INK)]
    return svg(w, h, "".join(body), label)


# ---------- Ficha de personaje ----------
HEART = [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."]


def _hearts(x, y, value, cell=2, total=3):
    """Corazones pixel: llenos, medio y vacíos (value admite .5)."""
    out = []
    for i in range(total):
        hx = x + i * (8 * cell)
        fill = min(max(value - i, 0), 1)
        out.append(grid(HEART, {"#": "#30363d"}, hx, y, cell))
        if fill >= 1:
            out.append(grid(HEART, {"#": "#f85149"}, hx, y, cell))
        elif fill > 0:
            out.append(grid([r[:4] for r in HEART], {"#": "#f85149"}, hx, y, cell))
    return "".join(out)


def _skill_rows(body, langs, x_label, x_bar, bar_w, x_pct, y, lang, segs, fs=14):
    top = max((l_["pct"] for l_ in langs), default=1)
    sw = bar_w / segs
    for l_ in langs:
        body.append(t(x_label, y, l_["name"].upper(), fs, TXT))
        filled = max(1, round(segs * l_["pct"] / top))
        for k in range(segs):
            col = l_["color"] if k < filled else "#21262d"
            body.append(f'<rect x="{x_bar + k*sw:.1f}" y="{y-12}" width="{sw-3:.1f}" height="13" fill="{col}"/>')
        pct = f'{l_["pct"]:.1f}'.replace(".", "," if lang == "es" else ".")
        body.append(t(x_pct, y, f"{pct} %" if lang == "es" else f"{pct}%", fs, TXT, anchor="end"))
        y += 26
    return y


def _exp(body, d, lang, live, x, y, wbar, fs=15):
    frac = min(live["active_days"] / 365, 1)
    body.append(f'<rect x="{x}" y="{y}" width="{wbar}" height="16" fill="#21262d"/>')
    body.append(f'<rect x="{x}" y="{y}" width="0" height="16" fill="{GREEN}">'
                f'<animate attributeName="width" from="0" to="{wbar*frac:.0f}" begin="0.3s" dur="1.6s" fill="freeze"/></rect>')
    body.append(f'<rect x="{x}" y="{y}" width="{wbar}" height="3" fill="#ffffff" opacity=".08"/>')
    body.append(t(x, y + 40, "EXP", fs, GREEN))
    body.append(t(x + fs * 3, y + 40, d["exp"].format(total=fmt_int(live["total"], lang), active=live["active_days"]), fs, TXT))


def sheet(d, lang, mode, cfg, live=None):
    w = WIDTH[mode]
    rows = d["sheet"]
    langs = (live or {}).get("languages", [])[:6]
    name = cfg["name"].upper()
    if mode == "desktop":
        xl, xv, maxc = 48, 210, 64
        blocks = [(k, wrap(v, maxc)) for k, v in rows]
        top = 76
        info_h = 50 + sum(26 * len(ls) for _, ls in blocks) + 34
        h = top + info_h + (80 + 34 + 26 * len(langs) if live else 0) + 30
        body, pad = section(w, h, d["sheet_title"])
        body.append(rule(48, w - 96))
        body.append(t(xl, top + 34, name, 26, TXT))
        y = top + 72
        for k, ls in blocks:
            body.append(t(xl, y, k, 14, MUTED))
            for ln in ls:
                body.append(t(xv, y, ln, 15, TXT))
                y += 26
        body.append(t(xl, y + 4, d["langs_label"], 14, MUTED))
        hx = xv
        for code, val in cfg["hearts"]:
            body.append(t(hx, y + 4, code, 15, TXT))
            body.append(_hearts(hx + 28, y - 9, val))
            hx += 120
        y = top + info_h + 6
        if live:
            _exp(body, d, lang, live, 48, y, w - 96)
            y += 84
            body.append(t(48, y, d["skills"], 17, MUTED))
            _skill_rows(body, langs, 48, 220, 500, w - 48, y + 34, lang, 20)
    else:
        x0, maxc = 30, 40
        blocks = [(k, wrap(v, maxc)) for k, v in rows]
        h = (76 + 40 + sum(20 + 20 * len(ls) + 10 for _, ls in blocks) + 70
             + (90 + 30 + 24 * len(langs) if live else 0) + 20)
        body, pad = section(w, h, d["sheet_title"])
        body.append(rule(x0, w - 2 * x0))
        body.append(t(x0, 104, name, 22, TXT))
        y = 140
        for k, ls in blocks:
            body.append(t(x0, y, k, 12, MUTED))
            y += 20
            for ln in ls:
                body.append(t(x0, y, ln, 14, TXT))
                y += 20
            y += 10
        body.append(t(x0, y, d["langs_label"], 12, MUTED))
        y += 24
        hx = x0
        for code, val in cfg["hearts"]:
            body.append(t(hx, y, code, 14, TXT))
            body.append(_hearts(hx + 26, y - 11, val))
            hx += 118
        y += 30
        if live:
            _exp(body, d, lang, live, x0, y, w - 2 * x0, fs=12)
            y += 80
            body.append(t(x0, y, d["skills"], 15, MUTED))
            _skill_rows(body, langs, x0, 140, 200, w - x0, y + 30, lang, 10, fs=12)
    alt = d["sheet_alt"]
    if live:
        alt += d["sheet_live_alt"].format(total=fmt_int(live["total"], lang), active=live["active_days"],
                                          langs=", ".join(f'{l_["name"]} {l_["pct"]} %' for l_ in langs))
    return svg(w, h, "".join(body), alt)


PAW = ["..##.##..", "..##.##..", "##.....##", "##.....##", "...###...",
       "..#####..", ".#######.", ".#######.", "..##.##.."]


def achievement_items(d, lang, live):
    """Lista de (hecho?, texto): los fijos de data/profile.json + los de datos vivos de GitHub."""
    items = [(ic == "★", txt) for ic, txt in d["ach"]]
    if live:
        lv = d["ach_live"]
        items.insert(0, (True, lv["best"].format(n=fmt_int(live["best_day"], lang))))
        if live.get("current_streak", 0) >= 2:
            items.append((True, lv["streak"].format(n=live["current_streak"])))
    return items


def achievements(d, lang, mode, cfg, live=None):
    """Logros como salida de `cat logros.log` en una terminal, con huella de lobo y estado [OK]/[WIP]."""
    w = WIDTH[mode]
    desk = mode == "desktop"
    items = achievement_items(d, lang, live)
    pad = 24 if desk else 12
    tx0, tw = pad, w - 2 * pad
    fs = 15 if desk else 12
    lh = fs + 12
    cell = 2
    tag_w = 6 * fs * CW
    text_x = tx0 + 16 + 9 * cell + 12 + tag_w
    maxc = int((tx0 + tw - 16 - text_x) / (fs * CW))
    wrapped = [(done, wrap(txt, maxc)) for done, txt in items]
    lines_h = sum(len(ls) * (fs + 6) + (lh - fs - 6) for _, ls in wrapped)
    term_top = 66
    th = 30 + lh + 10 + lines_h + lh + 14
    h = term_top + th + 22
    body, _ = section(w, h, d["ach_title"])
    body = body[:1] + body[2:]  # sin el marco de sección: la terminal hace de marco
    body.append(frame(tx0, term_top, tw, th, fill="#010409"))
    body.append(f'<rect x="{tx0+4}" y="{term_top+4}" width="{tw-8}" height="24" fill="{PANEL}"/>')
    for k, c in enumerate(["#f85149", "#d29922", GREEN]):
        body.append(f'<rect x="{tx0+14+k*16}" y="{term_top+12}" width="8" height="8" fill="{c}"/>')
    body.append(t(tx0 + tw / 2, term_top + 21, "maria@dev: ~/logros", 12, MUTED, anchor="middle"))
    y = term_top + 30 + lh
    body.append(t(tx0 + 16, y, "$", fs, PURPLE) + t(tx0 + 16 + 2 * fs * CW, y, "cat logros.log", fs, GREEN))
    y += 10
    for i, (done, ls) in enumerate(wrapped):
        y += lh
        tag, tcol = ("[OK] ", GREEN) if done else ("[WIP]", AMBER)
        g = [grid(PAW, {"#": AMBER if done else "#6e7681"}, tx0 + 16, y - 9 * cell + 1, cell),
             t(tx0 + 16 + 9 * cell + 12, y, tag, fs, tcol)]
        for k, ln in enumerate(ls):
            g.append(t(text_x, y + k * (fs + 6), ln, fs, TXT if done else "#c9d1d9"))
        body.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{0.6 + 0.35*i:.2f}s" fill="freeze"/>'
                    + "".join(g) + "</g>")
        y += (len(ls) - 1) * (fs + 6)
    y += lh
    n = len(wrapped)
    body.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{0.6 + 0.35*n:.2f}s" fill="freeze"/>'
                + t(tx0 + 16, y, "$", fs, PURPLE)
                + f'<rect class="cur" x="{tx0 + 16 + 2*fs*CW:.0f}" y="{y-fs+2}" width="{fs*CW:.0f}" height="{fs+2}" fill="{GREEN}"/></g>')
    alt = d["ach_title"].capitalize() + ": " + "; ".join(
        (txt if done else f'{txt} ({d["ach_wip"].rstrip("…").lower()})') for done, txt in items) + "."
    css = ".cur{animation:cur 1s steps(1) infinite}@keyframes cur{50%{fill:transparent}}"
    return svg(w, h, "".join(body), alt, css)


# ---------- Inventario ----------
def _pixel_icon(name, cx, top, cell):
    data = json.loads((ROOT / "gen" / "icons" / "pixel" / f"{name}.json").read_text(encoding="utf-8"))
    n = data["size"]
    s = cell * 16 / n  # todos los iconos ocupan lo mismo aunque su cuadrícula sea distinta
    return grid(data["rows"], data["palette"], round(cx - n * s / 2, 2), top, round(s, 2))


def inventory(d, lang, mode, cfg):
    w = WIDTH[mode]
    items = cfg["inventory"]
    if mode == "desktop":
        cols, cw, ch, gap, cell = 6, 124, 104, 10, 3
    else:
        cols, gap, cell = 3, 10, 3
        cw, ch = (w - 72 - 2 * gap) / 3, 100
    rows = (len(items) + cols - 1) // cols
    h = 84 + rows * (ch + 16) + 8
    body, pad = section(w, h, d["inv_title"])
    body.append(rule(pad + 24, w - 2 * pad - 48))
    x0 = (w - (cols * cw + (cols - 1) * gap)) / 2
    y0 = 84
    pos = []
    for i, (name, icon, _color) in enumerate(items):
        c, r = i % cols, i // cols
        x, y = x0 + c * (cw + gap), y0 + r * (ch + 16)
        pos.append((x, y))
        body.append(frame(x, y, cw, ch, fill="#1c2128", stroke="#2d333b", px=3))
        body.append(_pixel_icon(icon, x + cw / 2, y + 14, cell))
        body.append(t(x + cw / 2, y + ch - 16, name, 13, TXT, anchor="middle"))
    # cursor de selección que salta de casilla en casilla (como en un inventario de videojuego)
    step = 1.4
    vals = ";".join(f"{x:.1f} {y:.1f}" for x, y in pos)
    times = ";".join(f"{i/len(pos):.4f}" for i in range(len(pos)))
    arrow = grid(["######", ".####.", "..##.."], {"#": AMBER}, cw / 2 - 9, -15, 3)
    cursor = frame(0, 0, cw, ch, fill="none", stroke=AMBER, px=3) + f'<g class="bob">{arrow}</g>'
    body.append(f'<g>{cursor}<animateTransform attributeName="transform" type="translate" calcMode="discrete" '
                f'values="{vals}" keyTimes="{times}" dur="{step*len(pos):.1f}s" repeatCount="indefinite"/></g>')
    css = ".bob{animation:bob .7s steps(1) infinite}@keyframes bob{50%{transform:translateY(3px)}}"
    return svg(w, h, "".join(body), d["inv_alt"], css)


# ---------- Misiones ----------
QUEST_ICONS = {  # 12x12, '.' transparente
    "skyfence": (["....####....", "...######...", "..###..###..", "..##....##..", "..###..###..", "...######...",
                  "....####....", ".....##.....", ".....##.....", "..#..##..#..", ".#........#.", "..########.."],
                 {"#": "#f5a524"}),
    "casinoctf": (["##########..", "#wwwwwwww#..", "#w..rr..w#..", "#w.rrrr.w#..", "#wrrrrrrw#..", "#wrrrrrrw#..",
                   "#w..rr..w#..", "#w.rrrr.w#..", "#wwwwwwww#..", "##########..", "...........#", "..........##"],
                  {"#": "#db61a2", "w": "#f0e6c8", "r": "#db61a2"}),
    "secaudit": (["....####....", "..########..", ".##########.", ".###ggggg##.", ".##g####g##.", ".###g##g###.",
                  ".####gg####.", "..########..", "..########..", "...######...", "....####....", ".....##....."],
                 {"#": "#3fb950", "g": "#0d1117"}),
    "habitflow": ([".#..#..#..#.", "############", "#..........#", "#.##.##.##.#", "#.##.##.##.#", "#..........#",
                   "#.##.##..p.#", "#.##.##.pp.#", "#......pp..#", "#.pp.pp....#", "#..........#", "############"],
                  {"#": "#a371f7", "p": "#3fb950"}),
    "control-acceso-ble": (["...####.....", "..#....#....", "..#....#....", "..#....#....", ".########...", ".##bbbb##...",
                            ".#b#bb#b#...", ".#bb##bb#...", ".#b#bb#b#...", ".##bbbb##...", ".########...", "............"],
                           {"#": "#58a6ff", "b": "#c9d1d9"}),
    "rag-notas": (["#######.....", "#wwwww##....", "#w...w#w#...", "#wwwww#ww#..", "#w....###...", "#wwww#ooo#..",
                   "#w..#o...o#.", "#www#o...o#.", "#w..#o...o#.", "####.#ooo##.", ".......#####", "........###."],
                  {"#": "#f0e6c8", "w": "#30363d", "o": "#f5a524"}),
}
STAR = ["...#...", "...#...", "#######", ".#####.", "..###..", ".##.##.", "##...##"]
CARD_W = 412


def quests_title(d, lang, mode, cfg):
    w = WIDTH[mode]
    h = 64
    pad = 24 if mode == "desktop" else 12
    body = [f'<rect width="{w}" height="{h}" fill="{BG}"/>',
            frame(pad, 8, w - 2 * pad, h - 16, fill=PANEL, stroke=BORDER),
            t(pad + 24, 41, "▸ " + d["quests_title"], 18 if mode == "desktop" else 16, AMBER)]
    return svg(w, h, "".join(body), d["quests_title"])


def quest(d, lang, mode, cfg, q):
    """Tarjeta de misión. Mide 412 px: en PC caben dos por fila y en móvil ocupa todo el ancho."""
    w, h = CARD_W, 200
    color = NAMED[q["color"]]
    lines = wrap(q[lang], 42)[:2]
    body = [f'<rect width="{w}" height="{h}" fill="{BG}"/>',
            f'<rect x="2" y="2" width="{w-4}" height="{h-4}" fill="none" stroke="{color}" stroke-width="3"/>',
            f'<rect x="9" y="9" width="{w-18}" height="{h-18}" fill="{PANEL}" stroke="{color}" stroke-width="2" opacity="1"/>']
    rows, pal = QUEST_ICONS[q["slug"]]
    body.append(grid(rows, pal, 26, 26, 3))
    body.append(t(72, 50, q["name"], 19, color))
    if q.get("featured"):
        body.append(grid(STAR, {"#": "#f5a524"}, 72 + len(q["name"]) * 19 * CW + 10, 36, 2))
    y = 92
    for ln in lines:
        body.append(t(26, y, ln, 14, TXT))
        y += 22
    body.append(t(26, 146, q["stack"], 12, MUTED))
    label = d["status"][q["status"]]
    dot = GREEN if q["status"] == "done" else AMBER
    cw_ = 26 + len(label) * 13 * CW + 16
    body.append(f'<rect x="26" y="158" width="{cw_:.0f}" height="26" fill="#21262d"/>')
    body.append(f'<rect x="34" y="166" width="10" height="10" fill="{dot}"/>')
    body.append(t(52, 176, label, 13, TXT))
    return svg(w, h, "".join(body), f'{q["name"]} — {q[lang]} ({q["stack"]}). {label}.')


def quests_more(d, lang, mode, cfg):
    w = WIDTH[mode]
    pad = 24 if mode == "desktop" else 12
    n = cfg.get("more_quests")
    txt = d["quest_more_n"].format(n=n) if n else d["quest_more"]
    h = 56
    body = [f'<rect width="{w}" height="{h}" fill="{BG}"/>',
            frame(pad, 6, w - 2 * pad, h - 12, fill=PANEL, stroke=BORDER),
            grid(["#...", "##..", "###.", "####", "###.", "##..", "#..."], {"#": GREEN}, w / 2 - len(txt) * 13 * CW / 2 - 18, 21, 2),
            t(w / 2 + 6, 34, txt, 14 if mode == "desktop" else 13, BLUE, anchor="middle")]
    return svg(w, h, "".join(body), txt)


# ---------- Escena nocturna ----------
def night(d, lang, mode, cfg):
    w = WIDTH[mode]
    desk = mode == "desktop"
    h = 280 if desk else 240
    ground = h - 30
    body = ['<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#05070d"/><stop offset="1" stop-color="#16213a"/></linearGradient></defs>',
            f'<rect width="{w}" height="{h}" fill="url(#sky)"/>']
    rnd = random.Random(4)
    for i in range(55 if desk else 30):
        x, y = rnd.randrange(0, w, 3), rnd.randrange(4, h - 110, 3)
        body.append(f'<rect class="tw{i%4}" x="{x}" y="{y}" width="{rnd.choice([2, 2, 3])}" '
                    f'height="{rnd.choice([2, 2, 3])}" fill="{MOON}"/>')
    s = 6 if desk else 5
    mx, my = (730, 30) if desk else (w - 96, 22)
    r = 6 * s
    body.append(f'<circle cx="{mx+r}" cy="{my+r}" r="{r+26}" fill="{MOON}" opacity=".07"/>')
    body.append(f'<circle cx="{mx+r}" cy="{my+r}" r="{r+12}" fill="{MOON}" opacity=".08"/>')
    body.append(grid(MOON_SPRITE, {"#": MOON}, mx, my, s))
    for cx, cy in [(4, 3), (7, 6), (3, 8)]:
        body.append(f'<rect x="{mx+cx*s}" y="{my+cy*s}" width="{2*s}" height="{2*s}" fill="#d9cba4"/>')
    k = w / 900
    pts = [(0, 200), (90, 150), (160, 185), (260, 120), (360, 190), (460, 140), (560, 195),
           (690, 135), (800, 185), (900, 150)]
    off = 0 if desk else -40
    body.append(f'<path d="M{" L".join(f"{x*k:.0f} {y+off}" for x, y in pts)} V{h} H0Z" fill="#1c2742"/>')
    ws, gs = (6, 4) if desk else (5, 3)
    rx = 600 if desk else w - 190
    rock_top = ground - 28
    body.append(f'<path d="M{rx-20} {h} L{rx} {rock_top+16} L{rx+40} {rock_top} '
                f'L{rx+100} {rock_top+4} L{rx+130} {rock_top+26} L{rx+150} {h}Z" fill="#141c2c"/>')
    rnd2 = random.Random(7)
    for x in range(10, w, 34 if desk else 30):
        if rx - 10 < x < rx + 150:
            continue
        hh = rnd2.choice([60, 72, 84, 96] if desk else [48, 60, 72])
        base = ground - rnd2.randrange(0, 12, 3)
        for kk in range(hh // 12):
            wd = 6 + kk * 6
            body.append(f'<rect x="{x-wd/2}" y="{base-hh+kk*12}" width="{wd}" height="12" fill="#0f1a2c"/>')
        body.append(f'<rect x="{x-3}" y="{base}" width="6" height="10" fill="#2b1d14"/>')
    wy = rock_top + 6 - len(HOWL) * ws
    body.append(grid(HOWL, {"#": "#05070d"}, rx + 10, wy, ws))
    body.append(f'<g class="howl">{t(rx + 10 + 4 * ws, wy + 2 * ws, d["howl"], 16 if desk else 14, MOON, anchor="end")}</g>')
    body.append(f'<rect y="{ground}" width="{w}" height="30" fill="#070b14"/>')
    for x in range(0, w, 12):
        body.append(f'<rect x="{x}" y="{ground}" width="6" height="3" fill="#0f1a2c"/>')
    css = (TWINKLE_CSS + SCENE_CSS +
           ".howl{opacity:0;animation:howl 6s steps(1) infinite}"
           "@keyframes howl{0%,40%{opacity:0}45%,85%{opacity:1}90%,100%{opacity:0}}")
    return svg(w, h, "".join(body), d["night_alt"], css)


# ---------- Pulsa start ----------
def start(d, lang, mode, cfg):
    w = WIDTH[mode]
    email = cfg["links"]["email"]
    h = 120 if mode == "desktop" else 110
    body = [f'<rect width="{w}" height="{h}" fill="{BG}"/>',
            f'<g class="bl">{t(w/2, 48, "▶ " + d["start"] + " ◀", 22 if mode == "desktop" else 14, AMBER, anchor="middle")}</g>',
            t(w / 2, 84, email, 16 if mode == "desktop" else 14, TXT, anchor="middle")]
    css = ".bl{animation:bl 1.2s steps(1) infinite}@keyframes bl{50%{opacity:0}}"
    return svg(w, h, "".join(body), d["start_alt"].format(email=email), css)


