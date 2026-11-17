import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitest/config'
import solid from 'vite-plugin-solid'

const rendererSrc = fileURLToPath(new URL('./src/renderer/src', import.meta.url))
const sharedSrc = fileURLToPath(new URL('./src/shared', import.meta.url))

export default defineConfig({
  plugins: [solid({ hot: false })],
  resolve: {
    alias: {
      '@': rendererSrc,
      '@shared': sharedSrc,
    },
  },
  test: {
    environment: 'jsdom',
    globals: false,
    include: ['tests/unit/**/*.test.{ts,tsx}'],
    setupFiles: ['tests/setup.ts'],
  },
})
