import { createEffect, createSignal, onCleanup, type Accessor } from 'solid-js'

/**
 * Returns a debounced copy of the given accessor.
 * The value only updates after `delay` ms without a change.
 */
export function useDebouncedValue<T>(value: Accessor<T>, delay = 250): Accessor<T> {
  const [debounced, setDebounced] = createSignal(value())

  createEffect(() => {
    const current = value()
    const timer = setTimeout(() => setDebounced(() => current), delay)
    onCleanup(() => clearTimeout(timer))
  })

  return debounced
}
