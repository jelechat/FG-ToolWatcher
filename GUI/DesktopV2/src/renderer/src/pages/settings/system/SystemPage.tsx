import { createSignal } from 'solid-js'
import { PageTitle } from '../../../components/ui/PageTitle'
import { ConfirmDialog } from '../../../components/search/ConfirmDialog'
import { useI18n } from '../../../i18n'
import { useSettings } from '../../../providers/SettingsProvider'
import { useToast } from '../../../providers/ToastProvider'
import { resetUiState } from '../../../stores/ui'

/** Settings › System: update / restart / hard reset (all mocked). */
export function SystemPage() {
  const { t } = useI18n()
  const settings = useSettings()
  const { notify } = useToast()
  const [resetOpen, setResetOpen] = createSignal(false)

  const systemButton =
    'flex h-[46px] w-[240px] items-center justify-center rounded-[6px] font-semibold text-text transition-colors'

  return (
    <div class="flex max-w-[720px] flex-col gap-6 pb-[40px]">
      <div>
        <PageTitle>{t('page_settings.system.title')}</PageTitle>
        <p class="text-[13px] text-text-dim">{t('page_settings.system.subtitle')}</p>
      </div>

      <div class="flex flex-col items-center gap-4">
        <button
          type="button"
          class={`${systemButton} bg-button-info-bg hover:bg-[#005a9e]`}
          onClick={() => notify(t('page_settings.system.update.done'))}
        >
          {t('subpage_settings_system_update.button')}
        </button>
        <button
          type="button"
          class={`${systemButton} bg-button-warning-bg hover:bg-[#444444]`}
          onClick={() => notify(t('page_settings.system.restart.done'))}
        >
          {t('subpage_settings_system_restart.button')}
        </button>
        <button
          type="button"
          class={`${systemButton} bg-button-danger-bg hover:bg-error-dark`}
          onClick={() => setResetOpen(true)}
        >
          {t('subpage_settings_system_reset.button')}
        </button>
      </div>

      <ConfirmDialog
        open={resetOpen()}
        onOpenChange={setResetOpen}
        title={t('page_settings.system.reset.title')}
        description={t('page_settings.system.reset.subtitle')}
        confirmLabel={t('subpage_settings_system_reset.button')}
        danger
        onConfirm={() => {
          void settings.reset()
          resetUiState()
          notify(t('page_settings.system.reset.done'))
        }}
      />
    </div>
  )
}
