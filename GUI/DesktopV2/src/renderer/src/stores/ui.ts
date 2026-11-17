import { createSignal } from 'solid-js'
import { PRICE_SITES, type PriceSite, type TaxMode } from '@shared/domain'

export type ViewMode = 'table' | 'graph'

/** Dashboard view mode (table or graph placeholder). */
export const [viewMode, setViewMode] = createSignal<ViewMode>('table')

/** Dashboard tax mode (HTVA = excl. VAT, TTC = incl. VAT). */
export const [taxMode, setTaxMode] = createSignal<TaxMode>('HTVA')

/** Whether the quick add dialog is open. */
export const [quickAddOpen, setQuickAddOpen] = createSignal(false)

/** Whether the filter drawer is open. */
export const [filterOpen, setFilterOpen] = createSignal(false)

/** Current filter values. */
export const [brandFilter, setBrandFilter] = createSignal<string | null>(null)
export const [categoryFilter, setCategoryFilter] = createSignal<string | null>(null)

/** Merchant columns visible in the dashboard comparison table. */
export const [visiblePriceSites, setVisiblePriceSites] = createSignal<PriceSite[]>([
  ...PRICE_SITES,
])

/** Resets every UI state (used by the "hard reset" mock action). */
export function resetUiState(): void {
  setViewMode('table')
  setTaxMode('HTVA')
  setQuickAddOpen(false)
  setFilterOpen(false)
  setBrandFilter(null)
  setCategoryFilter(null)
  setVisiblePriceSites([...PRICE_SITES])
}
