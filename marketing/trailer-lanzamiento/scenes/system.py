"""E4 (v2): la solución en acción. Todavía sin marca.

Después de «Hay otra forma» el cuadrado vuelve a moverse, pero ahora ordena:
traza la guía de la interfaz y la retícula aparece alineada. Luego hace el
trabajo: «piensa», se expande y se convierte en la respuesta del agente; sale
de la burbuja, confirma la reserva, viaja por un conector y termina siendo la
celda reservada en el panel. El violeta en pantalla es siempre algo que hizo
el cuadrado. En E5 toda la interfaz converge de vuelta hacia él.
"""
import math

import skia

import config as cfg
from lib import ease as E
from lib import logo as L
from lib import timeline as TL
from lib.draw import draw_text, font, line, paint, rrect, wrap

C, T, D = cfg.C, cfg.T, cfg.DEMO
S6 = TL.S6

# ── Composición ──────────────────────────────────────────────────────────
X0, X1 = 90, 990
CONCEPT_Y = [250, 314, 378]
HEADER_Y = 466
GUIDE_Y = 488          # la línea que traza el cuadrado al ordenar el espacio
MSG1_Y, BOT_Y, MSG2_Y = 512, 706, 872
CHIP_Y, CHIP_H = 990, 76
PANEL = skia.Rect.MakeLTRB(X0, 1100, X1, 1518)
CELL, GAP = 64, 12
GRID_X, HEAD_Y, ROW0_Y = 200, 1272, 1290
WIRE_X = 1022

F_MSG = ("geist500", 36)
LINE_H = 46


def _bubble_size(text, max_w=600):
    f = font(*F_MSG)
    lines = wrap(text, f, max_w)
    w = max(f.measureText(l) for l in lines) + 56
    h = 92 + (len(lines) - 1) * LINE_H
    return lines, w, h


MSG1 = _bubble_size(D["cliente1"])
BOT = _bubble_size(D["bot1"], 620)
MSG2 = _bubble_size(D["cliente2"])
BOT_RECT = skia.Rect.MakeLTRB(X1 - BOT[1], BOT_Y, X1, BOT_Y + BOT[2])


def _cell_rect(row, col):
    x = GRID_X + col * (CELL + GAP)
    y = ROW0_Y + row * (CELL + GAP)
    return skia.Rect.MakeXYWH(x, y, CELL, CELL)


TARGET = (1, 7)
TARGET_RECT = _cell_rect(*TARGET)


def _chip_geom():
    f = font("geist600", 30)
    tw = f.measureText(D["confirmacion"])
    w = 16 + 44 + 18 + tw + 30
    x = 540 - w / 2
    sq = skia.Rect.MakeXYWH(x + 16, CHIP_Y + (CHIP_H - 44) / 2, 44, 44)
    return x, w, sq


CHIP_X, CHIP_W, CHIP_SQ = _chip_geom()

# conector: desde el cuadro de la confirmación hasta la celda reservada
WIRE = [
    (CHIP_SQ.centerX(), CHIP_SQ.centerY()),
    (CHIP_SQ.centerX(), CHIP_Y + CHIP_H + 14),
    (WIRE_X, CHIP_Y + CHIP_H + 14),
    (WIRE_X, TARGET_RECT.centerY()),
    (TARGET_RECT.centerX(), TARGET_RECT.centerY()),
]


def _poly_point(pts, k):
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    lens = [math.dist(a, b) for a, b in segs]
    total = sum(lens)
    d = k * total
    for (a, b), l in zip(segs, lens):
        if d <= l:
            return E.lerp_pt(a, b, d / l if l else 0), (a, b)
        d -= l
    return pts[-1], segs[-1]


def _poly_partial(pts, k):
    """Polilínea recortada a la fracción k de su longitud."""
    p = skia.Path()
    p.moveTo(*pts[0])
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    lens = [math.dist(a, b) for a, b in segs]
    d = k * sum(lens)
    for (a, b), l in zip(segs, lens):
        if d >= l:
            p.lineTo(*b)
            d -= l
        else:
            q = E.lerp_pt(a, b, d / l if l else 0)
            p.lineTo(*q)
            break
    return p


