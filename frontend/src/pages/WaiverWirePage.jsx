import { AnimatePresence, motion } from 'framer-motion'
import ConnectAndLeagueSteps from '../components/optimizer/ConnectAndLeagueSteps.jsx'
import WaiverWire from '../components/optimizer/WaiverWire.jsx'
import PageHeader from '../components/PageHeader.jsx'
import StatPill from '../components/StatPill.jsx'
import { useSleeper } from '../context/SleeperContext.jsx'
import { scoringFormatFor, scoringLabel } from '../lib/position.js'

export default function WaiverWirePage() {
  const { selectedLeague, record } = useSleeper()

  return (
    <div>
      <PageHeader
        title="Waiver Wire"
        subtitle="Find the best available free agents in your Sleeper league"
      />

      <div className="flex flex-col gap-5">
        <ConnectAndLeagueSteps />

        <AnimatePresence>
          {selectedLeague && (
            <motion.section
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="rounded-lg border border-[var(--color-border)] bg-[var(--color-canvas)] p-5"
            >
              <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold text-[var(--color-ink)]">
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[var(--color-accent-soft)] text-[11px] font-bold text-[var(--color-accent)]">
                  3
                </span>
                Find free agents
              </h2>

              <div className="mb-4 flex flex-wrap gap-2">
                <StatPill label="League" value={selectedLeague.name} />
                <StatPill label="Scoring" value={scoringLabel(selectedLeague.scoring_settings?.rec)} />
                {record && <StatPill label="Record" value={record} />}
              </div>

              <WaiverWire
                leagueId={selectedLeague.league_id}
                defaultFormat={scoringFormatFor(selectedLeague.scoring_settings?.rec)}
              />
            </motion.section>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
