import type { User } from '@shared/domain'
import type { ProfileService } from '../contracts'
import { MOCK_USER } from './fixtures'
import { delay } from './productService'

/** Key used to persist the user profile between two launches. */
export const PROFILE_STORAGE_KEY = 'toolwatcher.profile'

/** Reads the persisted profile (undefined when the user never filled it in). */
export function readStoredProfile(): User | undefined {
  try {
    const raw = globalThis.localStorage?.getItem(PROFILE_STORAGE_KEY)
    if (!raw) return undefined
    const parsed = JSON.parse(raw) as User
    if (!parsed?.mail) return undefined
    return { ...parsed }
  } catch {
    return undefined
  }
}

/** Persists the user profile (best effort). */
export function writeStoredProfile(user: User): void {
  try {
    globalThis.localStorage?.setItem(PROFILE_STORAGE_KEY, JSON.stringify(user))
  } catch {
    /* persistence is optional */
  }
}

export class MockProfileService implements ProfileService {
  /** The stored profile, or the pre-filled default when nothing is stored. */
  private user: User = { ...(readStoredProfile() ?? MOCK_USER) }

  async get(): Promise<User> {
    return delay({ ...this.user })
  }

  async save(user: User): Promise<User> {
    this.user = { ...user }
    writeStoredProfile(this.user)
    return delay({ ...this.user })
  }

  /**
   * True when a profile has actually been filled in (first launch detection).
   */
  async exists(): Promise<boolean> {
    return delay(readStoredProfile() !== undefined)
  }
}
