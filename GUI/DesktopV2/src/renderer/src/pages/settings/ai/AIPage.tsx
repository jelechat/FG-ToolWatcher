import { PageTitle } from '../../../components/ui/PageTitle'
import { Button } from '../../../components/ui/Button'
import { Badge } from '../../../components/ui/Badge'
import { Icon } from '../../../components/ui/Icon'
import { useI18n } from '../../../i18n'

/** Settings › AI: placeholder, the feature is not available yet. */
export function AIPage() {
  const { t } = useI18n()

  return (
    <div class="flex max-w-[720px] flex-col gap-6 pb-[40px]">
      <div class="flex items-center gap-3">
        <Icon name="ai" color="white" size={32} />
        <PageTitle>{t('page_settings.ai.title')}</PageTitle>
        <Badge tone="soon">SOON</Badge>
      </div>
      <p class="text-[13px] text-text-dim">{t('page_settings.ai.subtitle')}</p>

      <div class="flex justify-center">
        <Button variant="ghost" size="lg" disabled>
          {t('page_settings_save.button')}
        </Button>
      </div>
    </div>
  )
}
