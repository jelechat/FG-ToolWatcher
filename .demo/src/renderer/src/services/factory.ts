import type {
  MailService,
  ProductService,
  ProfileService,
  SearchService,
  SettingsService,
  WatcherService,
} from './contracts'
import { MockMailService } from './mock/mailService'
import { MockProductService } from './mock/productService'
import { MockProfileService } from './mock/profileService'
import { MockSearchService } from './mock/searchService'
import { MockSettingsService } from './mock/settingsService'
import { MockWatcherService } from './mock/watcherService'

export interface Services {
  product: ProductService
  search: SearchService
  settings: SettingsService
  profile: ProfileService
  watcher: WatcherService
  mail: MailService
}

/**
 * Creates the service container. Only mock implementations exist for now: the
 * factory is the single place to swap in a real backend later on.
 */
export function createServices(): Services {
  return {
    product: new MockProductService(),
    search: new MockSearchService(),
    settings: new MockSettingsService(),
    profile: new MockProfileService(),
    watcher: new MockWatcherService(),
    mail: new MockMailService(),
  }
}

let instance: Services | undefined

/** Lazily created singleton service container. */
export function getServices(): Services {
  if (!instance) instance = createServices()
  return instance
}

/** Replaces the singleton (used by tests). */
export function setServices(services: Services): void {
  instance = services
}
