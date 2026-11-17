import { useI18n } from '../../i18n'

/** Placeholder of the future visual analysis area. */
export function GraphPlaceholder() {
  const { t } = useI18n()

  return (
    <div class="flex h-full w-full items-center justify-center rounded-[6px] border border-dashed border-border bg-surface/40">
      <p class="text-[15px] text-text-dim">{t('page_dashboard.graph.placeholder')}</p>
    </div>
  )
}
