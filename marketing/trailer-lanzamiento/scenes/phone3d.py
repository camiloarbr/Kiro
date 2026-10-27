"""El celular 3D de la landing (DemoKiroBot.astro, «Así se ve en tu negocio»)
dentro de la escena de la solución, cuando el narrador dice «software a tu
medida».

Como en la web: el celular llega desde el fondo girando sobre su eje vertical
(translateZ −320 px, rotateY −28° → −10°), muestra la conversación y se va
hacia la izquierda girando (rotateY 32°) mientras entra el panel del negocio.
Diferencias por la regla de «la marca solo al final»: el contacto se llama
«Casa Ceiba», el avatar es el cuadrado violeta y no aparece «Kiro Bot».

Es 3D real: el plano del celular se proyecta en perspectiva con una
homografía (las 4 esquinas en 3D → pantalla) y Skia dibuja todo el contenido
vectorial con esa matriz. El grosor es una pila de siluetas detrás del frente.
"""
import math

import numpy as np
import skia

import config as cfg
from lib import ease as E
from lib import timeline as TL
from lib.draw import draw_text, font, paint, wrap

C, T, D = cfg.C, cfg.T, cfg.DEMO
S6 = TL.S6

# ── Geometría del celular (px locales; a escala 1 con z = 0) ─────────────
W, H = 470.0, 960.0
VP = (540.0, 960.0)            # punto de fuga (centro del cuadro)
POS = (0.0, 110.0)             # centro del celular respecto del punto de fuga → (540, 1070)
ZOOM = 1.15                    # tamaño del celular en pantalla (1 = 470 × 960 px)
FOCAL = 1500.0                 # «perspective» de la cámara
BEZEL, BODY_R, SCREEN_R = 16.0, 74.0, 58.0
DEPTH, SLICES = 18.0, 9        # grosor del celular

SCR = skia.Rect.MakeLTRB(BEZEL, BEZEL, W - BEZEL, H - BEZEL)
HEAD_H = 150.0
INPUT = skia.Rect.MakeLTRB(SCR.left() + 16, SCR.bottom() - 16 - 74, SCR.right() - 16, SCR.bottom() - 16)
CHAT_X0, CHAT_X1 = SCR.left() + 22, SCR.right() - 22

F_MSG = ("geist500", 27)
LH, PAD_X, PAD_Y = 35.0, 22.0, 18.0
MAX_W = 0.84 * (CHAT_X1 - CHAT_X0)
GAP = 16.0
CUR = TL.CURSOR_PX / ZOOM      # en pantalla mide lo mismo que el cuadrado suelto
SLOT_H = CUR + 2 * 10          # el hueco donde el cuadrado «escribe»

SCREEN_COL = "#F6F4FA"
BODY_COL = "#0F0C14"
EDGE_COL = "#2A2433"
RIM_COL = "#4A4258"
INK = "#1F1A27"


def _bubble(text):
    f = font(*F_MSG)
    lines = wrap(text, f, MAX_W - 2 * PAD_X)
    w = max(f.measureText(l) for l in lines) + 2 * PAD_X
    h = 2 * PAD_Y + (len(lines) - 1) * LH + 28
    return lines, w, h


MSG1 = _bubble(D["cliente1"])
BOT = _bubble(D["bot1"])
MSG2 = _bubble(D["cliente2"])


# ── Pose 3D ──────────────────────────────────────────────────────────────
def _rot(ry, rx):
    """rotateY · rotateX con las convenciones de CSS (y hacia abajo, z hacia el espectador)."""
    cy, sy = math.cos(ry), math.sin(ry)
    cx, sx = math.cos(rx), math.sin(rx)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    return Ry @ Rx


def pose(t):
    """(rotY, rotX, traslación xyz, escala, opacidad) del celular, o None si no se ve."""
    r = t - T["s6"]
    i0, i1 = S6["phone_in"]
    o0, o1 = S6["phone_out"]
    if r < i0 or r > o1:
        return None
    k_in = E.in_out_cubic(E.prog(r, i0, i1))
    k_out = E.in_out_cubic(E.prog(r, o0, o1))
    hold = E.in_out_sine(E.prog(r, i1, o0))
    ry = E.lerp(-28, -10, k_in) + 6 * hold          # se acomoda despacio mientras hablan
    ry = E.lerp(ry, 32, k_out)
    rx = 4 * math.sin(math.pi * hold) * (1 - k_out)  # leve cabeceo
    bob = 7 * math.sin(2 * math.pi * 0.45 * (r - i0)) * k_in * (1 - k_out)
    tx = E.lerp(0, -230, k_out)
    tz = E.lerp(-320, 0, k_in) + E.lerp(0, -320, k_out)
    sc = E.lerp(0.9, 1.0, k_in) * ZOOM
    a_in = E.prog(r, i0, i0 + 0.8 * (i1 - i0))
    a_out = 1 - E.prog(r, o0, o0 + 0.75 * (o1 - o0)) ** 0.8
    return math.radians(ry), math.radians(rx), (tx, bob, tz), sc, a_in * a_out


