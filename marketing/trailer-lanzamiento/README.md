# Tráiler de lanzamiento de Kiro — «Todo comienza con un punto»

Video vertical 1080 × 1920, 30 fps, H.264 + AAC, para Reels y TikTok.

**Versión actual: v6**, en dos voces (43,3 s cada una):

- `out/kiro-trailer-v6-carlos.mp4`: Carlos, toma nueva con menos respiración.
- `out/kiro-trailer-v6-mujer-grave.mp4`: Lucía, voz femenina más grave (151 Hz). Es la versión con mujer recomendada.
- `out/kiro-trailer-v6-mujer.mp4`: Daniela, voz femenina aguda (240 Hz).

Primero el problema, después la solución y al final la marca: el logo aparece
una sola vez y el narrador solo dice «Kiro». Antes del logo hay una transición
3D con el cubo 3×3×3 de la landing.

Cambios de la v6:

- **El cuadrado ya no salta.** Antes, la escena del crecimiento arrancaba
  antes de que terminara el recorrido anterior (un salto de 758 px en un
  fotograma) y la curva de movimiento era muy brusca. Ahora cada tramo dura
  según la distancia, la curva es suave y el cuadrado deja una estela corta.
  El paso máximo es de 78 px por fotograma.
- **El cubo 3D dura casi 6 s y se mueve más:** crece, se extruye, se separa en
  27 cubitos que giran sobre sí mismos, se vuelve a armar, hace dos giros de
  capa y un medio giro, flota y se comprime en el cursor.
- **Respiraciones.** `split_take.py` detecta los tramos sin voz (silencio o
  soplido) y los baja 20 dB.

| Escena | Tiempo | Qué pasa |
|---|---|---|
| 1 Intriga | 0–7,3 s | Silencio. El cuadrado aparece en el centro (1,6 s) y espera. «Todo negocio empieza con una idea.» (4,4 s) |
| 2 Tensión | 7,3–15,3 s | Sale del centro y activa una hoja de cálculo (cuadrícula completa), chats, pendientes y registros. «Pero cuando todo depende de hacerlo a mano, cada tarea se convierte en otra complicación.» |
| 3 Pausa | 15,3–18,8 s | Corte seco, todo se retira, vuelve al centro. «Hay otra forma.» |
| 4 Solución | 18,8–29,2 s | Ordena el espacio, se vuelve la respuesta del agente y la celda reservada. Sin marca. |
| 5 Revelación | 29,2–39,5 s | La interfaz converge en el cuadrado, que se vuelve el cubo 3D de la landing (29,6–36,2 s): se extruye, explota en cubitos, se rearma, hace dos giros de capa y se comprime en el cursor. Luego se transforma en «kiro». «Kiro.» |
| 6 Cierre | 39,5–43,3 s | Solo el logo. Parpadeo y firma sonora. |

Versiones anteriores, intactas: v1 a v5 en `out/`.

## Archivos

