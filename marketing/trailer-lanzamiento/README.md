# Tráiler de lanzamiento de Kiro — «Todo comienza con un punto»

Video vertical 1080 × 1920, 30 fps, H.264 + AAC, para Reels y TikTok.

**Versión actual: v20** (solo voz de mujer): `out/kiro-trailer-v20-mujer.mp4`
con Lucía, 46,3 s. Es igual a la v19, pero sin el subtítulo «Kiro.» del final.


La v19 agrega subtítulos en la parte blanca: «Creamos software a tu medida…»,
«para que tu negocio trabaje mejor.» y «Kiro.». En la solución van debajo del
panel (`SUBTITULOS_Y` en `config.py`). Ahora se muestran como máximo dos
renglones a la vez y las frases largas pasan de página.


La v18 recupera el sonido de explosión del cubo de la v16 (grave con
chasquido, barrido estéreo y acorde) y quita el de cuando se vuelve a armar.
Siguen igual los sonidos de movimiento (giros, vuelta, encajes) y la música
más baja durante el cubo.

La v17 dejó que el cubo 3D mandara en el sonido (los 27 pedazos no gustaron):

- **La música baja ≈10 dB durante el cubo.** El redoblante y el barrido de la
  subida quedan discretos.
- **Cuando el cubo se parte**, suenan un grave que empuja, aire que se abre y
  27 pedazos. Son golpecitos cortos y resonantes, uno por cubito, cada uno con
  su tono y su lado del estéreo: salen casi juntos y se van espaciando. Queda
  unos 12 dB por encima de la música.
- **Cuando se vuelve a armar** (sonido nuevo), hay una succión hacia adentro y
  los 27 pedazos llegan cada vez más seguidos hasta el encaje. Queda unos 7 dB
  por encima de la música.

La v16 cambió la música de la parte en blanco:

La v16 cambia la música de la parte en blanco: en vez de cuerdas pulsadas
(sonaban a guitarra) lleva un pulso electrónico a 112 BPM en Re mayor (Re – La –
Si m – Sol), generado en `music_groove()` de `audio/build_audio.py`.

- **Solución:** bajo de sierra que «bombea» con el bombo en cada tiempo,
  hi-hats y colchón de sintetizador. Desde el segundo compás entra un arpegio
  en semicorcheas que rebota de lado a lado.
- **Convergencia:** un respiro sin bombo, con el filtro cerrado.
- **Cubo 3D:** vuelve todo y sube. El redoblante va en corcheas, después en
  semicorcheas, y un barrido crece hasta que el cubo vuelve a ser el cursor;
  ahí se corta en seco.
- **Logo:** se arma sobre la nota grave sostenida. Sus notas son ahora de
  sintetizador (antes, de cuerda pulsada) y cierra con el golpe final.

La voz queda unos 6 dB por encima de la música mientras habla.

La v15 tenía 3 s de suspenso antes de la luz (20,6 s):

La v15 deja el suspenso en 3 segundos: la luz amanece a los 20,6 s. Todo lo
demás es igual a la v14, que se describe a continuación con 4 s.

La v14 llevó el suspenso a 4 segundos:

- **Oscuridad:** desde que Lucía termina «Hay otra forma.» (17,6 s) hasta que
  amanece la luz (21,6 s) pasan 4 s.
- **El cuadrado se achica** todo ese tiempo, hasta casi un punto (−62 %), como
  si fuera a desaparecer. Al principio parpadea dos veces, como un cursor que
  espera. Cuando amanece la luz vuelve a su tamaño.
- **Sonido:** por debajo crece un Re grave muy bajo con leve latido. En los
  últimos 2,5 s se suma una nota aguda muy suave que tiembla, y la firma del
  cursor llega al revés y se apaga antes de la luz. El amanecer no tiene
  golpes ni clics: el grave, el aire y el acorde de Re suben con ataques
  lentos.
- **Duración:** todo lo posterior se corrió 4 s en total respecto de la v11.

El resto de las mejoras de sonido de la v11 sigue igual (corte del caos,
cubo y logo).

La v11 hace el sonido más impactante (`audio/build_audio.py`):

- **Negro → blanco: el golpe grande del tráiler.** Lucía dice «Hay otra
  forma.» en silencio. Por debajo, la firma del cursor sube aspirada al revés
  y crece una subida de ruido. Siguen 80 ms de vacío total y, cuando la luz
  estalla desde el cuadrado, entran a la vez: subgrave, chasquido, cuerpo,
  aire que se abre a los lados, el ping del cursor y un acorde brillante de Re
  que sostiene hasta la solución. La luz ahora llega al terminar la frase
  (17,7 s), así el golpe no tapa la voz. El cuadrado se contrae y late con el
  golpe. Todo esto va en un bus propio, para que el silencio de la pausa no lo
  corte.
- **Corte del caos (15,3 s):** la música se frena como una cinta (el tono
  cae) y el corte es un golpe denso con subgrave.
- **Aparición del cuadrado:** un grave suave que lo sostiene, como si se
  «encendiera».
- **Cubo 3D:** la explosión tiene subgrave y chasquido, los encajes suenan
  más mecánicos (dos clics) y los giros y la compresión suben de nivel.
- **Logo:** subida en reversa antes del golpe final y subgrave.
- **Resto:** los recorridos del cuadrado se oyen un poco más (−37 dB) y la
  celda reservada tiene un grave corto.

Mezcla a −14 LUFS, pico −1,5 dBFS. El golpe de luz queda unos 7,5 dB por
encima de la música de la solución.

La v10 mezcla los dos colores de la marca:

- **El problema va en negro** (0–17 s): el caos y el trabajo a mano.
- **La luz se abre con «Hay otra forma»**: un círculo de Blanco Kiro sale del
  cuadrado violeta (16,9–17,8 s), así que es Kiro quien trae la luz.
