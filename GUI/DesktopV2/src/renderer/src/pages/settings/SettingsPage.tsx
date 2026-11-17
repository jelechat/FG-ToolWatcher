import { createSignal, Match, onCleanup, Switch } from 'solid-js'
import { useNavigate, useParams } from '@solidjs/router'
import { AppShell } from '../../components/layout/AppShell'
import { SettingsSidebar } from '../../components/layout/SettingsSidebar'
import { GeneralPage } from './general/GeneralPage'
import { WebsitesPage } from './websites/WebsitesPage'
import { SettingsProfilePage } from './profile/SettingsProfilePage'
import { SystemPage } from './system/SystemPage'
import { AIPage } from './ai/AIPage'

const SECTIONS = ['general', 'websites', 'profile', 'system', 'ai'] as const
type Section = (typeof SECTIONS)[number]

function isSection(value: string | undefined): value is Section {
  return SECTIONS.includes(value as Section)
}

/**
 * Settings shell: 260px sidebar + content stack with a fade transition.
 */
export function SettingsPage() {
  const params = useParams<{ section?: string }>()
  const navigate = useNavigate()
  const [locked, setLocked] = createSignal(false)

  const active = (): Section => (isSection(params.section) ? params.section : 'general')

  // The sidebar is locked during the fade transition: the timer releasing it
  // must be cleared when the component is unmounted.
  let unlockTimer: ReturnType<typeof setTimeout> | undefined
  onCleanup(() => {
    if (unlockTimer) clearTimeout(unlockTimer)
  })

  const select = (key: string) => {
    if (locked()) return
    setLocked(true)
    navigate(`/settings/${key}`)
    if (unlockTimer) clearTimeout(unlockTimer)
    unlockTimer = setTimeout(() => {
      unlockTimer = undefined
      setLocked(false)
    }, 300)
  }

  return (
    <AppShell>
      <div class="flex h-full">
        <SettingsSidebar active={active()} onSelect={select} locked={locked()} />
        <div class="min-w-0 flex-1 overflow-y-auto px-[60px] pt-[50px]">
          <Switch>
            <Match when={active() === 'general'}>
              <GeneralPage />
            </Match>
            <Match when={active() === 'websites'}>
              <WebsitesPage />
            </Match>
            <Match when={active() === 'profile'}>
              <SettingsProfilePage />
            </Match>
            <Match when={active() === 'system'}>
              <SystemPage />
            </Match>
            <Match when={active() === 'ai'}>
              <AIPage />
            </Match>
          </Switch>
        </div>
      </div>
    </AppShell>
  )
}
