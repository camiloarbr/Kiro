// Kai en 3D con three.js: carga el modelo oficial, lo arma en piezas que se pueden girar (cuerpo, cuello,
// cabeza), le pone los ojos en vivo y lo dibuja en un solo <canvas> que viaja entre los lugares de la página
// (portada → acompañante → contacto). Este archivo pesa (three.js): iniciar.ts lo carga solo cuando hace falta.
import {
  CanvasTexture,
  BackSide,
  BufferAttribute,
  DirectionalLight,
  Group,
  HemisphereLight,
  Mesh,
  MeshBasicMaterial,
  MeshStandardMaterial,
  NeutralToneMapping,
  PerspectiveCamera,
  PlaneGeometry,
  PMREMGenerator,
  Scene,
  SphereGeometry,
  SRGBColorSpace,
  Vector3,
  WebGLRenderer,
} from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
import { CAMARA, CUELLO, ENTRE_OJOS, PIES } from './forma';
import { ponerOjos, type UniformesOjos } from './ojos';
import { Comportamiento, type Pose } from './comportamiento';

export const MODELO = '/kai/kai-vivo.glb';

export const POSE_REPOSO: Pose = {
  cuerpoGiro: 0,
  cuerpoLado: 0,
  cabezaGiro: 0,
  cabezaCabeceo: 0,
  cabezaLado: 0,
  ojoX: 0,
  ojoY: 0,
  parpado: 1,
  respira: 0,
  salto: 0,
};

export interface EscenaKai {
  renderer: WebGLRenderer;
  aplicar(pose: Pose): void;
  dibujar(): void;
  /** Dónde quedan los ojos de Kai dentro del canvas (0…1 en x e y, desde arriba a la izquierda). */
  ojosEnCanvas: { x: number; y: number };
  liberar(): void;
}

/**
 * Arma la escena sobre un canvas. Devuelve funciones para poner una pose y dibujar.
 * La usa iniciarKai (página) y también sirve para generar los pósters estáticos con la misma cámara.
 */
/** Escena de estudio: luces, reflejos y cámara. La comparten Kai en la página y los pósters. */
export function montarEstudio(renderer: WebGLRenderer) {
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = SRGBColorSpace;
  // Tonemapping «neutral»: respeta los colores de la marca (otros, como ACES, apagan el morado)
  renderer.toneMapping = NeutralToneMapping;
  renderer.toneMappingExposure = 1;

  const escena = new Scene();
  const pmrem = new PMREMGenerator(renderer);
  // Reflejos para el vidrio de la pantalla: un cielo de estudio en degradado (claro arriba, oscuro abajo).
  // Sin paneles de luz: sus reflejos parecían manchas donde descansan los ojos
  escena.environment = pmrem.fromScene(cieloDeEstudio(), 0.02).texture;
  escena.environmentIntensity = 0.45;
  pmrem.dispose();

  // Luz de estudio: principal arriba a la izquierda, relleno lavanda y un contraluz que separa del fondo
  escena.add(new HemisphereLight(0xffffff, 0x9d86c4, 1.45));
  const principal = new DirectionalLight(0xffffff, 1.55);
  principal.position.set(-2.5, 4, 5);
  const relleno = new DirectionalLight(0xf0e6ff, 0.6);
  relleno.position.set(3, 1.5, 3);
  const contraluz = new DirectionalLight(0xffffff, 0.8);
  contraluz.position.set(1.5, 3, -4);
  escena.add(principal, relleno, contraluz);

  const camara = new PerspectiveCamera(CAMARA.fov, 1, 0.1, 50);
  const inc = (CAMARA.inclinacion * Math.PI) / 180;
  const mira = new Vector3(...CAMARA.mira);
  camara.position.set(mira.x, mira.y + CAMARA.distancia * Math.sin(inc), mira.z + CAMARA.distancia * Math.cos(inc));
  camara.lookAt(mira);
  return { escena, camara };
}