- **La solución, el cubo y el logo van en blanco.** El texto pasa a Kiro Black
  y el acento de texto a morado oscuro. El cierre usa la versión positiva del
  logo (letras negras).
- **Cómo se cambia:** `KIRO_TEMA=oscuro` vuelve a todo negro, `KIRO_TEMA=claro`
  pone todo en blanco y `LUZ` en `config.py` mueve el momento del cambio. Las
  paletas están en `config.py` y se aplican desde `lib/theme.py`.

La v9 vuelve a la escena de la solución de la v6 (chat plano, sin el celular
3D) y conserva el principio fluido de la v8. También suaviza los recorridos
del cuadrado en esa escena: la guía, la entrada al chat, la salida a la
confirmación y el conector (más largo). Ningún fotograma pasa de ≈80 px. El
código del celular 3D quedó guardado en `scenes/phone3d.py` y
`versiones/v8-celular/`, por si se quiere recuperar.

Novedades de la v8:

- **Recorrido continuo al principio.** En la v7, el cuadrado viajaba en tramos
  rectos y se quedaba quieto 6 fotogramas en cada elemento. Ahora recorre una
  curva suave (spline cardinal, `scenes/cursor.py`): al pasar por cada
  elemento baja la velocidad, pero no se detiene. Llega en los mismos
  instantes, así que las reacciones y los sonidos siguen sincronizados.
- **Rastros desde el primer movimiento.** Las líneas punteadas siguen el
  recorrido real y se dibujan mientras el cuadrado se mueve
  (`scenes/manual.py`, `draw_wires`). Antes solo aparecían desde la segunda
  mitad.

Novedad de la v7: con «software a tu medida» entra el **celular 3D de la
landing** (`scenes/phone3d.py`, réplica de `DemoKiroBot.astro`). Llega desde el
fondo girando, el cuadrado entra al chat y se vuelve la respuesta del agente,
y el celular se va girando a la izquierda mientras el panel entra en 3D desde
la derecha. Sin marca: el contacto es «Casa Ceiba» y el avatar es el cuadrado
violeta. También se suavizaron los recorridos del cuadrado en esa escena (paso
máximo ≈ 90 px por fotograma).

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
| 4 Solución | 18,8–29,2 s | Ordena el espacio; entra el celular 3D de la landing y el cuadrado se vuelve la respuesta del agente dentro del chat; el celular sale girando, entra el panel y el cuadrado termina siendo la celda reservada. Sin marca. |
| 5 Revelación | 29,2–39,5 s | La interfaz converge en el cuadrado, que se vuelve el cubo 3D de la landing (29,6–36,2 s): se extruye, explota en cubitos, se rearma, hace dos giros de capa y se comprime en el cursor. Luego se transforma en «kiro». «Kiro.» |
| 6 Cierre | 39,5–43,3 s | Solo el logo. Parpadeo y firma sonora. |

Versiones anteriores, intactas: v1 a v5 en `out/`.

## Archivos

| Ruta | Qué es |
|---|---|
| `out/kiro-trailer-v20-mujer.mp4` | **v20 con Lucía** (sin subtítulo «Kiro.» al final) |
| `out/kiro-trailer-v19-mujer.mp4` | v19 con Lucía (con subtítulo «Kiro.») |
| `out/kiro-trailer-v18-mujer.mp4` | v18 con Lucía (sin subtítulos en la parte blanca) |
| `out/kiro-trailer-v17-mujer.mp4` | v17 con Lucía (27 pedazos al partirse y al armarse) |
| `out/kiro-trailer-v16-mujer.mp4` | v16 con Lucía (música fuerte en el cubo) |
| `out/kiro-trailer-v15-mujer.mp4` | v15 con Lucía (cuerdas pulsadas) |
| `out/hoja-de-contacto-v15.png` | Un fotograma por segundo de la v15 |
| `out/kiro-trailer-v14-mujer.mp4` | v14 con Lucía (4 s de suspenso) |
| `out/hoja-de-contacto-v14.png` | Un fotograma por segundo de la v14 |
| `out/kiro-trailer-v13-mujer.mp4` | v13 con Lucía (2 s de suspenso) |
| `out/hoja-de-contacto-v13.png` | Un fotograma por segundo de la v13 |
| `out/kiro-trailer-v12-mujer.mp4` | v12 con Lucía (1 s de intriga) |
| `out/hoja-de-contacto-v12.png` | Un fotograma por segundo de la v12 |
| `out/kiro-trailer-v11-mujer.mp4` | v11 con Lucía (golpe seco al pasar a blanco) |
| `out/kiro-trailer-v10-mujer.mp4` | v10 con Lucía (negro → blanco, sonido anterior) |
| `out/hoja-de-contacto-v10.png` | Un fotograma por segundo de la v10 |
| `lib/theme.py` | Tema oscuro, claro o mezcla (paleta en vivo) |
| `out/kiro-trailer-v9-mujer.mp4` | v9 con Lucía (todo negro) |
| `out/hoja-de-contacto-v9.png` | Un fotograma por segundo de la v9 |
| `out/kiro-trailer-v8-carlos.mp4` | v8 con Carlos |
| `out/kiro-trailer-v8-mujer.mp4` | **v8 con Lucía** |
| `out/kiro-trailer-v7-carlos.mp4`, `out/kiro-trailer-v7-mujer.mp4` | v7 (celular 3D, recorrido a tramos) |
| `out/hoja-de-contacto-v7.png` | Un fotograma por segundo de la v7 |
| `scenes/phone3d.py` | El celular 3D de la landing (proyección en perspectiva) |
| `out/kiro-trailer-v6-carlos.mp4` | v6 con Carlos |
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
