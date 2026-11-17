import { createEffect, createSignal, Show } from 'solid-js'
import type { User } from '@shared/domain'
import { LabeledInput } from '../ui/LabeledInput'
import { Button } from '../ui/Button'
import { useI18n } from '../../i18n'
import { isValidEmail, isValidName } from '../../lib/validation'

export interface ProfileFormProps {
  initial: User
  /** Label keys (top-level profile vs. settings sub-page). */
  firstNameKey: string
  lastNameKey: string
  mailKey: string
  /** Returns true when the profile was saved. */
  onSave: (user: User) => Promise<void>
  title?: string
}

/**
 * Profile form shared by the onboarding screen and the settings sub-page.
 * The save button is only enabled when the form is valid and modified.
 */
export function ProfileForm(props: ProfileFormProps) {
  const { t } = useI18n()

  const [firstname, setFirstname] = createSignal(props.initial.firstname)
  const [lastname, setLastname] = createSignal(props.initial.lastname)
  const [mail, setMail] = createSignal(props.initial.mail)
  const [saved, setSaved] = createSignal(false)
  const [saving, setSaving] = createSignal(false)

  createEffect(() => {
    const initial = props.initial
    setFirstname(initial.firstname)
    setLastname(initial.lastname)
    setMail(initial.mail)
  })

  const emailError = () =>
    mail().length > 0 && !isValidEmail(mail()) ? t('page_profile.email.invalid') : ''
  const nameError = () =>
    firstname().length > 0 && !isValidName(firstname())
      ? t('page_profile.name.invalid')
      : ''

  const valid = () =>
    isValidEmail(mail()) && isValidName(firstname()) && isValidName(lastname())

  const dirty = () =>
    firstname() !== props.initial.firstname ||
    lastname() !== props.initial.lastname ||
    mail() !== props.initial.mail

  const canSave = () => valid() && dirty() && !saving()

  const save = async () => {
    if (!canSave()) return
    setSaving(true)
    try {
      await props.onSave({
        firstname: firstname().trim(),
        lastname: lastname().trim(),
        mail: mail().trim(),
      })
      setSaved(true)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div class="flex flex-col items-center gap-6">
      <Show when={props.title}>
        <h1 class="font-montserrat-black text-title tracking-[2px] text-text">{props.title}</h1>
      </Show>

      <LabeledInput
        id="profile-firstname"
        label={t(props.firstNameKey)}
        value={firstname()}
        error={nameError()}
        onInput={setFirstname}
      />
      <LabeledInput
        id="profile-lastname"
        label={t(props.lastNameKey)}
        value={lastname()}
        error={nameError()}
        onInput={setLastname}
      />
      <LabeledInput
        id="profile-mail"
        label={t(props.mailKey)}
        type="email"
        value={mail()}
        error={emailError()}
        onInput={setMail}
      />

      <Button variant="primary" size="lg" disabled={!canSave()} onClick={() => void save()}>
        {t('page_settings_save.button')}
      </Button>

      <Show when={saved()}>
        <span class="text-[13px] text-accent">{t('page_profile.saved')}</span>
      </Show>
    </div>
  )
}