/**
 * Arma a Kai sobre un canvas. Devuelve funciones para poner una pose y dibujar.
 * La usa iniciarKai (página) y también sirve para generar los pósters estáticos con la misma cámara.
 */
export async function crearEscena(canvas: HTMLCanvasElement): Promise<EscenaKai> {
  const renderer = new WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' });
  const { escena, camara } = montarEstudio(renderer);

  // ---- Modelo ----------------------------------------------------------------------------------
  const cargador = new GLTFLoader();
  cargador.setMeshoptDecoder(MeshoptDecoder);
  const gltf = await cargador.loadAsync(MODELO);
  gltf.scene.updateMatrixWorld(true);
  const cuerpo = gltf.scene.getObjectByName('cuerpo') as Mesh;
  const cabeza = gltf.scene.getObjectByName('cabeza') as Mesh;

  // Cada malla conserva su matriz propia (el GLB guarda las posiciones comprimidas y esta matriz las
  // devuelve a las medidas reales). Las colgamos de grupos que hacen de articulaciones.
  const fijar = (m: Mesh) => {
    const local = m.matrixWorld.clone();
    m.removeFromParent();
    m.matrixAutoUpdate = false;
    m.matrix.copy(local);
    return local;
  };
  fijar(cuerpo);
  const localCabeza = fijar(cabeza);

  //  raiz (pies en el piso, sube con el saltito)
  //   └ pies (balanceo del cuerpo) → cuerpo
  //      └ cuello (giro de la cabeza; sube y baja apenas al respirar) → cabeza
  // Nada se escala: la ficha técnica no permite deformar a Kai.
  const raiz = new Group();
  const pies = new Group();
  const cuello = new Group();
  const deshacerPies = new Group();
  const deshacerCuello = new Group();
  pies.position.set(PIES[0], 0, PIES[2]);
  deshacerPies.position.set(-PIES[0], -PIES[1], -PIES[2]);
  const cuelloSobrePies = new Vector3(CUELLO[0] - PIES[0], CUELLO[1] - PIES[1], CUELLO[2] - PIES[2]);
  cuello.position.copy(cuelloSobrePies);
  cuello.rotation.order = 'YXZ';
  deshacerCuello.position.set(-CUELLO[0], -CUELLO[1], -CUELLO[2]);
  raiz.add(pies);
  pies.add(deshacerPies, cuello);
  deshacerPies.add(cuerpo);
  cuello.add(deshacerCuello);
  deshacerCuello.add(cabeza);
  escena.add(raiz);

  // Material: el mismo del modelo; la cabeza lleva una copia con los ojos en vivo
  const matCuerpo = cuerpo.material as MeshStandardMaterial;
  const matCabeza = matCuerpo.clone();
  cabeza.material = matCabeza;
  const ojos: UniformesOjos = ponerOjos(matCabeza, localCabeza);

  // Sombra de contacto: un óvalo suave bajo los pies (se achica cuando salta)
  const sombra = new Mesh(
    new PlaneGeometry(1.25, 0.7),
    new MeshBasicMaterial({ map: texturaSombra(), transparent: true, depthWrite: false, opacity: 0.42 }),
  );
  sombra.rotation.x = -Math.PI / 2;
  sombra.position.y = 0.003;
  escena.add(sombra);

  // Dónde quedan los ojos en el canvas (para calcular hacia dónde mirar)
  const p = new Vector3(ENTRE_OJOS[0], ENTRE_OJOS[1] - PIES[1], ENTRE_OJOS[2]).project(camara);
  const ojosEnCanvas = { x: (p.x + 1) / 2, y: (1 - p.y) / 2 };

  function aplicar(pose: Pose) {
    raiz.position.y = pose.salto;
    pies.rotation.set(0, pose.cuerpoGiro, pose.cuerpoLado);
    // Respirar: la cabeza sube y baja 4 milésimas de su alto (el collar oculto tapa la unión)
    cuello.position.set(cuelloSobrePies.x, cuelloSobrePies.y + 0.008 * pose.respira, cuelloSobrePies.z);
    cuello.rotation.set(pose.cabezaCabeceo, pose.cabezaGiro, pose.cabezaLado);
    ojos.uOjo.value.set(pose.ojoX, pose.ojoY);
    ojos.uParpado.value = pose.parpado;
    const s = 1 - Math.min(pose.salto * 2.2, 0.5);
    sombra.scale.set(s, s, 1);
    (sombra.material as MeshBasicMaterial).opacity = 0.42 * s;
  }

  // Compila los shaders sin bloquear (en paralelo si el navegador lo permite) antes del primer cuadro
  aplicar(POSE_REPOSO);
  await renderer.compileAsync(escena, camara);

  return {
    renderer,
    aplicar,
    dibujar: () => renderer.render(escena, camara),
    ojosEnCanvas,
    liberar() {
      renderer.dispose();
      escena.traverse((o) => {
        if (o instanceof Mesh) {
          o.geometry.dispose();
          (o.material as MeshStandardMaterial).dispose();
        }
      });
    },
  };
}

