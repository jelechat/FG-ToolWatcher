import { LANGUAGES, type Lang } from '@shared/domain'

/** Key used to persist the selected language between two launches. */
export const LANGUAGE_STORAGE_KEY = 'toolwatcher.lang'

/** Reads the persisted language (undefined when nothing is stored). */
export function readStoredLanguage(): Lang | undefined {
  try {
    const stored = globalThis.localStorage?.getItem(LANGUAGE_STORAGE_KEY)
    if (stored && (LANGUAGES as readonly string[]).includes(stored)) return stored as Lang
  } catch {
    /* localStorage is not available */
  }
  return undefined
}

/** Persists the selected language (best effort). */
export function writeStoredLanguage(lang: Lang): void {
  try {
    globalThis.localStorage?.setItem(LANGUAGE_STORAGE_KEY, lang)
  } catch {
    /* persistence is optional */
  }
}
