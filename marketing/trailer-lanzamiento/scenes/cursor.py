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


# ── Recorrido continuo (v8) ─────────────────────────────────────────────
# Antes el cuadrado viajaba en tramos rectos y se detenía por completo en cada
# elemento (6 fotogramas quieto) antes de volver a arrancar: se veía a saltos.
# Ahora recorre una curva suave (spline cardinal) que pasa por todos los
# elementos: al llegar a cada uno baja la velocidad, lo «toca» y sigue sin
# detenerse. Las llegadas ocurren en los mismos instantes que antes, así que
# las reacciones de cada elemento y los sonidos siguen sincronizados.
TENSION = 0.35          # 0 = curva amplia (Catmull-Rom), 1 = tramos rectos
TOUCH = 0.65            # velocidad al pasar por un elemento (fracción de la menor media vecina)


def _build_path():
    pts = [TL.START] + [_anchor(k) for (_, _, k) in TL.ALL_MOVES]
    starts = [TL.ALL_MOVES[0][0]] + [a for (_, a, _) in TL.ALL_MOVES[:-1]]
    ends = [a for (_, a, _) in TL.ALL_MOVES]
    n = len(pts)
    P = [tuple(map(float, p)) for p in pts]
    # tangentes del spline cardinal (en el primer y último punto, hacia el vecino)
    tang = []
    for i in range(n):
        p0 = P[max(0, i - 1)]
        p1 = P[min(n - 1, i + 1)]
        f = (1 - TENSION) * (0.5 if 0 < i < n - 1 else 1.0)
        tang.append(((p1[0] - p0[0]) * f, (p1[1] - p0[1]) * f))
    tang[0] = (0.0, 0.0)   # sale del centro desde el reposo
    segs = []
    for i in range(n - 1):
        L = math.dist(P[i], P[i + 1])
        segs.append(dict(t0=starts[i], t1=ends[i], p0=P[i], p1=P[i + 1], m0=tang[i], m1=tang[i + 1], L=L))
    # velocidad al pasar por cada elemento: igual a ambos lados (sin tirones)
    for i, sg in enumerate(segs):
        avg = sg["L"] / max(1e-3, sg["t1"] - sg["t0"])
        sg["avg"] = avg
    for i, sg in enumerate(segs):
        v_in = 0.0 if i == 0 else TOUCH * min(segs[i - 1]["avg"], sg["avg"])
        v_out = 0.0 if i == len(segs) - 1 else TOUCH * min(sg["avg"], segs[i + 1]["avg"])
        sg["v0"] = v_in / max(1e-3, sg["avg"])
        sg["v1"] = v_out / max(1e-3, sg["avg"])
    return segs


def _hermite(p0, p1, m0, m1, u):
    u2, u3 = u * u, u * u * u
    h00, h10, h01, h11 = 2 * u3 - 3 * u2 + 1, u3 - 2 * u2 + u, -2 * u3 + 3 * u2, u3 - u2
    return (h00 * p0[0] + h10 * m0[0] + h01 * p1[0] + h11 * m1[0],
            h00 * p0[1] + h10 * m0[1] + h01 * p1[1] + h11 * m1[1])


def _time_ease(k, v0, v1):
    """Avance 0→1 en el tiempo con velocidad inicial v0 y final v1 (relativas a la media)."""
    k2, k3 = k * k, k * k * k
    return (-2 * k3 + 3 * k2) + v0 * (k3 - 2 * k2 + k) + v1 * (k3 - k2)


_SEGS = _build_path()


def path_point(t):
    """Posición sobre el recorrido continuo (sin la vuelta al centro de E4)."""
    if t <= _SEGS[0]["t0"]:
        return TL.START
    for sg in _SEGS:
        if t < sg["t1"]:
            k = (t - sg["t0"]) / (sg["t1"] - sg["t0"])
            u = min(1.0, max(0.0, _time_ease(k, sg["v0"], sg["v1"])))
            x, y = _hermite(sg["p0"], sg["p1"], sg["m0"], sg["m1"], u)
            return (min(1030.0, max(50.0, x)), min(1870.0, max(60.0, y)))
    return _SEGS[-1]["p1"]


def position(t):
    """(x, y, estiramiento_x, estiramiento_y) del cursor en E1–E3 (empieza y vuelve al centro)."""
    x, y = path_point(t)
    # estiramiento en la dirección del movimiento, según la velocidad (sutil)
    x2, y2 = path_point(t + 1 / 60)
    vx, vy = (x2 - x) * 60, (y2 - y) * 60
    stretch = min(0.16, math.hypot(vx, vy) / 9000)
    if abs(vx) >= abs(vy):
        sx, sy = 1 + stretch, 1 - stretch * 0.45
    else:
        sx, sy = 1 - stretch * 0.45, 1 + stretch
    # E4: regresa al centro
    a, b = TL.S4_CURSOR_HOME
    if t >= a:
        k = E.in_out_cubic(E.prog(t, a, b))
        x, y = E.lerp_pt((x, y), TL.START, k)
        sx = sy = 1.0
    return (x, y, sx, sy)


def alpha(t):
    """Aparición y parpadeo lento de E1. En E2–E4 queda fijo (está trabajando).
    v13: después de «Hay otra forma.» vuelve a parpadear dos veces, como un
    cursor esperando en la oscuridad, y se queda encendido antes de la luz."""
    if t < T["cursor_on"]:
        return 0.0
    if getattr(cfg, "TEMA", "oscuro") == "mezcla":
        b0, b1 = T["vo4"] + 1.05, T["vo4"] + 1.05 + 1.6
        if b0 <= t < b1:
            ph = ((t - b0) % 0.8) / 0.8
            if ph > 0.55:
                off = min(E.prog(ph, 0.55, 0.62), 1 - E.prog(ph, 0.93, 1.0))
                return 1 - off
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
    """Pequeño «pop» al aparecer y un latido fuerte cuando estalla la luz."""
    k = E.prog(t, T["cursor_on"], T["cursor_on"] + 0.22)
    base = 0.55 + 0.45 * E.out_back(k, 2.2) if k < 1 else 1.0
    if getattr(cfg, "TEMA", "oscuro") == "mezcla":
        # suspenso: durante los 3 s de oscuridad el cuadrado se va achicando
        # (cada vez más pequeño, como si fuera a desaparecer) y cuando amanece
        # la luz vuelve a su tamaño
        l0 = cfg.LUZ[0]
        shrink = E.in_out_sine(E.prog(t, l0 - 3.0, l0))
        release = E.in_out_sine(E.prog(t, l0, l0 + 1.1))
        base *= 1 - 0.62 * shrink * (1 - release)
    return base


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
