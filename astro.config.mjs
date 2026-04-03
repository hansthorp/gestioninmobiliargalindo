// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  // 1. EL CAMBIO CLAVE: Agrega el nombre de la carpeta de tu host
  // Si en el cPanel creaste la carpeta "galindo", ponlo así:
  base: '/galindo', 

  vite: {
    plugins: [tailwindcss()]
  }
});