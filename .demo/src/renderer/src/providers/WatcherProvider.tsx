import {
  createContext,
  createSignal,
  onCleanup,
  useContext,
  type Accessor,
  type ParentProps,
} from 'solid-js'
import { getServices } from '../services'

export interface WatcherContextValue {
  /** Current progress (0..100). */
  progress: Accessor<number>
  /** True while a run is in progress. */
  running: Accessor<boolean>
  /** Starts a simulated run and resolves when it is over. */
  start: () => Promise<void>
  /** Stops the current run. */
  stop: () => void
}

const WatcherContext = createContext<WatcherContextValue>()

export function WatcherProvider(props: ParentProps) {
  const services = getServices()
  const [progress, setProgress] = createSignal(0)
  const [running, setRunning] = createSignal(false)

  const unsubscribe = services.watcher.subscribe((value) => {
    setProgress(value)
    setRunning(services.watcher.isRunning())
  })

  onCleanup(unsubscribe)

  const start = async () => {
    setRunning(true)
    try {
      await services.watcher.start()
    } finally {
      setRunning(false)
    }
  }

  const stop = () => {
    services.watcher.stop()
    setRunning(false)
  }

  const value: WatcherContextValue = { progress, running, start, stop }

  return <WatcherContext.Provider value={value}>{props.children}</WatcherContext.Provider>
}

/** Access the watcher API. */
export function useWatcher(): WatcherContextValue {
  const context = useContext(WatcherContext)
  if (!context) throw new Error('useWatcher must be used inside a <WatcherProvider>.')
  return context
}
