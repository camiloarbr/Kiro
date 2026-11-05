// Los ojos de Kai se dibujan en vivo sobre su pantalla.
// En el modelo, la pantalla quedó limpia (sin ojos) y aquí el shader los pinta encima con la misma forma,
// tamaño, color y brillo de la ficha técnica. Así pueden mirar a los lados y parpadear sin deformar nada.
//
// Cómo: onBeforeCompile agrega unas líneas al shader estándar de three.js (MeshStandardMaterial).
// Cada píxel de la cabeza conoce su posición en el modelo original (vKai) y mide su distancia a los dos
// ojos (rectángulos redondeados). Distancia < 0 = dentro del ojo → blanco; cerca del borde → resplandor.
import { Color, Matrix4, Vector2, type MeshStandardMaterial } from 'three';
import { OJOS, PANTALLA } from './forma';

export interface UniformesOjos {
  uLocal: { value: Matrix4 };
  uOjo: { value: Vector2 };
  uParpado: { value: number };
  uHalo: { value: Color };
  uBlanco: { value: number };
}

const f = (n: number) => n.toFixed(5);

export function ponerOjos(material: MeshStandardMaterial, local: Matrix4): UniformesOjos {
  const u: UniformesOjos = {
    uLocal: { value: local },
    uOjo: { value: new Vector2() },
    uParpado: { value: 1 },
    // Lavanda del resplandor original (medido en la textura del modelo maestro), en color lineal
    uHalo: { value: new Color(1.0, 0.72, 1.05) },
    uBlanco: { value: 1.0 },
  };

  material.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, u);

    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nuniform mat4 uLocal;\nvarying vec3 vKai;')
      .replace('#include <begin_vertex>', '#include <begin_vertex>\nvKai = (uLocal * vec4(position, 1.0)).xyz;');

    sh.fragmentShader = sh.fragmentShader
      .replace(
        '#include <common>',
        /* glsl */ `#include <common>
varying vec3 vKai;
uniform vec2 uOjo;
uniform float uParpado;
uniform vec3 uHalo;
uniform float uBlanco;
// Distancia con signo a un rectángulo redondeado de medio tamaño b y radio r
float kaiRect(vec2 p, vec2 b, float r) {
  r = min(r, min(b.x, b.y));
  vec2 q = abs(p) - b + r;
  return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}`,
      )
      .replace(
        '#include <map_fragment>',
        /* glsl */ `#include <map_fragment>
vec2 kp = vKai.xy;
vec2 ks = max(abs((kp - vec2(${f(PANTALLA.centro[0])}, ${f(PANTALLA.centro[1])})) / vec2(${f(PANTALLA.semi[0])}, ${f(PANTALLA.semi[1])})), vec2(1e-5));
float kSe = pow(ks.x, ${f(PANTALLA.n)}) + pow(ks.y, ${f(PANTALLA.n)});
float kEnPantalla = (1.0 - smoothstep(0.86, 1.0, kSe)) * smoothstep(0.38, 0.45, vKai.z);
// Parpadeo: los ojos se aplastan hacia su centro (nunca del todo: quedan como una raya)
vec2 kb = vec2(${f(OJOS.medio[0])}, ${f(OJOS.medio[1])} * max(uParpado, 0.06));
float kd = min(
  kaiRect(kp - vec2(${f(OJOS.izq[0])}, ${f(OJOS.izq[1])}) - uOjo, kb, ${f(OJOS.radio)}),
  kaiRect(kp - vec2(${f(OJOS.der[0])}, ${f(OJOS.der[1])}) - uOjo, kb, ${f(OJOS.radio)})
);
float kAa = max(fwidth(kd), 1e-4);
float kNucleo = (1.0 - smoothstep(-0.024 - kAa, 0.008 + kAa, kd)) * kEnPantalla;
float kDd = max(kd, 0.0);
float kHalo = (0.32 * exp(-kDd / 0.012) + 0.11 * exp(-kDd / 0.055)) * kEnPantalla * sqrt(max(uParpado, 0.06));
diffuseColor.rgb = mix(diffuseColor.rgb, vec3(1.0), kNucleo);`,
      )
      .replace(
        '#include <roughnessmap_fragment>',
        '#include <roughnessmap_fragment>\nroughnessFactor = mix(roughnessFactor, 0.6, kNucleo);',
      )
      .replace(
        '#include <emissivemap_fragment>',
        '#include <emissivemap_fragment>\ntotalEmissiveRadiance += vec3(uBlanco) * kNucleo + uHalo * kHalo;',
      );
  };
  material.customProgramCacheKey = () => 'kai-ojos';
  return u;
}
