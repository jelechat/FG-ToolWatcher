import type { CacheDuration, PriceSite, Product, Site } from '@shared/domain'

/** Merchants displayed as columns of the comparison table. */
export const PRICE_SITES: readonly PriceSite[] = [
  'Georges',
  'Clabots',
  'Fixami',
  'Klium',
  'Lecot',
  'Toolnation',
]

export const MOCK_BRANDS = [
  'Makita',
  'Bosch',
  'DeWalt',
  'Wiha',
  '3M',
  'Stanley',
  'Festool',
  'Metabo',
] as const

export const MOCK_CATEGORIES = [
  'Drills',
  'Screwdrivers',
  'Workwear',
  'PPE',
  'Measuring',
  'Cutting',
] as const

interface Seed {
  name: string
  mpn: string
  ean: string
  brand: string
  category: string
  base: number
}

const SEEDS: Seed[] = [
  { name: 'Perceuse sans fil Makita DHP458', mpn: 'DHP458Z', ean: '088381559642', brand: 'Makita', category: 'Drills', base: 119 },
  { name: 'Perceuse Bosch GSB 18V-55', mpn: '06019F6000', ean: '3165140932105', brand: 'Bosch', category: 'Drills', base: 109 },
  { name: 'Tournevis DeWalt DCF680D2', mpn: 'DCF680D2', ean: '5030660664922', brand: 'DeWalt', category: 'Screwdrivers', base: 89 },
  { name: 'Vêtement de travail Wiha L', mpn: '-', ean: '-', brand: 'Wiha', category: 'Workwear', base: 45 },
  { name: 'EPI casque anti-bruit 3M', mpn: 'P3E', ean: '-', brand: '3M', category: 'PPE', base: 22 },
  { name: 'Perceuse Makita DHP484', mpn: 'DHP484Z', ean: '088381561410', brand: 'Makita', category: 'Drills', base: 132 },
  { name: 'Perceuse Makita DHP484-S', mpn: 'DHP484SZ', ean: '-', brand: 'Makita', category: 'Drills', base: 149 },
  { name: 'Visseuse Bosch GSR 18V-21', mpn: '06019H0602', ean: '3165140790206', brand: 'Bosch', category: 'Screwdrivers', base: 99 },
  { name: 'Visseuse Bosch GSR 12V-15', mpn: '06019B0805', ean: '3165140866305', brand: 'Bosch', category: 'Screwdrivers', base: 78 },
  { name: 'Perceuse DeWalt DCD778C2', mpn: 'DCD778C2', ean: '5030660666704', brand: 'DeWalt', category: 'Drills', base: 129 },
  { name: 'Perceuse DeWalt DCD776C2', mpn: 'DCD776C2', ean: '-', brand: 'DeWalt', category: 'Drills', base: 115 },
  { name: 'Tournevis DeWalt DWA1234', mpn: 'DWA1234', ean: '-', brand: 'DeWalt', category: 'Screwdrivers', base: 29 },
  { name: 'Veste de travail Wiha Professional', mpn: '-', ean: '-', brand: 'Wiha', category: 'Workwear', base: 54 },
  { name: 'Gants Wiha Profi Grip', mpn: '-', ean: '-', brand: 'Wiha', category: 'PPE', base: 12 },
  { name: 'Lunettes de protection 3M Solus', mpn: 'S200X', ean: '-', brand: '3M', category: 'PPE', base: 18 },
  { name: 'Masque anti-poussière 3M 8710', mpn: '8710', ean: '-', brand: '3M', category: 'PPE', base: 9 },
  { name: 'Mètre Stanley FatMax 5m', mpn: '1-30-686', ean: '4004591556034', brand: 'Stanley', category: 'Measuring', base: 27 },
  { name: 'Niveau Stanley FatMax 600mm', mpn: '0-40-612', ean: '4004591556102', brand: 'Stanley', category: 'Measuring', base: 35 },
  { name: 'Cutaw Stanley FatMax 190mm', mpn: '0-89-911', ean: '4004591586914', brand: 'Stanley', category: 'Cutting', base: 21 },
  { name: 'Perceuse Festool TS 55 FEB', mpn: '577010', ean: '4016519281862', brand: 'Festool', category: 'Drills', base: 219 },
  { name: 'Aspirateur Festool CTL 26', mpn: '587250', ean: '4016519283301', brand: 'Festool', category: 'Drills', base: 289 },
  { name: 'Scie plongeante Festool TS 55', mpn: '576020', ean: '-', brand: 'Festool', category: 'Cutting', base: 245 },
  { name: 'Perceuse Metabo KGS 18V-30', mpn: '600372000', ean: '4007405339581', brand: 'Metabo', category: 'Drills', base: 126 },
  { name: 'Meuleuse Metabo WQ 220', mpn: '600420000', ean: '4007405343384', brand: 'Metabo', category: 'Cutting', base: 119 },
  { name: 'Visseuse Metabo D 18 SL', mpn: '601039000', ean: '-', brand: 'Metabo', category: 'Screwdrivers', base: 93 },
  { name: 'Perceuse Bosch GBH 2-26', mpn: '061191000', ean: '3165140795000', brand: 'Bosch', category: 'Drills', base: 142 },
  { name: 'Marteau perforateur Bosch GBH 5-40', mpn: '061191300', ean: '-', brand: 'Bosch', category: 'Drills', base: 189 },
  { name: 'Perceuse Makita DHP481', mpn: 'DHP481Z', ean: '088381560027', brand: 'Makita', category: 'Drills', base: 105 },
  { name: 'Perceuse Makita DDF484', mpn: 'DDF484Z', ean: '-', brand: 'Makita', category: 'Drills', base: 118 },
  { name: 'Échelle Gorilla Professional 2x4', mpn: '-', ean: '-', brand: '3M', category: 'Workwear', base: 158 },
  { name: 'Couteau Stanley FatMax 99', mpn: '0-10-499', ean: '-', brand: 'Stanley', category: 'Cutting', base: 14 },
  { name: 'Équerre Stanley PowerLock 400', mpn: '0-30-126', ean: '4004591560188', brand: 'Stanley', category: 'Measuring', base: 19 },
  { name: 'Laser de chantier Bosch GLL 3-80', mpn: '0601332200', ean: '3165140735024', brand: 'Bosch', category: 'Measuring', base: 165 },
  { name: 'Gants de protection Wiha Profi', mpn: '-', ean: '-', brand: 'Wiha', category: 'PPE', base: 11 },
  { name: 'Veste de travail DeWalt DWR', mpn: '-', ean: '-', brand: 'DeWalt', category: 'Workwear', base: 62 },
  { name: 'Casque de chantier DeWalt', mpn: '-', ean: '-', brand: 'DeWalt', category: 'PPE', base: 24 },
  { name: 'Scie à bois Bosch GKS 190', mpn: '0603513100', ean: '3165140667027', brand: 'Bosch', category: 'Cutting', base: 112 },
]

