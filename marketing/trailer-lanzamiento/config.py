"""Configuración editable del tráiler «Todo comienza con un punto».

Todo lo que normalmente se querría cambiar vive aquí: tiempos, textos,
colores, voz y salida. La animación (render.py) y el audio (audio/build_audio.py)
leen ESTE archivo, así que un cambio de tiempo mueve imagen y sonido juntos.
"""

# ── Salida ───────────────────────────────────────────────────────────────
VERSION = "v6"           # nombre del render: out/kiro-trailer-v6-<voz>.mp4 (no pisa versiones anteriores)
W, H = 1080, 1920
FPS = 30
DURATION = 43.3          # segundos totales (incluye la cola de silencio)

# ── Voz ──────────────────────────────────────────────────────────────────
# Carpeta dentro de audio/voz/. v5: «carlos» (ElevenLabs, «Carlos – Premium
# Latin American Spanish Narrator (Español Neutro)», modelo eleven_v4).
# Alternativas cortadas igual: «luismiguel», «lujan» (ElevenLabs, latinas);
# «brian», «george» (ElevenLabs anglo, v1–v4); «claude», «ald» (Piper).
# Las tomas completas están en audio/voz/tomas/ y se cortan con
# audio/split_take.py, que también mide las palabras para los subtítulos.
VOICE = "carlos"

import os as _os
VOICE = _os.environ.get("KIRO_VOICE", VOICE)   # build.py --voice lo cambia sin editar este archivo

# ── Paleta oficial (manual de marca v1.0) ────────────────────────────────
C = dict(
    violet="#8B2CF5",       # Kiro Violet: cursor y acciones de Kiro (máx. 10 %)
    violet_dark="#5B17B8",
    violet_light="#B07CFF", # texto de acento sobre negro
    black="#0C0A10",        # fondo
    graphite="#1F1A27",     # superficies
    graphite_2="#2A2433",   # superficies elevadas (derivado de grafito)
    gray="#918A9E",         # texto secundario
    white="#F6F4FA",        # texto
    lav="#D9C4FF",          # lavanda media (extensión web aprobada)
)

# ── Línea de tiempo (segundos) ───────────────────────────────────────────
# v2: el logo solo aparece al final. Orden: problema → solución → marca.
T = dict(
    cursor_on=1.60,     # E1 intriga: aparece el cuadrado, en el centro
    vo1=4.40,           # «Todo negocio empieza con una idea.» (casi 3 s de silencio antes)
    s2=7.30,            # E2 tensión: el cuadrado empieza a activar cosas
    vo2=7.80,           # «Pero cuando todo depende de hacerlo a mano…»
    s3=10.90,           # la complejidad se acumula
    vo3=11.10,          # «…cada tarea se convierte en otra complicación.»
    slow=13.60,         # el movimiento empieza a frenarse
    freeze=15.30,       # corte: todo se detiene
    s4=15.30,           # E3 pausa: se retira todo, silencio real
    vo4=16.80,          # «Hay otra forma.»
    s6=18.80,           # E4 la solución: el cuadrado ordena el espacio y trabaja
    vo6a=19.60,         # «Creamos software a tu medida, automatizaciones y agentes inteligentes,»
    vo6b=24.75,         # «para que tu negocio trabaje mejor.»
    rv=29.20,           # E5 revelación: la interfaz converge; transición 3D (cubo de la landing)
    s5=36.50,           # el cuadrado empieza a transformarse en «kiro» (única vez)
    logo_done=39.50,    # «kiro» queda completo (impacto)
    vo5=40.05,          # «Kiro.»  (el cierre solo dice el nombre)
    close=41.00,        # el logo queda quieto (dirección web solo si config.URL no está vacía)
    sting=41.65,        # firma sonora final (parpadeo del cursor)
)

