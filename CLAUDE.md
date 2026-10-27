# Kiro — landing page

## Qué es Kiro
Kiro Solutions es una empresa de software de Medellín, Colombia, fundada por estudiantes de EAFIT (Camilo «Gallo» Arbeláez y Juan José Cárdenas). Hace **software a la medida** para negocios pequeños y medianos: páginas y plataformas web, agentes de IA y chatbots, automatización de procesos, sistemas internos y paneles, e integraciones. Hoy se enfoca en atención al cliente para **hoteles y consultorios de salud**. La landing sirve para dar credibilidad y conseguir conversaciones con clientes.

## Documentos clave (leer antes de construir)
- `docs/marca/MANUAL-DE-MARCA.md`: identidad oficial (logo, ícono, colores, tipografía, voz). La versión visual está en `docs/marca/manual-de-marca.html`.
- `docs/marca/assets/`: logos e íconos oficiales en SVG y PNG. **No redibujar el logo**: usar estos archivos.
- `docs/diseno/ESPECIFICACION-LANDING.md`: especificación del diseño final, sección por sección, con todos los textos.
- `docs/diseno/referencia/landing-estatica.html`: el diseño final funcionando. Ábrelo en Chrome; es la referencia visual exacta.
- `docs/diseno/referencia/*.dc.html`: código fuente del diseño (CSS, keyframes, medidas). Es solo referencia; no copiar su sintaxis.
- `docs/diseno/capturas/`: capturas de computador y celular. **Excepción:** la portada cambió a «bloques-cursor» (oct 2026); su referencia es `docs/diseno/referencia/portada-bloques-cursor.html` / `.dc.html` y ya no las capturas `*-01`/`*-02`/`*-03` ni los paneles de `Estilo-Glass.dc.html`.

## Stack
- **Astro 7** (sitio estático, sin framework de UI), **TypeScript** estricto. Se usa `typescript@6` porque `@astrojs/check` todavía no acepta TypeScript 7.
- **Tailwind CSS v4** vía `@tailwindcss/vite`. Los tokens de marca van en `@theme` dentro de `src/styles/global.css`.
- **Animaciones con CSS nativo:**
  - Scroll-driven animations (`animation-timeline`, `view-timeline`, `timeline-scope`) y keyframes 3D.
  - Sin librerías de animación.
  - JS vanilla mínimo, solo para el selector Hotel/Consultorio y la alternativa con `IntersectionObserver` en navegadores sin scroll-driven animations.
- **Fuentes autoalojadas** con Fontsource, versiones variables: `@fontsource-variable/montserrat` y `@fontsource-variable/geist` (familias `'Montserrat Variable'` y `'Geist Variable'`).
- **Gestor de paquetes:** pnpm.
- **Deploy:** Cloudflare Workers con *static assets*. El sitio es 100 % estático, así que no usa el adapter `@astrojs/cloudflare`: basta un `wrangler.jsonc` con `"assets": { "directory": "./dist", "not_found_handling": "404-page" }`. Build y deploy en un paso: `pnpm deploy` (`astro build` + `wrangler deploy`).
  - Cuenta de Cloudflare de la empresa (KiroSolutionsCol@gmail.com), Worker `kiro`, publicado en **https://kiro.kirosolutionsco.workers.dev** (`site` en `astro.config.mjs`).
  - Pendiente: dominio propio (Cloudflare Registrar). Al tenerlo: `"routes": [{ "pattern": "<dominio>", "custom_domain": true }]` en `wrangler.jsonc`, `site` al dominio y volver a publicar. Opcional: Workers Builds para publicar en cada push.

## Estructura esperada
```
src/
  layouts/BaseLayout.astro        ← <head>, fuentes, favicon, SEO
  components/                     ← un componente por sección
    Header.astro  Hero.astro  CuboViajero.astro  TuDia.astro
    Servicios.astro  Olas.astro  DemoKiroBot.astro
    ComoTrabajamos.astro  Contacto.astro  Footer.astro
  data/                           ← textos y datos (servicios, filas de «Tu día», escenarios del demo)
  styles/global.css               ← Tailwind + tokens + keyframes compartidas
  pages/index.astro
public/                           ← favicon y logos copiados de docs/marca/assets
```

## Reglas de trabajo
1. **Paso a paso.** Una sección o tarea por vez. Al terminar cada paso, para, muestra cómo verlo (`pnpm dev`) y espera el visto bueno de Gallo antes de seguir.
2. **Explica lo que haces.** Gallo estudia Ingeniería de Sistemas y quiere aprender. En cada paso explica en español y en lenguaje claro:
   - qué archivos creaste o cambiaste;
   - por qué está organizado así;
   - cómo funciona la parte importante del código, sobre todo las animaciones de scroll y el 3D;
   - qué conceptos nuevos aparecen.
   Deja comentarios breves en el código solo donde la lógica no sea obvia.
