// El «cerebro» de Kai: decide hacia dónde mira y qué hace en cada cuadro. No sabe nada de three.js:
// recibe puntos de la pantalla (cursor, botones, secciones) y devuelve una pose con ángulos y offsets.
//
// Orden de prioridad de la mirada: los OJOS siguen primero (rápido), la CABEZA acompaña después
// y el CUERPO apenas se mueve. Cada parte va hacia su objetivo con un resorte amortiguado, así nada salta.
import { RECORRIDO_OJOS } from './forma';

export interface Pose {
  cuerpoGiro: number; // rad, giro del cuerpo sobre los pies
  cuerpoLado: number; // rad, balanceo lateral
  cabezaGiro: number; // rad, izquierda / derecha
  cabezaCabeceo: number; // rad, + = mira hacia abajo
  cabezaLado: number; // rad, inclinación de curiosidad
  ojoX: number; // desplazamiento de los ojos en la pantalla (unidades del modelo)
  ojoY: number;
  parpado: number; // 1 abiertos … 0 cerrados
  respira: number; // -1 … 1
  salto: number; // altura extra de un saltito (unidades del modelo)
}

type Punto = { x: number; y: number };
type Reaccion = 'salto' | 'saludo' | 'atento';

/** Resorte críticamente amortiguado (solución exacta: estable aunque un cuadro tarde más). */
class Resorte {
  x = 0;
  v = 0;
  constructor(public w: number) {}
  paso(objetivo: number, dt: number) {
    const w = this.w;
    const c1 = this.x - objetivo;
    const c2 = this.v + w * c1;
    const e = Math.exp(-w * dt);
    this.x = objetivo + (c1 + c2 * dt) * e;
    this.v = (c2 - w * (c1 + c2 * dt)) * e;
    return this.x;
  }
}

const limitar = (v: number, a: number, b: number) => Math.min(b, Math.max(a, v));
const azar = (a: number, b: number) => a + Math.random() * (b - a);
// «Ruido» suave para los micromovimientos: suma de senos con frecuencias que no se repiten
const ruido = (t: number, s: number) => Math.sin(t * 0.71 + s) * 0.6 + Math.sin(t * 1.33 + s * 2.3) * 0.4;

/** Distancia virtual (px) entre los ojos de Kai y la pantalla: convierte px en ángulos. */
const DISTANCIA = 700;
/** Segundos sin mover el cursor para que Kai vuelva a su posición y mire por su cuenta. */
const QUIETO = 2.8;

export class Comportamiento {
  /** true con «reducir movimiento»: solo se mueven los ojos y el parpadeo. */
  reducido: boolean;

  private cursor: Punto | null = null;
  private cursorT = -99;
  private toque: Punto | null = null;
  private toqueT = -99;
  private boton: Element | null = null;
  private foco: Element | null = null;
  private abajo = 0; // 0…1: mirar al cubo de la portada

  private paseo: { yaw: number; pitch: number; hasta: number } | null = null;
  private proximoPaseo = azar(2, 4);
  private proximoParpadeo = azar(1.2, 3);
  private parpadeoT = -1;
  private dobleT = -1;
  private reaccion: { tipo: Reaccion; t: number } | null = null;
  private ultimoYaw = 0;

  private ojoX = new Resorte(26);
  private ojoY = new Resorte(26);
  private cabYaw = new Resorte(5.5);
  private cabPitch = new Resorte(5.5);
  private cabLado = new Resorte(4);
  private cuerpoYaw = new Resorte(2.6);
  private abajoR = new Resorte(6);

  constructor(reducido: boolean) {
    this.reducido = reducido;
  }

  // ---- Entradas -------------------------------------------------------------------------------
  moverCursor(x: number, y: number, t: number) {
    this.cursor = { x, y };
    this.cursorT = t;
  }
  soltarCursor() {
    this.cursor = null;
  }
  tocar(x: number, y: number, t: number) {
    this.toque = { x, y };
    this.toqueT = t;
  }
  mirarBoton(el: Element | null) {
    if (el && el !== this.boton) this.reaccionar('atento');
    this.boton = el;
  }
  cambiarFoco(el: Element | null) {
    this.foco = el;
  }
  /** 0…1: cuánto mira hacia abajo, al cubo, cuando empieza el scroll de la portada. */
  mirarAbajo(v: number) {
    this.abajo = v;
  }
  reaccionar(tipo: Reaccion) {
    if (this.reducido && tipo !== 'atento') {
      this.parpadear(0);
      return;
    }
    this.reaccion = { tipo, t: -1 };
  }

