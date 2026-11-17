import type { ParentProps } from 'solid-js'
import { BackgroundOverlay } from './BackgroundOverlay'
import { ToastHost } from '../ui/Toast'

export interface MinimalLayoutProps extends ParentProps {
  class?: string
}

/**
 * Minimal layout used by the setup and onboarding screens:
 * centered content, no top/bottom bars.
 */
export function MinimalLayout(props: MinimalLayoutProps) {
  return (
    <div class={['relative flex h-full w-full flex-col items-center justify-center overflow-hidden p-[15px]', props.class].join(' ')}>
      <BackgroundOverlay />
      <div class="relative z-10 flex h-full w-full flex-col items-center justify-center">
        {props.children}
      </div>
      <ToastHost />
    </div>
  )
}
