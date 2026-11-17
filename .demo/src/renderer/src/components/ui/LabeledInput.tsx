import { Show } from 'solid-js'
import { Input } from './Input'

export interface LabeledInputProps {
  label: string
  value: string
  placeholder?: string
  type?: 'text' | 'email'
  error?: string
  id?: string
  onInput: (value: string) => void
}

/** Centred label + input, used by the profile screens. */
export function LabeledInput(props: LabeledInputProps) {
  return (
    <div class="flex w-full flex-col items-center gap-2">
      <Input
        id={props.id}
        label={props.label}
        type={props.type ?? 'text'}
        value={props.value}
        placeholder={props.placeholder}
        error={props.error}
        onInput={props.onInput}
        inputClass="text-center"
        class="w-[420px] max-w-full"
      />
      <Show when={props.error}>
        <span class="sr-only">{props.error}</span>
      </Show>
    </div>
  )
}
