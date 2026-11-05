"""Sprites en ASCII: cada letra es un color de la paleta y '.' es transparente."""
from pixel import AMBER, BG, PURPLE, grid

# ---------- Chica ----------
GIRL = [
    "....HHHHHH....",
    "..HHHHHHHHHH..",
    ".HHhHHHHHHHHH.",
    ".HHHHHSSHHHHH.",
    ".HHSSSSSSSSHH.",
    "HHSSSSSSSSSSHH",
    "HHSESSSSSSESHH",
    "HHSSSSSSSSSSHH",
    "HHSBSSSSSSBSHH",
    "HHSSSSMMSSSSHH",
    "HH.SSSSSSSS.HH",
    "HH..sSSSSs..HH",
    "HHTTTTSSTTTTHH",
    "HTTTTTTTTTTTTH",
    ".TTTTTTTTTTTT.",
]
SKIN = "#f1c6a0"
GIRL_PAL = {"H": "#16131a", "h": "#3b3442", "S": SKIN, "s": "#d9a27c", "E": "#1b1f24",
            "B": "#e8908a", "M": "#b5535a", "T": PURPLE}

# ---------- Portátil (Y = logo de lobo) ----------
LAPTOP = [
    "AAAAAAAAAAAAAAAAAA",
    "ACCCCCCCCCCCCCCCCA",
    "ACCCCCCCYCCYCCCCCA",
    "ACCCCCCCYYYYCCCCCA",
    "ACCCCCCCCYYCCCCCCA",
    "ACCCCCCCCCCCCCCCCA",
    "ACCCCCCCCCCCCCCCCA",
    "AAAAAAAAAAAAAAAAAA",
]
LAPTOP_PAL = {"A": "#484f58", "C": "#6e7681"}

# ---------- Lobito ----------
PUP = [
    "D......D.",
    "DD....DD.",
    "DPDDDDPD.",
    "DGGGGGGD.",
    "GKGGGGKG.",
    "GGLLLLGG.",
    ".GLNNLG..",
    "..LLLL...",
    ".GGLLGG.G",
    "GGGLLGGGG",
    "GGGLLGGG.",
    "GG.LL.GG.",
]
PUP_PAL = {"D": "#484f58", "G": "#8b949e", "L": "#d0d7de", "P": "#c77d9a", "K": BG, "N": BG}

# ---------- Lobo aullando (silueta) ----------
HOWL = [
    ".................##.....",
    "................###.....",
    "...............####.....",
    "..........#...####......",
    "..........##.#####......",
    "..........########......",
    "...........#######......",
    "...........######.......",
    "...........######.......",
    "..........#######.......",
    "..........#######.......",
    ".........########.......",
    "........#########.......",
    ".......##########.......",
    "......###########.......",
    ".....############.......",
    ".....############.......",
    "....#############.......",
    "....##########.##.......",
    "....#########..##.......",
    "....########...##.......",
    "...#########...##.......",
    "..##########..###.......",
    "####.######...###.......",
    "###..#####...####.......",
]

MOON = [
    "...######...", ".##########.", "############", "####..######",
    "####..######", "############", "#######..###", "#######..###",
    "############", "############", ".##########.", "...######...",
]

# ---------- Animaciones CSS ----------
BLINK_CSS = (".blink{opacity:0;animation:blink 5s steps(1) infinite}"
             ".blink2{opacity:0;animation:blink 6s steps(1) infinite 2s}"
             "@keyframes blink{0%,93%{opacity:0}94%,97%{opacity:1}98%,100%{opacity:0}}")
TWINKLE_CSS = (".tw0{animation:tw 3s steps(1) infinite}.tw1{animation:tw 4s steps(1) infinite 1s}"
               ".tw2{animation:tw 5s steps(1) infinite 2s}.tw3{animation:tw 6s steps(1) infinite .5s}"
               "@keyframes tw{50%{opacity:.15}}")
SCENE_CSS = (".glow{animation:glow 2.4s ease-in-out infinite}@keyframes glow{50%{opacity:.45}}"
             ".code{animation:code 3s steps(3) infinite}@keyframes code{0%{opacity:0;transform:translateY(6px)}"
             "50%{opacity:1}100%{opacity:0;transform:translateY(-10px)}}")


