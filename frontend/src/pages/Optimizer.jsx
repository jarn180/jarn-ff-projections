import { AnimatePresence, motion } from 'framer-motion'
import { Search, Wand2 } from 'lucide-react'
import { useState } from 'react'
import ConnectCard from '../components/optimizer/ConnectCard.jsx'
import LeagueGrid from '../components/optimizer/LeagueGrid.jsx'
import LineupResults from '../components/optimizer/LineupResults.jsx'
import WaiverWire from '../components/optimizer/WaiverWire.jsx'
import PageHeader from '../components/PageHeader.jsx'
import Select from '../components/Select.jsx'
import Spinner from '../components/Spinner.jsx'
import StatPill from '../components/StatPill.jsx'
import { ErrorState } from '../components/StatusMessage.jsx'
import { api } from '../lib/api.js'
import { scoringLabel } from '../lib/position.js'

const FORMAT_OPTIONS = [
  { value: 'PPR', label: 'PPR' },
  { value: 'HALF_PPR', label: 'Half PPR' },
  { value: 'STANDARD', label: 'Standard' },
]

const SEASONS = ['2026', '2025']

export default function Optimizer() {
  const [user, setUser] = useState(null)
  const [connecting, setConnecting] = useState(false)
  const [connectError, setConnectError] = useState('')

  const [leagues, setLeagues] = useState(null)
  const [loadingLeagues, setLoadingLeagues] = useState(false)
  const [selectedLeague, setSelectedLeague] = useState(null)

  const [scoringFormat, setScoringFormat] = useState('PPR')
  const [record, setRecord] = useState('')
  const [optimizing, setOptimizing] = useState(false)
  const [optimizeError, setOptimizeError] = useState('')
  const [optimization, setOptimization] = useState(null)

  async function handleConnect(username) {
    setConnecting(true)
    setConnectError('')
    setLeagues(null)
    setSelectedLeague(null)
    setOptimization(null)
    try {
      const data = await api.getSleeperUser(username)
      setUser(data.user)
      setLoadingLeagues(true)
      let found = []
      for (const season of SEASONS) {
        const leaguesData = await api.getSleeperLeagues(data.user.user_id, season)
        if (leaguesData.leagues.length > 0) {
          found = leaguesData.leagues
          break
        }
      }
      setLeagues(found)
    } catch (error) {
      setConnectError(error.message)
      setUser(null)
    } finally {
      setConnecting(false)
      setLoadingLeagues(false)
    }
  }

  function handleSelectLeague(league) {
    setSelectedLeague(league)
    setOptimization(null)
    setOptimizeError('')
    setRecord('')
    const rec = parseFloat(league.scoring_settings?.rec || 0)
    setScoringFormat(rec === 1 ? 'PPR' : rec === 0.5 ? 'HALF_PPR' : 'STANDARD')

    api
      .getSleeperRoster(league.league_id, user.user_id)
      .then((data) => {
        const { wins = 0, losses = 0, ties = 0 } = data.roster.settings || {}
        setRecord(`${wins}-${losses}${ties > 0 ? `-${ties}` : ''}`)
      })
      .catch(() => setRecord(''))
  }

  async function handleOptimize() {
    if (!selectedLeague || !user) return
    setOptimizing(true)
    setOptimizeError('')
    try {
      const data = await api.optimizeLineup(selectedLeague.league_id, user.user_id, scoringFormat)
      setOptimization(data.optimization)
    } catch (error) {
      setOptimizeError(error.message)
    } finally {
      setOptimizing(false)
    }
  }

  return (
    <div>
      <PageHeader
        title="Start/Sit Optimizer"
        subtitle="Connect your Sleeper league and get the optimal lineup for the week"
      />

      <div className="flex flex-col gap-5">
        <ConnectCard user={user} onConnect={handleConnect} connecting={connecting} error={connectError} />

        <AnimatePresence>
          {leagues && (
            <LeagueGrid
              leagues={leagues}
              loading={loadingLeagues}
              selectedId={selectedLeague?.league_id}
              onSelect={handleSelectLeague}
            />
          )}
        </AnimatePresence>

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
                Optimize your lineup
              </h2>

              <div className="mb-4 flex flex-wrap gap-2">
                <StatPill label="League" value={selectedLeague.name} />
                <StatPill label="Scoring" value={scoringLabel(selectedLeague.scoring_settings?.rec)} />
                {record && <StatPill label="Record" value={record} />}
              </div>

              <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                <Select
                  label="Scoring format"
                  value={scoringFormat}
                  onChange={setScoringFormat}
                  options={FORMAT_OPTIONS}
                  className="w-full sm:w-40"
                />
                <button
                  type="button"
                  onClick={handleOptimize}
                  disabled={optimizing}
                  className="flex items-center justify-center gap-2 rounded-md bg-[var(--color-accent)] px-4 py-2 text-sm font-medium text-white transition-opacity disabled:opacity-50"
                >
                  {optimizing ? <Spinner size={15} className="text-white" /> : <Wand2 size={15} />}
                  {optimizing ? 'Optimizing…' : 'Optimize lineup'}
                </button>
              </div>

              {optimizeError && (
                <div className="mt-4">
                  <ErrorState message={optimizeError} />
                </div>
              )}

              <div className="mt-5">
                {optimization ? (
                  <LineupResults optimization={optimization} />
                ) : (
                  !optimizing && (
                    <div className="flex flex-col items-center gap-2 py-10 text-[var(--color-ink-faint)]">
                      <Search size={20} />
                      <p className="text-sm">Run the optimizer to see your best lineup.</p>
                    </div>
                  )
                )}
              </div>
            </motion.section>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {selectedLeague && <WaiverWire leagueId={selectedLeague.league_id} defaultFormat={scoringFormat} />}
        </AnimatePresence>
      </div>
    </div>
  )
}