# ── Salida (E5): todo converge hacia el cuadrado ─────────────────────────
EXIT_ORDER = ["concepts", "header", "msg1", "bot", "msg2", "chip", "wire", "panel"]


def exit_k(name, t):
    c0, c1 = TL.RV["converge"]
    a = T["rv"] + c0 + EXIT_ORDER.index(name) * 0.05
    return E.prog(t, a, a + (c1 - c0) - 0.35)


def _collapse(c, k, cx, cy):
    """Desplaza y encoge el elemento hacia la celda reservada (el cuadrado)."""
    if k <= 0:
        return 1.0
    e = E.in_out_cubic(k)
    tx, ty = TARGET_RECT.centerX(), TARGET_RECT.centerY()
    c.translate(E.lerp(cx, tx, e), E.lerp(cy, ty, e))
    sc = max(0.0, 1 - e)
    c.scale(sc, sc)
    c.translate(-cx, -cy)
    return 1 - E.prog(k, 0.55, 1.0)


# ── Piezas ───────────────────────────────────────────────────────────────
def _concepts(c, t):
    k_out = exit_k("concepts", t)
    if k_out >= 1:
        return
    f = font("mont700", 50)
    for i, (txt, dt) in enumerate(cfg.CONCEPTOS):
        ta = T["vo6a"] + dt - 0.08
        k = E.out_cubic(E.prog(t, ta, ta + 0.45))
        if k <= 0:
            continue
        # el más reciente en blanco; los anteriores bajan a gris
        newer = [T["vo6a"] + d for (_, d) in cfg.CONCEPTOS[i + 1:]]
        dim = E.prog(t, newer[0], newer[0] + 0.4) if newer else 0
        col = C["white"]
        a = k * (1 - 0.55 * dim) * (1 - k_out)
        y = CONCEPT_Y[i] + (1 - k) * 26
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(0, CONCEPT_Y[i] - 56, 1080, CONCEPT_Y[i] + 16))
        draw_text(c, txt, X0, y, f, col, a, tracking=-0.02)
        c.restore()


def _header(c, t, r):
    k = E.prog(r, *S6["header"])
    fade = 1 - exit_k("header", t)
    draw_text(c, f'{D["negocio"].upper()}  ·  {D["canal"].upper()}', X0, HEADER_Y,
              font("mono600", 24), C["gray"], k * fade, tracking=0.12)


def _client_msg(c, t, r, spec, y, window, name):
    lines, w, h = spec
    k = E.out_back(E.prog(r, *window), 1.1)
    if k <= 0:
        return
    kx = exit_k(name, t)
    c.save()
    fade = _collapse(c, kx, X0 + w / 2, y + h / 2)
    sc = 0.92 + 0.08 * k
    c.translate(X0, y + h)
    c.scale(sc, sc)
    c.translate(-X0, -(y + h))
    rect = skia.Rect.MakeXYWH(X0, y, w, h)
    rr = skia.RRect()
    rr.setRectRadii(rect, [skia.Point(28, 28), skia.Point(28, 28), skia.Point(28, 28), skia.Point(6, 6)])
    a = min(1, k) * fade
    c.drawRRect(rr, paint(C["graphite"], a))
    f = font(*F_MSG)
    for i, ln in enumerate(lines):
        draw_text(c, ln, X0 + 28, y + 58 + i * LINE_H, f, C["white"], a)
    c.restore()


def _bot(c, t, r):
    """Respuesta del agente: nace de la expansión del cursor."""
    a0, a1 = S6["bot"]
    if r < a0:
        return
    k = E.out_expo(E.prog(r, a0, a1))
    kx = exit_k("bot", t)
    cur = _cursor_rect_at_typing()
    rect = skia.Rect.MakeLTRB(E.lerp(cur.left(), BOT_RECT.left(), k), E.lerp(cur.top(), BOT_RECT.top(), k),
                              E.lerp(cur.right(), BOT_RECT.right(), k), E.lerp(cur.bottom(), BOT_RECT.bottom(), k))
    c.save()
    fade = _collapse(c, kx, BOT_RECT.centerX(), BOT_RECT.centerY())
    rad = 28 * k
    rr = skia.RRect()
    rr.setRectRadii(rect, [skia.Point(rad, rad), skia.Point(rad, rad), skia.Point(6 * k, 6 * k), skia.Point(rad, rad)])
    c.drawRRect(rr, paint(C["violet"], fade))
    ta = E.prog(r, a0 + 0.3, a1 + 0.1) * fade
    f = font(*F_MSG)
    for i, ln in enumerate(BOT[0]):
        draw_text(c, ln, BOT_RECT.left() + 28, BOT_Y + 58 + i * LINE_H, f, "#FFFFFF", ta)
    la = E.prog(r, a0 + 0.35, a1 + 0.2) * fade
    draw_text(c, D["agente"], X1, BOT_Y - 16, font("mono600", 24), C["violet_light"], la,
              align="right", tracking=0.06)
    c.restore()


