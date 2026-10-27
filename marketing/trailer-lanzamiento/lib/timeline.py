"""Línea de tiempo derivada: posiciones del cursor, eventos de cada escena y
cues de sonido. La imagen y el audio leen este mismo módulo, así que siempre
quedan sincronizados (sin temporizadores ni azar)."""
import config as cfg
from lib import logo as L

T = cfg.T
S = cfg.LOGO_SCALE

# ── Transformación logo (unidades SVG) → pantalla ───────────────────────
_LOGO_UNITS_CENTER = ((L.LEFT + L.RIGHT) / 2, (L.CURSOR.top() + 994.0) / 2)
LOGO_OX = cfg.LOGO_CENTER[0] - _LOGO_UNITS_CENTER[0] * S
LOGO_OY = cfg.LOGO_CENTER[1] - _LOGO_UNITS_CENTER[1] * S


def to_screen(ux, uy):
    return (LOGO_OX + ux * S, LOGO_OY + uy * S)


CURSOR_PX = L.CURSOR_SIDE * S                         # ~62 px
HOME = to_screen(L.CURSOR.centerX(), L.CURSOR.centerY())  # sitio del cursor en el logo
START = (cfg.W / 2, cfg.H / 2)                        # v3: el cuadrado empieza en el centro

# v3: la escena 2 se dibuja 110 px más arriba para dejar sitio a subtítulos grandes
MANUAL_DY = -110

# ── Escenas 2–3: fragmentos de trabajo manual ───────────────────────────
ANCHORS = dict(          # coordenadas de pantalla (ya incluyen MANUAL_DY)
    sheet=(452 + 31, 706 - 110),   # esquina superior izquierda de la hoja
    chat=(110, 1030 - 110),
    todo=(600, 1178 - 110),
    log=(118, 390 - 110),
    chat2=(110, 1370 - 110),
)

# Movimientos del cursor en E2: (sale, llega, destino, evento que dispara)
def _s2_moves():
    """Recorrido de E2: cada viaje dura según su distancia (velocidad legible,
    sin saltos) y entre viaje y viaje el cuadrado se detiene un instante."""
    import math
    seq = ["sheet", "chat", "todo", "log", "chat2"]
    moves, pos, t = [], START, T["s2"]
    for k in seq:
        dst = ANCHORS[k]
        dur = min(1.0, max(0.55, math.dist(pos, dst) / 1100.0))
        moves.append((t, t + dur, k))
        t += dur + 0.22
        pos = dst
    return moves


S2_MOVES = _s2_moves()

# E3: el cursor va y viene cada vez más rápido y luego se frena
_S3_CYCLE = ["sheet", "chat", "todo", "log", "chat2", "sheet", "todo", "chat",
             "log", "sheet", "chat2", "todo", "chat", "sheet", "log", "chat2"]


def _s3_moves():
    # empieza solo cuando el último movimiento de E2 ya llegó (antes se
    # solapaban y el cuadrado saltaba de un sitio a otro en un fotograma)
    last_s2 = max(a for (_, a, _) in S2_MOVES)
    moves, t, i = [], max(T["s3"] - 0.1, last_s2 + 0.12), 0
    while True:
        # intervalo: se acorta hasta T['slow'] y luego se alarga (frenado)
        if t < T["slow"]:
            k = (t - T["s3"]) / (T["slow"] - T["s3"])
            interval = 0.66 - 0.26 * max(0.0, min(1.0, k))
        else:
            k = (t - T["slow"]) / (T["freeze"] - T["slow"])
            interval = 0.40 + 0.45 * k * k
        travel = interval * 0.86       # viaja casi todo el intervalo: nunca «salta»
        # los viajes largos se toman más tiempo (velocidad máxima legible)
        import math
        prev = ANCHORS[moves[-1][2]] if moves else ANCHORS[S2_MOVES[-1][2]]
        travel = max(travel, math.dist(prev, ANCHORS[_S3_CYCLE[i % len(_S3_CYCLE)]]) / 1500.0)
        arrive = t + travel
        if arrive > T["freeze"] - 0.12:
            break
        moves.append((t, arrive, _S3_CYCLE[i % len(_S3_CYCLE)]))
        t = max(t + interval, arrive + 0.06)
        i += 1
    return moves


