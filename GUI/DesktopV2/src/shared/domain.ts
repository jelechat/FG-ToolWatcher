/**
 * Shared domain model between the Electron main process and the renderer.
 * This module must stay free of any Node/Electron specific import so that it
 * can be bundled in both contexts.
 */

export const SITES = [
  'CIPAC',
  'CLABOTS',
  'GEORGES',
  'FIXAMI',
  'KLIUM',
  'LECOT',
  'TOOLNATION',
] as const

export type Site = (typeof SITES)[number]

/** Merchants displayed as columns of the comparison table. */
export const PRICE_SITES = [
  'Georges',
  'Clabots',
  'Fixami',
  'Klium',
  'Lecot',
  'Toolnation',
] as const

export type PriceSite = (typeof PRICE_SITES)[number]

/** Sites that are not available yet (disabled in the UI). */
export const DISABLED_SITES: readonly Site[] = ['CIPAC', 'GEORGES']

export const CACHE_VALUES = [0, 1, 3, 7, 14] as const
export type CacheDuration = (typeof CACHE_VALUES)[number]

export const LANGUAGES = ['EN', 'FR', 'NL'] as const
export type Lang = (typeof LANGUAGES)[number]

export const DEFAULT_LANG: Lang = 'FR'

export type TaxMode = 'HTVA' | 'TTC'

export interface Product {
  /** Human readable article name. */
  name: string
  /** Manufacturer part number, "-" when unknown. */
  mpn: string
  /** EAN barcode, "-" when unknown. */
  ean: string
  /** Brand, "-" when unknown. */
  brand: string
  /** Category used by the Quick Add dialog. */
  category: string
  /** Price per site, excluding VAT (HTVA). */
  priceHTVA: Partial<Record<PriceSite, number>>
  /** Price per site, including VAT (TTC). */
  priceTTC: Partial<Record<PriceSite, number>>
  /** Merchant link, opened externally when the cell is clicked. */
  url?: string
}

export interface User {
  firstname: string
  lastname: string
  mail: string
}

export interface GeneralSettings {
  system_launch_on_startup: boolean
  system_notify_on_finish: boolean
  system_open_on_finish: boolean
  user_mail_send: boolean
}

export interface WebsitesSettings {
  websites_to_watch: Site[]
  websites_cache_duration: CacheDuration
}

export interface Settings {
  general: GeneralSettings
  websites: WebsitesSettings
  language: Lang
}

export interface AppInfo {
  version: string
  platform: string
  arch: string
  electron: string
  chrome: string
  node: string
}

export const EMPTY_PRICE = '—'
