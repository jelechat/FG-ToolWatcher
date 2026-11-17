import { createEffect, createMemo, createSignal, onMount, Show } from 'solid-js'
import { AppShell } from '../../components/layout/AppShell'
import { SearchBar } from '../../components/ui/SearchBar'
import { Icon } from '../../components/ui/Icon'
import { TableSkeleton } from '../../components/ui/Skeleton'
import { TaxSwitch } from '../../components/dashboard/TaxSwitch'
import { PriceComparisonTable } from '../../components/dashboard/ComparisonTable'
import { GraphPlaceholder } from '../../components/dashboard/GraphPlaceholder'
import { BottomActionBar } from '../../components/dashboard/BottomActionBar'
import { QuickAddDialog } from '../../components/dashboard/QuickAddDialog'
import { FilterDrawer } from '../../components/dashboard/FilterDrawer'
import { EmailDialog } from '../../components/dashboard/EmailDialog'
import { ConfirmDialog } from '../../components/search/ConfirmDialog'
import { useI18n } from '../../i18n'
import { useToast } from '../../providers/ToastProvider'
import { useWatcher } from '../../providers/WatcherProvider'
import { useDebouncedValue } from '../../hooks/useDebouncedValue'
import { getServices } from '../../services'
import {
  brandFilter,
  categoryFilter,
  filterOpen,
  quickAddOpen,
  setBrandFilter,
  setCategoryFilter,
  setFilterOpen,
  setQuickAddOpen,
  setTaxMode,
  setVisiblePriceSites,
  setViewMode,
  taxMode,
  visiblePriceSites,
  viewMode,
} from '../../stores/ui'
import {
  addToCatalog,
  catalog,
  clearCatalog,
  loadCatalog,
  removeFromCatalog,
} from '../../stores/catalog'
import { PRICE_SITES, type PriceSite, type Product } from '@shared/domain'

/**
 * Dashboard: live search, quick add, tax switch, comparison table / graph
 * placeholder and the bottom action bar.
 */
