import { afterEach } from 'vitest'
import { cleanup } from '@solidjs/testing-library'

// jsdom does not implement matchMedia (used by some Kobalte primitives).
if (!globalThis.matchMedia) {
  globalThis.matchMedia = ((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  })) as unknown as typeof globalThis.matchMedia
}

// jsdom does not implement ResizeObserver.
if (!globalThis.ResizeObserver) {
  globalThis.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as unknown as typeof globalThis.ResizeObserver
}

// jsdom implements scrollTo but throws "not implemented" (the router calls it).
globalThis.scrollTo = (() => {}) as unknown as typeof globalThis.scrollTo

afterEach(() => {
  cleanup()
})
