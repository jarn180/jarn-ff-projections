import { motion } from 'framer-motion'
import { ChevronRight, Users } from 'lucide-react'
import { scoringLabel } from '../../lib/position.js'
import { EmptyState, LoadingState } from '../StatusMessage.jsx'

export default function LeagueGrid({ leagues, loading, selectedId, onSelect }) {
  return (
    <motion.section
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-lg border border-[var(--color-border)] bg-[var(--color-canvas)] p-5"
    >
      <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold text-[var(--color-ink)]">
        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[var(--color-accent-soft)] text-[11px] font-bold text-[var(--color-accent)]">
          2
        </span>
        Select your league
      </h2>

      {loading ? (
        <LoadingState label="Loading your leagues…" />
      ) : leagues.length === 0 ? (
        <EmptyState message="No leagues found. Check your username and try again." />
      ) : (
        <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
          {leagues.map((league) => {
            const active = league.league_id === selectedId
            return (
              <button
                key={league.league_id}
                type="button"
                onClick={() => onSelect(league)}
                className={[
                  'flex items-center justify-between gap-3 rounded-md border px-4 py-3 text-left transition-colors',
                  active
                    ? 'border-[var(--color-accent)] bg-[var(--color-accent-soft)]'
                    : 'border-[var(--color-border)] hover:border-[var(--color-border-strong)] hover:bg-[var(--color-canvas-soft)]',
                ].join(' ')}
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-[var(--color-ink)]">{league.name}</p>
                  <div className="mt-1 flex flex-wrap items-center gap-1.5 text-xs text-[var(--color-ink-faint)]">
                    <span className="inline-flex items-center gap-1">
                      <Users size={12} />
                      {league.total_rosters} teams
                    </span>
                    <span>·</span>
                    <span>{scoringLabel(league.scoring_settings?.rec)}</span>
                  </div>
                </div>
                <ChevronRight size={16} className="shrink-0 text-[var(--color-ink-faint)]" />
              </button>
            )
          })}
        </div>
      )}
    </motion.section>
  )
}
