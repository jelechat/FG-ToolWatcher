import { Switch } from '@kobalte/core/switch'
import { Show } from 'solid-js'

export interface ToggleProps {
  checked: boolean
  onChange: (checked: boolean) => void
  /** Title of the setting. */
  label: string
  /** Optional description under the title. */
  description?: string
  disabled?: boolean
}

/**
 * iOS-like pill toggle (Kobalte Switch) used by the General settings page.
 * ON: #007e2d with a 3px black border, OFF: #cccccc.
 */
export function Toggle(props: ToggleProps) {
  return (
    <Switch
      checked={props.checked}
      onChange={props.onChange}
      disabled={props.disabled}
      class="flex items-start gap-4"
    >
      <Switch.Input class="sr-only" />
      <Switch.Control
        class="relative mt-[2px] h-[28px] w-[52px] shrink-0 cursor-pointer rounded-[14px] border-[3px] border-black transition-colors
               data-[checked]:bg-accent-active data-[unchecked]:bg-[#cccccc]
               disabled:cursor-not-allowed disabled:bg-disabled-bg"
      >
        <Switch.Thumb
          class="block h-[22px] w-[22px] rounded-full bg-white transition-transform
                 data-[checked]:translate-x-[24px] data-[unchecked]:translate-x-0"
        />
      </Switch.Control>
      <div class="flex flex-col">
        <Switch.Label class="font-montserrat-semibold text-label text-text">
          {props.label}
        </Switch.Label>
        <Show when={props.description}>
          <Switch.Description class="text-small text-text-dim">
            {props.description}
          </Switch.Description>
        </Show>
      </div>
    </Switch>
  )
}
