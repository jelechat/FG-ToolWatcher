import { useI18n } from '../../i18n'
import type { TaxMode } from '@shared/domain'

export interface TaxSwitchProps {
  mode: TaxMode
  onChange: (mode: TaxMode) => void
}

/**
 * HTVA / TTC switch (200x40 checkable button).
 * The active label uses the accent colour, the inactive one the muted colour.
 */
export function TaxSwitch(props: TaxSwitchProps) {
  const { t } = useI18n()

  const label = (mode: TaxMode) =>
    mode === 'HTVA' ? t('page_menu_tax_toggle_off.label') : t('page_menu_tax_toggle_on.label')

  return (
    <button
      type="button"
      role="switch"
      aria-label="Tax mode"
      aria-checked={props.mode === 'TTC'}
      onClick={() => props.onChange(props.mode === 'HTVA' ? 'TTC' : 'HTVA')}
      class="flex h-10 w-[200px] items-center justify-between rounded-[6px] border border-border-light bg-button-secondary-bg px-2 transition-colors hover:border-accent hover:bg-button-secondary-hover"
    >
      <span
        class={[
          'flex h-full flex-1 items-center justify-center rounded-[4px] font-montserrat-semibold text-[13px] transition-colors',
          props.mode === 'HTVA' ? 'text-accent' : 'text-text-muted',
        ].join(' ')}
      >
        {label('HTVA')}
      </span>
      <span class="h-[60%] w-px bg-border-light" />
      <span
        class={[
          'flex h-full flex-1 items-center justify-center rounded-[4px] font-montserrat-semibold text-[13px] transition-colors',
          props.mode === 'TTC' ? 'text-accent' : 'text-text-muted',
        ].join(' ')}
      >
        {label('TTC')}
      </span>
    </button>
  )
}
