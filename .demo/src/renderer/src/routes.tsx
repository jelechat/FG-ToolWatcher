import { HashRouter, Navigate, Route } from '@solidjs/router'
import type { ParentProps } from 'solid-js'
import { AppProviders } from './providers/AppProviders'
import { useMainMenuNavigation } from './hooks/useMainMenuNavigation'
import { SetupPage } from './pages/setup/SetupPage'
import { OnboardingPage } from './pages/onboarding/OnboardingPage'
import { DashboardPage } from './pages/dashboard/DashboardPage'
import { SearchPage } from './pages/search/SearchPage'
import { SettingsPage } from './pages/settings/SettingsPage'
import { NotFoundPage } from './pages/NotFound'

/** Root of the router: providers + main menu navigation handling. */
function RouterRoot(props: ParentProps) {
  useMainMenuNavigation()
  return <AppProviders>{props.children}</AppProviders>
}

/**
 * Application routes.
 * A HashRouter is used so that the app also works when loaded from `file://`.
 */
export function AppRoutes() {
  return (
    <HashRouter root={RouterRoot}>
      <Route path="/" component={() => <Navigate href="/setup" />} />
      <Route path="/setup" component={SetupPage} />
      <Route path="/onboarding" component={OnboardingPage} />
      <Route path="/profile" component={OnboardingPage} />
      <Route path="/dashboard" component={DashboardPage} />
      <Route path="/search" component={SearchPage} />
      <Route path="/settings" component={() => <Navigate href="/settings/general" />} />
      <Route path="/settings/:section" component={SettingsPage} />
      <Route path="*" component={NotFoundPage} />
    </HashRouter>
  )
}