  // ---- Un cuadro ------------------------------------------------------------------------------
  /** @param ojos dónde están los ojos de Kai en la pantalla (px de la ventana) */
  paso(dt: number, t: number, ojos: Punto): Pose {
    dt = Math.min(Math.max(dt, 0), 1 / 20);
    const atento = !!this.boton;

    // 1. ¿Hacia qué punto mira? Botón > toque reciente > cursor que se movió hace poco > foco o al frente
    let objetivo: Punto | null = null;
    if (this.boton) objetivo = centro(this.boton);
    else if (this.toque && t - this.toqueT < 2.5) objetivo = this.toque;
    else if (this.cursor && t - this.cursorT < QUIETO) objetivo = this.cursor;
    else if (this.foco) objetivo = centro(this.foco);

    let yaw = 0;
    let pitch = 0;
    if (objetivo) {
      yaw = Math.atan2(objetivo.x - ojos.x, DISTANCIA);
      pitch = Math.atan2(objetivo.y - ojos.y, DISTANCIA);
    }

    // 2. Quieto: cada tanto mira alrededor un momento y vuelve
    const quieto = !this.boton && !(this.cursor && t - this.cursorT < QUIETO) && !(this.toque && t - this.toqueT < 2.5);
    if (quieto && !this.reducido) {
      if (!this.paseo && t > this.proximoPaseo) {
        const lado = Math.random() < 0.5 ? -1 : 1;
        this.paseo = { yaw: lado * azar(0.25, 0.6), pitch: azar(-0.25, 0.12), hasta: t + azar(0.7, 1.4) };
      }
      if (this.paseo && t > this.paseo.hasta) {
        this.paseo = null;
        this.proximoPaseo = t + azar(2.5, 5.5);
      }
      if (this.paseo) {
        yaw = this.paseo.yaw;
        pitch = this.paseo.pitch;
      }
    } else {
      this.paseo = null;
      this.proximoPaseo = Math.max(this.proximoPaseo, t + 2);
    }

    // 3. Mirar al cubo cuando empieza el scroll de la portada
    const ab = this.abajoR.paso(this.abajo, dt);
    yaw *= 1 - ab;
    pitch = pitch * (1 - ab) + 0.55 * ab;

    yaw = limitar(yaw, -0.9, 0.9);
    pitch = limitar(pitch, -0.7, 0.7);

    // Un cambio grande de mirada (sacádico) a veces trae un parpadeo, como en las personas
    if (Math.abs(yaw - this.ultimoYaw) > 0.35 && Math.random() < 0.35) this.parpadear(t);
    this.ultimoYaw = yaw;

    // 4. Repartir la mirada: cuerpo (poco), cabeza (algo) y ojos (el resto)
    const reaccion = this.reaccionEn(dt, t);
    const quietoCuerpo = this.reducido;
    const cuerpoYaw = this.cuerpoYaw.paso(quietoCuerpo ? 0 : limitar(yaw * 0.12, -0.09, 0.09), dt);
    const factor = atento ? 0.62 : 0.5;
    const cabYaw = this.cabYaw.paso(quietoCuerpo ? 0 : limitar(yaw * factor, -0.38, 0.38), dt);
    const cabPitch = this.cabPitch.paso(quietoCuerpo ? 0 : limitar(pitch * 0.42, -0.1, 0.2), dt);
    const curiosidad = atento && !quietoCuerpo ? 0.07 * Math.sign(yaw || 1) : 0;
    const cabLado = this.cabLado.paso(quietoCuerpo ? 0 : curiosidad + reaccion.lado, dt);

    // Los ojos miran lo que la cabeza todavía no alcanza a girar
    const relYaw = yaw - cabYaw - cuerpoYaw;
    const relPitch = pitch - cabPitch;
    let ox = limitar(relYaw / 0.5, -1, 1) * RECORRIDO_OJOS.x;
    let oy = -limitar(relPitch / 0.45, -1, 1);
    oy *= oy > 0 ? RECORRIDO_OJOS.arriba : RECORRIDO_OJOS.abajo;
    // Que nunca se salgan de la pantalla: elipse de recorrido
    const ry = oy > 0 ? RECORRIDO_OJOS.arriba : RECORRIDO_OJOS.abajo;
    const e = Math.hypot(ox / RECORRIDO_OJOS.x, oy / ry);
    if (e > 1) {
      ox /= e;
      oy /= e;
    }
    const ojoX = this.ojoX.paso(ox, dt);
    const ojoY = this.ojoY.paso(oy, dt);

    // 5. Vida: respiración, micromovimientos y parpadeo
    const vivo = this.reducido ? 0 : 1;
    const respira = Math.sin((t * 2 * Math.PI) / 3.8) * vivo;
    const micro = vivo * (quieto ? 1 : 0.4);

    return {
      cuerpoGiro: cuerpoYaw,
      cuerpoLado: 0.012 * ruido(t * 0.6, 4) * vivo,
      cabezaGiro: cabYaw + 0.025 * ruido(t * 0.45, 0) * micro,
      cabezaCabeceo: cabPitch + 0.015 * ruido(t * 0.5, 2) * micro + 0.008 * respira,
      cabezaLado: cabLado + 0.02 * ruido(t * 0.4, 7) * micro,
      ojoX,
      ojoY,
      parpado: this.parpado(t),
      respira,
      salto: reaccion.salto,
    };
  }