def _project(p3):
    s = FOCAL / (FOCAL - p3[2])
    return VP[0] + p3[0] * s, VP[1] + p3[1] * s


def plane_matrix(rect, ry, rx, tr, sc, z=0.0, center=None):
    """Matriz (con perspectiva) que lleva el rectángulo plano rect a su
    proyección después de girar/trasladar. center = punto de pantalla donde está
    el centro del plano en reposo."""
    cx, cy = center if center else (rect.centerX(), rect.centerY())
    R = _rot(ry, rx)
    src, dst = [], []
    for (x, y) in [(rect.left(), rect.top()), (rect.right(), rect.top()),
                   (rect.right(), rect.bottom()), (rect.left(), rect.bottom())]:
        p = np.array([(x - rect.centerX()) * sc, (y - rect.centerY()) * sc, z])
        q = R @ p + np.array([tr[0] + cx - VP[0], tr[1] + cy - VP[1], tr[2]])
        src.append(skia.Point(x, y))
        dst.append(skia.Point(*_project(q)))
    m = skia.Matrix()
    m.setPolyToPoly(src, dst)
    return m


_PHONE_RECT = skia.Rect.MakeWH(W, H)
_PHONE_CENTER = (VP[0] + POS[0], VP[1] + POS[1])


def _phone_matrix(st, z=0.0):
    ry, rx, tr, sc, _ = st
    return plane_matrix(_PHONE_RECT, ry, rx, tr, sc, z, _PHONE_CENTER)


def project_local(t, x, y):
    """Punto local del celular → pantalla (para que el cuadrado entre y salga)."""
    st = pose(t)
    if st is None:
        return None
    pt = _phone_matrix(st).mapXY(x, y)
    return pt.x(), pt.y()


def local_scale(t):
    st = pose(t)
    if st is None:
        return 1.0
    ry, rx, tr, sc, _ = st
    return sc * FOCAL / (FOCAL - tr[2])


# ── Contenido (coordenadas locales) ──────────────────────────────────────
def _chat_layout(r):
    """Posición vertical de cada mensaje. Como en un chat real, los mensajes
    nuevos aparecen abajo y empujan a los anteriores hacia arriba."""
    k1 = E.out_cubic(E.prog(r, *S6["msg1"]))
    a0 = S6["cursor_to_chat"][1]
    k_slot = E.out_cubic(E.prog(r, a0 - 0.3, a0))
    k_bot = E.out_expo(E.prog(r, *S6["bot"]))
    k2 = E.out_cubic(E.prog(r, *S6["msg2"]))
    slot_h = E.lerp(SLOT_H, BOT[2], k_bot)
    items = [("msg1", MSG1[2], k1), ("slot", slot_h, k_slot), ("msg2", MSG2[2], k2)]
    y = INPUT.top() - 22
    out = {}
    for name, h, k in reversed(items):
        if k <= 0:
            out[name] = (y, k)
            continue
        out[name] = (y, k)           # y = borde inferior del mensaje
        y -= (h + GAP) * k
    return out, k_bot


def slot_cursor_rect(r):
    lay, _ = _chat_layout(r)
    yb, _ = lay["slot"]
    return skia.Rect.MakeXYWH(CHAT_X0, yb - 10 - CUR, CUR, CUR)


def bot_rect(r):
    lay, k_bot = _chat_layout(r)
    yb, _ = lay["slot"]
    return skia.Rect.MakeLTRB(CHAT_X0, yb - BOT[2], CHAT_X0 + BOT[1], yb)


def _rr(rect, tl, tr, br, bl):
    rr = skia.RRect()
    rr.setRectRadii(rect, [skia.Point(tl, tl), skia.Point(tr, tr), skia.Point(br, br), skia.Point(bl, bl)])
    return rr


def _client(c, spec, yb, k):
    if k <= 0:
        return
    lines, w, h = spec
    rect = skia.Rect.MakeLTRB(CHAT_X1 - w, yb - h, CHAT_X1, yb)
    c.save()
    s = 0.9 + 0.1 * k                    # m1 de la landing: sube y crece
    c.translate(rect.right(), rect.bottom() + (1 - k) * 30)
    c.scale(s, s)
    c.translate(-rect.right(), -rect.bottom())
    rr = _rr(rect, 26, 26, 7, 26)
    c.drawRRect(rr, paint("#FFFFFF", k))
    c.drawRRect(rr, paint("#E7E2EE", k, stroke=1.5))
    f = font(*F_MSG)
    for i, ln in enumerate(lines):
        draw_text(c, ln, rect.left() + PAD_X, rect.top() + PAD_Y + 22 + i * LH, f, INK, k)
    c.restore()


