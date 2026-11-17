import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import solid from 'vite-plugin-solid'
import tailwindcss from '@tailwindcss/vite'

const rendererSrc = fileURLToPath(new URL('./src/renderer/src', import.meta.url))
const sharedSrc = fileURLToPath(new URL('./src/shared', import.meta.url))

export default defineConfig({
  root: 'src/renderer',
  base: './',
  plugins: [solid({ hot: false }), tailwindcss()],
  resolve: {
    alias: {
      '@': rendererSrc,
      '@shared': sharedSrc,
    },
  },
  build: {
    outDir: '../../web',
    emptyOutDir: true,
  },
})