S3_MOVES = _s3_moves()
ALL_MOVES = S2_MOVES + S3_MOVES

# Contenidos que se acumulan
SHEET_HEAD = ["HUÉSPED", "FECHA", "ESTADO"]
SHEET_ROWS = [
    ["Laura M.", "sáb", "¿pagó?"], ["Andrés P.", "vie", "pendiente"], ["—", "dom", "llamar"],
    ["Sofía R.", "sáb", "¿?"], ["Grupo 4", "vie", "cotizar"], ["Juan C.", "sáb", "pendiente"],
    ["—", "dom", "¿confirmó?"], ["Marta L.", "vie", "llamar"], ["Pedro A.", "sáb", "¿?"],
]
CHAT_MSGS = [   # pares: chat principal · impares: chat de abajo (cortos)
    "¿Tienen cupo el sábado?", "¿Me confirmas?", "¿Sigue disponible?", "Hola??",
    "¿Aceptan transferencia?", "¿Me respondes?", "¿A qué hora es el check-in?", "¿Hay parqueadero?",
]
LOG_LINES = [
    "› copiar datos del huésped", "› registro_FINAL_v3.xlsx", "› llamar a confirmar",
    "› pasar pago a mano", "› registro_FINAL_v4.xlsx", "› revisar WhatsApp",
    "› copiar datos otra vez",
]
TODO_ITEMS = ["Confirmar por WhatsApp", "Pasar a Excel", "Enviar cotización"]
BADGE_STEPS = [1, 3, 6, 11, 19, 27, 38, 54, 71]


def arrivals(kind, t):
    """Cuántas veces ha llegado el cursor al elemento `kind` hasta t."""
    return sum(1 for (_, a, k) in ALL_MOVES if k == kind and a <= t)


def first_arrival(kind):
    return min(a for (_, a, k) in ALL_MOVES if k == kind)


# ── E4: retirada ─────────────────────────────────────────────────────────
S4_ORDER = ["chat2", "log", "todo", "chat", "sheet"]   # orden en que desaparecen
S4_START = T["s4"] + 0.25
S4_STAGGER = 0.16
S4_DUR = 0.42
S4_CURSOR_HOME = (T["s4"] + 0.35, T["s4"] + 1.45)   # vuelve al centro (START)

# ── E5: transformación (segundos desde T['s5']) ─────────────────────────
S5 = dict(
    hop=(0.00, 0.55),        # anticipación: sube y cae
    extrude=(0.45, 1.05),    # el cuadrado se duplica y cae formando el palo de la i
    guides=(0.95, 1.45),     # los bordes del palo se extienden: línea base y altura x
    k_stem=(1.20, 1.65),
    asc=(1.42, 1.80),        # línea de ascendentes
    k_arm=(1.50, 1.88),
    k_leg=(1.62, 2.00),
    r_stem=(1.72, 2.08),
    r_shoulder=(1.98, 2.32),
    o=(1.86, 2.55),
    retract=(2.45, 2.90),
    blink=(3.15, 3.38),      # el cursor parpadea una vez cuando todo encaja
    solutions=(3.30, 4.10),
)
S5_DONE = 3.0                # = T['logo_done'] - T['s5']

# ── E4 (v2): la solución en acción (segundos desde T['s6']) ─────────────
S6 = dict(
    organize=(0.00, 1.05),   # el cuadrado traza la guía de la interfaz: ordena el espacio
    header=(0.55, 0.95),
    cursor_to_chat=(1.05, 1.55),
    msg1=(1.15, 1.50),
    typing=(1.75, 2.55),     # el cursor «piensa»: late como un indicador de escritura
    bot=(2.55, 3.10),        # el cuadrado se expande y se vuelve la respuesta
    msg2=(4.05, 4.40),
    cursor_out=(4.45, 4.85), # sale de la burbuja y va a la confirmación
    chip=(4.85, 5.30),
    panel=(4.90, 5.55),
    wire=(5.35, 6.10),       # conector chip → celda
    land=(6.10, 6.40),       # el cuadrado se vuelve la celda reservada
    paid=(6.80, 7.20),
)