def _agent(c, r):
    """El cuadrado entra al chat, «escribe» y se expande en la respuesta."""
    a1 = S6["cursor_to_chat"][1]
    b0, b1 = S6["bot"]
    if r < a1:
        return
    if r < b0:
        cur = slot_cursor_rect(r)
        t0, t1 = S6["typing"]
        k = E.prog(r, t0, t1)
        sc = 1 - 0.2 * abs(math.sin(math.pi * k * 3)) if t0 <= r < t1 else 1
        cx, cy = cur.centerX(), cur.centerY()
        c.drawRect(skia.Rect.MakeXYWH(cx - CUR * sc / 2, cy - CUR * sc / 2, CUR * sc, CUR * sc), paint(C["violet"]))
        return
    k = E.out_expo(E.prog(r, b0, b1))
    cur = slot_cursor_rect(r)
    tgt = bot_rect(r)
    rect = skia.Rect.MakeLTRB(E.lerp(cur.left(), tgt.left(), k), E.lerp(cur.top(), tgt.top(), k),
                              E.lerp(cur.right(), tgt.right(), k), E.lerp(cur.bottom(), tgt.bottom(), k))
    rad = 26 * k
    c.drawRRect(_rr(rect, rad, rad, rad, 7 * k), paint(C["violet"]))
    ta = E.prog(r, b0 + 0.3, b1 + 0.1)
    f = font(*F_MSG)
    for i, ln in enumerate(BOT[0]):
        draw_text(c, ln, tgt.left() + PAD_X, tgt.top() + PAD_Y + 22 + i * LH, f, "#FFFFFF", ta)


def _screen(c, r):
    scr_rr = skia.RRect.MakeRectXY(SCR, SCREEN_R, SCREEN_R)
    c.drawRRect(scr_rr, paint(SCREEN_COL))
    c.save()
    c.clipRRect(scr_rr, doAntiAlias=True)
    # cabecera oscura con el contacto (el avatar es el cuadrado violeta)
    c.drawRect(skia.Rect.MakeLTRB(SCR.left(), SCR.top(), SCR.right(), SCR.top() + HEAD_H), paint(C["black"]))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(W / 2 - 52, SCR.top() + 14, 104, 30), 15, 15),
                paint("#000000"))
    av = skia.Rect.MakeXYWH(SCR.left() + 24, SCR.top() + 62, 60, 60)
    c.drawRRect(skia.RRect.MakeRectXY(av, 14, 14), paint(C["violet"]))
    draw_text(c, D["negocio"], av.right() + 18, av.top() + 26, font("geist600", 29), "#FFFFFF")
    draw_text(c, f'{D["agente"]} · en línea', av.right() + 18, av.top() + 56, font("geist500", 20),
              C["violet_light"])
    # conversación
    lay, _ = _chat_layout(r)
    _client(c, MSG1, *lay["msg1"])
    _agent(c, r)
    _client(c, MSG2, *lay["msg2"])
    # campo de texto
    c.drawRRect(skia.RRect.MakeRectXY(INPUT, 37, 37), paint("#FFFFFF"))
    c.drawRRect(skia.RRect.MakeRectXY(INPUT, 37, 37), paint("#E7E2EE", stroke=1.5))
    draw_text(c, "Escribe un mensaje", INPUT.left() + 28, INPUT.centerY() + 8, font("geist400", 23), "#6F6780")
    c.drawCircle(INPUT.right() - 37, INPUT.centerY(), 26, paint(C["violet"]))
    c.restore()


def draw(c, t):
    st = pose(t)
    if st is None:
        return
    alpha = st[4]
    if alpha <= 0.003:
        return
    r = t - T["s6"]
    c.saveLayerAlpha(skia.Rect.MakeWH(cfg.W, cfg.H), int(255 * alpha))
    body = skia.RRect.MakeRectXY(_PHONE_RECT, BODY_R, BODY_R)
    # grosor: siluetas del cuerpo desde atrás hacia el frente
    for i in range(SLICES):
        z = -DEPTH * (1 - i / (SLICES - 1))
        c.save()
        c.concat(_phone_matrix(st, z))
        c.drawRRect(body, paint(EDGE_COL if i < SLICES - 2 else RIM_COL))
        c.restore()
    c.save()
    c.concat(_phone_matrix(st))
    c.drawRRect(body, paint(BODY_COL))
    c.drawRRect(body, paint(RIM_COL, 0.9, stroke=2.0))
    _screen(c, r)
    c.restore()
    c.restore()
