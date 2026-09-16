import { AlertTriangle, Inbox } from 'lucide-react'
import Spinner from './Spinner.jsx'

export function LoadingState({ label = 'Loading…' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-[var(--color-border)] py-16 text-[var(--color-ink-faint)]">
      <Spinner size={22} />
      <p className="text-sm">{label}</p>
    </div>
  )
}

export function ErrorState({ message }) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-[var(--color-pos-qb-text)]/25 bg-[var(--color-pos-qb-bg)] px-4 py-3 text-sm text-[var(--color-pos-qb-text)]">
      <AlertTriangle size={16} className="mt-0.5 shrink-0" />
      <p>{message}</p>
    </div>
  )
}

export function EmptyState({ message }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-[var(--color-border)] py-16 text-[var(--color-ink-faint)]">
      <Inbox size={22} />
      <p className="text-sm">{message}</p>
    </div>
  )
}
