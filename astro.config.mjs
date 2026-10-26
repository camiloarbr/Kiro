// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  // TODO: poner aquí el dominio propio cuando esté comprado (lo usan el canonical y Open Graph).
  // site: 'https://<dominio>',
  vite: {
    plugins: [tailwindcss()],
    build: {
      // Lightning CSS (el minificador por defecto de Vite 8) fusiona animation-timeline dentro
      // del atajo «animation» («animation: linear both frase --hero»), que es inválido: el
      // navegador descarta la declaración y se rompen las animaciones con el scroll.
      cssMinify: 'esbuild',
    },
  },
});
