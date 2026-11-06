# Kai en 3D en la landing

Kai aparece como personaje 3D en tiempo real: sigue el cursor con los ojos, gira un poco la cabeza, parpadea, respira y reacciona a la página. Este documento explica cómo está hecho y qué no se puede cambiar.

## Dónde aparece

Un solo `<canvas>` con un solo Kai pasa por cuatro lugares (`data-kai`). Siempre está en el lugar que se ve; si se ven dos, gana el primero de esta lista:

| Lugar | Componente | Cuándo se ve |
| --- | --- | --- |
| `contacto` | `Contacto.astro` | Al llegar al contacto: da un saltito y mira el botón del correo |
| `acompanante` | `Acompanante.astro` | Computador, desde «Tu día» hasta antes del contacto, abajo a la izquierda |
| `portada` | `Hero.astro` (`.kai-ancla`) | Computador: parado en la tapa del cubo, girado y visto desde arriba como el cubo (vista «portada»). Cuando el cubo empieza a desarmarse, la explosión lo lanza: vuela hacia la derecha dando vueltas y cae con los bloques hasta perderse (5–18 % del scroll de la portada) |
| `portada-movil` | `Hero.astro` (`.hero-bot`) | Celular y tablet: al lado de «Conoce más»; sale de escena con el texto |

En todos se ve primero el **póster**: `public/kai/kai-3d-*.webp`, un render del mismo Kai en reposo con la misma cámara (en la portada, `kai-3d-portada-*.webp`, con la vista del cubo). Cuando el 3D está listo, el canvas aparece encima con un fundido y el cambio no se nota. Sin WebGL, sin JavaScript, con «ahorro de datos» o si algo falla, queda el póster.

## Archivos

```
public/kai/kai-vivo.glb          ← modelo para animar (274 kB): cabeza y cuerpo separados, pantalla sin ojos
public/kai/kai-3d-180|360|540.webp ← pósters (vista de frente)
public/kai/kai-3d-portada-180|360|540.webp ← pósters de la portada (vista del cubo)
src/components/KaiVivo.astro     ← el lugar: póster + script de arranque
src/scripts/kai/
  iniciar.ts        ← arranque liviano (1 kB). Carga lo demás solo cuando hace falta
  escena.ts         ← three.js: luces, cámara, modelo, articulaciones, el canvas que viaja y las entradas
  comportamiento.ts ← el «cerebro»: hacia dónde mirar, parpadeo, respiración y reacciones (sin three.js)
  ojos.ts           ← el shader que dibuja los ojos sobre la pantalla
  forma.ts          ← medidas de Kai sacadas del modelo (ojos, pantalla, cuello, cámara y vistas)
```

## Cómo funciona

**Carga.** `iniciar.ts` espera a que la persona haga algo (mover el mouse, tocar, hacer scroll o usar el teclado) o 6 s después del `load`. Recién ahí pide `escena.ts` (three.js, ≈165 kB con gzip) y el modelo. Así la carga inicial no cambia: Lighthouse móvil da 99 / 100 / 100 / 100.

**El modelo no tenía huesos.** `kai-maestro.glb` es una sola malla, sin esqueleto ni animaciones, y los ojos estaban pintados en la textura (y en relieve en la malla). Para moverlo sin cambiarlo se preparó `kai-vivo.glb` a partir del maestro:

1. **Cabeza y cuerpo separados** en el punto más angosto del cuello (y = −0,385). La cabeza gira sobre ese punto.
2. **Collar oculto:** un tubo del color del cuerpo dentro de la cabeza. Solo se ve si un giro abre la unión; en reposo no se ve.
3. **Pantalla limpia:** se quitaron los ojos y su resplandor de la textura (el vidrio de alrededor se reconstruyó con un ajuste suave) y se aplanó el relieve de los ojos en la malla.
4. Comprimido con meshopt y texturas WebP de 1024 px (de 2,6 MB a 274 kB), validado con el glTF Validator (0 errores).

**Los ojos.** `ojos.ts` agrega unas líneas al shader estándar de three.js: cada píxel de la cabeza mide su distancia a los dos ojos (rectángulos redondeados con las medidas de la ficha técnica). Adentro es blanco emisivo; cerca del borde, el halo lavanda medido en la textura original. Así los ojos se mueven sobre la pantalla sin salirse de ella y parpadean aplastándose hacia su centro. En reposo coinciden con el modelo maestro.

