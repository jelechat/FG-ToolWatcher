import { createSignal } from 'solid-js'
import { Dialog } from '../ui/Dialog'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { useI18n } from '../../i18n'
import { isValidEmail } from '../../lib/validation'

export interface EmailDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  defaultRecipient: string
  onSend: (recipient: string) => Promise<void>
}

/** Dialog used to send the results by e-mail (mocked, no SMTP). */
export function EmailDialog(props: EmailDialogProps) {
  const { t } = useI18n()
  const [recipient, setRecipient] = createSignal(props.defaultRecipient)
  const [error, setError] = createSignal('')
  const [sending, setSending] = createSignal(false)

  const close = () => {
    setError('')
    props.onOpenChange(false)
  }

  const send = async () => {
    if (!isValidEmail(recipient())) {
      setError(t('page_profile.email.invalid'))
      return
    }
    setSending(true)
    try {
      await props.onSend(recipient())
      close()
    } finally {
      setSending(false)
    }
  }

  return (
    <Dialog
      open={props.open}
      onOpenChange={(open) => (open ? props.onOpenChange(true) : close())}
      onOverlayClick={close}
      title={t('page_dashboard.email.title')}
      centered
    >
      <div class="flex flex-col gap-4">
        <Input
          id="email-recipient"
          label={t('page_dashboard.email.recipient')}
          type="email"
          value={recipient()}
          error={error()}
          onInput={(value) => {
            setRecipient(value)
            setError('')
          }}
        />
        <div class="flex items-center justify-end gap-3">
          <Button variant="secondary" onClick={close}>
            {t('common.cancel')}
          </Button>
          <Button variant="primary" disabled={sending()} onClick={() => void send()}>
            {t('page_dashboard.email.send')}
          </Button>
        </div>
      </div>
    </Dialog>
  )
}
