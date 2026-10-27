"""E2–E4: el cuadrado activa fragmentos de trabajo manual que se acumulan
(hoja de cálculo, chats sin responder, pendientes, registros) y en E4 se
retiran uno a uno hasta dejarlo solo."""
import math

import skia

import config as cfg
from lib import ease as E
from lib import timeline as TL
from lib.draw import draw_text, font, line, paint, rrect, text_width

C, T = cfg.C, cfg.T


# ── Retirada de E4: cada grupo se aplana a una línea y desaparece ───────
def collapse(kind, t):
    """0 = intacto, 1 = desaparecido."""
    i = TL.S4_ORDER.index(kind)
    a = TL.S4_START + i * TL.S4_STAGGER
    return E.prog(t, a, a + TL.S4_DUR)


def _apply_collapse(c, k, cx, cy):
    """Escala vertical hasta una línea (primer 55 %) y luego encoge la línea."""
    if k <= 0:
        return 1.0
    k1 = E.in_out_cubic(E.prog(k, 0, .55))
    k2 = E.in_cubic(E.prog(k, .55, 1))
    sy = max(0.012, 1 - k1)
    sx = max(0.0, 1 - k2)
    c.translate(cx, cy)
    c.scale(sx, sy)
    c.translate(-cx, -cy)
    return 1 - k2 * 0.6


# ── Retícula de fondo ────────────────────────────────────────────────────
def draw_grid(c, t):
    a_in = E.prog(t, T["s2"], T["s2"] + 1.2)
    a_out = 1 - E.prog(t, T["s4"] + 0.2, T["s4"] + 1.2)
    a = 0.075 * a_in * a_out
    if a <= 0.002:
        return
    p = paint(C["gray"], a)
    step = 72
    r = 1.6
    for gx in range(72, 1009, step):
        for gy in range(288, 1585, step):
            c.drawCircle(gx, gy, r, p)


# ── Hoja de cálculo ──────────────────────────────────────────────────────
SHEET_X, SHEET_Y, SHEET_W, ROW_H = 452, 706, 556, 58
COLS = [0, 196, 306]   # x relativa de cada columna


def draw_trail(c, t):
    """Rastro que deja el cuadrado al salir del centro hacia la hoja (coords. de pantalla)."""
    from scenes import cursor as CU
    dep, arr, _ = TL.S2_MOVES[0]
    if t < dep:
        return
    k = collapse("sheet", t)
    if k >= 1:
        return
    x0, y0 = TL.START
    if t < arr:
        x1, y1, _, _ = CU.position(t)
    else:
        x1, y1 = TL.ANCHORS["sheet"]
    fade = (1 - k) * (1 - E.prog(t, arr + 0.3, arr + 1.0))   # el rastro se desvanece al llegar
    if fade <= 0:
        return
    line(c, x0, y0, x1, y1, paint(C["gray"], 0.35 * fade, stroke=2))
    c.drawCircle(x0, y0, 4, paint(C["gray"], 0.5 * fade))


def draw_sheet(c, t):
    """Hoja de cálculo con la cuadrícula completa: bordes, encabezado, filas y columnas."""
    t0 = TL.first_arrival("sheet")
    k = collapse("sheet", t)
    if t < t0:
        return
    c.save()
    fade = _apply_collapse(c, k, SHEET_X + SHEET_W / 2, SHEET_Y + 200)
    gp = paint(C["gray"], 0.7 * fade, stroke=2)
    n_extra = max(0, TL.arrivals("sheet", t) - 1) * 2
    n_rows = min(3 + n_extra, 7)
    # horizontales: borde superior, línea del encabezado y una por fila
    # (se dibujan de izquierda a derecha, desde donde tocó el cursor)
    bottom = SHEET_Y
    for r in range(n_rows + 2):
        y = SHEET_Y + r * ROW_H
        ts = t0 + 0.05 * r if r <= 4 else _row_time(r - 1)
        pr = E.out_cubic(E.prog(t, ts, ts + 0.35))
        if pr <= 0:
            continue
        x0 = SHEET_X
        line(c, x0, y, x0 + SHEET_W * pr, y, paint(C["gray"], (0.95 if r == 1 else 0.7) * fade, stroke=2.5 if r == 1 else 2))
        if r >= 1:
            bottom += ROW_H * pr
    # verticales: borde izquierdo, divisiones de columna y borde derecho;
    # crecen junto con las filas para que la cuadrícula quede siempre cerrada
    pv = E.out_cubic(E.prog(t, t0 + 0.15, t0 + 0.55))
    for cx in COLS + [SHEET_W]:
        line(c, SHEET_X + cx, SHEET_Y, SHEET_X + cx, E.lerp(SHEET_Y, bottom, pv), gp)
    # encabezado
    fh = font("mono600", 24)
    ha = E.prog(t, t0 + 0.25, t0 + 0.5) * fade
    for j, h in enumerate(TL.SHEET_HEAD):
        draw_text(c, h, SHEET_X + COLS[j] + 14, SHEET_Y + 38, fh, C["gray"], ha, tracking=.08)
    # filas
    fr = font("mono400", 30)
    for r in range(n_rows):
        ts = t0 + 0.35 + 0.1 * r if r < 3 else _row_time(r)
        ra = E.prog(t, ts, ts + 0.18) * fade
        if ra <= 0:
            continue
        row = TL.SHEET_ROWS[r % len(TL.SHEET_ROWS)]
        y = SHEET_Y + (r + 1) * ROW_H + 39
        for j, v in enumerate(row):
            col = C["white"] if j == 0 else C["gray"]
            if j == 2:
                col = C["white"]
            draw_text(c, v, SHEET_X + COLS[j] + 14, y, fr, col, ra * (0.9 if j == 2 else 0.85))
    c.restore()