def _cursor_rect_at_typing():
    s = TL.CURSOR_PX
    cx, cy = BOT_RECT.right() - s / 2, BOT_RECT.centerY()
    return skia.Rect.MakeXYWH(cx - s / 2, cy - s / 2, s, s)


def _chip(c, t, r):
    a0, a1 = S6["chip"]
    if r < a0:
        return
    k = E.out_cubic(E.prog(r, a0, a1))
    kx = exit_k("chip", t)
    c.save()
    fade = _collapse(c, kx, 540, CHIP_Y + CHIP_H / 2)
    # la pastilla se despliega hacia la derecha desde el cuadro
    w = E.lerp(16 + 44 + 16, CHIP_W, k)
    rect = skia.Rect.MakeXYWH(CHIP_X, CHIP_Y, w, CHIP_H)
    c.drawRRect(skia.RRect.MakeRectXY(rect, CHIP_H / 2, CHIP_H / 2), paint(C["graphite"], fade))
    c.drawRRect(skia.RRect.MakeRectXY(rect, CHIP_H / 2, CHIP_H / 2), paint(C["violet_light"], 0.45 * fade, stroke=2))
    c.save()
    c.clipRect(rect)
    draw_text(c, D["confirmacion"], CHIP_SQ.right() + 18, CHIP_Y + 49, font("geist600", 30), C["white"],
              E.prog(r, a0 + 0.15, a1) * fade)
    c.restore()
    # al salir el cursor, en su lugar queda un visto blanco
    w0, _ = S6["wire"]
    ck = E.out_cubic(E.prog(r, w0 + 0.05, w0 + 0.3))
    if ck > 0:
        sq = CHIP_SQ
        c.drawRRect(skia.RRect.MakeRectXY(sq, 10, 10), paint(C["violet_light"], 0.18 * ck * fade))
        p = paint("#FFFFFF", ck * fade, stroke=4.5, cap=skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
        path = skia.Path()
        path.moveTo(sq.left() + 12, sq.centerY() + 1)
        path.lineTo(sq.left() + 19, sq.centerY() + 8)
        path.lineTo(sq.right() - 11, sq.top() + 14)
        c.drawPath(path, p)
    c.restore()


def _wire(c, t, r):
    a0, a1 = S6["wire"]
    if r < a0:
        return
    k = E.in_out_sine(E.prog(r, a0, a1))
    kx = exit_k("wire", t)
    settled = E.prog(r, a1, a1 + 0.6)
    p = paint(C["violet_light"], (0.85 - 0.4 * settled) * (1 - kx), stroke=3)
    p.setStrokeJoin(skia.Paint.kRound_Join)
    c.drawPath(_poly_partial(WIRE, k * (1 - kx)), p)


def _panel(c, t, r):
    a0, a1 = S6["panel"]
    if r < a0:
        return
    k = E.out_cubic(E.prog(r, a0, a1))
    kx = exit_k("panel", t)
    c.save()
    fade = _collapse(c, kx, PANEL.centerX(), PANEL.centerY())
    c.translate(0, (1 - k) * 60)
    a = k * fade
    c.drawRRect(skia.RRect.MakeRectXY(PANEL, 30, 30), paint(C["graphite"], a))
    c.drawRRect(skia.RRect.MakeRectXY(PANEL, 30, 30), paint(C["gray"], 0.18 * a, stroke=1.5))
    draw_text(c, D["panel_titulo"], X0 + 40, PANEL.top() + 64, font("mont600", 42), C["white"], a)
    draw_text(c, D["panel_sub"].upper(), X0 + 40, PANEL.top() + 106, font("mono400", 24), C["gray"], a, tracking=.06)
    # KPI de ocupación
    land0 = S6["land"][0]
    kk = E.out_cubic(E.prog(r, land0, land0 + 0.35))
    draw_text(c, "Ocupación sáb", X1 - 40, PANEL.top() + 52, font("geist400", 26), C["gray"], a, align="right")
    fk = font("mont700", 46)
    yk = PANEL.top() + 104
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(X1 - 200, yk - 46, X1 - 30, yk + 12))
    draw_text(c, "7/8", X1 - 40, yk - 60 * kk, fk, C["white"], a * (1 - kk), align="right")
    draw_text(c, "8/8", X1 - 40, yk + 60 * (1 - kk), fk, C["white"], a * kk, align="right")
    c.restore()
    pk = E.prog(r, *S6["paid"])
    if pk > 0:
        fp = font("mono600", 22)
        txt = "ANTICIPO PAGADO"
        draw_text(c, txt, X1 - 40, PANEL.top() + 140, fp, C["violet_light"], pk * fade, align="right", tracking=.08)
        from lib.draw import text_width
        cx0 = X1 - 40 - text_width(txt, fp, .08) - 30
        cy0 = PANEL.top() + 132
        pc = paint(C["violet_light"], pk * fade, stroke=3.2, cap=skia.Paint.kRound_Cap)
        pc.setStrokeJoin(skia.Paint.kRound_Join)
        ck = skia.Path()
        ck.moveTo(cx0, cy0)
        ck.lineTo(cx0 + 6, cy0 + 6)
        ck.lineTo(cx0 + 18, cy0 - 8)
        c.drawPath(ck, pc)
    # grilla de ocupación
    fh = font("mono400", 24)
    for j, col in enumerate(D["columnas"]):
        x = GRID_X + j * (CELL + GAP) + CELL / 2
        draw_text(c, col, x, HEAD_Y, fh, C["gray"], a * 0.9, align="center")
    fr = font("mono400", 26)
    for i, row in enumerate(D["filas"]):
        rr_ = _cell_rect(i, 0)
        draw_text(c, row, X0 + 40, rr_.centerY() + 8, fr, C["gray"], a)
        for j, v in enumerate(D["ocupacion"][i]):
            ca = a * E.prog(r, a0 + 0.15 + 0.012 * (i * 8 + j), a0 + 0.35 + 0.012 * (i * 8 + j))
            rect = _cell_rect(i, j)
            rr = skia.RRect.MakeRectXY(rect, 12, 12)
            if v == 1:
                c.drawRRect(rr, paint(C["graphite_2"], ca))
                c.drawRRect(rr, paint(C["gray"], 0.22 * ca, stroke=1.5))
            else:
                c.drawRRect(rr, paint(C["gray"], 0.35 * ca, stroke=2))
    c.restore()


