import type { Product } from '@shared/domain'
import type { SearchService } from '../contracts'
import { AppError } from '../errors'
import { MOCK_CATALOG, MOCK_PRODUCTS } from './fixtures'
import { delay } from './productService'

export class MockSearchService implements SearchService {
  private catalog: Product[] = [...MOCK_CATALOG]

  async getCatalog(): Promise<Product[]> {
    return delay([...this.catalog])
  }

  async addToCatalog(product: Product): Promise<Product[]> {
    if (this.catalog.some((item) => item.name === product.name)) {
      throw new AppError('duplicate', `The article "${product.name}" is already in the catalog.`)
    }
    this.catalog = [...this.catalog, product]
    return delay([...this.catalog])
  }

  async removeFromCatalog(name: string): Promise<Product[]> {
    this.catalog = this.catalog.filter((item) => item.name !== name)
    return delay([...this.catalog])
  }

  async clearCatalog(): Promise<Product[]> {
    this.catalog = []
    return delay([])
  }

  async suggest(query: string): Promise<string[]> {
    const needle = query.trim().toLowerCase()
    if (needle.length < 3) return delay([])
    const names = MOCK_PRODUCTS.map((product) => product.name).filter((name) =>
      name.toLowerCase().includes(needle),
    )
    return delay(names.slice(0, 8))
  }
}
