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


# ── Instrumentos de impacto (v11) ────────────────────────────────────────
def sub_boom(dur=1.8, f0=62, f1=29, decay=0.55, drive=1.6):
    """Subgrave de cine: un seno que cae de tono, con un poco de saturación
    para que se sienta también en parlantes de celular (armónicos)."""
    f = lambda t: f1 + (f0 - f1) * np.exp(-t / 0.18)
    x = sine(f, dur) * env_exp(dur, 0.004, decay)
    return np.tanh(drive * x) / np.tanh(drive)


def crack(dur=0.12, lo=1800):
    """Transitorio brillante (el «chasquido» del golpe)."""
    x = hp(noise(dur), lo) * env_exp(dur, 0.0004, 0.02)
    return x / (np.abs(x).max() + 1e-9)


def body_hit(dur=0.45):
    """Cuerpo del golpe: ruido grave filtrado (un «bum» de aire)."""
    x = lp(noise(dur), 500) * env_exp(dur, 0.002, 0.09)
    return x / (np.abs(x).max() + 1e-9)


def rev_swell(dur=1.2, lo=250, hi=7000, curve=3.0):
    """Subida en reversa (estéreo): crece cada vez más rápido y corta en seco."""
    t = t_axis(dur)
    e = (t / dur) ** curve
    L = sweep_noise(dur, lo, hi) * e
    R = sweep_noise(dur, lo * 1.07, hi * 0.95) * e
    st = np.stack([L, R])
    return st / (np.abs(st).max() + 1e-9)


def reverse_ping(dur=1.3):
    """La firma del cursor al revés: el ping pasado por reverberación y
    reproducido hacia atrás (llega «aspirado» hasta el golpe)."""
    x = pan(ping(880, dur, 0.5), 0)
    wet = reverb(np.pad(x, ((0, 0), (0, int(1.5 * SR)))), 2.4, 1.2, seed=5)
    rev = wet[:, ::-1][:, -int(dur * SR):]
    return rev / (np.abs(rev).max() + 1e-9)


def wide_air(dur=2.6, lo=1200, hi=9000):
    """Apertura: aire brillante que se abre a los lados y se apaga lento."""
    t = t_axis(dur)
    e = np.exp(-t / (dur / 4)) * np.clip(t / 0.01, 0, 1)
    L = sweep_noise(dur, lo, hi) * e
    R = sweep_noise(dur, lo * 1.1, hi * 0.9) * e
    st = np.stack([L, R])
    return st / (np.abs(st).max() + 1e-9)


