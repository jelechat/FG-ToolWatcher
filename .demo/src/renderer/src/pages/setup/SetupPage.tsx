import { createSignal, onCleanup, onMount, Show } from 'solid-js'
import { useNavigate } from '@solidjs/router'
import { MinimalLayout } from '../../components/layout/MinimalLayout'
import { Spinner } from '../../components/ui/Spinner'
import { Button } from '../../components/ui/Button'
import { useI18n } from '../../i18n'
import { getServices } from '../../services'

const STEP_KEYS = [
  'page_setup_start.text',
  'page_setup_step1.text',
  'page_setup_step2.text',
  'page_setup_step3.text',
  'page_setup_step4.text',
  'page_setup_step5.text',
] as const

const STEP_DURATION = 500

/**
 * Setup screen: simulated start-up sequence with a spinner and a step label.
 *
 * On the first launch (no profile yet) the user is sent to the onboarding
 * screen, otherwise straight to the dashboard.
 */
export function SetupPage() {
  const navigate = useNavigate()
  const { t } = useI18n()
  const services = getServices()

  const [step, setStep] = createSignal(0)
  const [done, setDone] = createSignal(false)
  const [error, setError] = createSignal(false)

  let timers: ReturnType<typeof setTimeout>[] = []

  /** Destination once the setup is over: onboarding on first launch. */
  const destination = async (): Promise<string> => {
    const hasProfile = await services.profile.exists()
    return hasProfile ? '/dashboard' : '/onboarding'
  }

  const goToApp = async () => {
    const target = await destination()
    navigate(target)
  }

  const finish = async () => {
    setDone(true)
    const timer = setTimeout(() => void goToApp(), 900)
    timers.push(timer)
  }

  onMount(() => {
    try {
      STEP_KEYS.forEach((_key, index) => {
        const timer = setTimeout(() => {
          if (index === STEP_KEYS.length - 1) void finish()
          else setStep(index + 1)
        }, STEP_DURATION * (index + 1))
        timers.push(timer)
      })
    } catch (cause) {
      console.error('[setup] failed', cause)
      setError(true)
    }
  })

  onCleanup(() => timers.forEach((timer) => clearTimeout(timer)))

  return (
    <MinimalLayout>
      <div class="flex flex-col items-center gap-6">
        <h1 class="font-montserrat-black text-title-lg tracking-[2px] text-text">
          {t('page_setup.title')}
        </h1>

        <Show
          when={!error()}
          fallback={
            <p class="font-montserrat-semibold text-[15px] text-error">
              {t('page_setup.error')}
            </p>
          }
        >
          <Spinner radius={40} dotSize={10} color="#007e2d" />
        </Show>

        <p class="max-w-[520px] text-center font-montserrat-semibold text-[15px] text-text">
          {done() ? t('page_setup_complete.text') : t(STEP_KEYS[step()])}
        </p>

        <Button variant="ghost" onClick={() => void goToApp()}>
          {t('page_setup.skip.button')}
        </Button>
      </div>
    </MinimalLayout>
  )
}
