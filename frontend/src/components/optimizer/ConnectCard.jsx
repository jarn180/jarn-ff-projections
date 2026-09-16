import { motion } from 'framer-motion'
import { ArrowRight, CheckCircle2 } from 'lucide-react'
import { useState } from 'react'
import Spinner from '../Spinner.jsx'
import { ErrorState } from '../StatusMessage.jsx'

export default function ConnectCard({ user, onConnect, connecting, error }) {
  const [username, setUsername] = useState('')

  function handleSubmit(event) {
    event.preventDefault()
    if (!username.trim() || connecting) return
    onConnect(username.trim())
  }

  return (
    <motion.section
      layout
      className="rounded-lg border border-[var(--color-border)] bg-[var(--color-canvas)] p-5"
    >
      <h2 className="mb-1 flex items-center gap-2 text-sm font-semibold text-[var(--color-ink)]">
        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[var(--color-accent-soft)] text-[11px] font-bold text-[var(--color-accent)]">
          1
        </span>
        Connect your Sleeper account
      </h2>

      <form onSubmit={handleSubmit} className="mt-3 flex flex-col gap-2.5 sm:flex-row">
        <input
          type="text"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          placeholder="Sleeper username"
          className="flex-1 rounded-md border border-[var(--color-border)] bg-[var(--color-canvas)] px-3 py-2 text-sm outline-none transition-colors placeholder:text-[var(--color-ink-faint)] focus:border-[var(--color-accent)]"
        />
        <button
          type="submit"
          disabled={connecting || !username.trim()}
          className="flex shrink-0 items-center justify-center gap-2 rounded-md bg-[var(--color-accent)] px-4 py-2 text-sm font-medium text-white transition-opacity disabled:opacity-50"
        >
          {connecting ? <Spinner size={15} className="text-white" /> : <ArrowRight size={15} />}
          {connecting ? 'Connecting…' : 'Connect'}
        </button>
      </form>

      {user && (
        <p className="mt-3 flex items-center gap-1.5 text-sm text-[var(--color-pos-rb-text)]">
          <CheckCircle2 size={15} />
          Connected as {user.display_name || user.username}
        </p>
      )}
      {error && <div className="mt-3">
        <ErrorState message={error} />
      </div>}
    </motion.section>
  )
}