def tape_stop(x, t_end, dur=0.45):
    """La música «se apaga» como una cinta que se frena (el tono cae) justo
    antes del corte del freeze."""
    a, b = int((t_end - dur) * SR), int(t_end * SR)
    n = b - a
    k = np.arange(n) / n
    rate = (1 - k) ** 1.6                       # velocidad de la cinta: 1 → 0
    pos = a + np.cumsum(rate)                   # posición de lectura
    for ch in range(x.shape[0]):
        seg = np.interp(pos, np.arange(x.shape[1]), x[ch])
        x[ch, a:b] = seg * (1 - k ** 3)
    return x


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
            # el punto «se enciende»: ping de la firma + un grave suave que lo sostiene
            place(fx, ping(880, 1.2, 0.35), at, db(-12), home_p)
            place(fx, sub_boom(1.4, 70, 55, 0.4, 1.0), at, db(-25), 0)
            place(fx, rev_swell(0.5, 800, 5000, 4.0), at - 0.5, db(-36))
        elif kind == "blink_soft":
            pass   # v5: el intro queda en silencio mientras el cursor parpadea
        elif kind == "move":
            place(fx, whoosh(0.22, 700, 3200), at, db(-37), 0)
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
            # corte seco: golpe denso que se interrumpe con el silencio (0,14 s)
            place(fx, click(0.02, 1800), at, db(-11), home_p)
            place(fx, crack(0.1, 1500), at, db(-15))
            place(fx, sub_boom(0.6, 90, 38, 0.2), at, db(-9), 0)
            place(fx, body_hit(0.3), at, db(-14), 0)
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
            x = synth(notes[i], 1.2, 12.0, 2.5, 0.08, 0.002, 0.45) + 0.4 * synth(notes[i] * 2, 1.2, 8.0, 2.0, 0.06, 0.002, 0.3, detune=5)
            place(fx, x / 1.4, at, db(-19), pans[i])
            place(fx, thump(0.2, 140, 70, 0.04), at, db(-26), pans[i])
        elif kind == "retract":
            place(fx, sweep_noise(0.45, 600, 4000)[::-1], at, db(-32), 0)
        elif kind == "impact":
            # el logo queda completo: subida en reversa + golpe con subgrave
            place(fx, rev_swell(0.9, 300, 6000), at - 0.9, db(-24))
            place(fx, sub_boom(2.2, 60, 30, 0.6), at, db(-10), 0)
            place(fx, crack(0.1, 2500), at, db(-22))
            place(fx, thump(1.0, 80, 38, 0.32), at, db(-12), 0)
            place(fx, chord([73.42, 110.0, 146.83, 220.0, 329.63, 369.99], 4.0, 0.03, 1.6, 0.6), at, db(-13))
            place(fx, ping(880, 1.6, 0.55), at + 0.02, db(-14), home_p)
        elif kind == "blink":
            place(fx, ping(1760, 0.3, 0.05), at, db(-30), home_p)
        elif kind == "dissolve":
            place(fx, sweep_noise(0.6, 4000, 700), at, db(-30), 0)
        elif kind == "phone_in":
            # el celular llega desde el fondo: soplo que sube y un golpe suave al asentarse
            place(fx, whoosh(0.8, 250, 2200, 0.7), at, db(-29), 0)
            place(fx, thump(0.35, 110, 55, 0.08), at + 0.82, db(-27), 0)
        elif kind == "phone_out":
            # se va girando hacia la izquierda
            place(fx, sweep_noise(0.8, 2600, 500) * 0.8, at, db(-31), -0.5)
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
            place(fx, ping(880, 0.9, 0.3), at, db(-16), 0.45)
            place(fx, sub_boom(0.7, 85, 42, 0.18), at, db(-17), 0)
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
            # v18: vuelve el sonido de la v16 (el que le gustaba a Gallo)
            place(fx, sub_boom(1.2, 70, 32, 0.35), at, db(-13), 0)
            place(fx, crack(0.12, 1800), at, db(-20))
            place(fx, rev_swell(0.35, 500, 4000), at - 0.35, db(-28))
            place(fx, thump(0.8, 70, 35, 0.25), at, db(-17), 0)
            st = np.stack([sweep_noise(0.9, 400, 5000), sweep_noise(0.9, 500, 5200)])
            place(fx, st, at, db(-26))
            place(fx, chord([293.66, 440.0, 659.26], 1.2, 0.01, 0.5, 0.8), at + 0.05, db(-30))
        elif kind == "cube_twist":
            st = np.stack([sweep_noise(0.55, 900, 4200), sweep_noise(0.55, 900, 4200)[::-1]])
            place(fx, st, at, db(-23))
        elif kind == "cube_lock":
            # encaje mecánico: dos clics muy juntos y un golpe corto
            place(fx, thump(0.25, 160, 90, 0.04), at, db(-16), 0)
            place(fx, click(0.012, 2200), at, db(-18), 0)
            place(fx, click(0.01, 3500), at + 0.028, db(-21), 0)
            place(fx, soft_note(587.33, 0.5, 0.002, 0.12), at, db(-28), 0)
        elif kind == "cube_spin":
            place(fx, whoosh(0.8, 300, 2000, 0.55), at, db(-21), 0)
        elif kind == "cube_collapse":
            place(fx, sweep_noise(0.65, 600, 4500)[::-1] * 0.9, at, db(-20), 0)
        elif kind == "cube_home":
            place(fx, sub_boom(0.8, 80, 40, 0.2), at, db(-17), 0)
            place(fx, thump(0.4, 90, 45, 0.1), at, db(-24), home_p)
            place(fx, ping(880, 0.8, 0.25), at, db(-24), home_p)
        elif kind == "sting":
            place(fx, ping(880, 1.8, 0.6), at, db(-13), home_p)
            place(fx, ping(1318.5, 1.6, 0.5), at + 0.14, db(-19), home_p + 0.1)
            place(fx, chord([73.42, 146.83, 220.0, 369.99, 554.37], 3.2, 0.08, 1.2, 0.6), at, db(-17))
    return reverb(fx, 1.6, 0.16)


