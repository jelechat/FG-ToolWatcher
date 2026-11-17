import { flatten } from '@solid-primitives/i18n'
import {
  createContext,
  createMemo,
  createSignal,
  useContext,
  type Accessor,
  type ParentProps,
} from 'solid-js'
import { DEFAULT_LANG, LANGUAGES, type Lang } from '@shared/domain'
import { readStoredLanguage, writeStoredLanguage } from '../lib/storage'
import en from './en.json'
import fr from './fr.json'
import nl from './nl.json'

type Dictionary = Record<string, string>

const RESOURCES: Record<Lang, Dictionary> = {
  EN: flatten(en as unknown as Record<string, unknown>) as Dictionary,
  FR: flatten(fr as unknown as Record<string, unknown>) as Dictionary,
  NL: flatten(nl as unknown as Record<string, unknown>) as Dictionary,
}

const FALLBACK: Dictionary = RESOURCES.EN

export interface I18nContextValue {
  /** Currently active language. */
  lang: Accessor<Lang>
  /** Changes the active language (retranslation is reactive). */
  setLang: (lang: Lang) => void
  /** Translates a key, falling back to English then to the key itself. */
  t: (key: string) => string
  /** Available languages. */
  languages: readonly Lang[]
}

const I18nContext = createContext<I18nContextValue>()

function readStoredLang(): Lang {
  return readStoredLanguage() ?? DEFAULT_LANG
}

function persistLang(lang: Lang): void {
  writeStoredLanguage(lang)
}

export function I18nProvider(props: ParentProps<{ initialLang?: Lang }>) {
  const [lang, setLangSignal] = createSignal<Lang>(props.initialLang ?? readStoredLang())

  const dictionary = createMemo(() => RESOURCES[lang()] ?? FALLBACK)

  const value: I18nContextValue = {
    lang,
    setLang(next: Lang) {
      setLangSignal(next)
      persistLang(next)
    },
    t(key: string) {
      const active = dictionary()[key]
      if (active !== undefined && active !== '') return active
      const fallback = FALLBACK[key]
      if (fallback !== undefined && fallback !== '') return fallback
      return active ?? key
    },
    languages: LANGUAGES,
  }

  return <I18nContext.Provider value={value}>{props.children}</I18nContext.Provider>
}

/** Access the i18n context. */
export function useI18n(): I18nContextValue {
  const context = useContext(I18nContext)
  if (!context) {
    throw new Error('useI18n must be used inside an <I18nProvider>.')
  }
  return context
}

export { RESOURCES as I18N_RESOURCES }
