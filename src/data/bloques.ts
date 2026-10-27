// Portada «bloques-cursor»: 27 bloques de 62 px (el cursor de la marca) que con el scroll
// pasan por 4 formas. Cada bloque recibe sus posiciones como variables CSS y la keyframe
// «bloque» de Hero.astro las recorre. Referencia: docs/diseno/referencia/portada-bloques-cursor.dc.html
//
//   0–6 %   cubo 3×3×3 a la derecha del título      → --x0 --y0 --z0
//   20 %    nube: los bloques explotan girando       → --xc --yc --zc --rx --ry --rz
//   36–64 % 3 mini cubos 2×2×2                        → --x2 --y2 --z2 (celular: --mx2 --my2)
//   76 %+   cubo 3×3×3 al centro                      → --x3 --y3 --z3

export const LADO = 62;
const MEDIO = LADO / 2;

type Trio = [number, number, number];

/*
  Celda del cubo 3×3×3 que ocupa cada bloque (-1, 0 o 1 en x, y, z). Es una permutación
  «desordenada» a propósito: así cada bloque recorre un camino distinto al formar los mini cubos.
  Mismo orden que en la referencia.
*/
const celdas: Trio[] = [
  [0, -1, -1], [-1, 0, 1], [1, 0, -1], [-1, 1, 1], [-1, 1, 0], [1, 1, 0], [0, 0, 1], [1, -1, -1], [1, 1, 1],
  [1, -1, 0], [0, 0, 0], [1, 1, -1], [0, 1, -1], [1, 0, 1], [-1, -1, -1], [-1, 1, -1], [0, 1, 0], [1, 0, 0],
  [0, -1, 1], [-1, 0, -1], [0, 1, 1], [-1, -1, 1], [-1, -1, 0], [1, -1, 1], [0, 0, -1], [-1, 0, 0], [0, -1, 0],
];

// Nube de la «explosión» (valores fijos de la referencia): x, y, z en px y giros X, Y, Z en grados.
const nube: [number, number, number, number, number, number][] = [
  [426, -74, 286, -163, 129, -76], [167, -247, -115, 114, -115, 29], [463, -89, 29, -157, -159, -106],
  [488, -55, -112, 31, -17, -72], [557, 113, -154, 27, 9, 135], [518, -141, 288, -137, -29, 93],
  [171, -17, -276, 61, 95, 26], [605, -125, 117, 34, 29, -16], [584, 266, -16, 59, -158, 73],
  [468, 296, 193, -78, -41, 61], [94, -34, -199, -138, -159, 97], [158, -166, -65, 134, -151, -18],
  [410, 228, 192, 131, -80, -30], [295, 228, 275, -126, -117, -96], [220, -19, 53, -85, -179, -29],
  [302, 31, 272, 69, 6, 42], [486, -287, 240, 101, 135, 107], [315, -73, -238, 48, -158, -156],
  [205, -219, -96, -161, -180, -126], [141, -95, -285, 135, 41, -127], [231, -105, -82, -136, 126, 178],
  [360, -20, -248, -143, -57, -85], [577, -220, -286, 162, 10, -127], [406, -303, 17, 172, 131, 71],
  [237, -93, -200, 98, 12, 100], [278, -182, 187, 175, 127, 110], [571, 139, -164, 6, -52, -170],
];

// Colores de las caras: frente/atrás, tapa y costados (más oscuro para dar volumen).
interface Tono {
  frente: string;
  tapa: string;
  lado: string;
}
const violeta: Tono = { frente: '#8B2CF5', tapa: '#B07CFF', lado: '#5B17B8' };
// Un tono por mini cubo: Entendemos (claro), Construimos (medio), Acompañamos (oscuro)
const tonosMiniCubos: Tono[] = [
  { frente: '#B07CFF', tapa: '#D9C4FF', lado: '#8B2CF5' },
  violeta,
  { frente: '#5B17B8', tapa: '#8B2CF5', lado: '#3A1677' },
];

/*
  Mini cubos: los bloques 0–8 forman el primero, 9–17 el segundo y 18–26 el tercero.
  En cada grupo, los 8 primeros son las esquinas (±31 px del centro) y el noveno queda en el
  centro, escondido adentro. Centros en x: -400, 0 y 400 (celular: en columna, y: -280, 0, 280).
*/
const CENTROS_X = [-400, 0, 400];
const CENTRO_Y = -20;
const CENTRO_X_MOVIL = -90;
const CENTROS_Y_MOVIL = [-280, 0, 280];

function miniCubo(b: number) {
  const grupo = Math.floor(b / 9);
  const k = b % 9;
  const esquina = k < 8;
  const dx = esquina ? (k & 4 ? MEDIO : -MEDIO) : 0;
  const dy = esquina ? (k & 2 ? MEDIO : -MEDIO) : 0;
  const dz = esquina ? (k & 1 ? MEDIO : -MEDIO) : 0;
  return {
    x: CENTROS_X[grupo] + dx,
    y: CENTRO_Y + dy,
    z: dz,
    xMovil: CENTRO_X_MOVIL + dx,
    yMovil: CENTROS_Y_MOVIL[grupo],
    tono: tonosMiniCubos[grupo],
  };
}

// Textos de los mini cubos y dónde van (px desde el centro de la escena)
export const pasos = [
  { titulo: 'Entendemos', texto: 'Mapeamos cómo opera tu negocio hoy.', x: -400, y: 140, xMovil: 0, yMovil: -235 },
  { titulo: 'Construimos', texto: 'Software a la medida, con módulos propios e IA.', x: 0, y: 140, xMovil: 0, yMovil: -55 },
  { titulo: 'Acompañamos', texto: 'Ajustamos contigo mientras tu negocio crece.', x: 400, y: 140, xMovil: 0, yMovil: 125 },
];

const px = (n: number) => `${n}px`;
const deg = (n: number) => `${n}deg`;

const igual = (a: Tono, b: Tono) => a.frente === b.frente && a.tapa === b.tapa && a.lado === b.lado;

export interface Bloque {
  /** Variables CSS del bloque, listas para el atributo style */
  estilo: string;
  /** El tono del mini cubo es distinto del violeta base: necesita la capa de color ::after */
  conMini: boolean;
}

export const bloques: Bloque[] = celdas.map(([cx, cy, cz], b) => ({
  estilo: variables([cx, cy, cz], b),
  conMini: !igual(miniCubo(b).tono, violeta),
}));

function variables([cx, cy, cz]: Trio, b: number): string {
  const [xc, yc, zc, rx, ry, rz] = nube[b];
  const m = miniCubo(b);
  const vars: Record<string, string> = {
    '--x0': px(380 + LADO * cx), '--y0': px(LADO * cy), '--z0': px(LADO * cz),
    '--xc': px(xc), '--yc': px(yc), '--zc': px(zc), '--rx': deg(rx), '--ry': deg(ry), '--rz': deg(rz),
    '--x2': px(m.x), '--y2': px(m.y), '--z2': px(m.z),
    '--mx2': px(m.xMovil), '--my2': px(m.yMovil),
    // El cubo final es el mismo 3×3×3, centrado en x y 40 px más abajo
    '--x3': px(LADO * cx), '--y3': px(40 + LADO * cy), '--z3': px(LADO * cz),
    '--cf': m.tono.frente, '--ct': m.tono.tapa, '--cs': m.tono.lado,
  };
  return Object.entries(vars).map(([k, v]) => `${k}:${v}`).join(';');
}
