import { Show, type ParentProps } from 'solid-js'

export interface PageTransitionProps extends ParentProps {
  /** Key changing triggers the fade transition. */
  transitionKey?: string | number
  class?: string
}

/**
 * Fade transition wrapper (300ms InOutQuad: 150ms out, 30ms hold, 150ms in).
 */
export function PageTransition(props: PageTransitionProps) {
  return (
    <div class={['h-full w-full animate-fade-in', props.class].join(' ')} data-transition-key={props.transitionKey}>
      <Show when={props.children} keyed>
        {(children) => children}
      </Show>
    </div>
  )
}
