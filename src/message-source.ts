/**
 * Message-source declaration for the notices dsh-github-bot injects.
 *
 * The host's `MessageSourceMap` is a merge-extensible sum type with no
 * catch-all `plugin` kind: each producer declares its own `kind` in its own
 * module, and the session-format admission path refuses a durable row whose
 * source is literally `kind: 'plugin'`. The plugin therefore declares
 * `'dsh-github-bot'` here and imports this module for its type side effect
 * wherever it builds a user-visible notice.
 * @module dsh-github-bot/message-source
 */
import type { ContextFormed } from '@deepseek-ai/dsh-llm/message'

declare module '@deepseek-ai/dsh-llm/message' {
  interface MessageSourceMap {
    /** A notice dsh-github-bot queued for the model on a human command's behalf. */
    'dsh-github-bot': { kind: 'dsh-github-bot' } & ContextFormed
  }
}

export {}
