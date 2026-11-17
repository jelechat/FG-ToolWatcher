import type {
  CacheDuration,
  GeneralSettings,
  Lang,
  Settings,
  Site,
} from '@shared/domain'
import type { SettingsService } from '../contracts'
import { readStoredLanguage, writeStoredLanguage } from '../../lib/storage'
import { MOCK_SETTINGS } from './fixtures'
import { delay } from './productService'

/** Key used to persist the settings between two launches. */
export const SETTINGS_STORAGE_KEY = 'toolwatcher.settings'

function cloneSettings(settings: Settings): Settings {
  return {
    general: { ...settings.general },
    websites: {
      websites_to_watch: [...settings.websites.websites_to_watch],
      websites_cache_duration: settings.websites.websites_cache_duration,
    },
    language: settings.language,
  }
}

/** Reads the persisted settings (undefined when nothing is stored). */
export function readStoredSettings(): Settings | undefined {
  try {
    const raw = globalThis.localStorage?.getItem(SETTINGS_STORAGE_KEY)
    if (!raw) return undefined
    const parsed = JSON.parse(raw) as Settings
    if (!parsed?.general || !parsed?.websites) return undefined
    return cloneSettings(parsed)
  } catch {
    return undefined
  }
}

/** Persists the settings (best effort: localStorage may be unavailable). */
export function writeStoredSettings(settings: Settings): void {
  try {
    globalThis.localStorage?.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(settings))
  } catch {
    /* persistence is optional */
  }
}

/** Removes the persisted settings. */
export function clearStoredSettings(): void {
  try {
    globalThis.localStorage?.removeItem(SETTINGS_STORAGE_KEY)
  } catch {
    /* ignore */
  }
}

export class MockSettingsService implements SettingsService {
  private settings: Settings = this.initialSettings()

  async get(): Promise<Settings> {
    return delay(cloneSettings(this.settings))
  }

  async save(settings: Settings): Promise<Settings> {
    this.settings = cloneSettings(settings)
    writeStoredSettings(this.settings)
    return delay(cloneSettings(this.settings))
  }

  async updateGeneral(general: GeneralSettings): Promise<Settings> {
    this.settings = { ...this.settings, general: { ...general } }
    writeStoredSettings(this.settings)
    return delay(cloneSettings(this.settings))
  }

  async updateWebsites(websites: {
    websites_to_watch: Site[]
    websites_cache_duration: CacheDuration
  }): Promise<Settings> {
    this.settings = {
      ...this.settings,
      websites: {
        websites_to_watch: [...websites.websites_to_watch],
        websites_cache_duration: websites.websites_cache_duration,
      },
    }
    writeStoredSettings(this.settings)
    return delay(cloneSettings(this.settings))
  }

  async setLanguage(language: Lang): Promise<Settings> {
    this.settings = { ...this.settings, language }
    writeStoredSettings(this.settings)
    writeStoredLanguage(language)
    return delay(cloneSettings(this.settings))
  }

  async reset(): Promise<Settings> {
    this.settings = cloneSettings(MOCK_SETTINGS as Settings)
    writeStoredSettings(this.settings)
    writeStoredLanguage(this.settings.language)
    return delay(cloneSettings(this.settings))
  }

  /**
   * Builds the initial settings.
   * The language has a single source of truth (`toolwatcher.lang`) so that the
   * i18n provider and the settings never disagree on start-up.
   */
  private initialSettings(): Settings {
    const stored = readStoredSettings()
    const base = stored ? cloneSettings(stored) : cloneSettings(MOCK_SETTINGS as Settings)
    const language = readStoredLanguage() ?? base.language
    return { ...base, language }
  }
}