  private parpadear(t: number) {
    if (this.parpadeoT < 0 || t - this.parpadeoT > 0.3) this.parpadeoT = t;
  }

  private parpado(t: number): number {
    if (t > this.proximoParpadeo) {
      this.parpadear(t);
      if (Math.random() < 0.18) this.dobleT = t + 0.26;
      this.proximoParpadeo = t + azar(2.2, 5.5);
    }
    if (this.dobleT > 0 && t > this.dobleT) {
      this.parpadeoT = t;
      this.dobleT = -1;
    }
    if (this.parpadeoT < 0) return 1;
    const u = t - this.parpadeoT;
    // Cierra en 70 ms, queda cerrado 40 ms y abre en 130 ms
    if (u < 0.07) return 1 - suave(u / 0.07);
    if (u < 0.11) return 0;
    if (u < 0.24) return suave((u - 0.11) / 0.13);
    return 1;
  }

  /** Reacciones cortas: saltito, saludo (saltito suave + parpadeo) y gesto de atención. */
  private reaccionEn(dt: number, t: number): { salto: number; lado: number } {
    const r = this.reaccion;
    if (!r) return { salto: 0, lado: 0 };
    if (r.t < 0) {
      r.t = 0;
      if (r.tipo !== 'atento') this.dobleT = t + 0.4;
    }
    r.t += dt;
    if (r.tipo === 'atento') {
      if (r.t > 1) this.reaccion = null;
      // Ladea la cabeza un momento, como quien presta atención
      return { salto: 0, lado: 0.06 * Math.sin(Math.PI * Math.min(r.t, 1)) };
    }
    const dur = r.tipo === 'salto' ? 0.55 : 0.42;
    const alto = r.tipo === 'salto' ? 0.12 : 0.05;
    if (r.t > dur) {
      this.reaccion = null;
      return { salto: 0, lado: 0 };
    }
    const u = r.t / dur;
    return { salto: alto * Math.sin(Math.PI * u), lado: 0.05 * Math.sin(Math.PI * 2 * u) };
  }
}

const suave = (u: number) => u * u * (3 - 2 * u);

function centro(el: Element): Punto {
  const r = el.getBoundingClientRect();
  // Elementos más altos que la ventana: el centro de la parte visible
  const y0 = Math.max(r.top, 0);
  const y1 = Math.min(r.bottom, window.innerHeight);
  return { x: r.left + r.width / 2, y: y1 > y0 ? (y0 + y1) / 2 : r.top + r.height / 2 };
}
