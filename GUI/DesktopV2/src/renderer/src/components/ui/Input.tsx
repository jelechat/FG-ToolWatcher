import { Show, splitProps, type JSX } from 'solid-js'

export interface InputProps {
  label?: string
  value: string
  placeholder?: string
  type?: 'text' | 'email' | 'password'
  disabled?: boolean
  error?: string
  id?: string
  class?: string
  inputClass?: string
  onInput: (value: string) => void
  onKeyDown?: JSX.EventHandlerUnion<HTMLInputElement, KeyboardEvent>
}

/** Labelled text input (focus border uses the accent colour). */
export function Input(props: InputProps) {
  const [local] = splitProps(props, [
    'label',
    'value',
    'placeholder',
    'type',
    'disabled',
    'error',
    'id',
    'class',
    'inputClass',
    'onInput',
    'onKeyDown',
  ])

  return (
    <div class={['flex flex-col gap-1', local.class].join(' ')}>
      <Show when={local.label}>
        <label
          for={local.id}
          class="font-montserrat-semibold text-label text-text-dim text-center"
        >
          {local.label}
        </label>
      </Show>
      <input
        id={local.id}
        type={local.type ?? 'text'}
        value={local.value}
        placeholder={local.placeholder}
        disabled={local.disabled}
        onInput={(event) => local.onInput(event.currentTarget.value)}
        onKeyDown={local.onKeyDown}
        class={[
          'h-10 w-full rounded-[8px] border border-[#cccccc] bg-[#333333] px-3 text-text',
          'placeholder:text-text-dim focus:border-2 focus:border-accent focus:outline-none',
          local.error ? 'border-error' : '',
          local.inputClass,
        ].join(' ')}
      />
      <Show when={local.error}>
        <span class="text-[12px] text-error">{local.error}</span>
      </Show>
    </div>
  )
}
