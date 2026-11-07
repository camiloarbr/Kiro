// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  // URL pública del sitio: la usan el canonical, Open Graph (og:url, og:image) y los datos de la empresa.
  // Dominio propio desde el 6 nov 2026 (Cloudflare Registrar). Las demás direcciones apuntan aquí con el canonical.
  site: 'https://kairosolutions.dev',
  vite: {
    plugins: [tailwindcss()],
    build: {
      // Lightning CSS (el minificador por defecto de Vite 8) fusiona animation-timeline dentro
      // del atajo «animation» («animation: linear both frase --hero»), que es inválido: el
      // navegador descarta la declaración y se rompen las animaciones con el scroll.
      cssMinify: 'esbuild',
      // three.js (Kai en 3D) es un solo archivo de ~650 kB sin comprimir (~165 kB con gzip). No frena la
      // carga: src/scripts/kai/iniciar.ts lo pide aparte, cuando el usuario interactúa. Sin esto Vite avisa.
      chunkSizeWarningLimit: 700,
    },
  },
});
