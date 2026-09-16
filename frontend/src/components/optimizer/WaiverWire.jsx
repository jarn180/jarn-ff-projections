import { motion } from 'framer-motion'
import { Search, TrendingUp } from 'lucide-react'
import { useState } from 'react'
import { api } from '../../lib/api.js'
import Badge from '../Badge.jsx'
import Select from '../Select.jsx'
import Spinner from '../Spinner.jsx'
import { EmptyState, ErrorState } from '../StatusMessage.jsx'

const FORMAT_OPTIONS = [
  { value: 'PPR', label: 'PPR' },
  { value: 'HALF_PPR', label: 'Half PPR' },
  { value: 'STANDARD', label: 'Standard' },
]

const POSITION_OPTIONS = [
  { value: 'ALL', label: 'All' },
  { value: 'QB', label: 'QB' },
  { value: 'RB', label: 'RB' },
  { value: 'WR', label: 'WR' },
  { value: 'TE', label: 'TE' },
  { value: 'FLEX', label: 'FLEX' },
  { value: 'K', label: 'K' },
  { value: 'DEF', label: 'DEF' },
]

export default function WaiverWire({ leagueId, defaultFormat = 'PPR' }) {
  const [format, setFormat] = useState(defaultFormat)
  const [position, setPosition] = useState('ALL')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [targets, setTargets] = useState(null)

  async function handleSearch() {
    setLoading(true)
    setError('')
    try {
      const data = await api.getWaiverWire(leagueId, format, position)
      setTargets(data.targets)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="rounded-lg border border-[var(--color-border)] bg-[var(--color-canvas)] p-5"
    >
      <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold text-[var(--color-ink)]">
        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[var(--color-accent-soft)] text-[11px] font-bold text-[var(--color-accent)]">
          4
        </span>
        Waiver wire targets
      </h2>
      <p className="mb-4 text-xs text-[var(--color-ink-faint)]">
        Every player in the league nobody has rostered, sorted by projected points.
      </p>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex flex-col gap-3 sm:flex-row">
          <Select label="Position" value={position} onChange={setPosition} options={POSITION_OPTIONS} className="w-full sm:w-32" />
          <Select label="Scoring format" value={format} onChange={setFormat} options={FORMAT_OPTIONS} className="w-full sm:w-40" />
        </div>
        <button
          type="button"
          onClick={handleSearch}
          disabled={loading}
          className="flex items-center justify-center gap-2 rounded-md bg-[var(--color-accent)] px-4 py-2 text-sm font-medium text-white transition-opacity disabled:opacity-50"
        >
          {loading ? <Spinner size={15} className="text-white" /> : <Search size={15} />}
          {loading ? 'Searching…' : 'Find free agents'}
        </button>
      </div>

      {error && (
        <div className="mt-4">
          <ErrorState message={error} />
        </div>
      )}

      <div className="mt-4">
        {targets === null && !loading && !error && (
          <div className="flex flex-col items-center gap-2 py-8 text-[var(--color-ink-faint)]">
            <TrendingUp size={20} />
            <p className="text-sm">Find the best available free agents in your league.</p>
          </div>
        )}
        {targets && targets.length === 0 && (
          <EmptyState message="No free agents found with a projection this week." />
        )}
        {targets && targets.length > 0 && (
          <ul className="divide-y divide-[var(--color-border)] rounded-lg border border-[var(--color-border)]">
            {targets.map((target, index) => (
              <li key={target.player_id} className="flex items-center gap-3 px-4 py-2.5">
                <span className="w-5 shrink-0 text-xs font-medium text-[var(--color-ink-faint)]">{index + 1}</span>
                <Badge position={target.position} />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-[var(--color-ink)]">{target.name}</p>
                  <p className="truncate text-xs text-[var(--color-ink-faint)]">
                    {target.team || 'FA'}
                    {target.injury_status ? ` · ${target.injury_status}` : ''}
                  </p>
                </div>
                <span className="shrink-0 text-sm font-semibold tabular-nums text-[var(--color-accent)]">
                  {target.projection.toFixed(1)} <span className="text-xs font-normal text-[var(--color-ink-faint)]">pts</span>
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </motion.section>
  )
}