export function DashboardPage() {
  const { t } = useI18n()
  const { notify } = useToast()
  const watcher = useWatcher()
  const services = getServices()

  const [search, setSearch] = createSignal('')
  const [suggestions, setSuggestions] = createSignal<string[]>([])
  const [availableBrands, setAvailableBrands] = createSignal<string[]>([])
  const [availableCategories, setAvailableCategories] = createSignal<string[]>([])
  const [emailRecipient, setEmailRecipient] = createSignal('')
  const [catalogReady, setCatalogReady] = createSignal(false)
  const [emailOpen, setEmailOpen] = createSignal(false)
  const [clearAllOpen, setClearAllOpen] = createSignal(false)
  const debouncedSearch = useDebouncedValue(search, 250)

  onMount(() => {
    void loadCatalog().finally(() => setCatalogReady(true))
    void services.product.listBrands().then(setAvailableBrands)
    void services.product.listCategories().then(setAvailableCategories)
  })

  createEffect(() => {
    const query = debouncedSearch().trim()
    if (query.length < 3) {
      setSuggestions([])
      return
    }
    void services.product
      .suggest(query)
      .then((matches) => setSuggestions(matches.map((product) => product.name)))
  })

  const products = createMemo<Product[]>(() => {
    const brand = brandFilter()
    const category = categoryFilter()
    return catalog().filter(
      (product) =>
        (!brand || product.brand === brand) && (!category || product.category === category),
    )
  })

  const brands = createMemo(() => [...new Set(catalog().map((product) => product.brand))])
  const categories = createMemo(() => [...new Set(catalog().map((product) => product.category))])

  const runUpdate = async () => {
    notify(t('page_dashboard.progress.running'))
    await watcher.start()
    notify(t('page_dashboard.progress.done'))
  }

  const quickAdd = async (brand: string | null, category: string | null) => {
    const candidates = await services.product.listProducts()
    const filtered = candidates.filter(
      (product) =>
        (!brand || product.brand === brand) && (!category || product.category === category),
    )
    for (const product of filtered) {
      try {
        await addToCatalog(product)
      } catch {
        /* already in the catalog */
      }
    }
    notify(t('page_dashboard.quickadd.done'))
  }

  const toggleView = () => {
    const next = viewMode() === 'table' ? 'graph' : 'table'
    setViewMode(next)
    notify(t(next === 'table' ? 'page_dashboard.view.table' : 'page_dashboard.view.graph'))
  }

  const removeProduct = async (product: Product) => {
    await removeFromCatalog(product.name)
    notify(t('page_dashboard.remove.done'))
  }

  const openEmailDialog = async () => {
    const profile = await services.profile.get()
    setEmailRecipient(profile.mail)
    setEmailOpen(true)
  }

  const addProduct = async (name: string) => {
    const candidates = await services.product.search(name)
    const product = candidates.find((candidate) => candidate.name === name) ?? candidates[0]
    if (!product) return

    try {
      await addToCatalog(product)
      notify(t('page_dashboard.add.done'))
    } catch (error) {
      notify(error instanceof Error ? error.message : t('page_dashboard.add.failed'), 4000)
    }

    setSearch('')
    setSuggestions([])
  }

  const removeAllProducts = async () => {
    await clearCatalog()
    notify(t('page_dashboard.remove_all.done'))
  }

  const togglePriceSite = (site: PriceSite) => {
    setVisiblePriceSites((current) =>
      current.includes(site) ? current.filter((item) => item !== site) : [...current, site],
    )
  }

  return (
    <AppShell>
      <div class="flex h-full flex-col gap-[15px] p-[20px]">
        {/* TOP BAR OF THE DASHBOARD */}
        <div class="flex items-center gap-[15px]">
          <SearchBar
            class="flex-1"
            minWidth={750}
            value={search()}
            placeholder={t('page_dashboard.search.add.placeholder')}
            suggestions={suggestions()}
            onInput={setSearch}
            onSuggestion={(name) => void addProduct(name)}
          />
          <button
            type="button"
            title={t('page_dashboard.action.quickadd')}
            aria-label={t('page_dashboard.action.quickadd')}
            onClick={() => setQuickAddOpen(true)}
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-[6px] border border-border-light bg-button-secondary-bg transition-colors hover:border-accent hover:bg-button-secondary-hover"
          >
            <Icon name="quickadd" color="white" size={20} />
          </button>
          <TaxSwitch mode={taxMode()} onChange={setTaxMode} />
        </div>

        {/* PROGRESS (mock watcher) */}
        <Show when={watcher.running()}>
          <div class="flex items-center gap-3">
            <div class="h-2 flex-1 overflow-hidden rounded-full bg-border">
              <div
                class="h-full rounded-full bg-accent transition-[width] duration-150"
                style={{ width: `${watcher.progress()}%` }}
              />
            </div>
            <span class="text-small text-text-dim">{Math.round(watcher.progress())}%</span>
          </div>
        </Show>

        {/* CONTENT */}
        <div class="min-h-0 flex-1">
          <Show
            when={catalogReady()}
            fallback={<TableSkeleton rows={8} columns={4 + visiblePriceSites().length} />}
          >
            <Show
              when={viewMode() === 'table'}
              fallback={<GraphPlaceholder />}
            >
              <PriceComparisonTable
                products={products()}
                taxMode={taxMode()}
                visibleSites={visiblePriceSites()}
                onRemove={(product) => void removeProduct(product)}
                emptyMessage={t('page_dashboard.empty')}
              />
            </Show>
          </Show>
        </div>

        {/* BOTTOM ACTION BAR */}
        <BottomActionBar
          onUpdate={() => void runUpdate()}
          onSave={() => notify(t('page_dashboard.action.save'))}
          onEmail={() => void openEmailDialog()}
          onAnalyze={() => notify(t('page_dashboard.action.analyze'))}
          onFilter={() => setFilterOpen(true)}
          onClearAll={() => setClearAllOpen(true)}
          clearAllDisabled={catalog().length === 0}
          viewMode={viewMode()}
          onToggleView={toggleView}
        />
      </div>

      <QuickAddDialog
        open={quickAddOpen()}
        onOpenChange={setQuickAddOpen}
        brands={availableBrands()}
        categories={availableCategories()}
        onAdd={(brand, category) => void quickAdd(brand, category)}
      />

      <FilterDrawer
        open={filterOpen()}
        onOpenChange={setFilterOpen}
        brands={brands()}
        categories={categories()}
        brand={brandFilter()}
        category={categoryFilter()}
        visibleSites={visiblePriceSites()}
        onApply={(brand, category) => {
          setBrandFilter(brand)
          setCategoryFilter(category)
        }}
        onToggleSite={togglePriceSite}
        onReset={() => {
          setBrandFilter(null)
          setCategoryFilter(null)
          setVisiblePriceSites([...PRICE_SITES])
        }}
      />

      <ConfirmDialog
        open={clearAllOpen()}
        onOpenChange={setClearAllOpen}
        title={t('page_search_remove_all.title')}
        description={t('page_search_remove_all.subtitle')}
        confirmLabel={t('page_search_remove_all.button')}
        danger
        onConfirm={() => void removeAllProducts()}
      />

      <EmailDialog
        open={emailOpen()}
        onOpenChange={setEmailOpen}
        defaultRecipient={emailRecipient()}
        onSend={async (recipient) => {
          await services.mail.send(recipient, t('page_dashboard.email.title'))
          notify(t('page_dashboard.email.sent'))
        }}
      />
    </AppShell>
  )
}
