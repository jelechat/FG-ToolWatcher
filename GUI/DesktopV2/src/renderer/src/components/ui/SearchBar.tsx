import { For, Show } from 'solid-js'

export interface SearchBarProps {
  value: string
  onInput: (value: string) => void
  placeholder?: string
  /** Minimum width in pixels (750 on the dashboard). */
  minWidth?: number
  /** Optional suggestion list (autocomplete). */
  suggestions?: string[]
  onSuggestion?: (suggestion: string) => void
  class?: string
}

/** Search input with a clear button and an optional suggestion popup. */
export function SearchBar(props: SearchBarProps) {
  const showSuggestions = () =>
    Boolean(props.suggestions?.length) && props.value.trim().length >= 3

  return (
    <div class={['relative flex items-center', props.class].join(' ')}>
      <input
        type="text"
        value={props.value}
        placeholder={props.placeholder}
        onInput={(event) => props.onInput(event.currentTarget.value)}
        style={{ 'min-width': `${props.minWidth ?? 300}px` }}
        class="h-10 w-full rounded-[6px] border border-border bg-surface px-5 text-text placeholder:text-text-dim focus:border-accent focus:outline-none"
      />
      <Show when={props.value.length > 0}>
        <button
          type="button"
          aria-label="Clear"
          onClick={() => props.onInput('')}
          class="absolute right-3 flex h-6 w-6 items-center justify-center rounded-full text-text-dim hover:bg-white/10 hover:text-text"
        >
          ✕
        </button>
      </Show>
      <Show when={showSuggestions()}>
        <ul class="absolute left-0 top-[42px] z-40 max-h-[260px] w-full overflow-auto rounded-[6px] border border-border bg-header-bg shadow-md">
          <For each={props.suggestions}>
            {(suggestion) => (
              <li>
                <button
                  type="button"
                  class="w-full px-3 py-2 text-left text-[13px] text-text hover:bg-white/10"
                  onClick={() => props.onSuggestion?.(suggestion)}
                >
                  {suggestion}
                </button>
              </li>
            )}
          </For>
        </ul>
      </Show>
    </div>
  )
}