function cieloDeEstudio() {
  const cielo = new Scene();
  const geo = new SphereGeometry(10, 32, 16);
  const pos = geo.attributes.position;
  const col = new Float32Array(pos.count * 3);
  for (let i = 0; i < pos.count; i++) {
    const y = pos.getY(i) / 10; // -1 abajo … 1 arriba
    const t = Math.min(Math.max((y + 0.15) / 1.0, 0), 1);
    const v = 0.12 + 0.88 * t * t;
    col.set([v * 0.96, v * 0.92, v], i * 3);
  }
  geo.setAttribute('color', new BufferAttribute(col, 3));
  cielo.add(new Mesh(geo, new MeshBasicMaterial({ vertexColors: true, side: BackSide })));
  return cielo;
}

function texturaSombra() {
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const g = c.getContext('2d')!;
  const d = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  d.addColorStop(0, 'rgba(46,16,96,0.85)');
  d.addColorStop(0.45, 'rgba(46,16,96,0.4)');
  d.addColorStop(1, 'rgba(46,16,96,0)');
  g.fillStyle = d;
  g.fillRect(0, 0, 128, 128);
  const t = new CanvasTexture(c);
  t.colorSpace = SRGBColorSpace;
  return t;
}

// =================================================================================================
// En la página: un canvas, varios lugares («ranuras») y el comportamiento
// =================================================================================================

/** Orden de preferencia cuando dos lugares se ven a la vez. */
const PRIORIDAD = ['contacto', 'acompanante', 'portada', 'portada-movil'];

