import { describe, expect, it } from 'vitest'
import { render, screen } from '@solidjs/testing-library'
import { I18nProvider } from '../../src/renderer/src/i18n'
import { PriceComparisonTable } from '../../src/renderer/src/components/dashboard/ComparisonTable'
import { MOCK_PRODUCTS } from '../../src/renderer/src/services'

const COLUMN_HEADERS = [
  'EAN',
  'MPN',
  'Article',
  'Georges (?)',
  'Clabots (?)',
  'Fixami (?)',
  'Klium (?)',
  'Lecot (?)',
  'Toolnation (?)',
]

function renderTable(taxMode: 'HTVA' | 'TTC' = 'HTVA') {
  return render(() => (
    <I18nProvider>
      <PriceComparisonTable products={MOCK_PRODUCTS.slice(0, 5)} taxMode={taxMode} />
    </I18nProvider>
  ))
}

describe('PriceComparisonTable', () => {
  it('renders the 9 columns of the comparison table', () => {
    renderTable()
    const headers = screen.getAllByRole('columnheader')
    expect(headers).toHaveLength(9)
    expect(headers.map((header) => header.textContent)).toEqual(COLUMN_HEADERS)
  })

  it('renders every column header of the specification', () => {
    renderTable()
    for (const header of COLUMN_HEADERS) {
      expect(screen.getByText(header)).toBeTruthy()
    }
  })

  it('renders the article names', () => {
    renderTable()
    expect(screen.getByText(MOCK_PRODUCTS[0].name)).toBeTruthy()
  })

  it('renders an em dash when a merchant has no offer', () => {
    renderTable()
    const missing = MOCK_PRODUCTS.find((product) => Object.keys(product.priceHTVA).length < 6)
    expect(missing).toBeTruthy()
    expect(document.body.textContent).toContain('—')
  })

  it('switches the prices between HTVA and TTC', () => {
    const { unmount } = renderTable('HTVA')
    const htvaText = document.body.textContent ?? ''
    unmount()

    renderTable('TTC')
    const ttcText = document.body.textContent ?? ''
    expect(htvaText).not.toBe(ttcText)
  })
})
