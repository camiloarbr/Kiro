"""Revelación final (v2): el cuadrado se transforma en «kiro», una sola vez.

Todo se dibuja en unidades del SVG oficial y con sus trazados reales; solo
se anima cómo se revelan (máscaras), nunca su forma final.

Secuencia (tiempos en lib/timeline.py → S5):
  1. el cuadrado salta (anticipación) y cae;
  2. se duplica y su copia cae estirándose: escribe el palo de la «i»;
  3. los bordes de ese palo se extienden: línea base y altura x;
  4. sobre esas guías se levantan la K, la r y la o (cada borde de avance
     lleva un filo Kiro Violet: el cursor «escribiendo»);
  5. las guías vuelven a entrar en la «i», el cursor parpadea una vez
     y aparece «solutions».
"""
import math

import skia

import config as cfg
from lib import ease as E
from lib import logo as L
from lib import timeline as TL
from lib.draw import color, paint

C = cfg.C
P = L.PARTS
# colores del logo: se leen de L.COLORS en cada fotograma (cambian con el tema)
VIOLET = L.COLORS["cursor"]
GUIDE_W = 3.0 / TL.S        # 3 px en pantalla


def _blend(h1, h2, k):
    a = [int(h1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(h2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(round(E.lerp(x, y, k))):02X}" for x, y in zip(a, b))


def _edge(c, x0, y0, x1, y1, k):
    """Filo violeta en el borde de avance de una máscara."""
    a = math.sin(math.pi * E.clamp(k)) ** 0.8
    if a > 0.01:
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), paint(VIOLET, a))


def _wipe_up(c, path, x0, x1, k, top=None):
    """Revela path desde la línea base hacia arriba."""
    if k <= 0:
        return
    b = path.getBounds()
    top = b.top() if top is None else top
    y = E.lerp(L.BASELINE + 10, top - 10, k)
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y, x1, L.BASELINE + 12))
    c.drawPath(path, paint(L.COLORS["word"]))
    c.restore()
    if k < 1:
        _edge(c, x0, y - 3 / TL.S, x1, y + 3 / TL.S, k)


def _wipe_right(c, path, x0, x1, k, y0=-60, y1=800):
    if k <= 0:
        return
    x = E.lerp(x0, x1, k)
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(x0, y0, x, y1))
    c.drawPath(path, paint(L.COLORS["word"]))
    c.restore()
    if k < 1:
        b = path.getBounds()
        _edge(c, x - 3 / TL.S, b.top(), x + 3 / TL.S, b.bottom(), k)


def _sweep(c, path, center, k):
    """Barrido angular (para la o), empezando arriba y en sentido horario."""
    if k <= 0:
        return
    cx, cy = center
    r = 420
    clip = skia.Path()
    if k >= 1:
        clip.addRect(skia.Rect.MakeLTRB(cx - r, cy - r, cx + r, cy + r))
    else:
        clip.moveTo(cx, cy)
        clip.arcTo(skia.Rect.MakeLTRB(cx - r, cy - r, cx + r, cy + r), -90, 360 * k, False)
        clip.close()
    c.save()
    c.clipPath(clip, skia.ClipOp.kIntersect, True)
    c.drawPath(path, paint(L.COLORS["word"]))
    c.restore()
    if k < 1:
        ang = math.radians(-90 + 360 * k)
        a = math.sin(math.pi * k) ** 0.8
        p = paint(VIOLET, a, stroke=6 / TL.S)
        c.drawLine(cx + math.cos(ang) * 150, cy + math.sin(ang) * 150,
                   cx + math.cos(ang) * 300, cy + math.sin(ang) * 300, p)


def _guide(c, y, x_left, x_right, a):
    if a <= 0.01 or x_right <= x_left:
        return
    c.drawRect(skia.Rect.MakeLTRB(x_left, y - GUIDE_W / 2, x_right, y + GUIDE_W / 2),
               paint(C["violet_light"], 0.8 * a))


TICKS = [L.LEFT, 228.0, 918.0, 1074.0, 1254.0, L.RIGHT]


