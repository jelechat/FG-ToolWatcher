import { EMPTY_PRICE } from '@shared/domain'

/** Formats a price using the French locale, without decimals when possible. */
export function formatPrice(value: number | undefined, currency = '€'): string {
  if (value === undefined || value === null || Number.isNaN(value)) return EMPTY_PRICE
  return `${value.toLocaleString('fr-FR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })} ${currency}`
}

/** Returns the placeholder used when a merchant has no offer. */
export function missingPrice(): string {
  return EMPTY_PRICE
}

/** Opens an external URL through the preload bridge (no-op in the browser). */
export async function openExternal(url: string): Promise<void> {
  const bridge = globalThis.window?.toolwatcher
  if (bridge) {
    await bridge.openExternal(url)
    return
  }
  globalThis.open?.(url, '_blank', 'noopener,noreferrer')
}
