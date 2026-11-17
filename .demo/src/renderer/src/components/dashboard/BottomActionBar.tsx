import { Icon, type IconName } from '../ui/Icon'
import { Button } from '../ui/Button'
import { useI18n } from '../../i18n'
import type { ViewMode } from '../../stores/ui'

export interface BottomActionBarProps {
  onUpdate: () => void
  onSave: () => void
  onEmail: () => void
  onAnalyze: () => void
  onFilter: () => void
  onClearAll: () => void
  clearAllDisabled: boolean
  viewMode: ViewMode
  onToggleView: () => void
}

const iconButton =
  'flex h-10 w-10 items-center justify-center rounded-[6px] border border-border-light bg-button-secondary-bg transition-colors hover:border-accent hover:bg-button-secondary-hover disabled:cursor-not-allowed disabled:bg-disabled-bg'

const primaryIconButton =
  'flex h-10 w-10 items-center justify-center rounded-[6px] bg-accent transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:bg-disabled-bg'

/**
 * Dashboard action bar: update / save / email / analyze ... filter / view toggle.
 */
export function BottomActionBar(props: BottomActionBarProps) {
  const { t } = useI18n()

  const action = (name: IconName, label: string, onClick: () => void, className = iconButton) => (
    <button type="button" class={className} title={label} aria-label={label} onClick={onClick}>
      <Icon name={name} color="white" size={20} />
    </button>
  )

  return (
    <div class="flex items-center gap-[10px]">
      {action('refresh', t('page_dashboard.action.update'), props.onUpdate)}
      {action('save', t('page_dashboard.action.save'), props.onSave)}
      {action('mail', t('page_dashboard.action.email'), props.onEmail)}
      {action('analyze', t('page_dashboard.action.analyze'), props.onAnalyze, primaryIconButton)}
      <div class="flex-1" />
      <Button
        variant="danger"
        disabled={props.clearAllDisabled}
        onClick={props.onClearAll}
        class="h-10 px-3 text-[13px]"
      >
        <span aria-hidden="true" class="text-[18px] leading-none">×</span>
        {t('page_search_remove_all.button')}
      </Button>
      {action('filter', t('page_dashboard.action.filter'), props.onFilter)}
      <button
        type="button"
        class={[
          iconButton,
          props.viewMode === 'graph' ? 'border-accent bg-accent-active' : '',
        ].join(' ')}
        title={props.viewMode === 'table' ? t('page_dashboard.view.graph') : t('page_dashboard.view.table')}
        aria-label={props.viewMode === 'table' ? t('page_dashboard.view.graph') : t('page_dashboard.view.table')}
        onClick={props.onToggleView}
      >
        <Icon name={props.viewMode === 'table' ? 'table' : 'graph'} color="white" size={20} />
      </button>
    </div>
  )
}