def _row_time(r):
    """Momento en que aparece la fila r (las filas extra llegan de a dos)."""
    arr = sorted(a for (_, a, k) in TL.ALL_MOVES if k == "sheet")
    idx = (r - 3) // 2 + 1
    if idx < len(arr):
        return arr[idx] + 0.08 * ((r - 3) % 2)
    return 1e9


# ── Chats sin responder ──────────────────────────────────────────────────
def _bubble(c, x, y, s, a, fnt):
    pad_x, h = 26, 76
    w = fnt.measureText(s) + pad_x * 2
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 26, 26)
    rr.setRectRadii(skia.Rect.MakeXYWH(x, y, w, h),
                    [skia.Point(26, 26), skia.Point(26, 26), skia.Point(26, 26), skia.Point(6, 6)])
    c.drawRRect(rr, paint(C["graphite"], a))
    draw_text(c, s, x + pad_x, y + 49, fnt, C["white"], a * 0.92)
    return w


def _chat_times(kind):
    return sorted(a for (_, a, k) in TL.ALL_MOVES if k == kind)


def draw_chat(c, t, kind, base_y, msg_offset):
    times = _chat_times(kind)
    if not times or t < times[0]:
        return
    k = collapse(kind, t)
    c.save()
    fade = _apply_collapse(c, k, 400, base_y + 40)
    fnt = font("geist500", 32)
    n = sum(1 for a in times if a <= t)
    # scroll: cada mensaje nuevo empuja los anteriores hacia arriba
    for m in range(n):
        ta = times[m]
        appear = E.out_back(E.prog(t, ta, ta + 0.28), 1.2)
        age = n - 1 - m
        last_t = times[n - 1]
        slide = E.out_cubic(E.prog(t, last_t, last_t + 0.3)) if age >= 1 else 0
        y = base_y - (age - 1 + slide) * 94 if age >= 1 else base_y
        a = appear * fade * (1.0 if age == 0 else max(0.0, 0.62 - 0.22 * (age - 1 + slide)))
        if a <= 0.01:
            continue
        sc = 0.9 + 0.1 * appear
        c.save()
        c.translate(150, y + 40)
        c.scale(sc, sc)
        c.translate(-150, -(y + 40))
        _bubble(c, 150, y, TL.CHAT_MSGS[(m * 2 + msg_offset) % len(TL.CHAT_MSGS)], a, fnt)
        c.restore()
    c.restore()


def draw_badge(c, t):
    """Contador de mensajes sin leer sobre el chat principal."""
    times = sorted(a for (_, a, k) in TL.ALL_MOVES if k.startswith("chat"))
    if t < times[0]:
        return
    k = collapse("chat", t)
    n = sum(1 for a in times if a <= t)
    val = TL.BADGE_STEPS[min(n - 1, len(TL.BADGE_STEPS) - 1)]
    last = max(a for a in times if a <= t)
    pop = 1 + 0.25 * (1 - E.out_cubic(E.prog(t, last, last + 0.25)))
    c.save()
    _apply_collapse(c, k, 400, 1030)
    fnt = font("geist600", 26)
    s = str(val)
    w = max(44, fnt.measureText(s) + 24)
    x, y = 548, 990
    c.translate(x, y)
    c.scale(pop, pop)
    rrect(c, -w / 2, -22, w, 44, 22, paint(C["white"], 1 - k))
    draw_text(c, s, 0, 9, fnt, C["black"], 1 - k, align="center")
    c.restore()


