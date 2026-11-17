import { createEffect, For } from 'solid-js'
import { useLocation, useNavigate } from '@solidjs/router'
import { Icon } from '../ui/Icon'
import { useI18n } from '../../i18n'
import { useSettings } from '../../providers/SettingsProvider'
import { useToast } from '../../providers/ToastProvider'
import { useWatcher } from '../../providers/WatcherProvider'
import { openExternal } from '../../lib/format'
import type { Lang } from '@shared/domain'

export interface TopBarProps {
  /** Disables the action buttons (setup / profile screens). */
  disabled?: boolean
}

const FLAG_BY_LANG: Record<Lang, 'english' | 'french' | 'netherlands'> = {
  EN: 'english',
  FR: 'french',
  NL: 'netherlands',
}

const DOCS_URL = 'https://github.com/jejeAKAgg/FG-ToolWatcher/wiki'

// TopBar is remounted when the router changes pages, so keep the return route
// at module scope while the settings view is open.
let lastPageOutsideSettings = '/dashboard'

/**
 * Top bar: [settings | sync] .... [EN | FR | NL] .... [docs]
 */
export function TopBar(props: TopBarProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const { t, lang } = useI18n()
  const settings = useSettings()
  const { notify } = useToast()
  const watcher = useWatcher()

  const settingsOpen = () =>
    location.pathname === '/settings' || location.pathname.startsWith('/settings/')

  createEffect(() => {
    const path = location.pathname
    if (path !== '/settings' && !path.startsWith('/settings/')) {
      lastPageOutsideSettings = path
    }
  })

  const toggleSettings = () => {
    if (settingsOpen()) {
      navigate(lastPageOutsideSettings)
      return
    }

    lastPageOutsideSettings = location.pathname
    navigate('/settings/general')
  }

  /**
   * Synchronization is a mock: it runs the simulated watcher and reports the
   * progression through a toast. It must never reset the user settings.
   */
  const runSync = async () => {
    if (watcher.running()) return
    notify(t('page_dashboard.progress.running'))
    await watcher.start()
    notify(t('page_dashboard.progress.done'))
  }

  const iconButtonClass =
    'flex h-[50px] w-[50px] items-center justify-center rounded-[25px] border border-border-light bg-button-secondary-bg transition-colors hover:border-accent hover:bg-button-secondary-hover disabled:cursor-not-allowed disabled:border-none disabled:bg-disabled-bg disabled:text-disabled-text'

  const menuButtonClass =
    'flex h-[50px] w-[100px] items-center justify-center rounded-[15px] border border-border-light bg-button-secondary-bg transition-colors hover:border-accent hover:bg-button-secondary-hover disabled:cursor-not-allowed disabled:border-none disabled:bg-disabled-bg'

  return (
    <div class="grid grid-cols-[1fr_auto_1fr] items-center gap-[10px] px-[5px]">
      {/* LEFT */}
      <div class="flex items-center gap-[15px]">
        <button
          type="button"
          class={[
            menuButtonClass,
            settingsOpen() ? 'border-accent bg-button-secondary-hover' : '',
          ].join(' ')}
          disabled={props.disabled}
          aria-pressed={settingsOpen()}
          title={t('page_menu.settings.button')}
          onClick={toggleSettings}
        >
          <Icon name="settings" color="white" size={28} />
        </button>
        <button
          type="button"
          class={iconButtonClass}
          disabled={props.disabled || watcher.running()}
          title={t('page_menu.sync.button')}
          onClick={() => void runSync()}
        >
          <Icon name="synchronize" color="white" size={28} />
        </button>
      </div>

      {/* CENTER: languages */}
      <div class="flex items-center gap-[10px]">
        <For each={['EN', 'FR', 'NL'] as Lang[]}>
          {(code) => (
            <button
              type="button"
              aria-label={code}
              aria-pressed={lang() === code}
              title={code}
              onClick={() => void settings.setLanguage(code)}
              class={[
                'flex h-[35px] w-[55px] items-center justify-center overflow-hidden rounded-[15px] bg-[#818386]/50 transition-colors hover:bg-[#6d6e70]/70',
                lang() === code ? 'ring-2 ring-accent' : '',
              ].join(' ')}
            >
              <Icon name={FLAG_BY_LANG[code]} size={26} />
            </button>
          )}
        </For>
      </div>

      {/* RIGHT */}
      <div class="flex items-center justify-end gap-[15px]">
        <button
          type="button"
          class={menuButtonClass}
          disabled={props.disabled}
          title={t('page_menu.docs.button')}
          onClick={() => void openExternal(DOCS_URL)}
        >
          <Icon name="documentation" color="white" size={28} />
        </button>
      </div>
    </div>
  )
}
