import { For } from 'solid-js'
import { PRICE_SITES, type PriceSite } from '@shared/domain'
import { Dialog } from '../ui/Dialog'
import { SelectField } from '../ui/Select'
import { Button } from '../ui/Button'
import { useI18n } from '../../i18n'

export interface FilterDrawerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  brands: string[]
  categories: string[]
  brand: string | null
  category: string | null
  visibleSites: PriceSite[]
  onApply: (brand: string | null, category: string | null) => void
  onToggleSite: (site: PriceSite) => void
  onReset: () => void
}

/** Filter drawer (right side) letting the user narrow down the results. */
export function FilterDrawer(props: FilterDrawerProps) {
  const { t } = useI18n()
  const allBrands = () => t('page_dashboard.quickadd.allBrands')
  const allCategories = () => t('page_dashboard.quickadd.allCategories')

  return (
    <Dialog
      open={props.open}
      onOpenChange={props.onOpenChange}
      onOverlayClick={() => props.onOpenChange(false)}
      title={t('page_dashboard.filter.title')}
      side="right"
    >
      <div class="flex h-full flex-col gap-4">
        <label class="flex flex-col gap-1">
          <span class="font-montserrat-semibold text-label text-text-dim">
            {t('page_dashboard.filter.brand')}
          </span>
          <SelectField
            options={[allBrands(), ...props.brands]}
            value={props.brand ?? ''}
            placeholder={allBrands()}
            onChange={(value) => props.onApply(value === allBrands() ? null : value, props.category)}
            ariaLabel={t('page_dashboard.filter.brand')}
          />
        </label>

        <label class="flex flex-col gap-1">
          <span class="font-montserrat-semibold text-label text-text-dim">
            {t('page_dashboard.filter.category')}
          </span>
          <SelectField
            options={[allCategories(), ...props.categories]}
            value={props.category ?? ''}
            placeholder={allCategories()}
            onChange={(value) => props.onApply(props.brand, value === allCategories() ? null : value)}
            ariaLabel={t('page_dashboard.filter.category')}
          />
        </label>

        <fieldset class="flex flex-col gap-2">
          <legend class="font-montserrat-semibold text-label text-text-dim">
            {t('page_dashboard.filter.sites')}
          </legend>
          <div class="flex max-h-[240px] flex-col gap-1 overflow-y-auto">
            <For each={PRICE_SITES}>
              {(site) => (
                <label class="flex cursor-pointer items-center gap-2 rounded px-2 py-1.5 text-[13px] text-text hover:bg-black/15">
                  <input
                    type="checkbox"
                    checked={props.visibleSites.includes(site)}
                    onChange={() => props.onToggleSite(site)}
                    class="accent-accent"
                  />
                  <span>{site}</span>
                </label>
              )}
            </For>
          </div>
        </fieldset>

        <div class="mt-auto flex items-center justify-end gap-3">
          <Button variant="secondary" onClick={props.onReset}>
            {t('page_dashboard.filter.reset')}
          </Button>
          <Button variant="primary" onClick={() => props.onOpenChange(false)}>
            {t('page_dashboard.filter.apply')}
          </Button>
        </div>
      </div>
    </Dialog>
  )
}
