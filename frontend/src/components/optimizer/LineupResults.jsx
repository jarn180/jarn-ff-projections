import { motion } from 'framer-motion'
import { ArrowLeftRight, CircleSlash, PartyPopper, Sparkles } from 'lucide-react'
import Badge from '../Badge.jsx'
import StatPill from '../StatPill.jsx'

const SLOT_LABELS = {
  FLEX: 'Flex (RB/WR/TE)',
  SUPER_FLEX: 'Superflex (QB/RB/WR/TE)',
  DEF: 'Defense / Special Teams',
}

function slotLabel(position) {
  return SLOT_LABELS[position] || position
}

function PlayerRow({ name, position, projection, injuryStatus, noLines, showPosition }) {
  const hasNoLine = noLines || projection <= 0

  return (
    <div className="flex items-center justify-between gap-3 rounded-md px-3 py-2 hover:bg-[var(--color-canvas-soft)]">
      <div className="flex min-w-0 items-center gap-2">
        {showPosition && <Badge position={position} />}
        <span className="truncate text-sm font-medium text-[var(--color-ink)]">{name}</span>
        {injuryStatus && (
          <span className="shrink-0 rounded bg-[var(--color-pos-qb-bg)] px-1.5 py-0.5 text-[10px] font-semibold text-[var(--color-pos-qb-text)]">
            {injuryStatus}
          </span>
        )}
      </div>
      {hasNoLine ? (
        <span className="flex shrink-0 items-center gap-1 rounded bg-[var(--color-border)] px-1.5 py-0.5 text-[11px] font-medium text-[var(--color-ink-faint)]">
          <CircleSlash size={11} />
          No line yet
        </span>
      ) : (
        <span className="shrink-0 text-sm font-semibold tabular-nums text-[var(--color-ink)]">
          {projection.toFixed(1)} <span className="text-xs font-normal text-[var(--color-ink-faint)]">pts</span>
        </span>
      )}
    </div>
  )
}

function RecommendationCard({ rec, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      className="rounded-md border border-[var(--color-border)] bg-[var(--color-canvas)] p-3"
    >
      <div className="mb-2 flex items-center justify-between">
        <Badge position={rec.position === 'SUPER_FLEX' ? 'FLEX' : rec.position} />
        <span className="text-xs font-semibold text-[var(--color-pos-rb-text)]">+{rec.projected_gain} pts</span>
      </div>
      <div className="flex items-center gap-2 text-sm">
        <div className="min-w-0 flex-1">
          <p className="text-[10px] font-semibold uppercase tracking-wide text-[var(--color-pos-rb-text)]">Start</p>
          <p className="truncate font-medium">{rec.bench_player}</p>
          <p className="text-xs text-[var(--color-ink-faint)]">{rec.bench_projection.toFixed(1)} pts</p>
        </div>
        <ArrowLeftRight size={16} className="shrink-0 text-[var(--color-ink-faint)]" />
        <div className="min-w-0 flex-1 text-right">
          <p className="text-[10px] font-semibold uppercase tracking-wide text-[var(--color-ink-faint)]">Sit</p>
          <p className="truncate font-medium text-[var(--color-ink-soft)]">{rec.starter_player}</p>
          <p className="text-xs text-[var(--color-ink-faint)]">{rec.starter_projection.toFixed(1)} pts</p>
        </div>
      </div>
    </motion.div>
  )
}

export default function LineupResults({ optimization }) {
  const starterGroups = Object.entries(optimization.starters).filter(([, players]) => players.length > 0)

  return (
    <motion.section
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col gap-5"
    >
      <div className="flex flex-wrap gap-2">
        <StatPill label="Projected points" value={optimization.total_projection} />
        <StatPill label="Week" value={optimization.current_week || 'TBD'} />
        <StatPill label="Format" value={optimization.scoring_format} />
      </div>

      {optimization.recommendations.length > 0 ? (
        <div>
          <h3 className="mb-1 flex items-center gap-1.5 text-sm font-semibold text-[var(--color-ink)]">
            <Sparkles size={15} className="text-[var(--color-accent)]" />
            Start/Sit recommendations
          </h3>
          <p className="mb-2.5 text-xs text-[var(--color-ink-faint)]">
            These bench players are projected to outscore who's currently starting at that spot.
          </p>
          <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
            {optimization.recommendations.map((rec, index) => (
              <RecommendationCard key={`${rec.bench_player}-${rec.starter_player}`} rec={rec} index={index} />
            ))}
          </div>
        </div>
      ) : (
        <div className="flex items-center gap-2 rounded-md border border-[var(--color-border)] bg-[var(--color-canvas-soft)] px-4 py-3 text-sm text-[var(--color-ink-soft)]">
          <PartyPopper size={16} className="text-[var(--color-accent)]" />
          Your lineup is optimal — no changes recommended.
        </div>
      )}

      <div>
        <h3 className="mb-1.5 text-sm font-semibold text-[var(--color-ink)]">Starting lineup</h3>
        <div className="divide-y divide-[var(--color-border)] rounded-lg border border-[var(--color-border)]">
          {starterGroups.map(([position, players]) => (
            <div key={position} className="px-2 py-1.5">
              <p className="px-1 py-1 text-[11px] font-semibold uppercase tracking-wide text-[var(--color-ink-faint)]">
                {slotLabel(position)}
              </p>
              {players.map((player) => (
                <PlayerRow key={player.player_id} {...player} showPosition={position === 'FLEX' || position === 'SUPER_FLEX'} />
              ))}
            </div>
          ))}
        </div>
      </div>

      {optimization.bench.length > 0 && (
        <div>
          <h3 className="mb-1.5 text-sm font-semibold text-[var(--color-ink-soft)]">Bench</h3>
          <div className="rounded-lg border border-[var(--color-border)] px-2 py-1.5">
            {optimization.bench.map((player) => (
              <PlayerRow key={player.player_id} {...player} showPosition />
            ))}
          </div>
        </div>
      )}
    </motion.section>
  )
}
