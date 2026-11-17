import type {
  CacheDuration,
  GeneralSettings,
  Lang,
  Product,
  Settings,
  Site,
  User,
} from '@shared/domain'

/** Read access to the product catalog, independent of its data source. */
export interface ProductService {
  listProducts(): Promise<Product[]>
  listBrands(): Promise<string[]>
  listCategories(): Promise<string[]>
  search(query: string): Promise<Product[]>
  suggest(query: string): Promise<Product[]>
  byBrand(brand: string): Promise<Product[]>
  byCategory(category: string): Promise<Product[]>
}

/** Read/write access to the user's selected products (the watch list). */
export interface SearchService {
  getCatalog(): Promise<Product[]>
  addToCatalog(product: Product): Promise<Product[]>
  removeFromCatalog(name: string): Promise<Product[]>
  clearCatalog(): Promise<Product[]>
}

/** Read/write access to the application settings. */
export interface SettingsService {
  get(): Promise<Settings>
  save(settings: Settings): Promise<Settings>
  updateGeneral(general: GeneralSettings): Promise<Settings>
  updateWebsites(websites: {
    websites_to_watch: Site[]
    websites_cache_duration: CacheDuration
  }): Promise<Settings>
  setLanguage(language: Lang): Promise<Settings>
  reset(): Promise<Settings>
}

/** Read/write access to the user profile. */
export interface ProfileService {
  get(): Promise<User>
  save(user: User): Promise<User>
  /** True when a profile has already been filled in (first launch detection). */
  exists(): Promise<boolean>
}

/** Starts and observes a catalog refresh, regardless of its implementation. */
export interface WatcherService {
  start(): Promise<void>
  stop(): void
  isRunning(): boolean
  progress(): number
  subscribe(listener: (progress: number) => void): () => void
}

/** Sends a report through the configured mail implementation. */
export interface MailService {
  send(to: string, subject: string, body?: string): Promise<void>
}
