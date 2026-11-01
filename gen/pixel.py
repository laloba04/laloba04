"""Núcleo pixel: paleta, fuente incrustada y utilidades para dibujar SVG."""
import base64
import pathlib
import re
from xml.sax.saxutils import escape as esc

ROOT = pathlib.Path(__file__).resolve().parents[1]

# ---------- Paleta "noche de lobo" ----------
BG = "#0d1117"
PANEL = "#161b22"
CARD = "#0b0f14"
BORDER = "#30363d"
TXT = "#e6edf3"
MUTED = "#8b949e"
AMBER = "#f5a524"
MOON = "#f0e6c8"
GREEN = "#3fb950"
PURPLE = "#a371f7"
BLUE = "#58a6ff"
PINK = "#db61a2"
NAMED = {"amber": AMBER, "moon": MOON, "green": GREEN, "purple": PURPLE, "blue": BLUE, "pink": PINK}

WIDTH = {"desktop": 900, "mobile": 420}

# ---------- Fuente pixel ----------
# VT323 tiene un ancho de 0,4 em; las medidas del diseño están pensadas para 0,6 em,
# así que el tamaño se multiplica por 1,5 y los anchos cuadran con cualquier texto.
FONT_FILE = ROOT / "fonts" / "vt323-pixel.woff2"
FONT_CHARS = set((ROOT / "fonts" / "vt323-pixel.chars").read_text(encoding="utf-8"))
FONT_SCALE = 1.5
FALLBACK = "'DejaVu Sans Mono', 'Segoe UI Symbol', 'Courier New', monospace"
_FONT_B64 = base64.b64encode(FONT_FILE.read_bytes()).decode()
FONT_CSS = (f"@font-face{{font-family:px;src:url(data:font/woff2;base64,{_FONT_B64}) format('woff2');}}"
            f"text{{font-family:px,{FALLBACK};}}.sym{{font-family:{FALLBACK};}}")


def svg(w, h, body, title, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}" shape-rendering="crispEdges">'
            f'<title>{esc(title)}</title><style>{FONT_CSS}{style}</style>{body}</svg>')


def _runs(s):
    """Separa el texto en tramos que la fuente pixel tiene y tramos de símbolos de reserva."""
    out, cur, cur_px = [], "", None
    for ch in s:
        px = ch in FONT_CHARS
        if cur and px != cur_px:
            out.append((cur, cur_px))
            cur = ""
        cur += ch
        cur_px = px
    if cur:
        out.append((cur, cur_px))
    return out


def t(x, y, s, size=14, fill=TXT, anchor="start", extra=""):
    """Texto en fuente pixel. `size` es el tamaño de diseño (equivalente a monoespaciada 0,6 em)."""
    px_size = round(size * FONT_SCALE, 1)
    parts = []
    for run, is_px in _runs(s):
        if is_px:
            parts.append(esc(run))
        else:
            # los símbolos de reserva miden ~0,6 em: se reduce su tamaño para no descuadrar
            parts.append(f'<tspan class="sym" font-size="{size}">{esc(run)}</tspan>')
    return (f'<text x="{x}" y="{y}" font-size="{px_size}" fill="{fill}" '
            f'text-anchor="{anchor}" xml:space="preserve" {extra}>{"".join(parts)}</text>')


def frame(x, y, w, h, fill=PANEL, stroke=BORDER, px=4):
    """Marco pixelado con esquinas recortadas."""
    p = px
    return (f'<path d="M{x+p} {y}h{w-2*p}v{p}h{p}v{h-2*p}h-{p}v{p}h-{w-2*p}v-{p}h-{p}v-{h-2*p}h{p}z" '
            f'fill="{fill}"/>'
            f'<path d="M{x+p} {y}h{w-2*p}M{x+w-p} {y+p}h{p}M{x+w} {y+p}v{h-2*p}M{x+w-p} {y+h-p}h{p}'
            f'M{x+p} {y+h}h{w-2*p}M{x} {y+p}v{h-2*p}M{x} {y+p}h{p}M{x} {y+h-p}h{p}" '
            f'stroke="{stroke}" stroke-width="{p}" fill="none"/>')


def grid(rows, palette, x0, y0, s):
    """Convierte un sprite ASCII (lista de cadenas) en rectángulos SVG."""
    out = []
    for j, row in enumerate(rows):
        for i, c in enumerate(row):
            if c in palette:
                out.append(f'<rect x="{x0+i*s}" y="{y0+j*s}" width="{s}" height="{s}" fill="{palette[c]}"/>')
    return "<g>" + "".join(out) + "</g>"


def mirror(half):
    return [r + r[::-1] for r in half]


def wrap(text, maxc):
    words, lines, cur = text.split(" "), [], ""
    for w_ in words:
        if cur and len(cur) + 1 + len(w_) > maxc:
            lines.append(cur)
            cur = w_
        else:
            cur = f"{cur} {w_}" if cur else w_
    if cur:
        lines.append(cur)
    return lines


def section(w, h, title):
    """Fondo + marco + título de sección. Devuelve (partes, margen)."""
    pad = 24 if w > 500 else 12
    return [f'<rect width="{w}" height="{h}" fill="{BG}"/>',
            frame(pad, 10, w - 2 * pad, h - 20),
            t(pad + 24, 46, "▸ " + title, 18 if w > 500 else 16, AMBER)], pad


def rule(x, w):
    return f'<rect x="{x}" y="58" width="{w}" height="4" fill="{BORDER}"/>'


_icon_n = [0]


def logo(name, x, y, size):
    """Incrusta un logotipo de gen/icons/<name>.svg como <svg> anidado, con ids únicos."""
    raw = (ROOT / "gen" / "icons" / f"{name}.svg").read_text(encoding="utf-8")
    raw = re.sub(r"<\?xml[^>]*>", "", raw)
    vb = re.search(r'viewBox="([^"]+)"', raw).group(1)
    inner = re.sub(r"^.*?<svg[^>]*>", "", raw, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner.strip())
    _icon_n[0] += 1
    pre = f"i{_icon_n[0]}_"
    for i in re.findall(r'id="([^"]+)"', inner):
        inner = (inner.replace(f'id="{i}"', f'id="{pre}{i}"')
                 .replace(f"url(#{i})", f"url(#{pre}{i})")
                 .replace(f'href="#{i}"', f'href="#{pre}{i}"'))
    return (f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{vb}" '
            f'shape-rendering="geometricPrecision">{inner}</svg>')


def fmt_int(n, lang):
    s = f"{n:,}"
    return s.replace(",", ".") if lang == "es" else s
