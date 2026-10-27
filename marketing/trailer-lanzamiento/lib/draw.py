"""Primitivas de dibujo sobre Skia: color, tipografía, texto con tracking y cajas."""
from functools import lru_cache
from pathlib import Path

import skia

FONTS = Path(__file__).resolve().parent.parent / "fonts"

_FILES = {
    "mont300": "montserrat-300.ttf", "mont500": "montserrat-500.ttf",
    "mont600": "montserrat-600.ttf", "mont700": "montserrat-700.ttf",
    "geist400": "geist-400.ttf", "geist500": "geist-500.ttf", "geist600": "geist-600.ttf",
    "mono400": "jetbrains-mono-400.ttf", "mono600": "jetbrains-mono-600.ttf",
}


@lru_cache(None)
def typeface(name):
    tf = skia.Typeface.MakeFromFile(str(FONTS / _FILES[name]))
    if tf is None:
        raise FileNotFoundError(f"No se pudo cargar la fuente {name}")
    return tf


@lru_cache(None)
def font(name, size):
    f = skia.Font(typeface(name), size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setHinting(skia.FontHinting.kNone)
    return f


def color(hexstr, alpha=1.0):
    h = hexstr.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    a = int(round(max(0.0, min(1.0, alpha)) * 255))
    return skia.Color(r, g, b, a)


def paint(hexstr, alpha=1.0, stroke=None, cap=skia.Paint.kButt_Cap):
    p = skia.Paint(AntiAlias=True, Color=color(hexstr, alpha))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(cap)
    return p


def text_width(s, fnt, tracking=0.0):
    """Ancho del texto con tracking (en em) aplicado entre letras."""
    if not s:
        return 0.0
    w = fnt.measureText(s)
    return w + tracking * fnt.getSize() * (len(s) - 1)


def draw_text(c, s, x, y, fnt, hexstr, alpha=1.0, align="left", tracking=0.0):
    """Dibuja s con la línea base en y. align: left | center | right."""
    if alpha <= 0.002 or not s:
        return
    w = text_width(s, fnt, tracking)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    p = paint(hexstr, alpha)
    if tracking == 0:
        c.drawString(s, x, y, fnt, p)
        return
    extra = tracking * fnt.getSize()
    for ch in s:
        c.drawString(ch, x, y, fnt, p)
        x += fnt.measureText(ch) + extra


def wrap(s, fnt, max_w):
    words, lines, cur = s.split(" "), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if fnt.measureText(test) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def rrect(c, x, y, w, h, r, p):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), p)


def line(c, x0, y0, x1, y1, p):
    c.drawLine(x0, y0, x1, y1, p)
