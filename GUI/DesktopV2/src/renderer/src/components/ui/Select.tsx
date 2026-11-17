import { Select } from '@kobalte/core/select'

export interface SelectProps {
  /** Option labels (the value is the label itself). */
  options: string[]
  /** Selected value (empty string when nothing is selected). */
  value: string
  onChange: (value: string) => void
  /** Text displayed when no option is selected. */
  placeholder?: string
  disabled?: boolean
  class?: string
  ariaLabel?: string
}

/**
 * Kobalte select styled like the PySide6 combo boxes.
 *
 * The listbox is rendered in a Kobalte portal attached to <body>: its z-index
 * (120) is higher than the modal layers (70/80) so that the options stay
 * clickable when the select is used inside a dialog. Kobalte copies the
 * computed z-index of the content onto its positioner element.
 */
export function SelectField(props: SelectProps) {
  const hasValue = () => props.value !== '' && props.options.includes(props.value)

  const selectedLabel = () => (hasValue() ? props.value : (props.placeholder ?? ''))

  return (
    <Select
      options={props.options}
      value={props.value || undefined}
      onChange={(value) => props.onChange(value ?? '')}
      disabled={props.disabled}
      itemComponent={(itemProps) => (
        <Select.Item
          item={itemProps.item}
          class="flex cursor-pointer items-center justify-between px-3 py-2 text-[13px] text-text outline-none data-[highlighted]:bg-white/10"
        >
          <Select.ItemLabel>{itemProps.item.rawValue}</Select.ItemLabel>
          <Select.ItemIndicator>✓</Select.ItemIndicator>
        </Select.Item>
      )}
    >
      <Select.Trigger
        aria-label={props.ariaLabel}
        class={[
          'flex h-10 w-full items-center justify-between rounded-[6px] border border-border bg-surface px-3 text-text',
          'focus:border-accent focus:outline-none disabled:cursor-not-allowed disabled:bg-disabled-bg disabled:text-disabled-text',
          props.class,
        ].join(' ')}
      >
        <span class={hasValue() ? 'truncate' : 'truncate text-text-dim'}>
          {selectedLabel()}
        </span>
        <Select.Icon class="text-text-dim">▾</Select.Icon>
      </Select.Trigger>
      <Select.Portal>
        <Select.Content class="z-[120] overflow-hidden rounded-[6px] border border-border bg-header-bg shadow-md">
          <Select.Listbox />
        </Select.Content>
      </Select.Portal>
    </Select>
  )
}
