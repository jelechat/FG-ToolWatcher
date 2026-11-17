import { Icon } from '../ui/Icon'

export interface BrandHeaderProps {
  class?: string
}

/** Logo + "TOOLWATCHER" title (the white variant is used on the dark theme). */
export function BrandHeader(props: BrandHeaderProps) {
  return (
    <header class={['flex items-center justify-center gap-4', props.class].join(' ')}>
      <Icon name="FG" color="white" size={64} class="opacity-90" />
      <h1 class="font-montserrat-black text-title-lg tracking-[2px] text-text">TOOLWATCHER</h1>
    </header>
  )
}
