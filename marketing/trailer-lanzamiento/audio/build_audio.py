"""Identidad sonora y mezcla del tráiler.

Todo el sonido (salvo la voz) se sintetiza aquí con NumPy: es original, no
depende de librerías de terceros con licencia dudosa y es determinista
(semilla fija). Los cues salen de lib/timeline.py, igual que la animación.

Salidas en audio/stems/:
  voz.wav · musica.wav · efectos.wav · mezcla.wav (48 kHz, estéreo)

Firma sonora de Kiro: un «ping» de cursor (La5 puro con un clic de tecla)
sobre un acorde abierto de Re (Re–La–Mi–Fa#). Se oye cuando aparece el
cuadrado, cuando la palabra queda completa y al cerrar.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import signal

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import config as cfg  # noqa: E402
from lib import timeline as TL  # noqa: E402

SR = 48000
N = int(cfg.DURATION * SR)
T = cfg.T
RNG = np.random.default_rng(1729)       # semilla fija → mismo sonido siempre
STEMS = ROOT / "audio" / "stems"


# ── Utilidades ───────────────────────────────────────────────────────────
def db(x):
    return 10 ** (x / 20)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def env_exp(dur, attack=0.004, decay=0.3):
    t = t_axis(dur)
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-np.maximum(t - attack, 0) / decay)


def sine(f, dur, phase=0.0):
    t = t_axis(dur)
    if callable(f):
        ph = 2 * np.pi * np.cumsum(f(t)) / SR
        return np.sin(ph + phase)
    return np.sin(2 * np.pi * f * t + phase)


def noise(dur):
    return RNG.standard_normal(int(dur * SR))


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x)


def pan(x, p):
    """p: -1 izquierda … +1 derecha (ley de potencia constante)."""
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)])


def place(bus, x, at, gain=1.0, p=0.0):
    st = pan(x, p) if x.ndim == 1 else x
    i = int(round(at * SR))
    if i >= bus.shape[1]:
        return
    j = min(bus.shape[1], i + st.shape[1])
    bus[:, i:j] += gain * st[:, : j - i]


def screen_pan(x_px):
    return float(np.clip((x_px - 540) / 540 * 0.7, -0.8, 0.8))


# ── Instrumentos ─────────────────────────────────────────────────────────
def click(dur=0.012, bright=4500):
    x = hp(noise(dur), bright) * env_exp(dur, 0.0005, 0.0025)
    return x / (np.abs(x).max() + 1e-9)


def ping(f=880.0, dur=0.6, decay=0.22):
    """El sonido del cursor: seno puro + segundo parcial + clic."""
    x = sine(f, dur) + db(-16) * sine(2 * f, dur) + db(-28) * sine(3 * f, dur)
    x *= env_exp(dur, 0.002, decay)
    c = click()
    x[: len(c)] += 0.35 * c
    return x * 0.8


def thump(dur=0.5, f0=95, f1=42, decay=0.16):
    f = lambda t: f1 + (f0 - f1) * np.exp(-t / 0.05)
    return sine(f, dur) * env_exp(dur, 0.003, decay)


def pluck(f, dur=1.4, bright=0.5):
    """Karplus–Strong: cuerda pulsada suave (para el pulso de E6–E7)."""
    n = int(dur * SR)
    period = int(SR / f)
    buf = lp(RNG.uniform(-1, 1, period), 2000 + 5000 * bright, 1)
    out = np.zeros(n)
    b = buf.copy()
    for i in range(n):
        k = i % period
        out[i] = b[k]
        b[k] = 0.4985 * (b[k] + b[(k + 1) % period])
    return lp(out, 5200) * env_exp(dur, 0.002, dur * 0.45)


def soft_note(f, dur, attack=0.02, decay=0.6, harm=0.18):
    x = sine(f, dur) + harm * sine(2 * f, dur) + 0.05 * sine(3 * f, dur)
    return x * env_exp(dur, attack, decay)


def whoosh(dur=0.35, lo=400, hi=3000, peak=0.5):
    t = t_axis(dur)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    e = np.where(t / dur < peak, np.sin(np.pi / 2 * t / (dur * peak)) ** 2,
                 np.cos(np.pi / 2 * (t - dur * peak) / (dur * (1 - peak))) ** 2)
    return bp(noise(dur), lo, hi) * e


def sweep_noise(dur, f_from, f_to, q=1.5):
    """Ruido filtrado con un pasabanda que se desliza (por bloques)."""
    x = noise(dur)
    out = np.zeros_like(x)
    blk = 960
    for i in range(0, len(x), blk):
        k = i / len(x)
        fc = f_from * (f_to / f_from) ** k
        lo, hi = fc / (1 + 1 / q), min(fc * (1 + 1 / q), SR / 2 - 100)
        seg = x[max(0, i - 2048): i + blk]
        y = bp(seg, lo, hi)
        out[i: i + blk] = y[-len(out[i: i + blk]):]
    t = t_axis(dur)
    return out * np.sin(np.pi * t / dur) ** 1.5


def chord(freqs, dur, attack=0.06, decay=1.8, spread=0.5):
    st = np.zeros((2, int(dur * SR)))
    for i, f in enumerate(freqs):
        p = spread * ((i / max(1, len(freqs) - 1)) * 2 - 1)
        st += pan(soft_note(f, dur, attack, decay, 0.12) / len(freqs) * 2, p)
    return st


def reverb(x, seconds=1.8, wet=0.22, seed=7):
    """Convolución con una cola exponencial de ruido (estéreo decorrelado)."""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    tail = np.exp(-t / (seconds / 6.9))
    out = np.zeros((2, x.shape[1] + n - 1))
    for ch in range(2):
        ir = lp(rng.standard_normal(n), 6500) * tail
        ir[: int(0.012 * SR)] = 0            # predelay
        ir /= np.sqrt(np.sum(ir ** 2))
        out[ch] = signal.fftconvolve(x[ch], ir)
    return x + wet * out[:, : x.shape[1]]


# ── Voz ──────────────────────────────────────────────────────────────────
def load_mp3(path):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", str(path), "-f", "f32le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def build_voice():
    bus = np.zeros((2, N))
    vdir = ROOT / "audio" / "voz" / cfg.VOICE
    for fname, cue, *_ in cfg.VO:
        x = load_mp3(vdir / fname)
        x = hp(x, 70)
        # nivela cada frase al mismo RMS de habla (−20 dBFS)
        active = x[np.abs(x) > 0.02]
        rms = np.sqrt(np.mean(active ** 2)) if len(active) else 0.1
        x *= db(-20) / rms
        # cola suave para que ninguna frase corte en seco
        fade = int(0.03 * SR)
        x[-fade:] *= np.linspace(1, 0, fade)
        place(bus, x, T[cue], 1.0, 0.0)
    return bus


# ── Efectos sincronizados con la imagen ─────────────────────────────────
def build_sfx():
    fx = np.zeros((2, N))
    home_p = screen_pan(TL.HOME[0])
    for at, kind in TL.sound_cues():
        if kind == "cursor_on":
            place(fx, ping(880, 1.2, 0.35), at, db(-12), home_p)
        elif kind == "blink_soft":
            pass   # v5: el intro queda en silencio mientras el cursor parpadea
        elif kind == "move":
            place(fx, whoosh(0.22, 700, 3200), at, db(-43), 0)
        elif kind.startswith("activate_"):
            what = kind.split("_", 1)[1]
            px = TL.ANCHORS.get(what, (540, 0))[0]
            p = screen_pan(px)
            if what == "sheet":
                for k in range(3):
                    place(fx, click(0.01, 3000), at + k * 0.045, db(-27), p)
                place(fx, soft_note(1174.7, 0.25, 0.002, 0.06), at, db(-30), p)
            elif what == "chat":
                place(fx, soft_note(1318.5, 0.35, 0.002, 0.08), at, db(-28), p)
                place(fx, soft_note(1760.0, 0.4, 0.002, 0.1), at + 0.07, db(-30), p)
            elif what == "todo":
                place(fx, whoosh(0.18, 1500, 6000, 0.3), at, db(-30), p)
                place(fx, soft_note(523.3, 0.3, 0.002, 0.07), at, db(-28), p)
            elif what == "log":
                for k in range(5):
                    place(fx, click(0.008, 2500), at + 0.03 + k * 0.055 + 0.012 * (k % 2), db(-30), p)
        elif kind == "freeze":
            place(fx, click(0.02, 1800), at, db(-12), home_p)
            place(fx, thump(0.25, 120, 60, 0.05), at, db(-16), 0)
        elif kind == "lift":
            f = lambda t: 440 * 2 ** (t / 0.3)
            place(fx, sine(f, 0.3) * env_exp(0.3, 0.12, 0.12), at, db(-30), home_p)
        elif kind == "extrude":
            place(fx, sweep_noise(0.55, 5000, 500), at, db(-24), home_p)
            f = lambda t: 330 * 0.5 ** (t / 0.4)
            place(fx, sine(f, 0.5) * env_exp(0.5, 0.01, 0.2), at, db(-24), home_p)
        elif kind == "guides":
            for side in (-1, 1):
                x = soft_note(2637, 0.6, 0.15, 0.2, 0.05) * 0.5 + 0.5 * soft_note(3520, 0.6, 0.2, 0.2, 0)
                st = np.stack([x * (0.5 - 0.5 * side * np.linspace(0, 1, len(x))),
                               x * (0.5 + 0.5 * side * np.linspace(0, 1, len(x)))])
                place(fx, st, at + (0.08 if side > 0 else 0), db(-31))
        elif kind.startswith("build_"):
            i = int(kind[-1])
            notes = [293.66, 369.99, 440.0, 554.37, 659.26]       # Re – Fa# – La – Do# – Mi
            pans = [-0.45, -0.3, -0.15, 0.15, 0.4]
            place(fx, pluck(notes[i], 1.2, 0.7), at, db(-17), pans[i])
            place(fx, thump(0.2, 140, 70, 0.04), at, db(-26), pans[i])
        elif kind == "retract":
            place(fx, sweep_noise(0.45, 600, 4000)[::-1], at, db(-32), 0)
        elif kind == "impact":
            place(fx, thump(1.0, 80, 38, 0.32), at, db(-12), 0)
            place(fx, chord([73.42, 110.0, 146.83, 220.0, 329.63, 369.99], 4.0, 0.03, 1.6, 0.6), at, db(-13))
            place(fx, ping(880, 1.6, 0.55), at + 0.02, db(-14), home_p)
        elif kind == "blink":
            place(fx, ping(1760, 0.3, 0.05), at, db(-30), home_p)
        elif kind == "dissolve":
            place(fx, sweep_noise(0.6, 4000, 700), at, db(-30), 0)
        elif kind == "msg_in":
            place(fx, soft_note(1318.5, 0.3, 0.002, 0.07), at, db(-27), -0.3)
            place(fx, click(0.008), at, db(-32), -0.3)
        elif kind == "type_tick":
            place(fx, click(0.008, 3500), at, db(-31), 0.4)
        elif kind == "bot_out":
            f = lambda t: 587.3 * 1.5 ** np.clip(t / 0.25, 0, 1)
            place(fx, sine(f, 0.6) * env_exp(0.6, 0.05, 0.18), at, db(-24), 0.3)
            place(fx, ping(880, 0.6, 0.18), at + 0.24, db(-22), 0.3)
        elif kind == "confirm":
            place(fx, ping(880, 0.5, 0.12), at, db(-22), -0.1)
            place(fx, ping(1318.5, 0.6, 0.16), at + 0.11, db(-24), -0.1)
        elif kind == "wire":
            place(fx, sweep_noise(0.75, 1200, 5000) * 0.7, at, db(-31), 0.4)
        elif kind == "land":
            place(fx, ping(880, 0.9, 0.3), at, db(-17), 0.45)
            place(fx, thump(0.4, 100, 50, 0.1), at, db(-20), 0.3)
        elif kind == "ok":
            place(fx, soft_note(1760, 0.3, 0.002, 0.06), at, db(-30), 0.4)
        elif kind == "guide_line":
            # el cuadrado traza la guía: un barrido limpio de izquierda a derecha
            x = sweep_noise(0.6, 2500, 6000) * 0.6 + 0.4 * soft_note(1760, 0.6, 0.2, 0.25, 0)
            st = np.stack([x * np.linspace(1, 0.2, len(x)), x * np.linspace(0.2, 1, len(x))])
            place(fx, st, at, db(-30))
        elif kind == "converge":
            # la interfaz es absorbida por el cuadrado (barrido inverso que se cierra)
            place(fx, sweep_noise(0.85, 600, 5000)[::-1], at, db(-26), 0)
        elif kind == "cube_grow":
            f = lambda t: 220 * 2 ** (np.clip(t / 0.6, 0, 1))
            place(fx, sine(f, 0.8) * env_exp(0.8, 0.25, 0.3), at, db(-27), 0)
        elif kind == "cube_grid":
            for q in range(3):
                place(fx, click(0.008, 4000), at + q * 0.06, db(-30), -0.3 + 0.3 * q)
        elif kind == "cube_extrude":
            place(fx, sweep_noise(1.2, 300, 2400) * 0.8, at, db(-25), 0)
            f = lambda t: 73.42 * (1 + 0.5 * np.clip(t / 1.0, 0, 1))
            place(fx, sine(f, 1.4) * env_exp(1.4, 0.4, 0.5), at, db(-20), 0)
        elif kind == "cube_explode":
            place(fx, thump(0.8, 70, 35, 0.25), at, db(-17), 0)
            st = np.stack([sweep_noise(0.9, 400, 5000), sweep_noise(0.9, 500, 5200)])
            place(fx, st, at, db(-26))
            place(fx, chord([293.66, 440.0, 659.26], 1.2, 0.01, 0.5, 0.8), at + 0.05, db(-30))
        elif kind == "cube_twist":
            st = np.stack([sweep_noise(0.55, 900, 4200), sweep_noise(0.55, 900, 4200)[::-1]])
            place(fx, st, at, db(-27))
        elif kind == "cube_lock":
            place(fx, thump(0.25, 160, 90, 0.04), at, db(-20), 0)
            place(fx, click(0.012, 2200), at, db(-22), 0)
            place(fx, soft_note(587.33, 0.5, 0.002, 0.12), at, db(-28), 0)
        elif kind == "cube_spin":
            place(fx, whoosh(0.8, 300, 2000, 0.55), at, db(-26), 0)
        elif kind == "cube_collapse":
            place(fx, sweep_noise(0.65, 600, 4500)[::-1] * 0.9, at, db(-25), 0)
        elif kind == "cube_home":
            place(fx, thump(0.4, 90, 45, 0.1), at, db(-24), home_p)
            place(fx, ping(880, 0.8, 0.25), at, db(-24), home_p)
        elif kind == "sting":
            place(fx, ping(880, 1.8, 0.6), at, db(-13), home_p)
            place(fx, ping(1318.5, 1.6, 0.5), at + 0.14, db(-19), home_p + 0.1)
            place(fx, chord([73.42, 146.83, 220.0, 369.99, 554.37], 3.2, 0.08, 1.2, 0.6), at, db(-17))
    return reverb(fx, 1.6, 0.16)


# ── Música / camas ───────────────────────────────────────────────────────
def build_music():
    mu = np.zeros((2, N))
    t_full = np.arange(N) / SR

    # E2–E3: cama tonal (sin ruido de fondo). El inicio queda en silencio real:
    # solo el «ping» del cursor. La cama entra cuando aparece el problema,
    # crece con la tensión y se corta en seco en el freeze.
    drone = (sine(55.0, cfg.DURATION) + 0.6 * sine(82.41, cfg.DURATION) + 0.25 * sine(110.0, cfg.DURATION))
    lfo = 0.8 + 0.2 * np.sin(2 * np.pi * 0.11 * t_full)
    k_in = np.clip((t_full - T["s2"]) / 2.5, 0, 1) ** 2
    k_up = 0.6 + 0.4 * np.clip((t_full - T["s3"]) / (T["freeze"] - T["s3"]), 0, 1)
    gate = (t_full < T["freeze"]).astype(float)
    mu += pan(lp(drone * lfo, 400) * k_in * k_up * gate, 0) * db(-30)

    # E2–E3: pulso que se acelera y luego se frena
    beats, tb = [], T["s2"] + 0.2
    while tb < T["freeze"] - 0.05:
        beats.append(tb)
        if tb < T["s3"]:
            step = 1.0
        elif tb < T["slow"]:
            step = 1.0 - 0.6 * (tb - T["s3"]) / (T["slow"] - T["s3"])
        else:
            step = 0.4 + 0.6 * ((tb - T["slow"]) / (T["freeze"] - T["slow"])) ** 1.5
        tb += step
    for i, b in enumerate(beats):
        lvl = -24 + 8 * min(1, (b - T["s2"]) / (T["freeze"] - T["s2"]))
        place(mu, thump(0.35, 70, 40, 0.09), b, db(lvl), 0)

    # E3: tensión (ruido que sube de banda + racimo de senos desafinados)
    dur = T["freeze"] - T["s3"]
    tt = t_axis(dur)
    cl = (sine(110.0, dur) + sine(116.54, dur) + 0.6 * sine(164.81, dur) + 0.5 * sine(233.08, dur))
    cl = lp(cl, 900)
    swell = (tt / dur) ** 2.2
    rise = sweep_noise(dur, 300, 4500) * 0.6
    tension = (cl * 0.35 + rise) * swell
    place(mu, tension, T["s3"], db(-20), 0)

    # E4: recuperación controlada — pulso estable (96 BPM) en Re, cuerdas pulsadas y colchón
    bpm = 96.0
    beat = 60 / bpm
    start = T["s6"] + 0.35
    end = T["rv"] + 0.9                 # se detiene cuando la interfaz converge
    arp = [146.83, 220.0, 329.63, 369.99, 220.0, 329.63, 440.0, 369.99]   # Re–La–Mi–Fa#
    n = int((end - start) / (beat / 2))
    for i in range(n):
        at = start + i * beat / 2
        k = min(1, i / 8) * min(1, (end - at) / 1.2)
        place(mu, pluck(arp[i % len(arp)], 1.0, 0.45), at, db(-29) * k, 0.35 * np.sin(i * 0.9))
        if i % 2 == 0:
            place(mu, thump(0.3, 75, 45, 0.08), at, db(-28) * k, 0)
    pad_dur = (T["rv"] + 1.6) - start
    pad = chord([73.42, 110.0, 146.83, 220.0, 277.18, 329.63], pad_dur, 1.2, 99, 0.7)
    tp = t_axis(pad_dur)
    pad *= np.clip(tp / 1.5, 0, 1) * np.clip((pad_dur - tp) / 1.4, 0, 1)
    place(mu, pad, start, db(-27))

    # E5: colchón que acompaña la transición 3D y lleva a la revelación
    c0 = T["rv"] + TL.RV["grow"][0]
    d = T["s5"] + 0.4 - c0
    tt = t_axis(d)
    swell = chord([73.42, 110.0, 146.83, 220.0, 329.63], d, 0.8, 99, 0.6)
    swell *= np.clip(tt / 1.2, 0, 1) * (0.5 + 0.5 * tt / d) * np.clip((d - tt) / 0.5, 0, 1)
    place(mu, lp(swell, 1600), c0, db(-27))

    # E5: el cuadrado solo — una nota grave que crece hacia la transformación
    a0 = T["rv"] + TL.RV["cube_home"][1] - 0.3
    d = T["s5"] + 0.6 - a0
    tt = t_axis(d)
    held = (sine(73.42, d) + 0.5 * sine(146.83, d)) * (tt / d) ** 1.6
    place(mu, held, a0, db(-26), 0)

    # E6: colchón sereno bajo la frase final, hasta después de la firma
    c0 = T["logo_done"] + 1.2
    d = cfg.DURATION - c0
    tt = t_axis(d)
    pad2 = chord([73.42, 146.83, 220.0, 329.63, 369.99], d, 1.5, 99, 0.6)
    pad2 *= np.clip(tt / 1.5, 0, 1) * np.clip((T["sting"] + 1.0 - c0 - tt) / 1.2, 0, 1)
    place(mu, pad2, c0, db(-29))
    return reverb(mu, 2.2, 0.2, seed=11)


# ── Mezcla ───────────────────────────────────────────────────────────────
def duck(music, voice, depth_db=-8):
    """Baja la música cuando habla el narrador (sidechain suave)."""
    env = np.abs(voice).max(axis=0)
    env = lp(env, 6, 1)
    env = np.clip(env / (env.max() + 1e-9) * 4, 0, 1)
    att = signal.lfilter([1 - 0.9995], [1, -0.9995], env)
    g = db(depth_db * np.clip(att * 1.6, 0, 1))
    return music * g


def limiter(x, ceiling_db=-1.5, look=0.004, release=0.12):
    """Limitador con anticipación: nunca supera el techo y no distorsiona."""
    ceil = db(ceiling_db)
    peak = np.abs(x).max(axis=0)
    w = int(look * SR)
    # máximo en ventana (anticipación)
    from scipy.ndimage import maximum_filter1d
    env = maximum_filter1d(peak, size=2 * w + 1)
    g = np.minimum(1.0, ceil / np.maximum(env, 1e-9))
    # liberación suave
    a = np.exp(-1 / (release * SR))
    out = np.empty_like(g)
    prev = 1.0
    for i in range(len(g)):     # ataque instantáneo, liberación exponencial
        prev = g[i] if g[i] < prev else a * prev + (1 - a) * g[i]
        out[i] = prev
    out = np.minimum(out, g)
    return x * out


def hard_silence(x):
    """Pausa: el sonido se corta de verdad en el freeze (sin colas de reverberación)."""
    a = int((T["freeze"] + 0.14) * SR)
    b = int((T["s6"] - 0.05) * SR)
    f = int(0.03 * SR)
    g = np.ones(x.shape[1])
    g[a:a + f] = np.linspace(1, 0, f)
    g[a + f:b] = 0
    return x * g


def write(path, x):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (np.clip(x.T, -1, 1) * 32767).astype("<i2").tobytes()
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    str(path)], input=data, check=True)
    print("→", path)


def cfg_target():
    return -14.0


def main():
    voice = build_voice()
    sfx = build_sfx()
    music = build_music()
    music = duck(music, voice, -9)
    sfx_d = duck(sfx, voice, -9)
    music = hard_silence(music)
    sfx_d = hard_silence(sfx_d)
    mix = voice + music + sfx_d
    # micro fundido final (la cola de silencio ya está en la línea de tiempo)
    tail = int(0.4 * SR)
    mix[:, -tail:] *= np.linspace(1, 0, tail)
    # sonoridad de redes (≈ −14 LUFS) con techo de −1,5 dBFS
    import pyloudnorm as pyln
    meter = pyln.Meter(SR)
    for _ in range(3):
        lufs = meter.integrated_loudness(mix.T)
        mix = limiter(mix * db(cfg_target() - lufs))
    print(f"  mezcla: {meter.integrated_loudness(mix.T):.1f} LUFS, pico {20*np.log10(np.abs(mix).max()):.1f} dBFS")
    write(STEMS / "voz.wav", voice)
    write(STEMS / "musica.wav", music)
    write(STEMS / "efectos.wav", sfx)
    write(STEMS / "mezcla.wav", mix)


if __name__ == "__main__":
    main()