# ── El cursor en E6 ──────────────────────────────────────────────────────
def cursor_rect(t):
    """Rectángulo (y radio) del cuadrado en E6, o None si no se ve suelto."""
    r = t - T["s6"]
    s = TL.CURSOR_PX
    home = skia.Rect.MakeXYWH(TL.START[0] - s / 2, TL.START[1] - s / 2, s, s)   # sale del centro
    typing = _cursor_rect_at_typing()
    o0, o1 = S6["organize"]
    ga, gb = _guide_ends()
    if r < o0:
        return home, 0
    if r < o0 + 0.45:                      # va al inicio de la guía
        k = E.in_out_sine(E.prog(r, o0, o0 + 0.45))
        return _lerp_rect(home, _sq(ga, s), k), 0
    if r < o1:                             # traza la guía de izquierda a derecha
        k = E.in_out_sine(E.prog(r, o0 + 0.45, o1))
        return _lerp_rect(_sq(ga, s), _sq(gb, s), k), 0
    a0, a1 = S6["cursor_to_chat"]
    if r < a1:
        k = E.in_out_sine(E.prog(r, a0, a1))
        return _lerp_rect(_sq(gb, s), typing, k), 0
    t0, t1 = S6["typing"]
    if r < S6["bot"][0]:
        k = E.prog(r, t0, t1)
        sc = 1 - 0.2 * abs(math.sin(math.pi * k * 3)) if t0 <= r < t1 else 1
        cx, cy = typing.centerX(), typing.centerY()
        return skia.Rect.MakeXYWH(cx - s * sc / 2, cy - s * sc / 2, s * sc, s * sc), 0
    o0, o1 = S6["cursor_out"]
    if r < o0:
        return None, 0
    w0, w1 = S6["wire"]
    land0, land1 = S6["land"]
    sq = CHIP_SQ
    if r < o1:
        # nace en la esquina inferior izquierda de la burbuja y baja al cuadro
        start = skia.Rect.MakeXYWH(BOT_RECT.left(), BOT_RECT.bottom() - s, s, s)
        grow = E.out_back(E.prog(r, o0, o0 + 0.12), 1.6)
        k = E.in_out_sine(E.prog(r, o0 + 0.06, o1))
        rect = _lerp_rect(start, sq, k)
        if grow < 1:
            rect = _scale_rect(rect, max(0.01, grow))
        return rect, 10 * k
    if r < w0:
        return sq, 10
    if r < land0:
        k = E.in_out_sine(E.prog(r, w0, w1))
        (x, y), _ = _poly_point(WIRE, k)
        size = E.lerp(44, CELL, E.prog(r, w0, w0 + 0.3))
        return skia.Rect.MakeXYWH(x - size / 2, y - size / 2, size, size), 12
    # ya es la celda reservada
    kl = E.prog(r, land0, land1)
    pulse = 1 + 0.12 * math.sin(math.pi * kl)
    return _scale_rect(TARGET_RECT, pulse), 12


