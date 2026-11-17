import type { Product } from '@shared/domain'
import type { ProductService } from '../contracts'
import { MOCK_PRODUCTS } from './fixtures'

/** Artificial latency (ms) applied to every mock call. */
let mockLatency = 0

/** Sets the artificial latency used by the mock services (0 in tests). */
export function setMockLatency(ms: number): void {
  mockLatency = Math.max(0, ms)
}

/** Current artificial latency. */
export function getMockLatency(): number {
  return mockLatency
}

/** Resolves after the configured mock latency. */
export function delay<T>(value: T, ms: number = mockLatency): Promise<T> {
  if (ms <= 0) return Promise.resolve(value)
  return new Promise((resolve) => setTimeout(() => resolve(value), ms))
}

function matches(product: Product, query: string): boolean {
  const needle = query.trim().toLowerCase()
  if (!needle) return true
  return (
    product.name.toLowerCase().includes(needle) ||
    product.brand.toLowerCase().includes(needle) ||
    product.mpn.toLowerCase().includes(needle) ||
    product.ean.toLowerCase().includes(needle) ||
    product.category.toLowerCase().includes(needle)
  )
}

export class MockProductService implements ProductService {
  async listProducts(): Promise<Product[]> {
    return delay([...MOCK_PRODUCTS])
  }

  async search(query: string): Promise<Product[]> {
    return delay(MOCK_PRODUCTS.filter((product) => matches(product, query)))
  }

  async suggest(query: string): Promise<Product[]> {
    const needle = query.trim().toLowerCase()
    if (needle.length < 3) return delay([])
    return delay(MOCK_PRODUCTS.filter((product) => matches(product, needle)).slice(0, 8))
  }

  async byBrand(brand: string): Promise<Product[]> {
    return delay(MOCK_PRODUCTS.filter((product) => product.brand === brand))
  }

  async byCategory(category: string): Promise<Product[]> {
    return delay(MOCK_PRODUCTS.filter((product) => product.category === category))
  }
}
