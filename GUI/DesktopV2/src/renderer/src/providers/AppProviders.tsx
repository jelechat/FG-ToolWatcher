import type { ParentProps } from 'solid-js'
import { I18nProvider } from '../i18n'
import { QueryProvider } from './QueryProvider'
import { SettingsProvider } from './SettingsProvider'
import { ToastProvider } from './ToastProvider'
import { WatcherProvider } from './WatcherProvider'

/**
 * Composes every application provider.
 * Order matters: settings depend on i18n, i18n is independent.
 */
export function AppProviders(props: ParentProps) {
  return (
    <QueryProvider>
      <I18nProvider>
        <ToastProvider>
          <SettingsProvider>
            <WatcherProvider>{props.children}</WatcherProvider>
          </SettingsProvider>
        </ToastProvider>
      </I18nProvider>
    </QueryProvider>
  )
}
