import { beforeEach, describe, expect, it } from 'vitest'
import {
  MockMailService,
  MockProductService,
  MockProfileService,
  MockSearchService,
  MockSettingsService,
  MockWatcherService,
  setMockLatency,
} from '../../src/renderer/src/services'
import {
  clearStoredSettings,
  SETTINGS_STORAGE_KEY,
} from '../../src/renderer/src/services/mock/settingsService'
import { PROFILE_STORAGE_KEY } from '../../src/renderer/src/services/mock/profileService'

describe('mock services', () => {
  beforeEach(() => {
    setMockLatency(0)
    globalThis.localStorage?.clear()
  })

  it('lists between 30 and 40 deterministic products', async () => {
    const products = await new MockProductService().listProducts()
    expect(products.length).toBeGreaterThanOrEqual(30)
    expect(products.length).toBeLessThanOrEqual(40)

    const again = await new MockProductService().listProducts()
    expect(again).toEqual(products)
  })

  it('exposes 6 merchant columns and some missing offers', async () => {
    const products = await new MockProductService().listProducts()
    expect(products.some((product) => Object.keys(product.priceHTVA).length < 6)).toBe(true)
    expect(products.every((product) => Object.keys(product.priceTTC).length === Object.keys(product.priceHTVA).length)).toBe(true)
  })

  it('filters products by name, brand, mpn and ean', async () => {
    const service = new MockProductService()
    expect((await service.search('makita')).length).toBeGreaterThan(0)
    expect((await service.search('DHP458')).length).toBeGreaterThan(0)
    expect((await service.search('088381559642')).length).toBeGreaterThan(0)
    expect((await service.search('nothing-at-all')).length).toBe(0)
  })

  it('only suggests products when the query is at least 3 characters long', async () => {
    const service = new MockProductService()
    expect(await service.suggest('ma')).toEqual([])
    expect((await service.suggest('mak')).length).toBeGreaterThan(0)
  })

  it('adds, removes and clears catalog items', async () => {
    const service = new MockSearchService()
    const products = await new MockProductService().listProducts()

    const initial = await service.getCatalog()
    expect(initial.length).toBe(2)

    await service.addToCatalog(products[2])
    expect((await service.getCatalog()).length).toBe(3)

    await expect(service.addToCatalog(products[2])).rejects.toThrow(/already in the catalog/)

    await service.removeFromCatalog(products[2].name)
    expect((await service.getCatalog()).length).toBe(2)

    await service.clearCatalog()
    expect((await service.getCatalog()).length).toBe(0)
  })

  it('persists the settings', async () => {
    const service = new MockSettingsService()
    const settings = await service.get()
    expect(settings.websites.websites_cache_duration).toBe(3)

    const updated = await service.updateWebsites({
      websites_to_watch: ['FIXAMI'],
      websites_cache_duration: 7,
    })
    expect(updated.websites.websites_cache_duration).toBe(7)
    expect(updated.websites.websites_to_watch).toEqual(['FIXAMI'])

    // A new service instance reads the persisted settings back.
    const reloaded = await new MockSettingsService().get()
    expect(reloaded.websites.websites_cache_duration).toBe(7)

    const reset = await service.reset()
    expect(reset.websites.websites_cache_duration).toBe(3)
    expect(globalThis.localStorage.getItem(SETTINGS_STORAGE_KEY)).toBeTruthy()
  })

  it('keeps the language as a single source of truth', async () => {
    const service = new MockSettingsService()
    await service.setLanguage('EN')

    expect(globalThis.localStorage.getItem('toolwatcher.lang')).toBe('EN')

    const reloaded = await new MockSettingsService().get()
    expect(reloaded.language).toBe('EN')

    clearStoredSettings()
  })

  it('saves the user profile and detects the first launch', async () => {
    const service = new MockProfileService()
    const user = await service.get()
    expect(user.mail).toContain('@')

    // No profile has been saved yet: first launch.
    expect(await service.exists()).toBe(false)

    const saved = await service.save({ ...user, firstname: 'Alex' })
    expect(saved.firstname).toBe('Alex')

    // The profile is now persisted: the profile exists.
    expect(await new MockProfileService().exists()).toBe(true)
    expect(globalThis.localStorage.getItem(PROFILE_STORAGE_KEY)).toBeTruthy()
  })

  it('simulates the watcher progress', async () => {
    const service = new MockWatcherService()
    const progress: number[] = []
    service.subscribe((value) => progress.push(value))

    const run = service.start()
    expect(service.isRunning()).toBe(true)
    service.stop()
    await run

    expect(service.isRunning()).toBe(false)
    expect(progress.length).toBeGreaterThan(0)
  })

  it('resolves the watcher run when the progress reaches 100%', async () => {
    const service = new MockWatcherService()
    const run = service.start()
    await run
    expect(service.progress()).toBe(100)
    expect(service.isRunning()).toBe(false)
  })

  it('never performs SMTP but records the message', async () => {
    const service = new MockMailService()
    await service.send('jerome@example.com', 'Results')
    expect(service.sent).toHaveLength(1)
    expect(service.sent[0].to).toBe('jerome@example.com')

    await expect(service.send('not-an-email', 'Results')).rejects.toThrow()
  })
})
