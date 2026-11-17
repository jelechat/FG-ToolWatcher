import type { AppInfo } from '../shared/domain'

export interface ToolWatcherApi {
  getInfo(): Promise<AppInfo>
  openExternal(url: string): Promise<boolean>
  onNavigate(callback: (path: string) => void): () => void
}

declare global {
  interface Window {
    toolwatcher?: ToolWatcherApi
  }
}

export {}
