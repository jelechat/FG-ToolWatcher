import { Portal } from 'solid-js/web'
import { Show } from 'solid-js'
import { useToast } from '../../providers/ToastProvider'

/**
 * Bottom-centered toast host. Only one toast is displayed at a time
 * (same behaviour as the PySide6 implementation).
 */
export function ToastHost() {
  const { toast } = useToast()

  return (
    <Portal>
      <Show when={toast().visible}>
        <div
          role="status"
          aria-live="polite"
          class={[
            'pointer-events-none fixed bottom-[10px] left-1/2 z-[140] flex h-[50px] -translate-x-1/2 items-center',
            'rounded-[10px] border border-accent-hover bg-toast-bg px-5',
            'font-montserrat-semibold text-label font-bold text-text shadow-md',
            toast().exiting ? 'animate-toast-out' : 'animate-toast-in',
          ].join(' ')}
        >
          {toast().message}
        </div>
      </Show>
    </Portal>
  )
}