| Ruta | Qué es |
|---|---|
| `out/kiro-trailer-v6-carlos.mp4` | **v6 con Carlos** |
| `out/kiro-trailer-v6-mujer-grave.mp4` | **v6 con Lucía (voz femenina grave)** |
| `out/kiro-trailer-v6-mujer.mp4` | v6 con Daniela (voz femenina aguda) |
| `out/hoja-de-contacto-v6.png` | Un fotograma por segundo de la v6 |
| `out/kiro-trailer-v5.mp4`, `out/hoja-de-contacto-v5.png` | v5 (Carlos con más respiración) |
| `out/kiro-trailer-v4.mp4`, `out/hoja-de-contacto-v4.png` | v4 (voz Brian) |
| `scenes/cube3d.py` | Transición 3D: el cubo 3×3×3 de la landing (geometría y animación) |
| `audio/split_take.py` | Corta una toma completa en frases y mide las palabras (subtítulos) |
| `audio/voz/carlos-v2/` | **Narración de la v6 «carlos»** (ElevenLabs Carlos, eleven_multilingual_v2) |
| `audio/voz/lucia/` | **Narración de la v6 «mujer-grave»** (ElevenLabs Lucía, eleven_multilingual_v2) |
| `audio/voz/daniela/` | Narración de la v6 «mujer» (ElevenLabs Daniela) |
| `audio/voz/carlos/` | Narración de la v5 (Carlos, eleven_v4) |
| `audio/voz/luismiguel/`, `audio/voz/lujan/` | Voces latinas alternativas, ya cortadas |
| `audio/voz/tomas/` | Tomas completas originales de ElevenLabs |
| `out/kiro-trailer-v3.mp4`, `out/hoja-de-contacto-v3.png` | v3 (voz «claude») |
| `out/kiro-trailer-v2.mp4`, `out/hoja-de-contacto-v2.png` | v2 (referencia) |
| `out/kiro-trailer.mp4` | v1 (referencia; no se sobrescribe) |
| `out/animatic.mp4`, `out/hoja-de-contacto.png` | Pruebas de la v1 |
| `audio/voz/brian/` | Narración de la v1–v4 (ElevenLabs, acento anglo) |
| `audio/voz/claude/` | Narración de la v3 (Piper es_MX, masculina, español latino neutro) |
| `audio/voz/ald/` | Alternativa abierta (Piper es_MX, masculina, más clara) |
| `audio/tts_piper.py` | Genera las dos voces anteriores (textos y ritmo de cada frase) |
| `audio/voz/george/` | Voz alternativa de ElevenLabs |
| `audio/voz/pruebas/` | Las dos pruebas cortas de voz |
| `audio/stems/` | `voz.wav`, `musica.wav`, `efectos.wav`, `mezcla.wav` |
| `config.py` | **Todo lo editable**: tiempos, textos, colores, voz, CTA |
| `lib/logo.py` | Lee la geometría del logo oficial desde `brand/` |
| `lib/timeline.py` | Eventos derivados (movimientos, cues de sonido) |
| `scenes/` | Una pieza por escena: cursor, trabajo manual (E2–E4), transformación (E5), sistema (E6), firma (E7), subtítulos |
| `audio/build_audio.py` | Diseño sonoro, música, mezcla y sonoridad |

## Cómo se ejecuta

Requisitos: Python 3.11+ y FFmpeg en el PATH.

```bash
pip install -r requirements.txt
python build.py              # audio + video → out/kiro-trailer-<VERSION>.mp4  (≈1 min)
python build.py --voice daniela --name mujer   # otra voz → out/kiro-trailer-<VERSION>-mujer.mp4
python audio/split_take.py toma.mp3 audio/voz/<nombre>   # corta una toma completa (y baja respiraciones)
python build.py --animatic   # solo 0–24 s → out/animatic.mp4
python render.py --frames 2.5 21.9 38   # fotogramas sueltos en out/frames/
python audio/build_audio.py  # solo rehace el audio
```

El render es determinista: no hay azar ni temporizadores. Imagen y sonido
leen la misma línea de tiempo (`config.T` → `lib/timeline.py`), así que si
mueves un tiempo en `config.py`, se mueven juntos.

## Cambios frecuentes

- **Cambiar de voz:** `python build.py --voice <carpeta> --name <sufijo>` o
  `VOICE = "<carpeta>"` en `config.py`. Voces listas: carlos-v2, lucia, daniela,
  carlos, luismiguel, lujan, brian, george, claude, ald.
- **Más o menos reducción de respiraciones:** `BREATH_DB` en
  `audio/split_take.py` (−20 dB por defecto, 0 la desactiva); vuelve a cortar
  la toma.
- **Regenerar la voz abierta:** descarga `es_MX-claude-high.onnx` y
  `es_MX-ald-medium.onnx` (con sus `.onnx.json`) de
  huggingface.co/rhasspy/piper-voices (carpeta `es/es_MX`), `pip install
  piper-tts` y corre `python audio/tts_piper.py --modelos <carpeta>`.
- **Otra toma de voz:** reemplaza el `.mp3` en `audio/voz/brian/` con el
  mismo nombre. Si la nueva toma dura distinto, ajusta el cue en `config.T`.
- **Dirección web del cierre:** `URL` en `config.py` (hoy
  kiro.kirosolutionsco.workers.dev).
