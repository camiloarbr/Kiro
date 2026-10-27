"""Transición 3D antes del logo: el cubo 3×3×3 de la landing de Kiro.

El cuadrado que queda solo después de la demo crece, se vuelve una retícula
de 3×3, se extruye en profundidad hasta ser el cubo de la web (27 cubitos),
gira, hace un giro de capa como en la portada de la landing y se comprime de
nuevo en un cuadrado plano que vuelve a su sitio de cursor para escribir
«kiro».

Es 3D real: cada cubito tiene 6 caras proyectadas en perspectiva, con
iluminación por normal y orden por profundidad (pintor). Determinista.
"""
import math

import numpy as np
import skia

import config as cfg
from lib import ease as E
from lib import timeline as TL
from lib.draw import paint

C, T = cfg.C, cfg.T

CENTER = (540.0, 900.0)       # centro de pantalla del cubo
CUBIE = 126.0                 # lado de cada cubito (px a distancia focal)
FOCAL = 1700.0                # distancia focal de la cámara (px)
CAM_DIST = 1700.0

# paleta de la landing: cara superior lavanda, frontal Kiro Violet, lateral morado oscuro
LIGHT = np.array([0xB4, 0x84, 0xFF], float)
MID = np.array([0x8B, 0x2C, 0xF5], float)
DARK = np.array([0x55, 0x16, 0xB4], float)
EDGE = "#D9C4FF"

# 6 caras de un cubo unitario centrado: (normal, 4 vértices)
_F = []
for axis in range(3):
    for sgn in (-1, 1):
        n = np.zeros(3)
        n[axis] = sgn
        u = np.zeros(3)
        v = np.zeros(3)
        u[(axis + 1) % 3] = 1
        v[(axis + 2) % 3] = 1
        c = n * 0.5
        verts = [c - u / 2 - v / 2, c + u / 2 - v / 2, c + u / 2 + v / 2, c - u / 2 + v / 2]
        _F.append((n, np.array(verts)))

_CUBIES = [(i, j, k) for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1)]


def _rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def _shade(n_cam):
    """Color por normal en cámara, como el cubo de la landing: cara superior
    lavanda, cara frontal Kiro Violet, cara lateral derecha morado oscuro.
    Las potencias altas hacen que cada cara tome el color de su orientación
    dominante y cambie suave al girar."""
    up = max(0.0, -n_cam[1]) ** 6
    side = max(0.0, n_cam[0]) ** 6
    front = max(0.0, -n_cam[2]) ** 6
    left = max(0.0, -n_cam[0]) ** 6
    tot = up + side + front + left + 1e-6
    col = (LIGHT * up + DARK * side + MID * (front + left)) / tot
    return skia.Color(int(col[0]), int(col[1]), int(col[2]))


def pose(t):
    """Estado del cubo en el instante t (o None si no se ve)."""
    p = TL.RV
    a0, a1 = p["cube"]
    r = t - T["rv"]
    if not (a0 <= r <= a1):
        return None
    ph = {k: (T["rv"] + v[0], T["rv"] + v[1]) for k, v in p.items()}
    # A) el cuadrado plano crece y aparece la retícula
    grow = E.out_cubic(E.prog(t, *ph["grow"]))
    lines = E.prog(t, ph["grow"][0] + 0.35, ph["grow"][1] + 0.1)
    # B) se extruye en profundidad mientras gira a la vista isométrica
    ext = E.in_out_cubic(E.prog(t, *ph["extrude"]))
    # C) giro de capa (la superior gira 90°) y medio giro del cubo
    tw = E.in_out_cubic(E.prog(t, *ph["twist"]))
    spin = E.in_out_cubic(E.prog(t, *ph["spin"]))
    # D) se comprime de vuelta a un cuadrado plano y viaja a su sitio de cursor
    col = E.in_out_cubic(E.prog(t, *ph["collapse"]))
    home = E.in_out_cubic(E.prog(t, *ph["home"]))

    # un cubo de cubitos iguales se ve idéntico tras un cuarto de vuelta, así
    # que al terminar cada giro se vuelve al ángulo base sin que se note
    explode = E.out_cubic(E.prog(t, *ph["explode"])) * (1 - E.in_out_cubic(E.prog(t, *ph["implode"])))
    tw2 = E.in_out_cubic(E.prog(t, *ph["twist2"]))
    # deriva continua: el cubo nunca está quieto mientras es 3D
    life = E.prog(t, ph["extrude"][0], ph["collapse"][0])
    drift = math.radians(28) * life * ext
    bob = math.sin(2 * math.pi * 0.55 * (t - ph["extrude"][0])) * 10 * ext * (1 - col)

    # un cubo de cubitos iguales se ve idéntico tras un cuarto de vuelta, así
    # que al terminar cada giro se vuelve al ángulo base sin que se note
    yaw = math.radians(38) * ext + drift + (math.radians(-90) * spin if spin < 1 else 0.0)
    pitch = math.radians(26) * ext + math.radians(6) * math.sin(math.pi * life) * ext
    # al comprimir vuelve a mirar de frente: yaw equivalente más cercano a 0
    yaw_eq = (yaw + math.pi / 4) % (math.pi / 2) - math.pi / 4
    if col > 0:
        yaw = E.lerp(yaw_eq, 0.0, col)
    pitch = E.lerp(pitch, 0.0, col)
    depth = ext * (1 - col)
    gap = (0.07 * lines) * (1 - col) + 0.42 * explode + 0.05 * math.sin(math.pi * tw) + 0.05 * math.sin(math.pi * tw2)
    s_full = E.lerp(TL.CURSOR_PX / 3, CUBIE, grow)
    # al separarse el cubo crece un poco hacia la cámara (empuje)
    s_full *= 1 + 0.08 * explode
    size = E.lerp(s_full, TL.CURSOR_PX / 3, col)
    cx = E.lerp(CENTER[0], TL.HOME[0], home)
    cy = E.lerp(CENTER[1] + bob, TL.HOME[1], home)
    return dict(yaw=yaw, pitch=pitch, depth=depth, gap=gap, size=size, center=(cx, cy),
                twist=math.radians(90) * tw if tw < 1 else 0.0,
                twist2=math.radians(90) * tw2 if tw2 < 1 else 0.0,
                explode=explode, lines=lines * (1 - col), alpha=1.0)