# ── El cubo se parte y se vuelve a armar (v17) ──────────────────────────
def shards(dur=0.5, n=27, seed=3, implode=False):
    """27 fragmentos (uno por cubito): golpecitos cortos y resonantes con tono
    y posición distintos. Al partirse salen casi juntos y se van espaciando;
    al armarse, al revés: llegan cada vez más seguidos hasta el encaje."""
    rng = np.random.default_rng(seed)
    out = np.zeros((2, int(dur * SR) + int(0.2 * SR)))
    for q in range(n):
        u = (q / (n - 1)) ** 1.8
        at = (1 - u) * (dur - 0.03) if implode else u * dur
        fc = rng.uniform(1800, 6500)
        d = rng.uniform(0.03, 0.07)
        tk = bp(noise(d), fc * 0.8, min(fc * 1.25, SR / 2 - 200)) * env_exp(d, 0.0005, d / 4)
        ring = sine(rng.uniform(700, 1700), d) * env_exp(d, 0.0005, d / 3)
        x = tk / (np.abs(tk).max() + 1e-9) + 0.4 * ring
        g = rng.uniform(0.45, 1.0)
        place(out, x, at, g, rng.uniform(-0.85, 0.85))
    return out / (np.abs(out).max() + 1e-9)


# ── Negro → blanco (v11): el golpe grande del tráiler ────────────────────
def soft_ping(f=880.0, dur=2.4, attack=0.06, decay=0.8):
    """El ping del cursor sin el clic de tecla y con ataque suave (no golpea)."""
    x = sine(f, dur) + db(-16) * sine(2 * f, dur) + db(-28) * sine(3 * f, dur)
    return 0.8 * x * env_exp(dur, attack, decay)


def build_light():
    """Negro → blanco (v13: suspenso, nada de golpes). Después de «Hay otra
    forma.» quedan dos segundos de oscuridad con el cursor parpadeando: un Re
    grave muy bajo crece despacio con un leve latido y la firma del cursor se
    acerca al revés, desvaneciéndose antes de la luz (no termina en pico).
    Cuando la luz amanece desde el cuadrado, el grave, el aire y el acorde de
    Re suben con ataques lentos (0,3–0,6 s) y el ping del cursor entra sin clic.
    No hay ningún transitorio: es un florecimiento, no un impacto."""
    bus = np.zeros((2, N))
    if getattr(cfg, "TEMA", "oscuro") != "mezcla":
        return bus
    H = cfg.LUZ[0]
    # 1) espera: Re grave que crece desde el final de la frase, con un latido leve
    d = H - (cfg.T["vo4"] + 0.75)
    tt = t_axis(d)
    held = (sine(36.71, d) + 0.7 * sine(73.42, d) + 0.25 * sine(110.0, d))
    held *= (tt / d) ** 2.0 * (0.8 + 0.2 * np.sin(2 * np.pi * 1.25 * tt))
    place(bus, np.tanh(1.3 * held) / np.tanh(1.3), H - d, db(-27), 0)
    # 1b) tensión: una nota aguda muy suave que tiembla y crece en los últimos 2,5 s
    d2 = 2.5
    t2 = t_axis(d2)
    hi = (sine(1760.0, d2) + 0.5 * sine(1864.66, d2)) * (0.6 + 0.4 * np.sin(2 * np.pi * 5.5 * t2))
    hi *= (t2 / d2) ** 2.5 * np.clip((d2 - t2) / 0.25, 0, 1)
    place(bus, hi, H - d2, db(-40), 0)
    # 2) la firma del cursor al revés, que se apaga antes de la luz
    rp = reverse_ping(1.8)
    k = np.ones(rp.shape[1])
    f = int(0.45 * SR)
    k[-f:] = np.linspace(1, 0, f) ** 1.5
    place(bus, rp * k, H - 1.8 + 0.1, db(-26))
    # 3) amanecer: todo con ataques lentos, ningún golpe
    sw = sub_boom(3.6, 48, 40, 1.4, 1.0) * np.clip(t_axis(3.6) / 0.45, 0, 1) ** 2
    place(bus, sw, H, db(-17), 0)
    air = wide_air(3.4, 700, 6000) * np.clip(t_axis(3.4) / 0.6, 0, 1) ** 2
    place(bus, air, H, db(-29))
    place(bus, soft_ping(880, 2.6, 0.08, 0.9), H + 0.25, db(-15), 0)
    place(bus, soft_ping(1318.5, 2.2, 0.08, 0.7), H + 0.55, db(-23), 0.2)
    bloom = chord([73.42, 146.83, 220.0, 293.66, 369.99, 440.0, 659.26], 5.0, 0.55, 2.1, 0.9)
    place(bus, bloom, H, db(-16))
    return reverb(bus, 3.4, 0.36, seed=23)