# ── Narración ────────────────────────────────────────────────────────────
# (archivo en audio/voz/<VOICE>/, cue de inicio, texto, palabras con tiempos
#  relativos de la toma «brian» medidos con ElevenLabs Scribe; con otra voz
#  los subtítulos se reparten solos a lo largo de la frase).
_TEXTS = [
    ("01-idea", "vo1", "Todo negocio empieza con una idea."),
    ("02-a-mano", "vo2", "Pero cuando todo depende de hacerlo a mano,"),
    ("03-crecimiento", "vo3", "cada tarea se convierte en otra complicación."),
    ("04-otra-forma", "vo4", "Hay otra forma."),
    ("05-kiro", "vo5", "Kiro."),
    ("06a-creamos", "vo6a", "Creamos software a tu medida, automatizaciones y agentes inteligentes,"),
    ("06b-para-que", "vo6b", "para que tu negocio trabaje mejor."),
]


def _load_vo():
    """Frases de config + tiempos por palabra medidos (audio/voz/<VOICE>/words.json)."""
    import json
    from pathlib import Path
    wf = Path(__file__).resolve().parent / "audio" / "voz" / VOICE / "words.json"
    words = json.loads(wf.read_text(encoding="utf-8")) if wf.exists() else {}
    out = []
    for name, cue, text in _TEXTS:
        w = words.get(name)
        if not w:   # sin medición: reparto uniforme
            toks = text.split()
            w = [(tk, 0.1 + i * 1.8 / len(toks)) for i, tk in enumerate(toks)]
        out.append((f"{name}.mp3", cue, text, [(a, float(b)) for a, b in w]))
    return out


VO = _load_vo()
VO_TIMINGS_FOR = VOICE   # los tiempos ya vienen de la voz elegida

# Subtítulos discretos para quien ve sin sonido (Reels/TikTok arrancan mudos).
SUBTITULOS = True
SUBTITULOS_EN = ["vo1", "vo2", "vo3", "vo4"]   # en la solución hablan los rótulos; en el cierre, la frase

# ── Textos en pantalla ───────────────────────────────────────────────────
URL = ""   # v4: sin dirección web; el cierre es solo el logo. Para mostrarla: "kiro.kirosolutionsco.workers.dev"

# Rótulos de E4 (los tres conceptos), cada uno entra con su palabra en la voz
def _word_time(cue, word, default):
    for _, c, _, ws in VO:
        if c == cue:
            for w, t in ws:
                if w.lower().strip(",.") == word:
                    return t
    return default


CONCEPTOS = [   # cada rótulo entra cuando el narrador dice su palabra (segundos desde vo6a)
    ("Software a tu medida", _word_time("vo6a", "software", 0.6)),
    ("Automatizaciones", _word_time("vo6a", "automatizaciones", 2.4)),
    ("Agentes inteligentes", _word_time("vo6a", "agentes", 4.0)),
]

# Demo de E4 (mismo escenario de muestra que la landing; no es un cliente real).
# Sin el nombre de la marca: el agente se presenta solo como «Agente inteligente».
DEMO = dict(
    agente="Agente inteligente",
    negocio="Casa Ceiba",
    canal="WhatsApp",
    cliente1="Hola, ¿hay habitación para el sábado?",
    bot1="¡Hola! Sí, nos queda la habitación 8. ¿Te la reservo?",
    cliente2="Sí, por favor",
    confirmacion="Reserva confirmada · Hab. 8 · sáb",
    panel_titulo="Reservas",
    panel_sub="Casa Ceiba · vie a dom",
    filas=["Vie", "Sáb", "Dom"],
    columnas=["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"],
    ocupacion=[[1, 1, 0, 1, 1, 1, 0, 1],
               [1, 1, 1, 1, 1, 1, 1, 2],   # 2 = la que reserva Kiro
               [1, 0, 0, 1, 0, 1, 0, 0]],
)

# ── Composición ──────────────────────────────────────────────────────────
LOGO_SCALE = 0.40        # 1 unidad del SVG = 0,40 px → logo de ~710 px de ancho
LOGO_CENTER = (540, 880) # centro del logo completo (con «solutions»)
