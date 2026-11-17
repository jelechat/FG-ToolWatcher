import { Tooltip } from '@kobalte/core/tooltip'
import { For } from 'solid-js'

export interface SitePillOption {
  value: string
  label: string
  disabled?: boolean
  disabledReason?: string
}

export interface ToggleGroupProps {
  options: SitePillOption[]
  /** Selected values. */
  selected: string[]
  onToggle: (value: string) => void
}

/**
 * Flow layout of website pills (ON = green, OFF = grey, disabled = faded).
 */
export function ToggleGroup(props: ToggleGroupProps) {
  const isSelected = (value: string) => props.selected.includes(value)

  return (
    <div class="flex flex-wrap gap-3">
      <For each={props.options}>
        {(option) => (
          <Tooltip
            openDelay={200}
            disabled={!option.disabled}
          >
            <Tooltip.Trigger
              as="button"
              type="button"
              disabled={option.disabled}
              aria-pressed={isSelected(option.value)}
              onClick={() => props.onToggle(option.value)}
              class={[
                'rounded-[20px] px-5 py-2 font-montserrat-semibold text-label transition-colors',
                'disabled:cursor-not-allowed disabled:bg-white/5 disabled:text-text-dim disabled:opacity-60',
                isSelected(option.value)
                  ? 'bg-[rgba(0,126,45,0.85)] text-text'
                  : 'bg-white/40 text-[#1a1a1a]',
              ].join(' ')}
            >
              {option.label}
            </Tooltip.Trigger>
            <Tooltip.Portal>
              <Tooltip.Content class="rounded-[6px] bg-header-bg px-3 py-2 text-small text-text shadow-md">
                {option.disabledReason}
                <Tooltip.Arrow />
              </Tooltip.Content>
            </Tooltip.Portal>
          </Tooltip>
        )}
      </For>
    </div>
  )
}
