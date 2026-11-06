// Medidas de Kai sacadas del modelo oficial (public/kai/kai-vivo.glb), en las unidades del modelo:
// mide 1,97 de alto, los pies están en y = -1 y la pantalla mira hacia +z.
// Ninguna de estas medidas cambia a Kai: solo dicen dónde está cada parte para poder moverla.

/** Los dos ojos en reposo (centro x, y) y su medio ancho / medio alto. Rectángulos redondeados. */
export const OJOS = {
  izq: [-0.132, 0.2329] as const,
  der: [0.1219, 0.2329] as const,
  medio: [0.108, 0.1222] as const,
  radio: 0.035,
};

/** Pantalla (superelipse): centro, semiejes y exponente. Los ojos y su brillo no salen de aquí. */
export const PANTALLA = { centro: [-0.013, 0.2775] as const, semi: [0.505, 0.405] as const, n: 3.16 };

/** Cuánto pueden moverse los ojos desde el reposo sin acercarse al borde rosa. */
export const RECORRIDO_OJOS = { x: 0.2, arriba: 0.22, abajo: 0.16 };

/** Puntos de giro: centro de los pies (el cuerpo se balancea aquí) y el cuello (la cabeza gira aquí). */
export const PIES = [0, -1.0, 0] as const;
export const CUELLO = [-0.015, -0.385, 0.02] as const;
/** Punto entre los dos ojos: desde aquí se calcula hacia dónde debe mirar Kai. */
export const ENTRE_OJOS = [-0.005, 0.233, 0.6] as const;

/**
 * Encuadre de la cámara (igual en el canvas y en los pósters): cuadrado, mirando 7° desde arriba, con los
 * pies al 89,9 % del alto y la coronilla al 11,7 %. Así el CSS sabe dónde quedan los pies sin mirar el 3D
 * (Hero, Acompanante y Contacto usan ese 0,899).
 */
export const CAMARA = { fov: 16, distancia: 8.894, inclinacion: 7 };
export const PIES_EN_CANVAS = 0.899;

/**
 * Vistas según el lugar. En la «portada» Kai está parado junto al cubo, a su derecha: gira 20° hacia el cubo
 * y el texto, y la cámara lo ve desde 12° arriba (el cubo se ve desde 24°: así el piso se lee igual, pero Kai
 * se ve de frente y cercano, no aplastado por la vista desde arriba).
 * En todas, la cámara se ajusta para que los pies sigan al 89,9 % del alto.
 */
export const VISTAS = {
  frente: { giro: 0, inclinacion: CAMARA.inclinacion },
  portada: { giro: -20, inclinacion: 12 },
} as const;
export type Vista = keyof typeof VISTAS;
export const vistaDe = (lugar: string): Vista => (lugar === 'portada' ? 'portada' : 'frente');
