import { For } from 'solid-js'
import { Icon, type IconName } from '../ui/Icon'
import { useI18n } from '../../i18n'

export interface SettingsSidebarProps {
  /** Key of the active sub-page. */
  active: string
  onSelect: (key: string) => void
  /** Disables the sidebar (during the fade transition). */
  locked?: boolean
}

interface SettingsEntry {
  key: string
  icon: IconName
  labelKey: string
}

const ENTRIES: SettingsEntry[] = [
  { key: 'general', icon: 'general', labelKey: 'page_settings_general.category' },
  { key: 'websites', icon: 'websites', labelKey: 'page_settings_websites.category' },
  { key: 'profile', icon: 'profile', labelKey: 'page_settings_profile.category' },
  { key: 'system', icon: 'system', labelKey: 'page_settings_system.category' },
  { key: 'ai', icon: 'ai', labelKey: 'page_settings_AI.category' },
]

/** Settings sidebar (5 categories, 260px wide). */
export function SettingsSidebar(props: SettingsSidebarProps) {
  const { t } = useI18n()

  return (
    <nav
      aria-label={t('page_settings.title')}
      class="h-full w-[260px] shrink-0 border-r-[5px] border-black pt-[30px]"
    >
      <ul class="flex flex-col gap-[6px] px-[12px]">
        <For each={ENTRIES}>
          {(entry) => {
            const selected = () => props.active === entry.key
            return (
              <li>
                <button
                  type="button"
                  disabled={props.locked}
                  aria-current={selected() ? 'page' : undefined}
                  onClick={() => props.onSelect(entry.key)}
                  class={[
                    'flex w-full items-center gap-[12px] rounded-[6px] border px-[12px] py-[10px] text-left transition-colors',
                    'disabled:cursor-not-allowed',
                    selected()
                      ? 'border-white/20 bg-black/25 font-montserrat-black text-[16px] text-text'
                      : 'border-transparent bg-transparent text-text-dim hover:bg-black/15',
                  ].join(' ')}
                >
                  <Icon name={entry.icon} color="white" size={22} />
                  <span class={selected() ? 'font-montserrat-black' : 'font-montserrat-semibold'}>
                    {t(entry.labelKey)}
                  </span>
                </button>
              </li>
            )
          }}
        </For>
      </ul>
    </nav>
  )
}
