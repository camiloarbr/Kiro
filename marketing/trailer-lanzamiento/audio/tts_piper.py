"""Narración con voces abiertas en español latino (Piper, licencias Apache-2.0 / Unlicense).

Genera cada frase de la narración como un archivo aparte en audio/voz/<voz>/,
con los mismos nombres que usa config.VO, para poder cambiar de voz sin
tocar la animación.

  python audio/tts_piper.py --modelos ruta/a/modelos

Modelos (descarga de huggingface.co/rhasspy/piper-voices, carpeta es/es_MX):
  es_MX-claude-high.onnx (+ .onnx.json)   → voz «claude»: masculina, grave
  es_MX-ald-medium.onnx  (+ .onnx.json)   → voz «ald»: masculina, más clara
"""
import argparse
import subprocess
import wave
from pathlib import Path

from piper import PiperVoice, SynthesisConfig

ROOT = Path(__file__).resolve().parent.parent

# Texto de cada frase (puntuación pensada para las pausas) y ritmo propio.
# length_scale > 1 habla más despacio.
LINEAS = {
    "01-idea": ("Todo negocio empieza con una idea.", 1.18),
    "02-a-mano": ("Pero cuando todo depende de hacerlo a mano,", 1.16),
    "03-crecimiento": ("cada tarea se convierte en otra complicación.", 1.16),
    "04-otra-forma": ("Hay otra forma.", 1.28),
    "05-kiro": ("Kiro.", 1.25),
    "06a-creamos": ("Creamos software a tu medida, automatizaciones, y agentes inteligentes,", 1.12),
    "06b-para-que": ("para que tu negocio trabaje mejor.", 1.14),
}

VOCES = {
    "claude": ("es_MX-claude-high.onnx", dict(noise_scale=0.6, noise_w_scale=0.75)),
    "ald": ("es_MX-ald-medium.onnx", dict(noise_scale=0.6, noise_w_scale=0.75)),
}


def synth(voice, text, length_scale, extra, dst_wav):
    cfg = SynthesisConfig(length_scale=length_scale, **extra)
    with wave.open(str(dst_wav), "wb") as wf:
        voice.synthesize_wav(text, wf, syn_config=cfg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelos", required=True)
    ap.add_argument("--voces", nargs="*", default=list(VOCES))
    a = ap.parse_args()
    for nombre in a.voces:
        archivo, extra = VOCES[nombre]
        voice = PiperVoice.load(str(Path(a.modelos) / archivo))
        out = ROOT / "audio" / "voz" / nombre
        out.mkdir(parents=True, exist_ok=True)
        for key, (texto, ls) in LINEAS.items():
            tmp = out / f"{key}.wav"
            synth(voice, texto, ls, extra, tmp)
            # a 48 kHz y MP3 de alta calidad, igual que las demás voces
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp), "-ar", "48000",
                            "-c:a", "libmp3lame", "-q:a", "2", str(out / f"{key}.mp3")], check=True)
            tmp.unlink()
            print("→", out / f"{key}.mp3")


if __name__ == "__main__":
    main()
