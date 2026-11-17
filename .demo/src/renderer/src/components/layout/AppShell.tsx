import { type ParentProps } from 'solid-js'
import { useLocation } from '@solidjs/router'
import { BackgroundOverlay } from './BackgroundOverlay'
import { BrandHeader } from './BrandHeader'
import { BottomBar } from './BottomBar'
import { TopBar } from './TopBar'
import { ToastHost } from '../ui/Toast'

export interface AppShellProps extends ParentProps {
  class?: string
}

/**
 * Main application shell: background, top bar, brand header, page stack and
 * bottom bar. Used by every page except setup and onboarding.
 */
export function AppShell(props: AppShellProps) {
  const location = useLocation()
  const disabled = () => location.pathname === '/setup' || location.pathname === '/onboarding'

  return (
    <div class={['relative flex h-full w-full flex-col gap-5 overflow-hidden p-[5px]', props.class].join(' ')}>
      <BackgroundOverlay />
      <div class="relative z-10 flex min-h-0 flex-1 flex-col gap-5">
        <TopBar disabled={disabled()} />
        <BrandHeader />
        <main class="min-h-0 flex-1 overflow-hidden rounded-[6px]">
          {props.children}
        </main>
        <BottomBar disabled={disabled()} />
      </div>
      <ToastHost />
    </div>
  )
}
