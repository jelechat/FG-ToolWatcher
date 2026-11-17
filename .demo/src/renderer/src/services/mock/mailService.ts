import type { MailService } from '../contracts'
import { AppError } from '../errors'
import { delay } from './productService'

/**
 * Simulated mail delivery. No SMTP connection is ever opened: the message is
 * only logged, exactly like the TODO in the original PySide6 GUI.
 */
export class MockMailService implements MailService {
  readonly sent: Array<{ to: string; subject: string; body: string }> = []

  async send(to: string, subject: string, body = ''): Promise<void> {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(to)) {
      throw new AppError('invalid-recipient', `"${to}" is not a valid e-mail address.`)
    }
    await delay(undefined)
    this.sent.push({ to, subject, body })
    console.info('[mock-mail] message sent (mock):', { to, subject })
  }
}
