import { createResource } from 'solid-js'
import { ProfileForm } from '../../../components/profile/ProfileForm'
import { PageTitle } from '../../../components/ui/PageTitle'
import { useI18n } from '../../../i18n'
import { getServices } from '../../../services'
import type { User } from '@shared/domain'

/** Settings › Profile: same form as the onboarding screen. */
export function SettingsProfilePage() {
  const { t } = useI18n()
  const services = getServices()
  const [user, { mutate }] = createResource<User>(() => services.profile.get())

  const save = async (next: User) => {
    const saved = await services.profile.save(next)
    mutate(saved)
  }

  return (
    <div class="flex max-w-[720px] flex-col gap-6 pb-[40px]">
      <div>
        <PageTitle>{t('page_settings.profile.title')}</PageTitle>
        <p class="text-[13px] text-text-dim">{t('page_settings.profile.subtitle')}</p>
      </div>

      {user() && (
        <ProfileForm
          initial={user()!}
          firstNameKey="subpage_settings_profile_firstname.title"
          lastNameKey="subpage_settings_profile_lastname.title"
          mailKey="subpage_settings_profile_email.title"
          onSave={save}
        />
      )}
    </div>
  )
}
