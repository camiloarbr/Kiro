"""E5–E6 (v2): revelación única y cierre.

E5: la interfaz converge en el cuadrado (scenes/system.py), y el cuadrado
—que en ese momento es la celda reservada— viaja al centro, pierde las
esquinas redondeadas y vuelve a ser el cursor. Se queda solo un instante.
Después scenes/logo_build.py lo transforma en «kiro» (una sola vez).

E6: el logo ya armado se queda quieto (el narrador solo dice «Kiro») y entra
la dirección web. Cierra un parpadeo del cursor con la firma sonora.
"""
import skia

import config as cfg
from lib import ease as E
from lib import timeline as TL
from lib.draw import draw_text, font, paint
from scenes import system

C, T = cfg.C, cfg.T


def _home_rect():
    s = TL.CURSOR_PX
    return skia.Rect.MakeXYWH(TL.HOME[0] - s / 2, TL.HOME[1] - s / 2, s, s)


def sting_alpha(t):
    """Parpadeo final del cursor (lo usa logo_build)."""
    b0, b1 = T["sting"], T["sting"] + 0.26
    if b0 <= t <= b1 + 0.05:
        return 1 - min(E.prog(t, b0, b0 + 0.04), 1 - E.prog(t, b1, b1 + 0.05))
    return 1.0


def _cube(c, t):
    """La celda reservada viaja al centro (E5); allí la toma scenes/cube3d.py,
    y al terminar el 3D queda como cursor en su sitio del logo."""
    from scenes import cube3d
    r = t - T["rv"]
    c0, c1 = TL.RV["cube"]
    if c0 <= r <= c1:
        cube3d.draw(c, t)
        return
    if r > c1:                                   # ya es el cursor, quieto en su sitio
        b = _home_rect()
        c.drawRect(b, paint(C["violet"]))
        return
    h0, h1 = TL.RV["to_center"]
    k = E.in_out_cubic(E.prog(r, h0, h1))
    a = system.TARGET_RECT
    s = TL.CURSOR_PX
    b = skia.Rect.MakeXYWH(cube3d.CENTER[0] - s / 2, cube3d.CENTER[1] - s / 2, s, s)
    # pulso cuando la interfaz termina de entrar en él
    cv0, cv1 = TL.RV["converge"]
    pulse = 1 + 0.18 * E.clamp(1 - abs(r - (cv1 - 0.15)) / 0.18) if r < h0 + 0.1 else 1
    rect = skia.Rect.MakeLTRB(E.lerp(a.left(), b.left(), k), E.lerp(a.top(), b.top(), k),
                              E.lerp(a.right(), b.right(), k), E.lerp(a.bottom(), b.bottom(), k))
    if pulse != 1:
        cx, cy, w, h = rect.centerX(), rect.centerY(), rect.width() * pulse, rect.height() * pulse
        rect = skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h)
    rad = 12 * (1 - k)
    c.drawRRect(skia.RRect.MakeRectXY(rect, rad, rad), paint(C["violet"]))


def _closing_text(c, t):
    """v3: el cierre solo dice «Kiro». Debajo del logo queda únicamente la
    dirección web, discreta (vacía en config.URL = sin texto)."""
    if not cfg.URL:
        return
    k = E.out_cubic(E.prog(t, *TL.CLOSE["url"]))
    if k > 0:
        draw_text(c, cfg.URL, 540, 1250 + (1 - k) * 16, font("mono400", 30), C["violet_light"], 0.85 * k,
                  align="center")


def draw(c, t):
    if T["rv"] <= t < T["s5"]:
        _cube(c, t)
    if t >= T["close"]:
        _closing_text(c, t)
