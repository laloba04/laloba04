"""Cada función devuelve el SVG de una sección del perfil para (idioma, formato)."""
import json
import random

from pixel import (AMBER, BG, BLUE, BORDER, CARD, GREEN, MOON, MUTED, NAMED, PANEL, PURPLE, ROOT, TXT,
                   WIDTH, fmt_int, frame, grid, rule, section, svg, t, wrap)
from sprites import BLINK_CSS, HOWL, MOON as MOON_SPRITE, SCENE_CSS, TWINKLE_CSS, girl_head, girl_scene

CW = 0.6  # ancho de carácter en múltiplos del tamaño de diseño


# ---------- Portada ----------
PREFIX_COLOR = {"$": PURPLE, "✓": GREEN, "!": AMBER, ">": MUTED}


def _terminal(body, d, lang, mode, tx, ty, tw, th, fsize, lh):
    body.append(frame(tx, ty, tw, th, fill="#010409"))
    body.append(f'<rect x="{tx+4}" y="{ty+4}" width="{tw-8}" height="24" fill="{PANEL}"/>')
    for k, c in enumerate(["#f85149", "#d29922", GREEN]):
        body.append(f'<rect x="{tx+14+k*16}" y="{ty+12}" width="8" height="8" fill="{c}"/>')
    body.append(t(tx + tw / 2, ty + 21, "maria@lobera: ~", 12, MUTED, anchor="middle"))
    cw = fsize * CW
    y = ty + 30 + lh
    delay = 0.3
    for i, (p, line) in enumerate(d["term"][mode]):
        is_cmd = p == "$"
        col = GREEN if is_cmd else (AMBER if p == "!" else TXT)
        chars = len(line) + 2
        dur = max(0.4, chars * (0.06 if is_cmd else 0.02))
        cid = f"c{lang}{mode[0]}{i}"
        # el texto se "escribe": un recorte que crece de izquierda a derecha
        body.append(f'<clipPath id="{cid}"><rect x="{tx+14}" y="{y-fsize-2}" width="0" height="{fsize+8}">'
                    f'<animate attributeName="width" begin="{delay:.2f}s" '
                    f'dur="{dur:.2f}s" fill="freeze" calcMode="discrete" '
                    f'values="{";".join(str(round(k * cw + 2)) for k in range(chars + 2))}"/></rect></clipPath>')
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
    "lang": [".....#...", ".....##..", "########.", ".....##..", ".....#...", ".........",
             "...#.....", "..##.....", ".########", "..##.....", "...#....."],
}
BUTTON_STYLE = {  # clave: (relleno, sombra, icono) — colores de la paleta del perfil
    "portfolio": ("#f5a524", "#9a5f00", "play"),      # ámbar (ojos del lobo)
    "linkedin": ("#a371f7", "#5b2fa8", "linkedin"),   # lila (sudadera)
    "email": ("#f0e6c8", "#a39470", "mail"),          # luna
    "cv": ("#db61a2", "#8a2a5e", "download"),         # rosa (orejas del lobito)
    "lang": ("#8b949e", "#484f58", "lang"),           # gris lobo
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
def _xp_bar(body, x, y, wbar, label_x=None, label_y=None):
    seg = wbar / 10
    body.append(f'<rect x="{x}" y="{y-12}" width="{wbar}" height="16" fill="{BORDER}"/>')
    body.append(f'<rect x="{x}" y="{y-12}" width="0" height="16" fill="{AMBER}">'
                f'<animate attributeName="width" from="0" to="{seg*3.5:.0f}" begin="0.4s" dur="1.6s" fill="freeze"/></rect>')
    for i in range(1, 10):
        body.append(f'<rect x="{x+i*seg:.0f}" y="{y-12}" width="2" height="16" fill="{BG}"/>')
    body.append(t(label_x if label_x is not None else x + wbar + 14,
                  label_y if label_y is not None else y + 2, "JUNIOR → ???", 14, AMBER))


def sheet(d, lang, mode, cfg):
    w = WIDTH[mode]
    rows = d["sheet"]
    if mode == "desktop":
        h = 70 + len(rows) * 34 + 62
        body, pad = section(w, h, d["sheet_title"])
        body.append(rule(48, w - 200))
        body.append(girl_head(w - 48 - 14 * 5, 14, 5))
        y = 94
        for k, v in rows:
            body.append(t(48, y, k, 14, MUTED))
            body.append(t(210, y, v, 15, TXT))
            y += 34
        body.append(t(48, y + 2, "XP", 14, MUTED))
        _xp_bar(body, 210, y, 400)
    else:
        x0, maxc = 36, 38
        blocks = [(k, wrap(v, maxc)) for k, v in rows]
        h = 80 + sum(20 + 20 * len(ls) + 12 for _, ls in blocks) + 86
        body, pad = section(w, h, d["sheet_title"])
        body.append(rule(x0, w - 2 * x0 - 70))
        body.append(girl_head(w - x0 - 14 * 4, 14, 4))
        y = 92
        for k, ls in blocks:
            body.append(t(x0, y, k, 12, MUTED))
            y += 20
            for ln in ls:
                body.append(t(x0, y, ln, 14, TXT))
                y += 20
            y += 12
        body.append(t(x0, y, "XP", 12, MUTED))
        _xp_bar(body, x0, y + 24, w - 2 * x0, label_x=x0, label_y=y + 50)
    return svg(w, h, "".join(body), d["sheet_alt"])


# ---------- Puntuación (datos vivos de GitHub) ----------
def stats(d, lang, mode, cfg, live):
    w = WIDTH[mode]
    desk = mode == "desktop"
    values = [live["total"], live["active_days"], live["current_streak"], live["longest_streak"]]
    langs = live.get("languages", [])[:6]
    cols = 4 if desk else 2
    box_h = 84
    nrows = 4 // cols
    legend_rows = (len(langs) + (2 if desk else 1)) // (3 if desk else 2)
    h = 80 + nrows * (box_h + 12) + 40 + 26 + legend_rows * 22 + 40
    body, pad = section(w, h, d["stats_title"])
    x_in = pad + 24
    body.append(rule(x_in, w - 2 * x_in))
    gap = 12
    bw = (w - 2 * x_in - (cols - 1) * gap) / cols
    for i, (label, val) in enumerate(zip(d["stats_labels"], values)):
        c, r = i % cols, i // cols
        x, y = x_in + c * (bw + gap), 76 + r * (box_h + 12)
        body.append(frame(x, y, bw, box_h, fill=CARD, stroke=BORDER, px=3))
        num = fmt_int(val, lang) + (f" {d['stats_days']}" if i >= 2 else "")
        body.append(t(x + bw / 2, y + 40, num, 22 if desk else 20, AMBER, anchor="middle"))
        body.append(t(x + bw / 2, y + 62, label, 11, TXT, anchor="middle"))
        if i == 0:
            body.append(t(x + bw / 2, y + 76, d["stats_sub"], 10, MUTED, anchor="middle"))
    y = 76 + nrows * (box_h + 12) + 18
    body.append(t(x_in, y, d["stats_langs"], 12, MUTED))
    y += 14
    barw = w - 2 * x_in
    total = sum(l_["pct"] for l_ in langs) or 1
    xx = x_in
    for l_ in langs:
        seg = barw * l_["pct"] / total
        body.append(f'<rect x="{xx:.1f}" y="{y}" width="{seg:.1f}" height="14" fill="{l_["color"]}"/>')
        xx += seg
    for i in range(1, int(barw // 8)):
        body.append(f'<rect x="{x_in + i*8}" y="{y}" width="1" height="14" fill="{BG}" opacity=".35"/>')
    y += 36
    per = 3 if desk else 2
    colw = barw / per
    for i, l_ in enumerate(langs):
        c, r = i % per, i // per
        lx, ly = x_in + c * colw, y + r * 22
        body.append(f'<rect x="{lx}" y="{ly-10}" width="10" height="10" fill="{l_["color"]}"/>')
        pct = f'{l_["pct"]:.1f}'.replace(".", "," if lang == "es" else ".")
        body.append(t(lx + 18, ly, f'{l_["name"]} {pct} %' if lang == "es" else f'{l_["name"]} {pct}%', 13, TXT))
    y += legend_rows * 22 + 6
    body.append(t(w - x_in, y, f'{d["stats_updated"]}: {live["updated"]}', 11, MUTED, anchor="end"))
    alt = d["stats_alt"].format(total=fmt_int(values[0], lang), active=values[1], current=values[2],
                                longest=values[3], langs=", ".join(l_["name"] for l_ in langs))
    return svg(w, h, "".join(body), alt)


# ---------- Logros ----------
def achievements(d, lang, mode, cfg):
    w = WIDTH[mode]
    items = d["ach"]
    cols, cardw, fs, rowh = (2, 392, 13, 46) if mode == "desktop" else (1, w - 72, 12, 44)
    nrows = (len(items) + cols - 1) // cols
    h = 80 + nrows * rowh + 24
    body, pad = section(w, h, d["ach_title"])
    x_start = pad + 24
    body.append(rule(x_start, w - 2 * x_start))
    for i, (ic, txt) in enumerate(items):
        col, row = i % cols, i // cols
        x = x_start + col * (cardw + 20)
        y = 96 + row * rowh
        c = AMBER if ic == "★" else MUTED
        body.append(f'<g class="pop" style="animation-delay:{0.25*i:.2f}s">'
                    + frame(x, y - 22, cardw, 36, fill=CARD, stroke=BORDER, px=2)
                    + t(x + 12, y + 2, ic, 16, c) + t(x + 34, y + 1, txt, fs, TXT) + '</g>')
    css = ".pop{opacity:0;animation:pop .4s steps(2) forwards}@keyframes pop{to{opacity:1}}"
    return svg(w, h, "".join(body), d["ach_alt"], css)


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
def quests_title(d, lang, mode, cfg):
    w = WIDTH[mode]
    h = 60
    pad = 24 if mode == "desktop" else 12
    tw_ = len(d["quests_title"]) * 14 + 70
    body = [f'<rect width="{w}" height="{h}" fill="{BG}"/>',
            f'<rect x="{pad}" y="28" width="{w-2*pad}" height="4" fill="{BORDER}"/>',
            f'<rect x="{(w-tw_)/2}" y="12" width="{tw_}" height="36" fill="{BG}"/>',
            t(w / 2, 38, "⚔ " + d["quests_title"] + " ⚔", 22 if mode == "desktop" else 20, AMBER, anchor="middle")]
    return svg(w, h, "".join(body), d["quests_title"])


def quest(d, lang, mode, cfg, q):
    w = WIDTH[mode]
    pad = 24 if mode == "desktop" else 12
    desc, color = q[lang], NAMED[q["color"]]
    label = d["status"][q["status"]]
    stc = GREEN if q["status"] == "done" else AMBER
    lw = len(label) * 12 * CW + 22
    lines = [desc] if mode == "desktop" else wrap(desc, 40)
    h = 112 if mode == "desktop" else 100 + 20 * len(lines)
    cw_ = w - 2 * pad
    body = [f'<rect width="{w}" height="{h}" fill="{BG}"/>',
            frame(pad, 4, cw_, h - 8, fill=PANEL, stroke=color),
            f'<rect x="{pad+4}" y="8" width="8" height="{h-16}" fill="{color}" opacity=".5"/>',
            t(pad + 28, 40, q["name"], 20, color),
            frame(pad + cw_ - 16 - lw, 20, lw, 26, fill=BG, stroke=stc, px=2),
            t(pad + cw_ - 16 - lw / 2, 38, label, 12, stc, anchor="middle")]
    y = 68
    for ln in lines:
        body.append(t(pad + 28, y, ln, 14, TXT))
        y += 20
    body.append(t(pad + 28, y + 6, q["stack"], 12, MUTED))
    return svg(w, h, "".join(body), f'{q["name"]} — {desc} ({q["stack"]})')


def quests_more(d, lang, mode, cfg):
    w = WIDTH[mode]
    pad = 24 if mode == "desktop" else 12
    txt = d["quest_more"] if mode == "desktop" else d["quest_more_m"]
    h = 56
    body = [f'<rect width="{w}" height="{h}" fill="{BG}"/>',
            frame(pad, 6, w - 2 * pad, h - 12, fill=PANEL, stroke=BORDER),
            t(w / 2, 34, "» " + txt + " «", 14 if mode == "desktop" else 13, TXT, anchor="middle")]
    return svg(w, h, "".join(body), d["quest_more"])


# ---------- Escena nocturna ----------
def night(d, lang, mode, cfg):
    w = WIDTH[mode]
    desk = mode == "desktop"
    h = 280 if desk else 240
    ground = h - 30
    body = [f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#05070d"/><stop offset="1" stop-color="#16213a"/></linearGradient></defs>',
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
    body.append(f'<path d="M{rx-130} {h} L{rx-110} {rock_top+10} L{rx-40} {rock_top} L{rx+40} {rock_top} '
                f'L{rx+100} {rock_top+4} L{rx+130} {rock_top+26} L{rx+150} {h}Z" fill="#141c2c"/>')
    rnd2 = random.Random(7)
    for x in range(10, w, 34 if desk else 30):
        if rx - 130 < x < rx + 150:
            continue
        hh = rnd2.choice([60, 72, 84, 96] if desk else [48, 60, 72])
        base = ground - rnd2.randrange(0, 12, 3)
        for kk in range(hh // 12):
            wd = 6 + kk * 6
            body.append(f'<rect x="{x-wd/2}" y="{base-hh+kk*12}" width="{wd}" height="12" fill="#0f1a2c"/>')
        body.append(f'<rect x="{x-3}" y="{base}" width="6" height="10" fill="#2b1d14"/>')
    wy = rock_top + 6 - len(HOWL) * ws
    body.append(grid(HOWL, {"#": "#05070d"}, rx + 10, wy, ws))
    body.append(girl_scene(rx - 105, rock_top - 20 * gs + 2, gs, silhouette="#05070d", pup=False))
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


