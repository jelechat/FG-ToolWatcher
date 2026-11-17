import type { ParentProps } from 'solid-js'

export interface PageTitleProps extends ParentProps {
  class?: string
}

/** Big page title (Montserrat Black, 26px, letter-spacing 2px). */
export function PageTitle(props: PageTitleProps) {
  return (
    <h1
      class={[
        'font-montserrat-black text-title tracking-[2px] text-text',
        props.class,
      ].join(' ')}
    >
      {props.children}
    </h1>
  )
}
