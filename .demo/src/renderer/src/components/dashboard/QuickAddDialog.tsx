import { createSignal } from 'solid-js'
import { Dialog } from '../ui/Dialog'
import { SelectField } from '../ui/Select'
import { Button } from '../ui/Button'
import { useI18n } from '../../i18n'

export interface QuickAddDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  brands: string[]
  categories: string[]
  /** Returns the selected brand / category (null = "all"). */
  onAdd: (brand: string | null, category: string | null) => void
}

/** Quick Add dialog: pick a brand and/or a category, then add the batch. */
export function QuickAddDialog(props: QuickAddDialogProps) {
  const { t } = useI18n()
  const allBrands = () => t('page_dashboard.quickadd.allBrands')
  const allCategories = () => t('page_dashboard.quickadd.allCategories')

  const [brand, setBrand] = createSignal('')
  const [category, setCategory] = createSignal('')

  const close = () => {
    setBrand('')
    setCategory('')
    props.onOpenChange(false)
  }

  const submit = () => {
    props.onAdd(brand() || null, category() || null)
    close()
  }

  return (
    <Dialog
      open={props.open}
      onOpenChange={(open) => (open ? props.onOpenChange(true) : close())}
      onOverlayClick={close}
      title={t('page_dashboard.quickadd.title')}
      centered
    >
      <div class="flex flex-col gap-4">
        <label class="flex flex-col gap-1">
          <span class="font-montserrat-semibold text-label text-text-dim">
            {t('page_dashboard.quickadd.brand')}
          </span>
          <SelectField
            options={[allBrands(), ...props.brands]}
            value={brand()}
            placeholder={allBrands()}
            onChange={(value) => setBrand(value === allBrands() ? '' : value)}
            ariaLabel={t('page_dashboard.quickadd.brand')}
          />
        </label>

        <label class="flex flex-col gap-1">
          <span class="font-montserrat-semibold text-label text-text-dim">
            {t('page_dashboard.quickadd.category')}
          </span>
          <SelectField
            options={[allCategories(), ...props.categories]}
            value={category()}
            placeholder={allCategories()}
            onChange={(value) => setCategory(value === allCategories() ? '' : value)}
            ariaLabel={t('page_dashboard.quickadd.category')}
          />
        </label>

        <div class="mt-2 flex items-center justify-end gap-3">
          <Button variant="secondary" onClick={close}>
            {t('page_dashboard.quickadd.cancel')}
          </Button>
          <Button variant="primary" onClick={submit}>
            {t('page_dashboard.quickadd.add')}
          </Button>
        </div>
      </div>
    </Dialog>
  )
}
