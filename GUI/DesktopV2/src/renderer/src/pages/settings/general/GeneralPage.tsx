import { createEffect, createSignal } from 'solid-js'
import { PageTitle } from '../../../components/ui/PageTitle'
import { Toggle } from '../../../components/ui/Toggle'
import { Button } from '../../../components/ui/Button'
import { useI18n } from '../../../i18n'
import { useSettings } from '../../../providers/SettingsProvider'
import { useToast } from '../../../providers/ToastProvider'
import type { GeneralSettings } from '@shared/domain'

const DEFAULTS: GeneralSettings = {
  system_launch_on_startup: false,
  system_notify_on_finish: true,
  system_open_on_finish: false,
  user_mail_send: false,
}

/** Settings › General: four toggles + a save button. */
export function GeneralPage() {
  const { t } = useI18n()
  const settings = useSettings()
  const { notify } = useToast()

  const [draft, setDraft] = createSignal<GeneralSettings>({ ...DEFAULTS })
  const [dirty, setDirty] = createSignal(false)

  // The draft is seeded once: refreshing the settings (language change, save,
  // ...) must not discard the modifications that are not saved yet.
  let seeded = false
  createEffect(() => {
    const current = settings.settings()
    if (!current || seeded) return
    seeded = true
    setDraft({ ...current.general })
    setDirty(false)
  })

  const update = (key: keyof GeneralSettings, value: boolean) => {
    setDraft((previous) => ({ ...previous, [key]: value }))
    setDirty(true)
  }

  const save = async () => {
    await settings.saveGeneral(draft())
    setDirty(false)
    notify(t('page_settings.saved'))
  }

  return (
    <div class="flex max-w-[720px] flex-col gap-6 pb-[40px]">
      <div>
        <PageTitle>{t('page_settings.general.title')}</PageTitle>
        <p class="text-[13px] text-text-dim">{t('page_settings.general.subtitle')}</p>
      </div>

      <div class="flex flex-col gap-5">
        <Toggle
          checked={draft().system_launch_on_startup}
          onChange={(value) => update('system_launch_on_startup', value)}
          label={t('subpage_settings_general_startup.title')}
          description={t('subpage_settings_general_startup.subtitle')}
        />
        <Toggle
          checked={draft().system_notify_on_finish}
          onChange={(value) => update('system_notify_on_finish', value)}
          label={t('subpage_settings_general_notification.title')}
          description={t('subpage_settings_general_notification.subtitle')}
        />
        <Toggle
          checked={draft().system_open_on_finish}
          onChange={(value) => update('system_open_on_finish', value)}
          label={t('subpage_settings_general_open.title')}
          description={t('subpage_settings_general_open.subtitle')}
        />
        <Toggle
          checked={draft().user_mail_send}
          onChange={(value) => update('user_mail_send', value)}
          label={t('subpage_settings_general_send_email.title')}
          description={t('subpage_settings_general_send_email.subtitle')}
        />
      </div>

      <div class="flex justify-center">
        <Button
          variant="ghost"
          size="lg"
          disabled={!dirty() || settings.saving()}
          onClick={() => void save()}
        >
          {t('page_settings_save.button')}
        </Button>
      </div>
    </div>
  )
}
