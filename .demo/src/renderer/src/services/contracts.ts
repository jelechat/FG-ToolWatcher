import type {
  CacheDuration,
  GeneralSettings,
  Lang,
  Product,
  Settings,
  Site,
  User,
} from '@shared/domain'

/** Read access to the (mocked) product catalog. */
export interface ProductService {
  listProducts(): Promise<Product[]>
  search(query: string): Promise<Product[]>
  suggest(query: string): Promise<Product[]>
  byBrand(brand: string): Promise<Product[]>
  byCategory(category: string): Promise<Product[]>
}

/** Read/write access to the user catalog (the "watch list"). */
export interface SearchService {
  getCatalog(): Promise<Product[]>
  addToCatalog(product: Product): Promise<Product[]>
  removeFromCatalog(name: string): Promise<Product[]>
  clearCatalog(): Promise<Product[]>
  suggest(query: string): Promise<string[]>
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

/** Simulated watcher (scraping) progress. */
export interface WatcherService {
  start(): Promise<void>
  stop(): void
  isRunning(): boolean
  progress(): number
  subscribe(listener: (progress: number) => void): () => void
}

/** Simulated mail delivery. Never performs SMTP. */
export interface MailService {
  send(to: string, subject: string, body?: string): Promise<void>
}
