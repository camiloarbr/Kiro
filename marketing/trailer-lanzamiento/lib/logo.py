"""Geometría oficial del logo de Kiro, leída del SVG del manual de marca.

No se redibuja ninguna letra: todas las formas salen de
brand/kiro-logo-principal-negativo.svg. Este módulo solo separa el trazado
en sus piezas (palo y brazos de la K, palo de la i, r, o, cursor y
«solutions») para poder animarlas por separado.
"""
import re
from pathlib import Path

import skia

BRAND = Path(__file__).resolve().parent.parent / "brand"
SVG_FULL = BRAND / "kiro-logo-principal-negativo.svg"

_TOKEN = re.compile(r"[MLHVQZmlhvqz]|-?\d+(?:\.\d+)?")


def parse_subpaths(d):
    """Convierte un atributo d (M, L, H, V, Q, Z absolutos) en una lista de
    skia.Path, una por subtrazado."""
    toks = _TOKEN.findall(d)
    paths, p = [], None
    i, cmd = 0, None
    x = y = 0.0
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in "Zz":
                p.close()
                paths.append(p)
                p = None
                continue
            continue
        if cmd == "M":
            x, y = float(toks[i]), float(toks[i + 1])
            i += 2
            p = skia.Path()
            p.moveTo(x, y)
            cmd = "L"  # pares implícitos después de M son lineTo
        elif cmd == "L":
            x, y = float(toks[i]), float(toks[i + 1])
            i += 2
            p.lineTo(x, y)
        elif cmd == "H":
            x = float(toks[i])
            i += 1
            p.lineTo(x, y)
        elif cmd == "V":
            y = float(toks[i])
            i += 1
            p.lineTo(x, y)
        elif cmd == "Q":
            cx, cy, x, y = map(float, toks[i:i + 4])
            i += 4
            p.quadTo(cx, cy, x, y)
        else:
            raise ValueError(f"Comando SVG no soportado: {cmd}")
    if p is not None:
        paths.append(p)
    return paths


COLORS = {}  # colores tal como vienen en el SVG oficial (palabra, cursor, «solutions»)


def _load():
    svg = SVG_FULL.read_text(encoding="utf-8")
    svg = re.sub(r"<metadata>.*?</metadata>", "", svg, flags=re.S)
    ds = re.findall(r'<path d="([^"]+)"', svg)
    rect = re.search(r'<rect x="([\d.]+)" y="(-?[\d.]+)" width="([\d.]+)" height="([\d.]+)"', svg)
    word, solutions = ds[0], ds[1]
    subs = parse_subpaths(word)
    # Orden en el SVG: brazo K, palo K, pierna K, palo i, r, o (exterior), o (contraforma)
    k_arm, k_stem, k_leg, i_stem, r, o_out, o_in = subs
    o = skia.Path(o_out)
    o.addPath(o_in)
    o.setFillType(skia.PathFillType.kEvenOdd)
    sol = skia.Path()
    for sp in parse_subpaths(solutions):
        sol.addPath(sp)
    sol.setFillType(skia.PathFillType.kWinding)
    cx, cy, cw, ch = map(float, rect.groups())
    fills = re.findall(r'fill="(#[0-9A-Fa-f]{6})"', svg)
    COLORS.update(word=fills[0], cursor=fills[1], solutions=fills[2])
    return dict(
        k_arm=k_arm, k_stem=k_stem, k_leg=k_leg, i_stem=i_stem, r=r, o=o,
        solutions=sol, cursor=skia.Rect.MakeXYWH(cx, cy, cw, ch),
    )


PARTS = _load()

# Medidas de referencia en unidades del SVG
BASELINE = 742.0
XHEIGHT = 204.0      # tope del palo de la i (la r y la o rebasan levemente)
ASCENDER = 0.0       # tope del palo de la K
LEFT = 72.0
RIGHT = 1845.0
CURSOR = PARTS["cursor"]          # 672, -30, 156 × 156
CURSOR_SIDE = CURSOR.width()
O_CENTER = (1550.0, 473.0)
R_SHOULDER_X = 1046.0             # donde el palo de la r se convierte en hombro


def full_logo_path(include_solutions=True):
    p = skia.Path()
    for k in ("k_arm", "k_stem", "k_leg", "i_stem", "r", "o"):
        p.addPath(PARTS[k])
    if include_solutions:
        p.addPath(PARTS["solutions"])
    return p
