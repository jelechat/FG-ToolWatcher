import type { ParentProps } from 'solid-js'

export interface ScrollAreaProps extends ParentProps {
  class?: string
}

/** Scrollable container with the custom scrollbar of the application. */
export function ScrollArea(props: ScrollAreaProps) {
  return (
    <div class={['overflow-y-auto overflow-x-hidden', props.class].join(' ')}>
      {props.children}
    </div>
  )
}
