import {
  createContext,
  createSignal,
  onCleanup,
  useContext,
  type Accessor,
  type ParentProps,
} from 'solid-js'

export interface ToastState {
  message: string
  visible: boolean
  exiting: boolean
}

export interface ToastContextValue {
  /** Current toast state (reactive). */
  toast: Accessor<ToastState>
  /** Displays a toast, replacing the one currently shown. */
  notify: (message: string, duration?: number) => void
  /** Hides the current toast. */
  dismiss: () => void
}

const ToastContext = createContext<ToastContextValue>()

const DEFAULT_DURATION = 3000
const EXIT_DURATION = 300

export function ToastProvider(props: ParentProps) {
  const [state, setState] = createSignal<ToastState>({
    message: '',
    visible: false,
    exiting: false,
  })

  let hideTimer: ReturnType<typeof setTimeout> | undefined
  let exitTimer: ReturnType<typeof setTimeout> | undefined

  const clearTimers = () => {
    if (hideTimer) {
      clearTimeout(hideTimer)
      hideTimer = undefined
    }
    if (exitTimer) {
      clearTimeout(exitTimer)
      exitTimer = undefined
    }
  }

  // No timer may survive the unmount of the provider.
  onCleanup(clearTimers)

  const dismiss = () => {
    if (hideTimer) {
      clearTimeout(hideTimer)
      hideTimer = undefined
    }
    setState((current) => ({ ...current, exiting: true }))
    exitTimer = setTimeout(() => {
      exitTimer = undefined
      setState({ message: '', visible: false, exiting: false })
    }, EXIT_DURATION)
  }

  const notify = (message: string, duration: number = DEFAULT_DURATION) => {
    // A new toast cancels the pending timers of the previous one.
    clearTimers()
    setState({ message, visible: true, exiting: false })
    hideTimer = setTimeout(() => {
      hideTimer = undefined
      dismiss()
    }, duration)
  }

  const value: ToastContextValue = { toast: state, notify, dismiss }

  return <ToastContext.Provider value={value}>{props.children}</ToastContext.Provider>
}

/** Access the toast API. */
export function useToast(): ToastContextValue {
  const context = useContext(ToastContext)
  if (!context) throw new Error('useToast must be used inside a <ToastProvider>.')
  return context
}