# ── E5 (v2): revelación (segundos desde T['rv']) ────────────────────────
RV = dict(
    converge=(0.00, 0.85),   # la interfaz se recoge hacia el cuadrado
    to_center=(0.60, 1.25),  # el cuadrado (la celda) viaja al centro
    # transición 3D: el cubo 3×3×3 de la landing (scenes/cube3d.py)
    cube=(1.20, 6.95),
    grow=(1.20, 1.85),       # el cuadrado crece y aparece la retícula 3×3
    extrude=(1.75, 2.85),    # se extruye en profundidad y gira a vista 3/4
    explode=(2.90, 3.45),    # los 27 cubitos se separan…
    implode=(3.65, 4.05),    # …y vuelven a encajar
    twist=(4.10, 4.60),      # la capa superior gira 90°
    twist2=(4.70, 5.20),     # la capa derecha gira 90°
    spin=(5.15, 5.95),       # el cubo da un cuarto de vuelta
    collapse=(5.90, 6.50),   # se comprime en un cuadrado plano
    home=(6.25, 6.95),       # y vuelve a su sitio de cursor
)
RV["cube_home"] = RV["home"]  # compatibilidad: fin del viaje del cuadrado

# ── E6: cierre (absolutos) ─────────────────────────────────────────
CLOSE = dict(            # v3: el cierre solo muestra el logo y la dirección web
    url=(T["close"], T["close"] + 0.7),
)


# ── Cues de sonido (los lee audio/build_audio.py) ───────────────────────
def sound_cues():
    cues = []
    a = cues.append
    a((T["cursor_on"], "cursor_on"))
    for k in range(2):   # coincide con los apagados del parpadeo (scenes/cursor.py)
        a((T["cursor_on"] + 0.75 + 1.1 * k + 0.68, "blink_soft"))
    # E2: cada llegada del cursor activa algo
    for (dep, arr, kind) in ALL_MOVES:
        a((dep, "move"))
        a((arr, "activate_" + ("chat" if kind.startswith("chat") else kind)))
    a((T["freeze"], "freeze"))
    # E4: la solución
    s6 = T["s6"]
    a((s6 + S6["organize"][0], "lift"))
    a((s6 + 0.45, "guide_line"))
    a((s6 + S6["msg1"][0], "msg_in"))
    for k in range(4):
        a((s6 + S6["typing"][0] + k * 0.2, "type_tick"))
    a((s6 + S6["bot"][0], "bot_out"))
    a((s6 + S6["msg2"][0], "msg_in"))
    a((s6 + S6["chip"][0], "confirm"))
    a((s6 + S6["wire"][0], "wire"))
    a((s6 + S6["land"][0], "land"))
    a((s6 + S6["paid"][0], "ok"))
    # E5: revelación (única)
    rv = T["rv"]
    a((rv + RV["converge"][0], "converge"))
    a((rv + RV["grow"][0], "cube_grow"))
    a((rv + RV["grow"][0] + 0.4, "cube_grid"))
    a((rv + RV["extrude"][0], "cube_extrude"))
    a((rv + RV["explode"][0], "cube_explode"))
    a((rv + RV["implode"][1], "cube_lock"))
    a((rv + RV["twist"][0], "cube_twist"))
    a((rv + RV["twist"][1], "cube_lock"))
    a((rv + RV["twist2"][0], "cube_twist"))
    a((rv + RV["twist2"][1], "cube_lock"))
    a((rv + RV["spin"][0], "cube_spin"))
    a((rv + RV["spin"][1], "cube_lock"))
    a((rv + RV["collapse"][0], "cube_collapse"))
    a((rv + RV["home"][1], "cube_home"))
    s5 = T["s5"]
    a((s5 + S5["hop"][0], "lift"))
    a((s5 + S5["extrude"][0], "extrude"))
    a((s5 + S5["guides"][0], "guides"))
    for key, note in (("k_stem", 0), ("k_arm", 1), ("k_leg", 2), ("r_stem", 3), ("o", 4)):
        a((s5 + S5[key][0], f"build_{note}"))
    a((s5 + S5["retract"][0], "retract"))
    a((T["logo_done"], "impact"))
    a((s5 + S5["blink"][0], "blink"))
    a((T["sting"], "sting"))
    return sorted(cues)
