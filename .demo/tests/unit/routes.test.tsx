import { describe, expect, it } from 'vitest'
import { render, screen, waitFor } from '@solidjs/testing-library'
import { App } from '../../src/renderer/src/App'

describe('routing', () => {
  it('renders the setup screen on the root route', async () => {
    globalThis.location.hash = ''
    render(() => <App />)
    await waitFor(() => {
      expect(screen.getAllByText('ToolWatcher').length).toBeGreaterThan(0)
    })
  })

  it('renders the dashboard and its comparison table', async () => {
    globalThis.location.hash = '#/dashboard'
    render(() => <App />)
    await waitFor(() => {
      expect(screen.getAllByText('TOOLWATCHER').length).toBeGreaterThan(0)
    })
    await waitFor(() => {
      expect(screen.getAllByText('EAN').length).toBeGreaterThan(0)
    })
  })

  it('renders the settings shell', async () => {
    globalThis.location.hash = '#/settings/general'
    render(() => <App />)
    await waitFor(() => {
      expect(screen.getAllByText('Général').length).toBeGreaterThan(0)
    })
  })

  it('renders the 404 page for an unknown route', async () => {
    globalThis.location.hash = '#/does-not-exist'
    render(() => <App />)
    await waitFor(() => {
      expect(screen.getAllByText('404').length).toBeGreaterThan(0)
    })
  })
})
