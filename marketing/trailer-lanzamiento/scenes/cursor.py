"""El protagonista: el cuadrado Kiro Violet (cursor de terminal).

Este módulo solo resuelve DÓNDE está y CÓMO se ve el cursor en E1–E4.
Desde E5 la escena dueña del momento lo dibuja, porque ahí deja de ser un
objeto suelto y pasa a ser parte del logo, de una burbuja o de una celda.
"""
import math

import skia

import config as cfg
from lib import ease as E
from lib import timeline as TL
from lib.draw import paint

T = cfg.T


def _anchor(kind):
    return TL.ANCHORS[kind]


def position(t):
    """(x, y, estiramiento_x, estiramiento_y) del cursor en E1–E3 (empieza y vuelve al centro)."""
    pos = TL.START
    sx = sy = 1.0
    # Recorre los movimientos en orden; el cursor queda donde llegó.
    for (dep, arr, kind) in TL.ALL_MOVES:
        target = _anchor(kind)
        if t < dep:
            break
        if t >= arr:
            pos = target
            continue
        k = (t - dep) / (arr - dep)
        # curvas suaves: el cuadrado acelera y frena, pero se le ve viajar
        e = E.in_out_sine(k)
        start = pos
        pos = E.lerp_pt(start, target, e)
        # estiramiento en la dirección del movimiento (sutil)
        dx, dy = target[0] - start[0], target[1] - start[1]
        stretch = 0.16 * math.sin(math.pi * k)
        if abs(dx) >= abs(dy):
            sx, sy = 1 + stretch, 1 - stretch * 0.45
        else:
            sx, sy = 1 - stretch * 0.45, 1 + stretch
        return (pos[0], pos[1], sx, sy)
    # E4: regresa a su sitio en el logo
    a, b = TL.S4_CURSOR_HOME
    if t >= a:
        k = E.in_out_cubic(E.prog(t, a, b))
        pos = E.lerp_pt(pos, TL.START, k)
    return (pos[0], pos[1], sx, sy)


def alpha(t):
    """Aparición y parpadeo lento de E1. En E2–E4 queda fijo (está trabajando)."""
    if t < T["cursor_on"]:
        return 0.0
    a = E.prog(t, T["cursor_on"], T["cursor_on"] + 0.08)
    blink_from, blink_to = T["cursor_on"] + 0.75, T["s2"] - 0.1
    if blink_from <= t < blink_to:
        ph = ((t - blink_from) % 1.1) / 1.1
        # 0–0.62 encendido, luego apagado suave (fundidos de 70 ms)
        if ph > 0.62:
            off = min(E.prog(ph, 0.62, 0.685), 1 - E.prog(ph, 0.935, 1.0))
            a *= 1 - off
    return a


def scale(t):
    """Pequeño «pop» al aparecer."""
    k = E.prog(t, T["cursor_on"], T["cursor_on"] + 0.22)
    return 0.55 + 0.45 * E.out_back(k, 2.2) if k < 1 else 1.0


TRAIL = 5          # muestras de la estela de movimiento (desenfoque de movimiento)


def draw(c, t):
    if t >= T["s6"]:
        return
    a = alpha(t)
    if a <= 0:
        return
    s = TL.CURSOR_PX * scale(t)
    # estela: posiciones del último fotograma, cada vez más tenues, para que
    # el ojo lea el recorrido aunque el movimiento sea rápido
    x0, y0, _, _ = position(t)
    for q in range(TRAIL, 0, -1):
        tq = t - q / (cfg.FPS * TRAIL) * 1.6
        if tq < T["cursor_on"]:
            continue
        xq, yq, sxq, syq = position(tq)
        if abs(xq - x0) + abs(yq - y0) < 2:
            continue
        w, h = s * sxq, s * syq
        c.drawRect(skia.Rect.MakeXYWH(xq - w / 2, yq - h / 2, w, h),
                   paint(cfg.C["violet"], a * 0.10 * (TRAIL - q + 1) / TRAIL))
    x, y, sx, sy = x0, y0, *position(t)[2:]
    w, h = s * sx, s * sy
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), paint(cfg.C["violet"], a))
