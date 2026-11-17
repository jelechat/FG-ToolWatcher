import { Dialog } from '../ui/Dialog'
import { Button } from '../ui/Button'
import { useI18n } from '../../i18n'

export interface ConfirmDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description: string
  confirmLabel?: string
  cancelLabel?: string
  danger?: boolean
  onConfirm: () => void
}

/** Generic confirmation dialog ("Remove all", "Hard reset", ...). */
export function ConfirmDialog(props: ConfirmDialogProps) {
  const { t } = useI18n()

  return (
    <Dialog
      open={props.open}
      onOpenChange={props.onOpenChange}
      onOverlayClick={() => props.onOpenChange(false)}
      title={props.title}
      centered
    >
      <p class="text-[13px] text-text-dim">{props.description}</p>
      <div class="mt-5 flex items-center justify-end gap-3">
        <Button variant="secondary" onClick={() => props.onOpenChange(false)}>
          {props.cancelLabel ?? t('common.cancel')}
        </Button>
        <Button
          variant={props.danger ? 'danger' : 'primary'}
          onClick={() => {
            props.onConfirm()
            props.onOpenChange(false)
          }}
        >
          {props.confirmLabel ?? t('common.confirm')}
        </Button>
      </div>
    </Dialog>
  )
}