# ── Pendientes (tarjetas que se apilan) ──────────────────────────────────
TODO_X, TODO_Y, TODO_W, TODO_H = 600, 1186, 408, 252


def _todo_card(c, x, y, a, reveal):
    rrect(c, x, y, TODO_W, TODO_H, 20, paint(C["graphite"], a))
    rrect(c, x, y, TODO_W, TODO_H, 20, paint(C["gray"], 0.25 * a, stroke=1.5))
    draw_text(c, "Pendientes", x + 28, y + 52, font("mont600", 34), C["white"], a)
    fi = font("geist400", 28)
    for i, it in enumerate(TL.TODO_ITEMS):
        ia = a * E.prog(reveal, 0.2 + i * 0.22, 0.45 + i * 0.22)
        yy = y + 112 + i * 52
        c.drawRect(skia.Rect.MakeXYWH(x + 28, yy - 23, 26, 26), paint(C["gray"], ia * 0.9, stroke=2))
        draw_text(c, it, x + 70, yy, fi, C["gray"], ia)


def draw_todo(c, t):
    times = sorted(a for (_, a, k) in TL.ALL_MOVES if k == "todo")
    if t < times[0]:
        return
    k = collapse("todo", t)
    c.save()
    fade = _apply_collapse(c, k, TODO_X + TODO_W / 2, TODO_Y + 150)
    n = min(sum(1 for a in times if a <= t), 5)
    for i in range(n):
        ta = times[i]
        p = E.out_cubic(E.prog(t, ta, ta + 0.35))
        off = i * 14
        x = TODO_X + off - 8
        y = TODO_Y + off - 8
        # despliegue desde la esquina donde tocó el cursor
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(x, y, TODO_W * p + 1, TODO_H * min(1, p * 1.4) + 1))
        _todo_card(c, x, y, fade, E.prog(t, ta, ta + 1.0))
        c.restore()
    c.restore()


# ── Registro (texto de terminal) ─────────────────────────────────────────
LOG_X, LOG_Y = 172, 400


def draw_log(c, t):
    times = sorted(a for (_, a, k) in TL.ALL_MOVES if k == "log")
    if t < times[0]:
        return
    k = collapse("log", t)
    c.save()
    fade = _apply_collapse(c, k, 340, 520)
    fnt = font("mono400", 30)
    # primera visita: 3 líneas; luego una por visita
    starts = [times[0] + 0.05, times[0] + 0.40, times[0] + 0.75] + [a + 0.03 for a in times[1:]]
    n = sum(1 for s in starts if s <= t)
    shown = min(n, 6)
    first = max(0, n - 6)
    for j in range(first, n):
        s = TL.LOG_LINES[j % len(TL.LOG_LINES)]
        chars = int(len(s) * E.prog(t, starts[j], starts[j] + 0.32))
        row = j - first
        y = LOG_Y + row * 46
        a = fade * (1.0 if j == n - 1 else 0.55)
        draw_text(c, s[:chars], LOG_X, y, fnt, C["gray"], a)
    c.restore()


# ── Cables que no conectan (E3) ──────────────────────────────────────────
def _anchor_xy(kind):
    return TL.ANCHORS[kind]


def draw_wires(c, t):
    out = E.prog(t, T["s4"] + 0.1, T["s4"] + 0.6)
    if out >= 1:
        return
    prev = None
    for (dep, arr, kind) in TL.ALL_MOVES:
        p1 = _anchor_xy(kind)
        if prev is not None and dep >= T["s3"] and t >= dep:
            p0 = prev
            k = E.out_cubic(E.prog(t, dep, arr)) * 0.8   # nunca llega: queda un hueco
            k *= (1 - out)
            x1 = E.lerp(p0[0], p1[0], k)
            y1 = E.lerp(p0[1], p1[1], k)
            age = E.prog(t, arr, arr + 1.2)
            p = paint(C["gray"], (0.42 - 0.2 * age), stroke=2)
            p.setPathEffect(skia.DashPathEffect.Make([10, 12], 0))
            line(c, p0[0], p0[1], x1, y1, p)
        prev = p1


def draw(c, t):
    if t < T["s2"] - 0.2 or t > T["s6"]:
        return
    draw_grid(c, t)
    draw_wires(c, t)          # coordenadas de pantalla (los anclajes ya están desplazados)
    draw_trail(c, t)
    c.save()
    c.translate(0, TL.MANUAL_DY)   # v3: todo el bloque 110 px más arriba
    draw_log(c, t)
    draw_sheet(c, t)
    draw_chat(c, t, "chat", 990, 0)
    draw_chat(c, t, "chat2", 1330, 1)
    draw_badge(c, t)
    draw_todo(c, t)
    c.restore()
