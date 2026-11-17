import type { WatcherService } from '../contracts'
import { delay } from './productService'

const TICK_MS = 120
const TOTAL_TICKS = 24

/**
 * Simulates a scraping run: progresses from 0 to 100 and notifies subscribers.
 * No network call is performed.
 *
 * `start()` resolves once the run is over (or when it is stopped), so the
 * caller can display a "running" state and a "done" state in sequence.
 */
export class MockWatcherService implements WatcherService {
  private value = 0
  private running = false
  private timer: ReturnType<typeof setInterval> | undefined
  private listeners = new Set<(progress: number) => void>()
  private completion: (() => void) | undefined

  async start(): Promise<void> {
    if (this.running) return this.completionPromise()

    this.running = true
    this.value = 0
    this.emit()

    await delay(undefined)

    return new Promise<void>((resolve) => {
      this.completion = resolve
      this.timer = setInterval(() => {
        this.value = Math.min(100, this.value + 100 / TOTAL_TICKS)
        this.emit()
        if (this.value >= 100) this.stop()
      }, TICK_MS)
    })
  }

  stop(): void {
    if (this.timer) {
      clearInterval(this.timer)
      this.timer = undefined
    }
    this.running = false
    this.resolveCompletion()
  }

  isRunning(): boolean {
    return this.running
  }

  progress(): number {
    return this.value
  }

  subscribe(listener: (progress: number) => void): () => void {
    this.listeners.add(listener)
    listener(this.value)
    return () => {
      this.listeners.delete(listener)
    }
  }

  private completionPromise(): Promise<void> {
    return new Promise<void>((resolve) => {
      const previous = this.completion
      this.completion = () => {
        previous?.()
        resolve()
      }
    })
  }

  private resolveCompletion(): void {
    const completion = this.completion
    this.completion = undefined
    completion?.()
  }

  private emit(): void {
    for (const listener of this.listeners) listener(this.value)
  }
}
