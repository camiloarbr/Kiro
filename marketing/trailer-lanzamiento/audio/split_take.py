"""Corta una toma completa de narración (un solo archivo con todo el guion)
en las frases que usa el tráiler, y guarda los tiempos de cada palabra para
los subtítulos.

  python audio/split_take.py toma.mp3 audio/voz/carlos

Necesita faster-whisper (pip install faster-whisper). Escribe en la carpeta
destino 01-idea.mp3 … 06b-para-que.mp3 y words.json.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 48000
BREATH_DB = -20.0   # atenuación de respiraciones entre palabras (0 = desactivado)
# (archivo, primera palabra de la frase); el orden es el del guion
SEGMENTS = [
    ("01-idea", "todo"),
    ("02-a-mano", "pero"),
    ("03-crecimiento", "cada"),
    ("04-otra-forma", "hay"),
    ("06a-creamos", "creamos"),
    ("06b-para-que", "para"),
    ("05-kiro", "kiro"),
]


def load(path, sr):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", str(path), "-f", "f32le", "-ac", "1",
                          "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def norm(w):
    return "".join(ch for ch in w.lower() if ch.isalpha() or ch in "áéíóúñü")


def _frames(y16, hop=160, win=320):
    """Energía (dB) y planitud espectral de cada ventana de 20 ms (paso 10 ms)."""
    n = (len(y16) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    fr = y16[idx] * np.hanning(win)
    db = 10 * np.log10(np.mean(fr ** 2, axis=1) + 1e-12)
    mag = np.abs(np.fft.rfft(fr, axis=1)) + 1e-9
    flat = np.exp(np.mean(np.log(mag), axis=1)) / np.mean(mag, axis=1)
    return db, flat


def breath_runs(y16):
    """Tramos sin voz de al menos 150 ms: silencio (más de 20 dB bajo la voz) o
    soplido (más de 12 dB bajo la voz y espectro plano, típico de una
    inhalación). Las consonantes como la «s» también son ruidosas, pero duran
    mucho menos de 150 ms y suenan más fuerte, así que no entran."""
    db, flat = _frames(y16)
    sp = np.percentile(db[db > db.max() - 40], 70)
    cand = (db < sp - 20) | ((db < sp - 12) & (flat > 0.3))
    runs, i = [], 0
    while i < len(cand):
        if cand[i]:
            j = i
            while j < len(cand) and cand[j]:
                j += 1
            if j - i >= 15:
                runs.append((i / 100, j / 100 + 0.02))
            i = j
        else:
            i += 1
    return runs


def refine_starts(words, runs):
    """Whisper a veces pega la pausa (y la inhalación) al inicio de la palabra
    siguiente: «pero» 1,9–3,6 s cuando en realidad suena en 3,4 s. Si un tramo
    sin voz cubre el inicio de una palabra, la palabra empieza al final de ese
    tramo."""
    out = []
    for w, s, e in words:
        for r0, r1 in runs:
            if r0 <= s + 0.1 and s < r1 < e - 0.02:
                s = r1 - 0.03
        out.append((w, s, e))
    return out


def gate_breaths(y, runs):
    """Reductor de respiraciones: baja BREATH_DB cada tramo sin voz, dejando
    30 ms de margen y fundidos de 30 ms para no morder las palabras."""
    g = np.ones(len(y))
    f = int(0.03 * SR)
    lo = 10 ** (BREATH_DB / 20)
    for r0, r1 in runs:
        ia, ib = max(0, int((r0 + 0.03) * SR)), min(len(y), int((r1 - 0.03) * SR))
        if ib - ia > 2 * f:
            g[ia:ib] = lo
            g[ia:ia + f] = np.linspace(1, lo, f)
            g[ib - f:ib] = np.linspace(lo, 1, f)
    return (y * g).astype(np.float32)

def main(src, dst):
    from faster_whisper import WhisperModel
    dst = Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    y = load(src, SR)
    y16 = load(src, 16000)
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(y16, language="es", beam_size=5, word_timestamps=True,
                           initial_prompt="Kiro es una empresa de software.")
    words = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
    runs = breath_runs(y16)
    words = refine_starts(words, runs)
    # índice de la palabra donde empieza cada frase (buscando en orden)
    starts, i = [], 0
    for _, first in SEGMENTS:
        while norm(words[i][0]) != first:
            i += 1
        starts.append(i)
        i += 1
    if BREATH_DB:
        y = gate_breaths(y, runs)
    env = np.convolve(np.abs(y), np.ones(480) / 480, "same")

    def quiet_point(a, b):
        """El instante más silencioso entre a y b (segundos)."""
        ia, ib = int(a * SR), max(int(a * SR) + 1, int(b * SR))
        return (ia + int(np.argmin(env[ia:ib]))) / SR

    bounds = [0.0]
    for k in range(1, len(starts)):
        prev_end = words[starts[k] - 1][2]
        nxt = words[starts[k]][1]
        bounds.append(quiet_point(prev_end, max(nxt, prev_end + 0.02)))
    bounds.append(len(y) / SR)
    out = {}
    for k, (name, _) in enumerate(SEGMENTS):
        a, b = bounds[k], bounds[k + 1]
        # recorta el silencio largo: deja 0,12 s antes de la primera palabra
        w0 = words[starts[k]][1]
        a = max(a, w0 - 0.12)
        a = max(0.0, min(a, w0 - 0.08))   # al menos 80 ms antes (consonante inicial)
        last = starts[k + 1] - 1 if k + 1 < len(starts) else len(words) - 1
        b = min(b, words[last][2] + 0.45)
        seg = y[int(a * SR): int(b * SR)].copy()
        f = int(0.01 * SR)
        seg[:f] *= np.linspace(0, 1, f)
        seg[-f * 3:] *= np.linspace(1, 0, f * 3)
        wav = dst / f"{name}.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-c:a", "libmp3lame", "-q:a", "1", str(dst / f"{name}.mp3")],
                       input=seg.astype(np.float32).tobytes(), check=True)
        out[name] = [(w, round(s - a, 2)) for (w, s, e) in words[starts[k]: last + 1]]
        print(f"{name}: {b - a:.2f} s  " + " ".join(w for w, _ in out[name]))
    if "--debug" in sys.argv:
        print([(w, round(s_, 2), round(e_, 2)) for w, s_, e_ in words])
        print("tramos atenuados:", [(round(a_, 2), round(b_, 2)) for a_, b_ in runs])
    (dst / "words.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
