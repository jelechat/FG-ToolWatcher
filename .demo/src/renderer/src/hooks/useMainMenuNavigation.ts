import { onCleanup, onMount } from 'solid-js'
import { useNavigate } from '@solidjs/router'

/**
 * Handles the navigation requests sent by the Electron application menu
 * (File > Settings). The subscription is removed when the component is
 * unmounted.
 */
export function useMainMenuNavigation(): void {
  const navigate = useNavigate()

  onMount(() => {
    const bridge = globalThis.window?.toolwatcher
    if (!bridge) return
    const unsubscribe = bridge.onNavigate((path) => navigate(path))
    onCleanup(unsubscribe)
  })
}
