"""Construye el tráiler completo: audio → video → MP4 final.

  python build.py              # todo: out/kiro-trailer-<VERSION>.mp4 (VERSION en config.py)
  python build.py --animatic   # solo E1–E5 (0–24 s) con sonido: out/animatic.mp4
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import config as cfg  # noqa: E402

OUT = ROOT / "out"


def run(cmd):
    print("$", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)


def mux(video, audio, dst, t0=0.0, t1=None):
    t1 = cfg.DURATION if t1 is None else t1
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-ss", str(t0), "-to", str(t1), "-i", str(audio),
         "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-shortest", "-movflags", "+faststart", str(dst)])
    print("→", dst)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--animatic", action="store_true")
    ap.add_argument("--voice", help="carpeta de voz en audio/voz/ (sobrescribe config.VOICE)")
    ap.add_argument("--name", help="sufijo del archivo: out/kiro-trailer-<VERSION>-<name>.mp4")
    a = ap.parse_args()
    import os
    if a.voice:
        os.environ["KIRO_VOICE"] = a.voice
    py = sys.executable
    run([py, str(ROOT / "audio" / "build_audio.py")])
    mix = ROOT / "audio" / "stems" / "mezcla.wav"
    if a.animatic:
        t1 = cfg.T["s6"]
        run([py, str(ROOT / "render.py"), "--from", "0", "--to", str(t1), "--out", str(OUT / "_animatic_video.mp4")])
        mux(OUT / "_animatic_video.mp4", mix, OUT / "animatic.mp4", 0, t1)
    else:
        run([py, str(ROOT / "render.py"), "--out", str(OUT / "_video.mp4")])
        suffix = f"-{a.name}" if a.name else ""
        mux(OUT / "_video.mp4", mix, OUT / f"kiro-trailer-{cfg.VERSION}{suffix}.mp4")