def girl_scene(x0, y0, s, silhouette=None, anim=True, pup=True):
    """Chica con portátil y lobito sentado al lado. Ocupa 32 x 21 celdas de tamaño s."""
    def pal(p):
        return {k: silhouette for k in p} if silhouette else p

    out = []
    gx, gy = x0 + 4 * s, y0
    out.append(grid(GIRL, pal(GIRL_PAL), gx, gy, s))
    if anim and not silhouette:
        out.append(f'<g class="blink"><rect x="{gx+3*s}" y="{gy+6*s}" width="{s}" height="{s}" fill="{SKIN}"/>'
                   f'<rect x="{gx+10*s}" y="{gy+6*s}" width="{s}" height="{s}" fill="{SKIN}"/></g>')
    lx, ly = x0 + 2 * s, y0 + 11 * s
    out.append(grid(LAPTOP, pal(LAPTOP_PAL), lx, ly, s))
    logo = [r.replace("A", ".").replace("C", ".") for r in LAPTOP]
    if silhouette:
        out.append(f'<circle cx="{lx+10*s}" cy="{ly+3.5*s}" r="{2.5*s}" fill="{AMBER}" opacity=".15"/>')
    out.append(f'<g class="{"glow" if anim else ""}">' + grid(logo, {"Y": AMBER}, lx, ly, s) + '</g>')
    out.append(f'<rect x="{x0}" y="{ly+8*s}" width="{22*s}" height="{s}" fill="{silhouette or "#30363d"}"/>')
    if not silhouette:  # manos sobre el teclado
        out.append(f'<rect x="{lx-s}" y="{ly+7*s}" width="{s}" height="{s}" fill="{SKIN}"/>'
                   f'<rect x="{lx+18*s}" y="{ly+7*s}" width="{s}" height="{s}" fill="{SKIN}"/>')
    if pup:
        out.append(grid(PUP, pal(PUP_PAL), x0 + 23 * s, y0 + 8 * s, s))
        if anim and not silhouette:
            out.append(f'<g class="blink2"><rect x="{x0+24*s}" y="{y0+12*s}" width="{s}" height="{s}" fill="#8b949e"/>'
                       f'<rect x="{x0+29*s}" y="{y0+12*s}" width="{s}" height="{s}" fill="#8b949e"/></g>')
    return "".join(out)



# ---------- Letras grandes (5x7) para el nombre ----------
BIG = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
}


def big_width(text, cell):
    return len(text) * 6 * cell + cell // 2 - cell


def big_text(text, x, y, cell, color, shadow="#30363d"):
    """Texto grande y grueso: cada letra 5x7, trazo engordado medio píxel y sombra abajo-derecha."""
    out_s, out_c = [], []
    half = cell / 2
    for i, ch in enumerate(text.upper()):
        rows = BIG.get(ch, BIG[" "])
        gx = x + i * 6 * cell
        for j, row in enumerate(rows):
            for k, c in enumerate(row):
                if c == "#":
                    px, py = gx + k * cell, y + j * cell
                    out_s.append(f'<rect x="{px+half}" y="{py+half}" width="{cell+half}" height="{cell}" fill="{shadow}"/>')
                    out_c.append(f'<rect x="{px}" y="{py}" width="{cell+half}" height="{cell}" fill="{color}"/>')
    return "<g>" + "".join(out_s) + "</g><g>" + "".join(out_c) + "</g>"


def ascii_howl():
    """El lobo que aúlla y la luna de la escena de noche, en ASCII (2 columnas por píxel, 2 filas por línea)."""
    h, w = len(HOWL), len(HOWL[0])
    g = [list(r.ljust(w + 16, ".")) for r in HOWL]
    for j, row in enumerate(MOON):
        for i, c in enumerate(row):
            if c == "#" and j < h:
                g[j][w + 3 + i] = "m"
    rows = ["".join(r) for r in g]
    if h % 2:
        rows.append("." * len(rows[0]))

    def cell(a, b):
        if a != "." and b != ".":
            return "@@" if a == "#" else "OO"
        if a != ".":
            return '""' if a == "#" else "''"
        if b != ".":
            return ",," if b == "#" else ".."
        return "  "

    return "\n".join("".join(cell(rows[j][i], rows[j + 1][i]) for i in range(len(rows[0]))).rstrip()
                     for j in range(0, len(rows), 2))