3. **Fidelidad al diseño.** Igualar `landing-estatica.html` en computador (1440 px) y celular (390 px). Antes de cerrar un paso visual, compara contra las capturas.
4. **Marca.**
   - Colores, fuentes y logos solo del manual.
   - No copiar contenido de somoszora.com: se tomó solo el estilo visual.
   - No inventar clientes, cifras ni testimonios.
5. **Rendimiento y accesibilidad.**
   - Animar solo `transform` y `opacity`.
   - Respetar `prefers-reduced-motion`.
   - HTML semántico, contraste AA y textos alternativos.
   - Meta: Lighthouse ≥ 90 en las cuatro categorías.
6. **Git y autoría.**
   - El autor del código y de los commits es **Gallo**. Los commits usan su configuración de git (`user.name` / `user.email`).
   - **Nunca** agregues `Co-Authored-By` ni menciones a Claude en commits o PR. `.claude/settings.json` ya lo desactiva.
   - Al final de cada paso, propón el mensaje de commit (en español, estilo `feat: portada con paneles de vidrio`) y haz el commit solo si Gallo lo aprueba.
   - **Nunca hagas `git push`**: el push lo hace Gallo.
7. **Decisiones técnicas que no hay que deshacer:**
   - `astro.config.mjs` usa `cssMinify: 'esbuild'`. Lightning CSS (el minificador por defecto de Vite 8) mete `animation-timeline` dentro del atajo `animation`, que es inválido: en producción se rompen todas las animaciones con el scroll. Verificar siempre sobre `pnpm build` + `pnpm preview`, no solo con `pnpm dev`.
   - En los keyframes 3D (portada y demo), todos los pasos repiten la misma lista de funciones de `transform`. Si se "simplifican", el navegador interpola con matrices y los giros cambian.
   - Animaciones con scroll dentro de `@supports (animation-timeline: view())` y `prefers-reduced-motion: no-preference`. El CSS base es la versión estática legible. Firefox usa la clase `.io` + `src/scripts/revelar.ts`.
   - Hover sobre elementos que tienen animación de entrada: usar `translate` (no `transform`), porque la animación siempre le gana al `:hover`.
   - Contraste ajustado a AA frente a la referencia: tachado de «Tu día» en `tenue`, filas de «Cómo trabajamos» con vidrio oscuro y texto blanco, eyebrow «Hablemos» en Morado oscuro.
   - `pnpm-workspace.yaml` bloquea los scripts de instalación de `esbuild` y `workerd` (no hacen falta). No agregar excepciones a `minimumReleaseAge`.
   - Los nombres de `@keyframes` son **globales** aunque estén en el `<style>` de un componente: si dos componentes usan el mismo nombre, uno pisa al otro. Usar un prefijo por componente (la portada usa `portada-…`).
   - El offset del header se hace con `scroll-margin-top` en `section[id]`, **nunca** con `scroll-padding-top` en `html`: el scroll-padding recorta el área de las `view-timeline` y corre todas las animaciones con scroll.
   - `overflow-x: clip` va en `html` y en `body`. Solo en `body` no llega al viewport en celular y lo que sobresale (riel, olas, panel del demo) ensancha la página.
   - Portada: las posiciones de los 27 bloques se generan en `src/data/bloques.ts`. No escribirlas a mano en el componente.
   - Portada: los colores de las caras **no se animan**. Cada cara tiene su violeta fijo y, solo en los bloques que cambian de tono, capas `::before` («ik») y `::after` (mini cubo) que se cruzan con `opacity`. Animar colores (`@property`) mandaba toda la animación de los bloques al hilo principal (~31 fps con CPU 4×). Sin `will-change` en los bloques: `preserve-3d` ya crea las capas.
   - «Tu día» sube `--solape` px (320 / 240 en celular, definido en `.recorrido`) sobre el final de la portada para entrar cuando el cubo llega al carril. La línea del carril usa el mismo valor.
   - Franjas claro → oscuro (`Transicion.astro`): degradado fijo y corto, con altura por instancia (160 px «Tu día» → Servicios, 72 px contacto → footer).
   - Cloudflare Web Analytics: token en `src/data/analitica.ts`; vacío = no se carga.
8. **Pendientes conocidos:**
   - El contacto es **solo por correo** (decisión de Gallo, oct 2026): sin teléfono ni WhatsApp de Kiro en la página. El correo vive en `src/data/contacto.ts`.
   - Los pasos claro → oscuro («Tu día» → Servicios y Contacto → footer) usan `src/components/Transicion.astro`.
   - Los nombres de ejemplo («Casa Ceiba», «Ceiba Odontología», «Laura M.») son de muestra.
