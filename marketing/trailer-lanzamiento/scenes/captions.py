"""Subtítulos grandes: cada palabra entra cuando el narrador la dice y la
palabra que suena se marca en morado claro. Sirven para quien ve el video sin
sonido (Reels y TikTok arrancan mudos)."""
import config as cfg
from lib import ease as E
from lib.draw import draw_text, font, text_width

C, T = cfg.C, cfg.T
BASE_Y = 1440      # centro vertical del bloque de subtítulos
LINE_H = 78
MAX_W = 940
FONT = ("mont700", 60)


def _layout(words, fnt):
    lines, cur, w = [], [], 0
    space = fnt.measureText(" ")
    for wd, tt in words:
        ww = fnt.measureText(wd)
        if cur and w + space + ww > MAX_W:
            lines.append(cur)
            cur, w = [], 0
        cur.append((wd, tt, ww))
        w += (space if len(cur) > 1 else 0) + ww
    if cur:
        lines.append(cur)
    return lines, space


def draw(c, t):
    if not cfg.SUBTITULOS:
        return
    fnt = font(*FONT)
    for fname, cue, text, words in cfg.VO:
        if cue not in cfg.SUBTITULOS_EN:
            continue
        start = T[cue]
        if cfg.VOICE != cfg.VO_TIMINGS_FOR:   # sin tiempos medidos: reparto uniforme
            n = len(words)
            words = [(w, 0.15 + i * 1.8 / max(1, n)) for i, (w, _) in enumerate(words)]
        end = start + words[-1][1] + 0.9
        fade_len = 0.45
        # si la siguiente frase empieza antes, esta sale a tiempo (sin encimarse)
        nexts = [T[cu] for (_, cu, _, _) in cfg.VO if cu in cfg.SUBTITULOS_EN and T[cu] > start]
        if nexts and end + fade_len > min(nexts) - 0.05:
            end, fade_len = min(nexts) - 0.25, 0.2
        if not (start - 0.1 <= t <= end + fade_len):
            continue
        out = E.prog(t, end, end + fade_len)
        lines, space = _layout(words, fnt)
        # v19: como máximo 2 renglones a la vez; las frases largas pasan de
        # página cuando empieza la palabra del renglón siguiente
        pages = [lines[i:i + 2] for i in range(0, len(lines), 2)]
        if len(pages) > 1:
            k = 0
            for j in range(1, len(pages)):
                if t >= start + pages[j][0][0][1] - 0.05:
                    k = j
            if k < len(pages) - 1:
                nxt_page = start + pages[k + 1][0][0][1] - 0.05
                out = max(out, E.prog(t, nxt_page - 0.12, nxt_page))
            lines = pages[k]
        base_y = cfg.SUBTITULOS_Y.get(cue, BASE_Y) if hasattr(cfg, "SUBTITULOS_Y") else BASE_Y
        y = base_y - (len(lines) - 1) * LINE_H / 2 + 20
        for ln in lines:
            total = sum(w for _, _, w in ln) + space * (len(ln) - 1)
            x = 540 - total / 2
            flat = [w for l in lines for w in l]
            for wd, tt, ww in ln:
                k = E.prog(t, start + tt - 0.05, start + tt + 0.12)
                if k > 0:
                    rise = (1 - E.out_cubic(k)) * 14
                    # la palabra que suena va en morado claro hasta que entra la siguiente
                    idx = next(i for i, w in enumerate(flat) if w[1] == tt and w[0] == wd)
                    nxt = start + (flat[idx + 1][1] if idx + 1 < len(flat) else tt + 0.45)
                    hot = 1 - E.prog(t, nxt - 0.02, nxt + 0.14)
                    col = C["violet_light"] if hot > 0.5 else C["white"]
                    draw_text(c, wd, x, y + rise, fnt, col, k * (1 - out), tracking=-0.01)
                x += ww + space
            y += LINE_H