export async function iniciarKai(ranuras: HTMLElement[], reducidoInicial: boolean) {
  const canvas = document.createElement('canvas');
  canvas.className = 'kai-canvas';
  canvas.setAttribute('aria-hidden', 'true');
  const kai = await crearEscena(canvas);
  const cerebro = new Comportamiento(reducidoInicial);
  const html = document.documentElement;

  ranuras.sort((a, b) => PRIORIDAD.indexOf(a.dataset.kai!) - PRIORIDAD.indexOf(b.dataset.kai!));

  let actual: HTMLElement | null = null;
  let anchoCss = 0;
  let altoCss = 0;
  let razon = 0;
  let calidad = 1;
  let corriendo = false;
  let ultimo = performance.now();
  let lentos = 0;
  let cuadros = 0;
  let ultimaEntrada = performance.now(); // último mouse, toque, tecla o scroll
  let perdido = false; // el navegador quitó el contexto WebGL

  // ---- ¿Dónde debe estar Kai ahora? -----------------------------------------------------------
  function visible(r: HTMLElement) {
    if (r.getClientRects().length === 0) return false; // display: none (o un padre)
    if (getComputedStyle(r).visibility !== 'visible') return false;
    const b = r.getBoundingClientRect();
    return b.width > 2 && b.bottom > 0 && b.top < innerHeight && b.right > 0 && b.left < innerWidth;
  }
  const elegir = () => ranuras.find(visible) ?? null;

  function ajustarTamano(forzar = false) {
    if (!actual) return;
    const w = actual.clientWidth;
    const h = actual.clientHeight;
    // En la portada el lugar está dentro de la perspectiva del cubo y se ve más grande que su tamaño CSS:
    // la resolución sale del tamaño real en pantalla para que no se vea borroso
    const b = actual.getBoundingClientRect();
    const aumento = w > 0 ? b.width / w : 1;
    const r = Math.min(devicePixelRatio * aumento, 2.5) * calidad;
    if (forzar || w !== anchoCss || h !== altoCss || Math.abs(r - razon) > 0.05) {
      anchoCss = w;
      altoCss = h;
      razon = r;
      kai.renderer.setPixelRatio(r);
      kai.renderer.setSize(w, h, false);
    }
  }

  let ultimoLugar = '';
  function mudarse(destino: HTMLElement | null) {
    if (destino === actual) return;
    actual?.classList.remove('kai-en-vivo');
    actual = destino;
    html.dataset.kaiEn = destino?.dataset.kai ?? '';
    if (!destino) return;
    destino.append(canvas);
    ajustarTamano(true);
    // Saluda al llegar a otro lugar (también al volver a la portada); en el contacto, un saltito
    const lugar = destino.dataset.kai!;
    if (lugar !== ultimoLugar) {
      if (lugar === 'contacto') cerebro.reaccionar('salto');
      else if (ultimoLugar) cerebro.reaccionar('saludo');
    }
    ultimoLugar = lugar;
  }

  // ---- Cuadro a cuadro -------------------------------------------------------------------------
  const portada = document.getElementById('inicio');
  function cuadro(ahora: number) {
    if (!corriendo) return;
    // Si nadie interactúa hace 4 s, Kai solo respira y parpadea: basta con 30 cuadros por segundo
    const enReposo = ahora - ultimaEntrada > 4000;
    if (enReposo && ahora - ultimo < 31) {
      requestAnimationFrame(cuadro);
      return;
    }
    // El primer cuadro puede traer una hora un poco anterior a «ultimo»: nunca un dt negativo
    const dt = Math.max(0, (ahora - ultimo) / 1000);
    ultimo = ahora;

    mudarse(elegir());
    if (!actual) {
      detener();
      return;
    }
    if (++cuadros % 30 === 0) ajustarTamano();

    // Mirar al cubo cuando empieza el scroll de la portada
    if (portada && actual.dataset.kai?.startsWith('portada')) {
      const bajado = -portada.getBoundingClientRect().top;
      cerebro.mirarAbajo(Math.min(Math.max((bajado - 8) / 110, 0), 1));
    } else cerebro.mirarAbajo(0);

    const b = canvas.getBoundingClientRect();
    const pose = cerebro.paso(dt, ahora / 1000, {
      x: b.left + kai.ojosEnCanvas.x * b.width,
      y: b.top + kai.ojosEnCanvas.y * b.height,
    });
    kai.aplicar(pose);
    kai.dibujar();
    if (!actual.classList.contains('kai-en-vivo')) actual.classList.add('kai-en-vivo');

    // Si el equipo no da abasto (cuadros de más de 28 ms seguidos), baja la resolución.
    // En reposo los cuadros duran 33 ms a propósito: esos no cuentan
    if (!enReposo) lentos = dt > 0.028 ? lentos + 1 : Math.max(0, lentos - 1);
    if (lentos > 90 && calidad > 0.55) {
      calidad *= 0.75;
      lentos = 0;
      ajustarTamano(true);
    }
    requestAnimationFrame(cuadro);
  }
  function arrancar() {
    if (corriendo || document.hidden || perdido) return;
    corriendo = true;
    ultimo = performance.now();
    requestAnimationFrame(cuadro);
  }
  function detener() {
    corriendo = false;
  }

  // ---- Entradas --------------------------------------------------------------------------------
  const seg = () => performance.now() / 1000;
  const actividad = () => (ultimaEntrada = performance.now());
  for (const e of ['pointermove', 'pointerdown', 'keydown', 'scroll', 'wheel'])
    addEventListener(e, actividad, { passive: true });
  addEventListener(
    'pointermove',
    (e) => {
      if (e.pointerType === 'touch') cerebro.tocar(e.clientX, e.clientY, seg());
      else cerebro.moverCursor(e.clientX, e.clientY, seg());
    },
    { passive: true },
  );
  addEventListener(
    'pointerdown',
    (e) => {
      if (e.pointerType === 'touch') cerebro.tocar(e.clientX, e.clientY, seg());
    },
    { passive: true },
  );
  document.addEventListener('mouseout', (e) => {
    if (!e.relatedTarget) cerebro.soltarCursor();
  });

  // Botones principales: los mira al pasar el mouse o llegar con el teclado, y salta al hacer clic
  for (const el of document.querySelectorAll('[data-kai-mira]')) {
    el.addEventListener('pointerenter', () => cerebro.mirarBoton(el));
    el.addEventListener('pointerleave', () => cerebro.mirarBoton(null));
    el.addEventListener('focusin', () => cerebro.mirarBoton(el));
    el.addEventListener('focusout', () => cerebro.mirarBoton(null));
    el.addEventListener('click', () => cerebro.reaccionar('salto'));
  }

  // Secciones: cuando el cursor está quieto, Kai mira el contenido que se está leyendo
  const proporcion = new Map<Element, number>();
  let foco: Element | null = null;
  const observador = new IntersectionObserver(
    (entradas) => {
      for (const en of entradas) proporcion.set(en.target, en.isIntersecting ? en.intersectionRatio : 0);
      let mejor: Element | null = null;
      let max = 0.15;
      for (const [el, p] of proporcion) if (p > max) [mejor, max] = [el, p];
      if (mejor !== foco) {
        foco = mejor;
        cerebro.cambiarFoco(mejor);
        if (mejor && actual?.dataset.kai === 'acompanante') cerebro.reaccionar('atento');
      }
    },
    { threshold: [0, 0.15, 0.3, 0.5, 0.75, 1] },
  );
  for (const el of document.querySelectorAll('[data-kai-foco]')) observador.observe(el);

  // ---- Arrancar, pausar y casos raros ------------------------------------------------------------
  // Pausado, cada scroll revisa si algún lugar volvió a verse. En el cuadro siguiente y no en el evento:
  // las animaciones con scroll (que muestran u ocultan al acompañante) se actualizan después del evento
  let revisando = false;
  const revisar = () => {
    if (corriendo || revisando) return;
    revisando = true;
    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        revisando = false;
        if (!corriendo && elegir()) arrancar();
      }),
    );
  };
  addEventListener('scroll', revisar, { passive: true });
  addEventListener('scrollend', revisar);
  addEventListener('resize', () => {
    ajustarTamano(true);
    revisar();
  });
  document.addEventListener('visibilitychange', () => (document.hidden ? detener() : arrancar()));
  matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => (cerebro.reducido = e.matches));

  // Si el navegador pierde el contexto WebGL, vuelven los pósters estáticos
  canvas.addEventListener('webglcontextlost', () => {
    perdido = true;
    detener();
    actual?.classList.remove('kai-en-vivo');
    canvas.remove();
    html.dataset.kaiEn = '';
  });

  // Primer cuadro igual al póster (pose de reposo), así el cambio de imagen a 3D no se nota
  kai.aplicar(POSE_REPOSO);
  arrancar();
}

export type { Pose };
