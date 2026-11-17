import { createSignal } from 'solid-js'
import type { Product } from '@shared/domain'
import { getServices } from '../services'

const services = getServices()

/** Items of the user catalog. */
export const [catalog, setCatalog] = createSignal<Product[]>([])

/** Name of the currently selected catalog item. */
export const [selectedCatalogItem, setSelectedCatalogItem] = createSignal<string | null>(null)

/** Loads the catalog from the service layer. */
export async function loadCatalog(): Promise<void> {
  setCatalog(await services.search.getCatalog())
}

/** Adds a product to the catalog (deduplicated by name). */
export async function addToCatalog(product: Product): Promise<void> {
  setCatalog(await services.search.addToCatalog(product))
}

/** Removes a product from the catalog. */
export async function removeFromCatalog(name: string): Promise<void> {
  setCatalog(await services.search.removeFromCatalog(name))
  if (selectedCatalogItem() === name) setSelectedCatalogItem(null)
}

/** Empties the catalog. */
export async function clearCatalog(): Promise<void> {
  setCatalog(await services.search.clearCatalog())
  setSelectedCatalogItem(null)
}
