import { type PriceSite, type Product, type TaxMode } from '@shared/domain'
import { ComparisonTable, type Column } from '../ui/Table'
import { useI18n } from '../../i18n'
import { formatPrice, missingPrice, openExternal } from '../../lib/format'

export interface ComparisonTableProps {
  products: Product[]
  taxMode: TaxMode
  visibleSites: PriceSite[]
  onRemove: (product: Product) => void
  emptyMessage?: string
}

/**
 * Comparison table with product identifiers and selected merchant columns.
 * A missing offer is rendered as an em dash ("—").
 */
export function PriceComparisonTable(props: ComparisonTableProps) {
  const { t } = useI18n()

  const headerKey: Record<PriceSite, string> = {
    Georges: 'page_dashboard.table.georges',
    Clabots: 'page_dashboard.table.clabots',
    Fixami: 'page_dashboard.table.fixami',
    Klium: 'page_dashboard.table.klium',
    Lecot: 'page_dashboard.table.lecot',
    Toolnation: 'page_dashboard.table.toolnation',
  }

  const columns = (): Column<Product>[] => {
    const base: Column<Product>[] = [
      {
        key: 'ean',
        header: t('page_dashboard.table.ean'),
        cell: (product) => product.ean,
        cellClass: 'whitespace-nowrap',
      },
      {
        key: 'brand',
        header: t('page_dashboard.table.brand'),
        cell: (product) => product.brand,
        cellClass: 'whitespace-nowrap',
      },
      {
        key: 'mpn',
        header: t('page_dashboard.table.mpn'),
        cell: (product) => product.mpn,
        cellClass: 'whitespace-nowrap',
      },
      {
        key: 'article',
        header: t('page_dashboard.table.article'),
        cell: (product) => <span class="font-semibold">{product.name}</span>,
        cellClass: 'min-w-[180px]',
      },
    ]

    const priceColumns: Column<Product>[] = props.visibleSites.map((site) => ({
      key: site,
      header: t(headerKey[site]),
      cell: (product) => {
        const price =
          props.taxMode === 'HTVA' ? product.priceHTVA[site] : product.priceTTC[site]
        if (price === undefined) {
          return <span class="text-text-muted">{missingPrice()}</span>
        }
        return (
          <button
            type="button"
            class="rounded-[4px] px-1 text-accent hover:bg-white/10 hover:underline"
            title={product.url ?? ''}
            onClick={() => product.url && void openExternal(product.url)}
          >
            {formatPrice(price)}
          </button>
        )
      },
      cellClass: 'whitespace-nowrap',
    }))

    return [
      ...base,
      ...priceColumns,
      {
        key: 'remove',
        header: '',
        cell: (product) => (
          <button
            type="button"
            class="mx-auto flex h-7 w-7 items-center justify-center rounded text-[20px] leading-none text-text-dim hover:bg-error-dark hover:text-white"
            aria-label={`${t('page_dashboard.table.remove')}: ${product.name}`}
            title={t('page_dashboard.table.remove')}
            onClick={(event) => {
              event.stopPropagation()
              props.onRemove(product)
            }}
          >
            ×
          </button>
        ),
        class: 'w-[34px] min-w-[34px] max-w-[34px] px-0 text-center',
        cellClass: 'w-[34px] min-w-[34px] max-w-[34px] px-0 text-center',
      },
    ]
  }

  return (
    <ComparisonTable<Product>
      columns={columns()}
      rows={props.products}
      rowKey={(product) => (product.ean !== '-' ? product.ean : `${product.name}`)}
      emptyMessage={props.emptyMessage}
      class="h-full"
    />
  )
}
