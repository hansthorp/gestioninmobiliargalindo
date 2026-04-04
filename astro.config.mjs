// astro.config.mjs
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  // BORRAMOS EL BASE PARA TRABAJAR EN LA RAÍZ
  vite: {
    plugins: [tailwindcss()]
  }
});