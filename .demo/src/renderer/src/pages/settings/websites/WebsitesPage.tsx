import { createEffect, createSignal, For } from 'solid-js'
import { CACHE_VALUES, DISABLED_SITES, SITES, type CacheDuration, type Site } from '@shared/domain'
import { PageTitle } from '../../../components/ui/PageTitle'
import { ToggleGroup } from '../../../components/ui/ToggleGroup'
import { CacheSlider } from '../../../components/ui/Slider'
import { Button } from '../../../components/ui/Button'
import { Badge } from '../../../components/ui/Badge'
import { useI18n } from '../../../i18n'
import { useSettings } from '../../../providers/SettingsProvider'
import { useToast } from '../../../providers/ToastProvider'

const CACHE_LABEL_KEYS = [
  'subpage_settings_websites_0day.label',
  'subpage_settings_websites_1day.label',
  'subpage_settings_websites_3day.label',
  'subpage_settings_websites_7day.label',
  'subpage_settings_websites_14day.label',
] as const

/** Settings › Websites: merchant pills + cache duration slider. */
export function WebsitesPage() {
  const { t } = useI18n()
  const settings = useSettings()
  const { notify } = useToast()

  const [sites, setSites] = createSignal<Site[]>([])
  const [cacheIndex, setCacheIndex] = createSignal(2)
  const [dirty, setDirty] = createSignal(false)

  // The draft is seeded once: refreshing the settings (language change, save,
  // ...) must not discard the modifications that are not saved yet.
  let seeded = false
  createEffect(() => {
    const current = settings.settings()
    if (!current || seeded) return
    seeded = true
    setSites([...current.websites.websites_to_watch])
    setCacheIndex(Math.max(0, CACHE_VALUES.indexOf(current.websites.websites_cache_duration)))
    setDirty(false)
  })

  const toggleSite = (value: string) => {
    const site = value as Site
    setSites((previous) =>
      previous.includes(site)
        ? previous.filter((item) => item !== site)
        : [...previous, site],
    )
    setDirty(true)
  }

  const save = async () => {
    await settings.saveWebsites({
      websites_to_watch: sites(),
      websites_cache_duration: CACHE_VALUES[cacheIndex()] as CacheDuration,
    })
    setDirty(false)
    notify(t('page_settings.saved'))
  }

  const options = () =>
    SITES.map((site) => ({
      value: site,
      label: site,
      disabled: DISABLED_SITES.includes(site),
      disabledReason: t('subpage_settings_websites.disabled'),
    }))

  return (
    <div class="flex max-w-[720px] flex-col gap-6 pb-[40px]">
      <div>
        <PageTitle>{t('page_settings.websites.title')}</PageTitle>
        <p class="text-[13px] text-text-dim">{t('page_settings.websites.subtitle')}</p>
      </div>

      <div class="flex flex-col gap-3">
        <ToggleGroup options={options()} selected={sites()} onToggle={toggleSite} />
        <div class="flex items-center gap-2">
          <For each={DISABLED_SITES}>
            {(site) => (
              <Badge tone="neutral">
                {site} · {t('subpage_settings_websites.disabled')}
              </Badge>
            )}
          </For>
        </div>
      </div>

      <div class="flex flex-col gap-3">
        <span class="font-montserrat-semibold text-label text-text">
          {t('subpage_settings_websites_cache.title')}
        </span>
        <CacheSlider
          index={cacheIndex()}
          onIndexChange={(index) => {
            setCacheIndex(index)
            setDirty(true)
          }}
          labels={CACHE_LABEL_KEYS.map((key) => t(key))}
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
