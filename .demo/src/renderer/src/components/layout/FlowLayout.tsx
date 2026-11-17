import type { ParentProps } from 'solid-js'

export interface FlowLayoutProps extends ParentProps {
  class?: string
}

/** Flex container that wraps its children (used for the website pills). */
export function FlowLayout(props: FlowLayoutProps) {
  return <div class={['flex flex-wrap gap-3', props.class].join(' ')}>{props.children}</div>
}
