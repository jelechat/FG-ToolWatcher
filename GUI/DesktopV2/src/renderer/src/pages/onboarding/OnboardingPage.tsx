import { createResource } from 'solid-js'
import { useNavigate } from '@solidjs/router'
import { MinimalLayout } from '../../components/layout/MinimalLayout'
import { ProfileForm } from '../../components/profile/ProfileForm'
import { useI18n } from '../../i18n'
import { getServices } from '../../services'
import type { User } from '@shared/domain'

/**
 * Onboarding screen (first run): collects the user information.
 */
export function OnboardingPage() {
  const navigate = useNavigate()
  const { t } = useI18n()
  const services = getServices()
  const [user, { mutate }] = createResource<User>(() => services.profile.get())

  const save = async (next: User) => {
    const saved = await services.profile.save(next)
    mutate(saved)
  }

  return (
    <MinimalLayout>
      <div class="w-full max-w-[640px]">
        {user() && (
          <ProfileForm
            initial={user()!}
            firstNameKey="page_profile_firstname.subtitle"
            lastNameKey="page_profile_lastname.subtitle"
            mailKey="page_profile_mail.subtitle"
            title={t('page_profile_informations.title')}
            onSave={save}
          />
        )}
      </div>
      <button
        type="button"
        class="mt-6 text-[13px] text-text-dim underline hover:text-text"
        onClick={() => navigate('/dashboard')}
      >
        {t('page_onboarding.skip.button')}
      </button>
    </MinimalLayout>
  )
}
