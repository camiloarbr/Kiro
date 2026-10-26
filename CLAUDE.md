# Kiro — landing page

## Qué es Kiro
Kiro Solutions es una empresa de software de Medellín, Colombia, fundada por estudiantes de EAFIT (Camilo «Gallo» Arbeláez y Juan José Cárdenas). Hace **software a la medida** para negocios pequeños y medianos: páginas y plataformas web, agentes de IA y chatbots, automatización de procesos, sistemas internos y paneles, e integraciones. Hoy se enfoca en atención al cliente para **hoteles y consultorios de salud**. La landing sirve para dar credibilidad y conseguir conversaciones con clientes.

## Documentos clave (leer antes de construir)
- `docs/marca/MANUAL-DE-MARCA.md`: identidad oficial (logo, ícono, colores, tipografía, voz). La versión visual está en `docs/marca/manual-de-marca.html`.
- `docs/marca/assets/`: logos e íconos oficiales en SVG y PNG. **No redibujar el logo**: usar estos archivos.
- `docs/diseno/ESPECIFICACION-LANDING.md`: especificación del diseño final, sección por sección, con todos los textos.
- `docs/diseno/referencia/landing-estatica.html`: el diseño final funcionando. Ábrelo en Chrome; es la referencia visual exacta.
- `docs/diseno/referencia/*.dc.html`: código fuente del diseño (CSS, keyframes, medidas). Es solo referencia; no copiar su sintaxis.
- `docs/diseno/capturas/`: capturas de computador y celular.

## Stack
- **Astro 7** (sitio estático, sin framework de UI), **TypeScript** estricto. Se usa `typescript@6` porque `@astrojs/check` todavía no acepta TypeScript 7.
- **Tailwind CSS v4** vía `@tailwindcss/vite`. Los tokens de marca van en `@theme` dentro de `src/styles/global.css`.
- **Animaciones con CSS nativo:**
  - Scroll-driven animations (`animation-timeline`, `view-timeline`, `timeline-scope`) y keyframes 3D.
  - Sin librerías de animación.
  - JS vanilla mínimo, solo para el selector Hotel/Consultorio y la alternativa con `IntersectionObserver` en navegadores sin scroll-driven animations.
- **Fuentes autoalojadas** con Fontsource, versiones variables: `@fontsource-variable/montserrat` y `@fontsource-variable/geist` (familias `'Montserrat Variable'` y `'Geist Variable'`).
- **Gestor de paquetes:** pnpm.
- **Deploy:** Cloudflare Workers con *static assets*. El sitio es 100 % estático, así que no usa el adapter `@astrojs/cloudflare`: basta un `wrangler.jsonc` con `"assets": { "directory": "./dist", "not_found_handling": "404-page" }`. Build: `pnpm astro build`; deploy: `npx wrangler deploy`, conectado al repo con Workers Builds. Dominio propio (comprado en Cloudflare Registrar), por definir.

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
8. **Pendientes conocidos:**
   - El número de WhatsApp es un placeholder: ponerlo en una sola constante en `src/data/contacto.ts`.
   - Los nombres de ejemplo («Casa Ceiba», «Ceiba Odontología», «Laura M.») son de muestra.
