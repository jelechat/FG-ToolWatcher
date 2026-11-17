import { A } from '@solidjs/router'
import { useI18n } from '../i18n'
import { Button } from '../components/ui/Button'

/** 404 page. */
export function NotFoundPage() {
  const { t } = useI18n()

  return (
    <div class="flex h-full w-full flex-col items-center justify-center gap-4 p-[20px]">
      <span class="font-montserrat-black text-[72px] leading-none text-accent">404</span>
      <h1 class="font-montserrat-black text-title tracking-[2px] text-text">
        {t('page_notfound.title')}
      </h1>
      <p class="text-[13px] text-text-dim">{t('page_notfound.subtitle')}</p>
      <A href="/dashboard">
        <Button variant="ghost" size="lg">
          {t('common.back')}
        </Button>
      </A>
    </div>
  )
}
