import { AnimatePresence, motion } from 'framer-motion'
import { X } from 'lucide-react'
import { formatMatchup } from '../lib/matchup.js'
import Badge from './Badge.jsx'

const FORMAT_LABELS = {
  PPR: 'PPR',
  HALF_PPR: 'Half PPR',
  STANDARD: 'Standard',
}

export default function PlayerModal({ player, projections, onClose }) {
  const open = Boolean(player)
  const entries = open ? projections.filter((p) => p.player === player) : []
  const meta = entries[0]

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-0 sm:items-center sm:p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-t-2xl bg-[var(--color-canvas)] shadow-[var(--shadow-notion-lg)] sm:rounded-2xl"
            initial={{ y: 40, opacity: 0, scale: 0.98 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: 20, opacity: 0, scale: 0.98 }}
            transition={{ type: 'spring', stiffness: 380, damping: 32 }}
            onClick={(event) => event.stopPropagation()}
          >
            <div className="sticky top-0 flex items-center justify-between border-b border-[var(--color-border)] bg-[var(--color-canvas)] px-5 py-4">
              <div className="flex items-center gap-2.5">
                {meta && <Badge position={meta.position} />}
                <div>
                  <h2 className="text-base font-semibold">{player}</h2>
                  {meta && (
                    <p className="text-xs text-[var(--color-ink-faint)]">
                      {meta.week || 'TBD'} ·{' '}
                      {formatMatchup({
                        awayTeam: meta.away_team,
                        homeTeam: meta.home_team,
                        awayTotal: meta.away_implied_total,
                        homeTotal: meta.home_implied_total,
                      })}
                    </p>
                  )}
                </div>
              </div>
              <button
                type="button"
                onClick={onClose}
                aria-label="Close"
                className="rounded-md p-1.5 text-[var(--color-ink-faint)] hover:bg-[var(--color-border)] hover:text-[var(--color-ink)]"
              >
                <X size={18} />
              </button>
            </div>

            <div className="divide-y divide-[var(--color-border)] px-5">
              {entries.map((proj) => (
                <div key={proj.format} className="py-4">
                  <div className="flex items-baseline justify-between">
                    <h3 className="text-sm font-semibold text-[var(--color-ink-soft)]">
                      {FORMAT_LABELS[proj.format] || proj.format}
                    </h3>
                    <p className="text-2xl font-bold text-[var(--color-accent)]">
                      {proj.total_points.toFixed(2)}
                      <span className="ml-1 text-xs font-medium text-[var(--color-ink-faint)]">pts</span>
                    </p>
                  </div>

                  <div className="mt-3 grid grid-cols-3 gap-2">
                    {Object.entries(proj.breakdown)
                      .filter(([, value]) => value !== 0)
                      .map(([key, value]) => (
                        <div
                          key={key}
                          className="rounded-md bg-[var(--color-canvas-soft)] px-2.5 py-2 text-center"
                        >
                          <p className="text-[10px] uppercase tracking-wide text-[var(--color-ink-faint)]">{key}</p>
                          <p className="text-sm font-semibold">{value.toFixed(2)}</p>
                        </div>
                      ))}
                  </div>

                  {Object.keys(proj.stats).length > 0 && (
                    <div className="mt-3">
                      <p className="mb-1.5 text-[11px] font-medium uppercase tracking-wide text-[var(--color-ink-faint)]">
                        Projected stats
                      </p>
                      <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 sm:grid-cols-3">
                        {Object.entries(proj.stats).map(([stat, value]) => (
                          <div key={stat} className="flex items-center justify-between text-xs">
                            <span className="capitalize text-[var(--color-ink-faint)]">
                              {stat.replace('player_', '').replaceAll('_', ' ')}
                            </span>
                            <span className="font-medium text-[var(--color-ink)]">{value.toFixed(2)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
            <div className="h-4" />
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
