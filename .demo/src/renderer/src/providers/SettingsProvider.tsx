import { createQuery, useQueryClient } from '@tanstack/solid-query'
import {
  createContext,
  createEffect,
  createMemo,
  createSignal,
  useContext,
  type Accessor,
  type ParentProps,
} from 'solid-js'
import type { GeneralSettings, Lang, Settings, Site, CacheDuration } from '@shared/domain'
import { getServices } from '../services'
import { useI18n } from '../i18n'

export interface SettingsContextValue {
  /** Current settings (undefined while loading). */
  settings: Accessor<Settings | undefined>
  /** True while the settings are loading. */
  loading: Accessor<boolean>
  /** True while a save is in progress. */
  saving: Accessor<boolean>
  /** Persists the general settings. */
  saveGeneral: (general: GeneralSettings) => Promise<void>
  /** Persists the websites settings. */
  saveWebsites: (websites: {
    websites_to_watch: Site[]
    websites_cache_duration: CacheDuration
  }) => Promise<void>
  /** Changes the application language. */
  setLanguage: (lang: Lang) => Promise<void>
  /** Restores the default settings. */
  reset: () => Promise<void>
}

const SettingsContext = createContext<SettingsContextValue>()

export function SettingsProvider(props: ParentProps) {
  const services = getServices()
  const queryClient = useQueryClient()
  const i18n = useI18n()

  const query = createQuery(() => ({
    queryKey: ['settings'],
    queryFn: () => services.settings.get(),
  }))

  const settings = createMemo(() => query.data)

  // Keep the i18n language in sync with the persisted settings.
  // The settings language is only applied once (on the first load): applying
  // it on every change would override the language chosen by the user (and
  // the one persisted in localStorage) as soon as the settings are refreshed.
  let languageApplied = false
  createEffect(() => {
    const current = settings()
    if (!current || languageApplied) return
    languageApplied = true
    if (current.language !== i18n.lang()) {
      i18n.setLang(current.language)
    }
  })

  const [saving, setSaving] = createSignal(false)

  const saveGeneral = async (general: GeneralSettings) => {
    setSaving(true)
    try {
      const updated = await services.settings.updateGeneral(general)
      queryClient.setQueryData(['settings'], updated)
    } finally {
      setSaving(false)
    }
  }

  const saveWebsites = async (websites: {
    websites_to_watch: Site[]
    websites_cache_duration: CacheDuration
  }) => {
    setSaving(true)
    try {
      const updated = await services.settings.updateWebsites(websites)
      queryClient.setQueryData(['settings'], updated)
    } finally {
      setSaving(false)
    }
  }

  const setLanguage = async (lang: Lang) => {
    i18n.setLang(lang)
    const updated = await services.settings.setLanguage(lang)
    queryClient.setQueryData(['settings'], updated)
  }

  const reset = async () => {
    const updated = await services.settings.reset()
    queryClient.setQueryData(['settings'], updated)
    i18n.setLang(updated.language)
  }

  const value: SettingsContextValue = {
    settings,
    loading: () => query.isPending,
    saving,
    saveGeneral,
    saveWebsites,
    setLanguage,
    reset,
  }

  return <SettingsContext.Provider value={value}>{props.children}</SettingsContext.Provider>
}

/** Access the settings API. */
export function useSettings(): SettingsContextValue {
  const context = useContext(SettingsContext)
  if (!context) throw new Error('useSettings must be used inside a <SettingsProvider>.')
  return context
}
