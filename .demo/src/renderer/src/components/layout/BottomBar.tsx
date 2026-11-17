import { Icon } from '../ui/Icon'
import { useI18n } from '../../i18n'
import { openExternal } from '../../lib/format'

export interface BottomBarProps {
  disabled?: boolean
}

const GITHUB_URL = 'https://github.com/jejeAKAgg/FG-ToolWatcher'

/** Bottom bar: [ticket] .......... [github] */
export function BottomBar(props: BottomBarProps) {
  const { t } = useI18n()

  const className =
    'flex h-[50px] w-[100px] items-center justify-center rounded-[15px] border border-border-light bg-button-secondary-bg transition-colors hover:border-accent hover:bg-button-secondary-hover disabled:cursor-not-allowed disabled:border-none disabled:bg-disabled-bg'

  return (
    <div class="flex items-center justify-between px-[5px]">
      <button
        type="button"
        class={className}
        disabled={props.disabled}
        title={t('page_menu.ticket.button')}
        onClick={() => void openExternal(`${GITHUB_URL}/issues`)}
      >
        <Icon name="bug" color="white" size={28} />
      </button>
      <button
        type="button"
        class={className}
        disabled={props.disabled}
        title={t('page_menu.github.button')}
        onClick={() => void openExternal(GITHUB_URL)}
      >
        <Icon name="github" color="white" size={28} />
      </button>
    </div>
  )
}
