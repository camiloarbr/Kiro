// Arranque liviano de Kai en 3D. Mientras tanto se ve el póster: una imagen del mismo Kai 3D en reposo,
// con la misma cámara, así que el cambio a 3D no se nota.
//
// three.js (≈165 kB comprimido) y el modelo (≈275 kB) se cargan cuando la persona hace algo (mueve el
// mouse, toca, hace scroll o usa el teclado) o, si no hace nada, 6 s después del load. Así no compiten con
// el título, las fuentes ni la primera pintura, y no suman tiempo de bloqueo a la carga inicial.
// No se carga si: no hay WebGL, el usuario pidió «ahorro de datos» o falla la descarga (queda el póster).

function hayWebGL() {
  try {
    const c = document.createElement('canvas');
    const gl = c.getContext('webgl2') ?? c.getContext('webgl');
    if (!gl) return false;
    gl.getExtension('WEBGL_lose_context')?.loseContext();
    return true;
  } catch {
    return false;
  }
}

function enUnMomentoLibre(fn: () => void) {
  if ('requestIdleCallback' in window) requestIdleCallback(fn, { timeout: 1000 });
  else setTimeout(fn, 50);
}

const ranuras = [...document.querySelectorAll<HTMLElement>('[data-kai]')];
const conexion = (navigator as Navigator & { connection?: { saveData?: boolean } }).connection;
const EVENTOS = ['pointermove', 'pointerdown', 'keydown', 'wheel', 'touchstart', 'scroll'] as const;

if (ranuras.length && !conexion?.saveData && hayWebGL()) {
  let iniciado = false;
  const empezar = (e?: Event) => {
    // El navegador manda movimientos «falsos» del mouse al cargar o al hacer layout (movimiento 0): no cuentan
    if (e instanceof PointerEvent && e.type === 'pointermove' && !e.movementX && !e.movementY) return;
    if (iniciado) return;
    iniciado = true;
    for (const e of EVENTOS) removeEventListener(e, empezar);
    enUnMomentoLibre(() => {
      const reducido = matchMedia('(prefers-reduced-motion: reduce)').matches;
      import('./escena')
        .then((m) => m.iniciarKai(ranuras, reducido))
        .catch(() => {
          /* Sin 3D: los pósters ya están en su lugar */
        });
    });
  };
  for (const e of EVENTOS) addEventListener(e, empezar, { passive: true });
  const despuesDelLoad = () => setTimeout(() => empezar(), 6000);
  if (document.readyState === 'complete') despuesDelLoad();
  else addEventListener('load', despuesDelLoad, { once: true });
}