const VAT_RATE = 0.21

function round2(value: number): number {
  return Math.round(value * 100) / 100
}

/**
 * Deterministic fixture builder.
 * The number of merchants offering a product decreases with the index so that
 * the "—" (missing offer) rendering path is exercised.
 */
export const MOCK_PRODUCTS: Product[] = SEEDS.map((seed, index) => {
  const offerCount = 6 - (index % 5)
  const rotation = index % PRICE_SITES.length
  const orderedSites = [...PRICE_SITES.slice(rotation), ...PRICE_SITES.slice(0, rotation)]

  const priceHTVA: Partial<Record<PriceSite, number>> = {}
  const priceTTC: Partial<Record<PriceSite, number>> = {}

  orderedSites.slice(0, offerCount).forEach((site, slot) => {
    const price = round2(seed.base + slot * 2.5 + (index % 7))
    priceHTVA[site] = price
    priceTTC[site] = round2(price * (1 + VAT_RATE))
  })

  return {
    name: seed.name,
    mpn: seed.mpn === '-' ? '-' : seed.mpn,
    ean: seed.ean === '-' ? '-' : seed.ean,
    brand: seed.brand,
    category: seed.category,
    priceHTVA,
    priceTTC,
    url: `https://example.com/${encodeURIComponent(seed.name.toLowerCase().replace(/[^a-z0-9]+/g, '-'))}`,
  }
})

/** Default catalog content (2 articles, as in the original GUI). */
export const MOCK_CATALOG: Product[] = [MOCK_PRODUCTS[0], MOCK_PRODUCTS[1]]

export const MOCK_USER = {
  firstname: 'Jérôme',
  lastname: 'LECHAT',
  mail: 'jerome@example.com',
}

export const MOCK_SETTINGS = {
  general: {
    system_launch_on_startup: false,
    system_notify_on_finish: true,
    system_open_on_finish: false,
    user_mail_send: false,
  },
  websites: {
    websites_to_watch: ['FIXAMI', 'KLIUM', 'LECOT', 'TOOLNATION'] as Site[],
    websites_cache_duration: 3 as CacheDuration,
  },
  language: 'FR' as const,
}