**La mirada.** Cada cuadro, `comportamiento.ts` convierte el punto que mira (cursor, botón, toque o sección) en un ángulo y lo reparte: los ojos van primero (rápido), la cabeza acompaña después y el cuerpo apenas gira. Cada parte va hacia su objetivo con un resorte amortiguado, así nada salta. Los ojos miran lo que la cabeza todavía no alcanzó a girar, como las personas.

**Prioridad de la mirada:** botón con el mouse encima o con el foco del teclado → toque reciente → cursor en movimiento → contenido de la sección que se lee (`data-kai-foco`) → al frente.

**Vistas.** En la portada Kai está parado en la tapa del cubo, que CSS gira con `rotateX(-24deg) rotateY(-35deg)`. Kai es un dibujo plano dentro de ese 3D: CSS no puede girarlo, así que el giro va dentro de three.js. En la vista «portada» el cuerpo (con su sombra) gira −35° y la cámara lo mira desde 24° arriba, en vez de los 7° de la vista «frente» que usan los demás lugares. `ponerCamara()` sube el punto que mira la cámara lo justo para que los pies sigan al 89,9 % del alto, así el CSS de cada lugar no cambia. El canvas cambia de vista al mudarse (`verDesde`). La mirada sigue siendo relativa al cuerpo: en reposo Kai mira hacia donde mira el cubo.

**Rendimiento.** Se dibuja solo mientras algún lugar se ve y la pestaña está activa. La resolución sale del tamaño real en pantalla (máx. 2,5×) y baja sola si el equipo no alcanza 35 cuadros por segundo.

## Comportamiento

| Qué | Cómo |
| --- | --- |
| Seguir el cursor | Ojos dentro de la pantalla; cabeza hasta ±22° de lado, 11° hacia abajo y 6° hacia arriba; cuerpo hasta ±5° |
| Parpadeo | Cada 2,2–5,5 s, a veces doble; también, a veces, al cambiar mucho de mirada |
| Respirar | La cabeza sube y baja muy poco cada 3,8 s |
| Quieto | Si el cursor no se mueve en 2,8 s, vuelve al frente o mira el contenido; cada tanto mira a un lado y vuelve |
| Botones (`data-kai-mira`) | Al pasar el mouse o llegar con Tab: los mira y ladea la cabeza. Al hacer clic: saltito |
| Scroll en la portada | Mira hacia abajo, al cubo. Al explotar el cubo sale volando en parábola (CSS: x, y y giro en propiedades separadas) y, si el 3D cargó, da además una vuelta sobre sí mismo (`girarExtra`, mismo tramo del scroll) |
| Cambio de lugar | Saluda (saltito corto y parpadeo). En el contacto: saltito |
| Celular | Mira hacia donde se toca; el resto igual |
| «Reducir movimiento» | Solo mueve los ojos y parpadea: sin giros, respiración ni saltos |

## Reglas que no se rompen

- Kai sale del modelo maestro. Nada se escala ni se deforma: solo se giran o se mueven piezas enteras.
- Los ojos conservan forma, tamaño, color y brillo de la ficha técnica. Parpadear es la única variación; no hay otras expresiones (decisión D8).
- Los colores del modelo no se tocan: las luces son blancas y la escena usa tonemapping «neutral», que respeta el morado.
- No usar `RoomEnvironment` de three.js: sus paneles de luz se reflejaban en el vidrio como manchas donde descansan los ojos. Los reflejos salen de un cielo de estudio en degradado.

## Cambiar algo

- **Tamaño o lugar:** `--kai-lado` en el CSS de cada componente. El cuadro es cuadrado y los pies quedan al 89,9 % de su alto.
- **Comportamiento:** constantes de `comportamiento.ts` (`DISTANCIA`, `QUIETO`, los `Resorte` y los límites de cada parte).
- **Luces o cámara:** `montarEstudio()` en `escena.ts`, y `CAMARA` y `VISTAS` en `forma.ts`. Si cambian (o cambia el giro del cubo de la portada en `Hero.astro`), hay que volver a generar los pósters de cada vista con la misma pose de reposo: `crearEscena(canvas, vista)`, `aplicar(POSE_REPOSO)`, `dibujar()` y `canvas.toDataURL('image/webp', 0.9)` a 180, 360 y 540 px.
- **Modelo:** `kai-vivo.glb` se genera desde `kai-maestro.glb` con el script de la carpeta compartida (`marca/kai/3d/kai-vivo/`). No se edita a mano.