- **Nueva versión sin pisar la anterior:** cambia `VERSION` en `config.py`.
- **Subtítulos:** `SUBTITULOS = False` los quita.
- **Textos de la demo** (Casa Ceiba, mensajes, panel): `DEMO` en `config.py`.

## Decisiones de producción

- **Logo:** no se redibujó ninguna letra. `lib/logo.py` lee los trazados de
  `brand/kiro-logo-principal-negativo.svg` (el del manual) y la animación solo
  decide cómo se revelan. El fotograma final es idéntico al SVG oficial,
  incluido el gris `#B9B3C4` de «solutions».
- **Transformación:** el cuadrado salta, se duplica y su copia cae para
  escribir el palo de la «i»; los bordes de ese palo se extienden como línea
  base y altura x; sobre esas guías se levantan la K, la r y la o, cada una con
  un filo violeta en el borde que avanza; las guías vuelven a la «i» y el
  cursor parpadea una vez. La cámara se acerca en el silencio y se aleja
  mientras se arma la palabra.
- **Violeta = Kiro actuando:** en la demo, el cuadrado se expande y se vuelve
  la respuesta del agente, luego viaja por el conector y termina siendo la
  celda reservada. En el cierre esa celda vuelve a su sitio en el logo.
- **Render:** Python + Skia (dibujo vectorial con antialiasing) y FFmpeg. Se
  eligió sobre Remotion porque el repo de la landing es Astro (no React) y
  así no hace falta un navegador para renderizar.
- **Sonido:** música y efectos se sintetizan en `audio/build_audio.py` con
  NumPy: son originales, sin licencias de terceros. La firma sonora es un
  «ping» de cursor (La5) sobre un acorde abierto de Re; suena al aparecer el
  cuadrado, cuando la palabra queda completa y al cerrar. En el freeze de E4
  el sonido se corta en seco (sin cola de reverberación) y la música baja
  sola cuando habla el narrador. Mezcla final a −14 LUFS, pico −1,5 dBFS.
- **Voz:** ElevenLabs, con el conector de la cuenta de Kiro. La v6 usa
  `eleven_multilingual_v2`, que respira menos que `eleven_v4`. Cada voz se
  genera como una sola toma con pausas de 1,5 s (`<break time="1.5s" />`) para
  que la entonación sea continua. `split_take.py` corta la toma en frases,
  mide cada palabra para los subtítulos y baja 20 dB las respiraciones. Las
  tomas de la v6 se midieron así:

  | Toma | Respiraciones audibles |
  |---|---|
  | Carlos v5 | Hasta −3 dB respecto de la voz |
  | Carlos v6 | −24 dB o menos |
  | Daniela | −11 dB o menos |

  Tono medio (mediana de la frecuencia fundamental): Daniela 240 Hz, Valeria
  222 Hz, Lucía 151 Hz. Se midieron también las muestras de Athena (169 Hz),
  Kate 3 (165 Hz) y Paloma (131 Hz, acento mexicano). La toma de Kate 3 falló
  por el bloqueo de la cuenta.

  Las de Daniela además quedan reducidas por el filtro.

## Limitaciones y pendientes

1. **Cuenta de ElevenLabs.** Durante la v6, ElevenLabs bloqueó el plan
   gratuito de la cuenta («actividad inusual», algo que suele pasar con
   conexiones por proxy). Por eso falló una de las dos tomas de Valeria. Para
   generar más voces hace falta un plan de pago, o pedirle a soporte de
   ElevenLabs que revise la cuenta.
2. **Tomas.** Hay más tomas completas sin usar en `audio/voz/tomas/`
   (carlos-v2-b, daniela-b, valeria). Para probar una, córtala con
   `split_take.py` y haz un build con `--voice`.
3. **Licencias.** Uso comercial de las voces de ElevenLabs: según el plan de la
   cuenta (el plan gratuito exige atribución y no permite uso comercial). Las
   voces Piper son de uso libre (claude: Apache-2.0; ald: Unlicense).
4. **Demo.** «Casa Ceiba» es un negocio de muestra, igual que en la landing.