# ── Sintetizadores (v16) ─────────────────────────────────────────────────
def synth(f, dur, bright0=14.0, bright1=3.0, tau=0.12, attack=0.004, decay=0.35, detune=0.0):
    """Sierra limitada en banda con «filtro» que se cierra: cada armónico k
    pesa exp(-k / K(t)), y K baja de bright0 a bright1 (ataque brillante que se
    oscurece, como un sintetizador con envolvente de filtro)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    kmax = int(min(40, (SR / 2 - 200) / f))
    k = np.arange(1, kmax + 1)[:, None]
    K = bright1 + (bright0 - bright1) * np.exp(-t / tau)
    w = np.exp(-k / K[None, :]) / k
    f2 = f * 2 ** (detune / 1200)
    x = (w * np.sin(2 * np.pi * k * f2 * t[None, :])).sum(axis=0)
    x *= env_exp(dur, attack, decay)[:n]
    return x / (np.abs(x).max() + 1e-9)


def kick(dur=0.42):
    f = lambda t: 46 + 74 * np.exp(-t / 0.035)
    x = sine(f, dur) * env_exp(dur, 0.002, 0.13)
    x[: int(0.004 * SR)] += 0.25 * hp(noise(0.004), 3000)
    return np.tanh(1.8 * x) / np.tanh(1.8)


def hat(dur=0.05, open_=False):
    d = 0.22 if open_ else dur
    x = hp(noise(d), 7500) * env_exp(d, 0.001, 0.07 if open_ else 0.012)
    return x / (np.abs(x).max() + 1e-9)


def snare(dur=0.2):
    body = sine(185.0, dur) * env_exp(dur, 0.001, 0.05)
    nz = bp(noise(dur), 1200, 7000) * env_exp(dur, 0.001, 0.07)
    x = 0.5 * body + nz
    return x / (np.abs(x).max() + 1e-9)


def music_groove(mu):
    """La solución (en blanco) y el cubo 3D: pulso electrónico a 112 BPM en Re
    mayor (Re – La – Si m – Sol). Bajo de sierra que «bombea» con el bombo,
    arpegio de sintetizador en semicorcheas que rebota de lado a lado, colchón
    amplio y hi-hats. Con la convergencia hay un respiro (sin bombo) y con el
    cubo vuelve todo con una subida: redoblante en corcheas, después en
    semicorcheas y un barrido que crece, y se corta en seco cuando el cubo
    vuelve a ser el cursor. El logo se arma sobre la nota grave sostenida."""
    bpm = 112.0
    beat = 60 / bpm
    start = T["s6"] + 0.35
    rv = T["rv"]
    brk0, brk1 = rv, rv + TL.RV["extrude"][0]            # respiro: la interfaz converge
    b_eighth = rv + TL.RV["explode"][0]                   # redoblante en corcheas
    b_six = rv + TL.RV["spin"][0]                         # redoblante en semicorcheas
    end = rv + TL.RV["home"][1] - 0.04                    # corte seco al volver a ser cursor
    roots = [73.42, 55.0, 61.74, 49.0]                     # Re2 · La1 · Si1 · Sol1
    arps = [[293.66, 369.99, 440.0, 587.33], [277.18, 329.63, 440.0, 554.37],
            [246.94, 293.66, 369.99, 493.88], [196.0, 246.94, 293.66, 392.0]]
    pads = [[146.83, 220.0, 293.66, 369.99], [138.59, 220.0, 277.18, 329.63],
            [123.47, 185.0, 246.94, 293.66], [98.0, 196.0, 246.94, 293.66]]
    n_beats = int((end - start) / beat) + 1
    bass_bus = np.zeros((2, N))
    pad_bus = np.zeros((2, N))
    side = np.zeros(N)            # envolvente del bombo para el «bombeo»
    for i in range(n_beats):
        at = start + i * beat
        if at >= end:
            break
        bar = i // 4
        ch = bar % 4
        in_brk = brk0 <= at < brk1
        k_in = min(1.0, (i + 1) / 6)                     # entra en 1,5 compases
        # bombo en cada tiempo (menos en el respiro)
        if not in_brk:
            place(mu, kick(), at, db(-17) * k_in, 0)
            j = int(at * SR)
            m = min(N - j, int(0.3 * SR))
            side[j:j + m] = np.maximum(side[j:j + m], np.exp(-np.arange(m) / (0.11 * SR)))
        # bajo en corcheas (el segundo de cada par más corto)
        for h in range(2):
            ta = at + h * beat / 2
            if ta >= end:
                break
            dur = beat / 2 * (0.95 if h == 0 else 0.7)
            br = 5.0 if in_brk else 9.0
            x = synth(roots[ch], dur + 0.05, br, 2.0, 0.08, 0.003, 0.25)
            x2 = synth(roots[ch] * 2, dur + 0.05, br, 2.5, 0.08, 0.003, 0.2, detune=7)
            place(bass_bus, x + 0.35 * x2, ta, db(-19) * k_in, 0)
        # arpegio en semicorcheas desde el segundo compás, rebotando en estéreo
        if bar >= 1:
            pat = [0, 1, 2, 3, 2, 1, 2, 3]
            for q in range(4):
                ta = at + q * beat / 4
                if ta >= end:
                    break
                idx = pat[(i * 4 + q) % 8]
                note = arps[ch][idx]
                br = 4.0 if in_brk else 10.0
                x = synth(note, 0.28, br, 2.0, 0.05, 0.002, 0.09, detune=4 * (-1) ** q)
                place(mu, x, ta, db(-27 if not in_brk else -31), 0.55 * (-1) ** q)
        # hi-hats: contratiempo; abierto al final de cada dos compases
        if not in_brk:
            place(mu, hat(), at + beat / 2, db(-30) * k_in, 0.25)
            if i % 8 == 7:
                place(mu, hat(open_=True), at + beat / 2, db(-29), -0.2)
        # colchón: un acorde por compás (sierras desafinadas, ataque lento)
        if i % 4 == 0:
            bar_d = 4 * beat + 0.4
            for nf in pads[ch]:
                for dt, pp in ((-6, -0.6), (6, 0.6)):
                    x = synth(nf, bar_d, 3.0, 2.0, 1.0, 0.25, 1.2, detune=dt)
                    place(pad_bus, x, at, db(-37), pp)
    # redoblante de la subida: corcheas y luego semicorcheas, en crescendo
    t_s = b_eighth
    while t_s < end - 0.02:
        k = (t_s - b_eighth) / max(0.1, end - b_eighth)
        place(mu, snare(), t_s, db(-40 + 8 * k), 0)
        t_s += beat / 2 if t_s < b_six else beat / 4
    # barrido que crece hasta el corte
    d = end - b_eighth
    rise = sweep_noise(d, 400, 9000) * (t_axis(d) / d) ** 2.2
    place(mu, rise, b_eighth, db(-34), 0)
    # bombeo: el bajo y el colchón bajan con cada bombo
    g = 1 - 0.55 * side
    bass_bus *= g
    pad_bus *= g
    # v17: durante el cubo 3D la música baja ~10 dB para que mande el cubo
    t_full = np.arange(N) / SR
    c0 = rv + TL.RV["grow"][0]
    cube_gain = 1 - (1 - db(-10)) * np.clip((t_full - c0) / 0.6, 0, 1)
    _CUBE_GAIN[0] = cube_gain
    # corte seco al final
    e = int(end * SR)
    f = int(0.012 * SR)
    for bus in (bass_bus, pad_bus):
        bus[:, e:e + f] *= np.linspace(1, 0, f)
        bus[:, e + f:] = 0
    mu += bass_bus + pad_bus


_CUBE_GAIN = [None]


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

    # E4–E5 (v16): música electrónica en vez de las cuerdas pulsadas
    groove = np.zeros_like(mu)
    music_groove(groove)
    mu += groove * _CUBE_GAIN[0]          # v17: el cubo manda (la música baja ~10 dB)

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
    music = tape_stop(music, T["freeze"] + 0.02, 0.45)   # la cama se frena antes del corte
    music = duck(music, voice, -9)
    sfx_d = duck(sfx, voice, -9)
    music = hard_silence(music)
    sfx_d = hard_silence(sfx_d)
    light = duck(build_light(), voice, -10)
    mix = voice + music + sfx_d + light
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
    write(STEMS / "efectos.wav", sfx_d + light)
    write(STEMS / "mezcla.wav", mix)


if __name__ == "__main__":
    main()
