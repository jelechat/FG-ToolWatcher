/** Error raised by the service layer. */
export class AppError extends Error {
  readonly code: string
  readonly cause?: unknown

  constructor(code: string, message: string, cause?: unknown) {
    super(message)
    this.name = 'AppError'
    this.code = code
    this.cause = cause
  }
}

/** Normalizes any thrown value into an AppError. */
export function toAppError(error: unknown, fallbackCode = 'unknown'): AppError {
  if (error instanceof AppError) return error
  if (error instanceof Error) return new AppError(fallbackCode, error.message, error)
  return new AppError(fallbackCode, String(error), error)
}

/** True when the error is an AppError with the given code. */
export function hasCode(error: unknown, code: string): boolean {
  return error instanceof AppError && error.code === code
}