def draw(c, t):
    st = pose(t)
    if st is None:
        return
    R = _rot_x(st["pitch"]) @ _rot_y(st["yaw"])
    tw_R = _rot_y(st["twist"])
    tw2_R = _rot_x(st["twist2"])
    s, g, d = st["size"], st["gap"], st["depth"]
    cx, cy = st["center"]
    faces = []
    for (i, j, k) in _CUBIES:
        # la capa superior (j = -1) gira primero; luego la derecha (i = +1)
        Mt = tw_R if j == -1 else np.eye(3)
        if i == 1:
            Mt = tw2_R @ Mt
        pos = np.array([i, j, k * d], float) * (1 + g)
        # al separarse, cada cubito gira un poco sobre sí mismo (determinista)
        ex = st["explode"]
        Sc = np.eye(3)
        if ex > 0:   # giro propio, alrededor del centro del cubito
            Sc = _rot_y(ex * 0.24 * ((i * 7 + j * 3 + k * 5) % 5 - 2)) @ _rot_x(ex * 0.2 * ((i * 3 + j * 5 + k * 7) % 5 - 2))
        scale = np.array([1.0, 1.0, max(d, 0.002)])
        for n, verts in _F:
            # en plano (d≈0) solo se dibuja la cara frontal, sin costuras
            if d < 0.02 and not (n[2] < 0 and k == -1):
                continue
            vw = ((verts * scale) @ Sc.T + pos) @ Mt.T @ R.T * s
            nw = (Mt @ Sc @ (n / scale)) @ R.T
            nw /= np.linalg.norm(nw) + 1e-9
            z = vw[:, 2] + CAM_DIST
            if np.any(z <= 50):
                continue
            px = cx + vw[:, 0] * FOCAL / z
            py = cy + vw[:, 1] * FOCAL / z
            # descarte de caras que no miran a la cámara (cámara en z = -CAM_DIST)
            fc = vw.mean(axis=0)
            if d >= 0.02 and float(nw @ np.array([fc[0], fc[1], fc[2] + CAM_DIST])) >= 0:
                continue
            faces.append((z.mean(), px, py, nw))
    faces.sort(key=lambda f: -f[0])
    edge = paint(EDGE, 0.45 * st["lines"] + 0.12 * d, stroke=1.6)
    edge.setStrokeJoin(skia.Paint.kRound_Join)
    for _, px, py, nw in faces:
        path = skia.Path()
        path.moveTo(px[0], py[0])
        for q in range(1, 4):
            path.lineTo(px[q], py[q])
        path.close()
        col = _shade(nw) if d >= 0.02 else skia.Color(0x8B, 0x2C, 0xF5)
        c.drawPath(path, skia.Paint(AntiAlias=True, Color=col))
        if st["lines"] > 0.01 or d > 0.02:
            c.drawPath(path, edge)