def _guide_ends():
    s = TL.CURSOR_PX
    return (X0 + s / 2, GUIDE_Y), (X1 - s / 2, GUIDE_Y)


def _sq(p, s):
    return skia.Rect.MakeXYWH(p[0] - s / 2, p[1] - s / 2, s, s)


def _organize(c, t, r):
    """La guía que deja el cuadrado y una retícula alineada (orden, no ruido)."""
    o0, o1 = S6["organize"]
    if r < o0 + 0.45:
        return
    k = E.in_out_sine(E.prog(r, o0 + 0.45, o1))
    fade = 1 - exit_k("header", t)
    ga, gb = _guide_ends()
    x_end = E.lerp(X0, X1, k)
    c.drawRect(skia.Rect.MakeLTRB(X0, GUIDE_Y - 1, x_end, GUIDE_Y + 1), paint(C["gray"], 0.45 * fade))
    # retícula de puntos: aparece fila por fila detrás de la guía
    ga_ = 0.07 * E.prog(r, o0 + 0.6, o1 + 0.8) * (1 - E.prog(t, T["rv"], T["rv"] + 0.6))
    if ga_ > 0.003:
        p = paint(C["gray"], ga_)
        for gx in range(90, 991, 75):
            for gy in range(560, 1561, 75):
                c.drawCircle(gx, gy, 1.6, p)


def _lerp_rect(a, b, k):
    return skia.Rect.MakeLTRB(E.lerp(a.left(), b.left(), k), E.lerp(a.top(), b.top(), k),
                              E.lerp(a.right(), b.right(), k), E.lerp(a.bottom(), b.bottom(), k))


def _scale_rect(rc, s):
    cx, cy = rc.centerX(), rc.centerY()
    w, h = rc.width() * s, rc.height() * s
    return skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h)


def draw(c, t):
    if not (T["s6"] <= t < T["rv"] + TL.RV["converge"][1] + 0.1):
        return
    r = t - T["s6"]
    _organize(c, t, r)
    _concepts(c, t)
    _header(c, t, r)
    _client_msg(c, t, r, MSG1, MSG1_Y, S6["msg1"], "msg1")
    _client_msg(c, t, r, MSG2, MSG2_Y, S6["msg2"], "msg2")
    _panel(c, t, r)
    _wire(c, t, r)
    _chip(c, t, r)
    _bot(c, t, r)
    if t < T["rv"]:
        rect, rad = cursor_rect(t)
        if rect is not None:
            c.drawRRect(skia.RRect.MakeRectXY(rect, rad, rad), paint(C["violet"]))