def draw_build(c, u, cursor_alpha=1.0, show_cursor=True, solutions=None, hop=True,
               word_alpha=1.0):
    """Dibuja el logo en construcción. u = segundos desde el inicio de E5
    (o su equivalente comprimido en E7). Se dibuja en unidades del SVG."""
    S5 = TL.S5
    pr = lambda key: E.prog(u, *S5[key])

    c.save()
    c.translate(TL.LOGO_OX, TL.LOGO_OY)
    c.scale(TL.S, TL.S)
    if word_alpha < 1:
        c.saveLayerAlpha(None, int(255 * word_alpha))

    # 3) guías ─────────────────────────────────────────────────────────
    g = E.out_cubic(pr("guides"))
    g2 = E.out_cubic(E.prog(u, S5["guides"][0] + 0.08, S5["guides"][1] + 0.08))
    rt = E.in_out_cubic(pr("retract"))
    mid = L.CURSOR.centerX()
    if g > 0 and rt < 1:
        def span(k):
            left = E.lerp(L.CURSOR.left(), 30, k)
            right = E.lerp(L.CURSOR.right(), 1890, k)
            return E.lerp(left, mid, rt), E.lerp(right, mid, rt)
        l0, r0 = span(g)
        _guide(c, L.BASELINE, l0, r0, 1 - rt * .5)
        l1, r1 = span(g2)
        _guide(c, L.XHEIGHT, l1, r1, 1 - rt * .5)
        # marcas de módulo donde empieza y termina cada letra
        for x in TICKS:
            if l0 <= x <= r0:
                reach = (mid - l0) if x < mid else (r0 - mid)
                ta = (1 - rt) * E.clamp((reach - abs(x - mid)) / 120.0)
                c.drawRect(skia.Rect.MakeLTRB(x - GUIDE_W / 2, L.BASELINE + 14, x + GUIDE_W / 2, L.BASELINE + 54),
                           paint(C["violet_light"], 0.55 * ta))
        # línea de ascendentes: nace del tope del palo de la K
        ga = E.out_cubic(pr("asc"))
        if ga > 0:
            al = E.lerp(L.LEFT, 30, ga)
            ar = E.lerp(228, 640, ga)
            _guide(c, L.ASCENDER, E.lerp(al, 150, rt), E.lerp(ar, 150, rt), 1 - rt)

    # 4) letras ────────────────────────────────────────────────────────
    _wipe_up(c, P["k_stem"], 72, 228, E.out_cubic(pr("k_stem")))
    _wipe_right(c, P["k_arm"], 196, 662, E.out_cubic(pr("k_arm")))
    _wipe_right(c, P["k_leg"], 284, 670, E.out_cubic(pr("k_leg")))
    # r: palo (sube) y hombro (avanza a la derecha)
    rs = E.out_cubic(pr("r_stem"))
    if rs > 0:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(900, -60, L.R_SHOULDER_X, 800))
        _wipe_up(c, P["r"], 918, L.R_SHOULDER_X, rs, top=204)
        c.restore()
        if rs < 1:
            pass
    _wipe_right(c, P["r"], L.R_SHOULDER_X, 1262, E.out_cubic(pr("r_shoulder")), y0=180, y1=760)
    # (las dos máscaras de la r se solapan a propósito para no dejar costura)
    _sweep(c, P["o"], L.O_CENTER, E.in_out_cubic(pr("o")))

    # 2) palo de la i: copia del cursor que cae ───────────────────────
    ex = pr("extrude")
    if ex > 0:
        e = E.out_expo(ex)
        top = E.lerp(L.CURSOR.top(), L.XHEIGHT, e)
        bot = E.lerp(L.CURSOR.bottom(), L.BASELINE, e)
        col = _blend(VIOLET, L.COLORS["word"], E.in_out_cubic(E.prog(u, S5["extrude"][0] + 0.18, S5["extrude"][1])))
        c.drawRect(skia.Rect.MakeLTRB(L.CURSOR.left(), top, L.CURSOR.right(), bot), paint(col))

    # 5) «solutions» ─────────────────────────────────────────────────
    sk = E.out_cubic(pr("solutions")) if solutions is None else solutions
    if sk > 0:
        b = P["solutions"].getBounds()
        cx = b.centerX()
        half = (b.width() / 2 + 20) * sk
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(cx - half, b.top() - 10, cx + half, b.bottom() + 10))
        c.drawPath(P["solutions"], paint(L.COLORS["solutions"], E.clamp(sk * 1.3)))
        c.restore()

    # 1) el cursor ────────────────────────────────────────────────────
    if show_cursor:
        dy, sx, sy = 0.0, 1.0, 1.0
        if hop:
            h = pr("hop")
            if 0 < h < 1:
                if h < 0.55:
                    k = E.out_cubic(h / 0.55)
                    dy = -46 * k
                    sy = 1 + 0.06 * k
                    sx = 1 - 0.04 * k
                else:
                    k = E.in_cubic((h - 0.55) / 0.45)
                    dy = -46 * (1 - k)
                    sy = 1 - 0.1 * k if k > 0.85 else 1
                    sx = 1 + 0.08 * k if k > 0.85 else 1
        a = cursor_alpha
        b0, b1 = S5["blink"]
        if b0 <= u <= b1 + 0.04:
            a *= 1 - min(E.prog(u, b0, b0 + 0.04), 1 - E.prog(u, b1, b1 + 0.04))
        cr = L.CURSOR
        w, hgt = cr.width() * sx, cr.height() * sy
        cx, by = cr.centerX(), cr.bottom() + dy
        c.drawRect(skia.Rect.MakeLTRB(cx - w / 2, by - hgt, cx + w / 2, by), paint(VIOLET, a))

    if word_alpha < 1:
        c.restore()
    c.restore()


def draw_static(c, solutions=1.0, show_cursor=True, cursor_alpha=1.0):
    """Logo completo, idéntico al SVG oficial."""
    draw_build(c, 99.0, cursor_alpha=cursor_alpha, show_cursor=show_cursor, solutions=solutions, hop=False)


def draw(c, t):
    """Única aparición del logo (v2): desde T['s5'] hasta el final, sin repetirse."""
    T = cfg.T
    if t < T["s5"]:
        return
    from scenes.signature import sting_alpha
    draw_build(c, t - T["s5"], cursor_alpha=sting_alpha(t))
