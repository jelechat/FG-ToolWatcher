import { createEffect, createSignal, onMount } from 'solid-js'
import { AppShell } from '../../components/layout/AppShell'
import { SearchBar } from '../../components/ui/SearchBar'
import { Button } from '../../components/ui/Button'
import { CatalogList } from '../../components/search/CatalogList'
import { BrandQuickAccess } from '../../components/search/BrandQuickAccess'
import { ConfirmDialog } from '../../components/search/ConfirmDialog'
import { useI18n } from '../../i18n'
import { useToast } from '../../providers/ToastProvider'
import { getServices, MOCK_BRANDS } from '../../services'
import {
  addToCatalog,
  catalog,
  clearCatalog,
  loadCatalog,
  removeFromCatalog,
  selectedCatalogItem,
  setSelectedCatalogItem,
} from '../../stores/catalog'
import { useDebouncedValue } from '../../hooks/useDebouncedValue'

/**
 * Search page: manage the catalog of watched articles.
 */
export function SearchPage() {
  const { t } = useI18n()
  const { notify } = useToast()
  const services = getServices()

  const [query, setQuery] = createSignal('')
  const [suggestions, setSuggestions] = createSignal<string[]>([])
  const [confirmOpen, setConfirmOpen] = createSignal(false)
  const debouncedQuery = useDebouncedValue(query, 250)

  onMount(() => {
    void loadCatalog()
  })

  createEffect(() => {
    const current = debouncedQuery()
    if (current.trim().length < 3) {
      setSuggestions([])
      return
    }
    void services.search.suggest(current).then(setSuggestions)
  })

  const addProduct = async (name: string) => {
    const products = await services.product.search(name)
    const product = products.find((item) => item.name === name) ?? products[0]
    if (!product) return
    try {
      await addToCatalog(product)
      notify(t('page_search_add.button'))
    } catch (error) {
      notify(error instanceof Error ? error.message : t('page_search_add.button'), 4000)
    }
    setQuery('')
    setSuggestions([])
  }

  const addFirstSuggestion = async () => {
    const first = suggestions()[0]
    if (!first) return
    await addProduct(first)
  }

  const removeSelected = async () => {
    const selected = selectedCatalogItem()
    if (!selected) return
    await removeFromCatalog(selected)
    notify(t('page_search_remove.button'))
  }

  const addBrand = async (brand: string) => {
    const products = await services.product.byBrand(brand)
    for (const product of products) {
      try {
        await addToCatalog(product)
      } catch {
        /* already present */
      }
    }
    notify(t('page_search_add.button'))
  }

  const clearAll = async () => {
    await clearCatalog()
    notify(t('page_search_remove_all.button'))
  }

  return (
    <AppShell>
      <div class="flex h-full gap-[20px] p-[20px]">
        {/* LEFT: catalog + input */}
        <div class="flex min-w-0 flex-1 flex-col gap-[15px]">
          <div class="flex items-center gap-[10px]">
            <SearchBar
              class="flex-1"
              value={query()}
              placeholder={t('page_search_input.placeholder')}
              suggestions={suggestions()}
              onInput={setQuery}
              onSuggestion={(value) => void addProduct(value)}
            />
            <Button variant="primary" onClick={() => void addFirstSuggestion()}>
              {t('page_search_add.button')}
            </Button>
            <Button variant="secondary" onClick={() => void removeSelected()}>
              {t('page_search_remove.button')}
            </Button>
            <Button variant="danger" onClick={() => setConfirmOpen(true)}>
              {t('page_search_remove_all.button')}
            </Button>
          </div>

          <CatalogList
            items={catalog()}
            selected={selectedCatalogItem()}
            onSelect={setSelectedCatalogItem}
            emptyMessage={t('page_search.empty')}
          />
        </div>

        {/* RIGHT: quick access */}
        <BrandQuickAccess
          brands={[...MOCK_BRANDS]}
          label={t('page_search_rapid_access.label')}
          onSelect={(brand) => void addBrand(brand)}
        />
      </div>

      <ConfirmDialog
        open={confirmOpen()}
        onOpenChange={setConfirmOpen}
        title={t('page_search_remove_all.title')}
        description={t('page_search_remove_all.subtitle')}
        confirmLabel={t('page_search_remove_all.button')}
        danger
        onConfirm={() => void clearAll()}
      />
    </AppShell>
  )
}
