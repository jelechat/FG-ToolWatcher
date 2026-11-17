import { describe, expect, it } from 'vitest'
import { render, screen, fireEvent } from '@solidjs/testing-library'
import { I18nProvider, useI18n } from '../../src/renderer/src/i18n'

function Probe() {
  const { t, lang, setLang } = useI18n()
  return (
    <div>
      <span data-testid="label">{t('page_settings_save.button')}</span>
      <span data-testid="lang">{lang()}</span>
      <button type="button" onClick={() => setLang('EN')}>
        en
      </button>
      <button type="button" onClick={() => setLang('FR')}>
        fr
      </button>
    </div>
  )
}

describe('I18nProvider', () => {
  it('translates and retranslates dynamically', async () => {
    render(() => (
      <I18nProvider>
        <Probe />
      </I18nProvider>
    ))

    expect(screen.getByTestId('label').textContent).toBe('Enregistrer')
    expect(screen.getByTestId('lang').textContent).toBe('FR')

    fireEvent.click(screen.getByText('en'))
    expect(screen.getByTestId('label').textContent).toBe('Save')
    expect(screen.getByTestId('lang').textContent).toBe('EN')

    fireEvent.click(screen.getByText('fr'))
    expect(screen.getByTestId('label').textContent).toBe('Enregistrer')
  })

  it('falls back to English for an unknown key', () => {
    function Unknown() {
      const { t } = useI18n()
      return <span data-testid="unknown">{t('does.not.exist')}</span>
    }
    render(() => (
      <I18nProvider initialLang="NL">
        <Unknown />
      </I18nProvider>
    ))
    expect(screen.getByTestId('unknown').textContent).toBe('does.not.exist')
  })
})
