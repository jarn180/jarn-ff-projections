import { motion } from 'framer-motion'
import { Clock, Users } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import PlayerModal from '../components/PlayerModal.jsx'
import ProjectionsTable from '../components/ProjectionsTable.jsx'
import SearchInput from '../components/SearchInput.jsx'
import SegmentedTabs from '../components/SegmentedTabs.jsx'
import Select from '../components/Select.jsx'
import StatPill from '../components/StatPill.jsx'
import { EmptyState, ErrorState, LoadingState } from '../components/StatusMessage.jsx'
import { api } from '../lib/api.js'

const FORMAT_OPTIONS = [
  { value: 'ALL', label: 'All Formats' },
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
]

export default function Projections() {
  const [state, setState] = useState({ status: 'loading', projections: [], totalPlayers: 0, lastUpdated: '' })
  const [format, setFormat] = useState('PPR')
  const [position, setPosition] = useState('ALL')
  const [search, setSearch] = useState('')
  const [selectedPlayer, setSelectedPlayer] = useState(null)

  useEffect(() => {
    let cancelled = false
    api
      .getProjections()
      .then((data) => {
        if (cancelled) return
        setState({
          status: 'ready',
          projections: data.projections,
          totalPlayers: data.total_players,
          lastUpdated: data.last_updated,
        })
      })
      .catch((error) => {
        if (cancelled) return
        setState((prev) => ({ ...prev, status: 'error', error: error.message }))
      })
    return () => {
      cancelled = true
    }
  }, [])

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase()
    return state.projections.filter((proj) => {
      const matchesSearch = !term || proj.player.toLowerCase().includes(term)
      const matchesFormat = format === 'ALL' || proj.format === format
      const matchesPosition =
        position === 'ALL' ||
        (position === 'FLEX' ? ['RB', 'WR', 'TE'].includes(proj.position) : proj.position === position)
      return matchesSearch && matchesFormat && matchesPosition
    })
  }, [state.projections, search, format, position])

  const rows = useMemo(() => {
    if (format === 'ALL') {
      const byPlayer = new Map()
      filtered.forEach((proj) => {
        if (!byPlayer.has(proj.player)) {
          byPlayer.set(proj.player, {
            player: proj.player,
            position: proj.position,
            week: proj.week,
            matchup: proj.matchup,
          })
        }
        const entry = byPlayer.get(proj.player)
        if (proj.format === 'PPR') entry.ppr = proj.total_points
        if (proj.format === 'HALF_PPR') entry.halfPpr = proj.total_points
        if (proj.format === 'STANDARD') entry.standard = proj.total_points
      })
      return [...byPlayer.values()].sort((a, b) => (b.ppr || 0) - (a.ppr || 0))
    }

    return filtered
      .map((proj) => ({
        player: proj.player,
        position: proj.position,
        week: proj.week,
        matchup: proj.matchup,
        total: proj.total_points,
        passing: proj.breakdown.passing,
        rushing: proj.breakdown.rushing,
        receiving: proj.breakdown.receiving,
      }))
      .sort((a, b) => b.total - a.total)
  }, [filtered, format])

  return (
    <div>
      <PageHeader
        title="Fantasy Football Projections"
        subtitle="Vegas props-based projections for NFL players"
      />

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25, delay: 0.05 }}
        className="mb-5 flex flex-col gap-4"
      >
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div className="flex flex-col gap-3 sm:flex-row">
            <Select label="Scoring format" value={format} onChange={setFormat} options={FORMAT_OPTIONS} className="w-full sm:w-40" />
            <SearchInput
              value={search}
              onChange={setSearch}
              placeholder="Search player…"
              className="w-full sm:w-64"
            />
          </div>

          {state.status === 'ready' && (
            <div className="flex flex-wrap gap-2">
              <StatPill icon={Users} label="Players" value={state.totalPlayers} />
              <StatPill icon={Clock} label="Updated" value={state.lastUpdated || 'Unknown'} />
            </div>
          )}
        </div>

        <SegmentedTabs
          layoutId="position-tab"
          options={POSITION_OPTIONS}
          value={position}
          onChange={setPosition}
        />
      </motion.div>

      {state.status === 'loading' && <LoadingState label="Fetching projections…" />}
      {state.status === 'error' && <ErrorState message={state.error} />}
      {state.status === 'ready' &&
        (rows.length === 0 ? (
          <EmptyState message="No players found matching your criteria." />
        ) : (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.25 }}>
            <ProjectionsTable rows={rows} mode={format} onSelectPlayer={setSelectedPlayer} />
          </motion.div>
        ))}

      <PlayerModal
        player={selectedPlayer}
        projections={state.projections}
        onClose={() => setSelectedPlayer(null)}
      />
    </div>
  )
}
