"""Render del tráiler: dibuja cada fotograma con Skia y lo envía a FFmpeg.

Uso:
  python render.py                       # video completo (sin audio) → out/video.mp4
  python render.py --from 0 --to 19      # solo un tramo (animatic)
  python render.py --frames 2.5 17 21.9  # fotogramas sueltos en PNG → out/frames/
  python render.py --contact             # hoja de contacto → out/hoja-de-contacto.png

Después, `python build.py` mezcla el audio y produce el MP4 final.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
import skia

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import config as cfg  # noqa: E402
from lib.draw import color  # noqa: E402
from lib import ease as E, theme, timeline as TL  # noqa: E402
from scenes import captions, cursor, logo_build, manual, system, signature  # noqa: E402

OUT = ROOT / "out"


def camera_zoom(t):
    """Acercamiento lento mientras el cuadrado se queda solo antes de la
    revelación y alejamiento mientras se construye la palabra: la marca «se
    abre» desde el cuadrado."""
    T, S5 = cfg.T, TL.S5
    z_in = E.in_out_sine(E.prog(t, T["rv"] + TL.RV["cube_home"][1] - 0.2, T["s5"] + 0.3))
    z_out = E.in_out_cubic(E.prog(t, T["s5"] + S5["extrude"][1] - 0.1, T["s5"] + S5["retract"][1]))
    return 1 + 0.30 * z_in * (1 - z_out)


def draw_frame(c, t):
    """Tema mezcla: hasta «Hay otra forma» todo es oscuro; ahí la luz se abre
    en círculo desde el cuadrado (se dibuja el fotograma oscuro y encima, dentro
    del círculo, el mismo fotograma con la paleta clara)."""
    k = theme.luz(t)
    if k <= 0:
        theme.apply("oscuro")
        _draw(c, t)
        return
    if k >= 1:
        theme.apply("claro")
        _draw(c, t)
        return
    theme.apply("oscuro")
    _draw(c, t)
    x, y = TL.START
    r = k * 1.04 * max(((x - a) ** 2 + (y - b) ** 2) ** 0.5 for a in (0, cfg.W) for b in (0, cfg.H))
    c.save()
    clip = skia.Path()
    clip.addCircle(x, y, max(r, 0.5))
    c.clipPath(clip, doAntiAlias=True)
    theme.apply("claro")
    _draw(c, t)
    c.restore()


def _draw(c, t):
    c.drawColor(color(cfg.C["black"]))
    manual.draw(c, t)        # E2–E3: el problema
    system.draw(c, t)        # E4: la solución (sin marca)
    z = camera_zoom(t)
    c.save()
    if z != 1:
        c.translate(*TL.HOME)
        c.scale(z, z)
        c.translate(-TL.HOME[0], -TL.HOME[1])
    cursor.draw(c, t)        # E1–E3 (el protagonista)
    if t < cfg.T["s5"]:
        signature.draw(c, t)     # E5: el cuadrado vuelve al centro (dentro de la cámara)
    logo_build.draw(c, t)    # E5–E6: única revelación del logo
    c.restore()
    if t >= cfg.T["s5"]:
        signature.draw(c, t)     # E6: frase y dirección web
    captions.draw(c, t)


def frame_image(t):
    surf = skia.Surface(cfg.W, cfg.H)
    with surf as c:
        draw_frame(c, t)
    return surf.makeImageSnapshot()


def render_video(t0, t1, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    n0, n1 = int(round(t0 * cfg.FPS)), int(round(t1 * cfg.FPS))
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
           "-s", f"{cfg.W}x{cfg.H}", "-r", str(cfg.FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-tune", "animation",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = skia.Surface(cfg.W, cfg.H)
    for n in range(n0, n1):
        t = n / cfg.FPS
        with surf as c:
            draw_frame(c, t)
        arr = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
        proc.stdin.write(np.ascontiguousarray(arr).tobytes())
        if n % 60 == 0:
            print(f"  {t:5.1f} s", flush=True)
    proc.stdin.close()
    proc.wait()
    print("→", path)


def save_frames(times):
    d = OUT / "frames"
    d.mkdir(parents=True, exist_ok=True)
    for t in times:
        p = d / f"f_{t:06.2f}.png"
        frame_image(t).save(str(p))
        print("→", p)


def contact_sheet(times, path, cols=6, w=270):
    h = int(w * cfg.H / cfg.W)
    rows = (len(times) + cols - 1) // cols
    pad, lab = 14, 34
    sheet = skia.Surface(cols * (w + pad) + pad, rows * (h + pad + lab) + pad)
    from lib.draw import draw_text, font
    with sheet as c:
        c.clear(color("#000000"))
        for i, t in enumerate(times):
            img = frame_image(t)
            x = pad + (i % cols) * (w + pad)
            y = pad + (i // cols) * (h + pad + lab)
            c.drawImageRect(img, skia.Rect.MakeXYWH(x, y, w, h), skia.SamplingOptions(skia.FilterMode.kLinear))
            c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), skia.Paint(Color=color("#333333"), Style=skia.Paint.kStroke_Style, StrokeWidth=1))
            draw_text(c, f"{t:.1f} s", x, y + h + 24, font("mono400", 20), "#BBBBBB")
    sheet.makeImageSnapshot().save(str(path))
    print("→", path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, default=cfg.DURATION)
    ap.add_argument("--out", default=None)
    ap.add_argument("--frames", nargs="*", type=float)
    ap.add_argument("--contact", action="store_true")
    a = ap.parse_args()
    if a.frames:
        save_frames(a.frames)
    elif a.contact:
        times = [round(x * 0.5 + 0.0, 2) for x in range(int(cfg.DURATION / 0.5) + 1)]
        times = [t for t in times if t <= cfg.DURATION - 0.05]
        contact_sheet(times[::2] + [], OUT / "hoja-de-contacto.png")
    else:
        out = Path(a.out) if a.out else OUT / "video.mp4"
        render_video(a.t0, a.t1, out)
