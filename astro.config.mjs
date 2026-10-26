// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  // TODO: poner aquí el dominio propio cuando esté comprado (lo usan el canonical y Open Graph).
  // site: 'https://<dominio>',
  vite: {
    plugins: [tailwindcss()],
  },
});
