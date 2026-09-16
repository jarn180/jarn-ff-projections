import { ChevronRight } from 'lucide-react'
import { formatMatchup } from '../lib/matchup.js'
import Badge from './Badge.jsx'

function RankBadge({ rank }) {
  return <span className="w-6 shrink-0 text-xs font-medium text-[var(--color-ink-faint)]">{rank}</span>
}

export default function ProjectionsTable({ rows, mode, onSelectPlayer }) {
  return (
    <div className="overflow-hidden rounded-lg border border-[var(--color-border)]">
      {/* Desktop table */}
      <table className="hidden w-full text-sm md:table">
        <thead>
          <tr className="border-b border-[var(--color-border)] bg-[var(--color-canvas-soft)] text-left text-xs font-medium uppercase tracking-wide text-[var(--color-ink-faint)]">
            <th className="w-10 px-4 py-2.5"></th>
            <th className="px-2 py-2.5">Pos</th>
            <th className="px-2 py-2.5">Player</th>
            <th className="px-2 py-2.5">Week</th>
            <th className="px-2 py-2.5">Matchup</th>
            {mode === 'ALL' ? (
              <>
                <th className="px-2 py-2.5 text-right">PPR</th>
                <th className="px-2 py-2.5 text-right">Half PPR</th>
                <th className="px-2 py-2.5 text-right">Standard</th>
              </>
            ) : (
              <>
                <th className="px-2 py-2.5 text-right">Total</th>
                <th className="px-2 py-2.5 text-right">Pass</th>
                <th className="px-2 py-2.5 text-right">Rush</th>
                <th className="px-2 py-2.5 text-right">Rec</th>
              </>
            )}
            <th className="w-8 px-4 py-2.5"></th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr
              key={row.player}
              onClick={() => onSelectPlayer(row.player)}
              className="cursor-pointer border-b border-[var(--color-border)] last:border-0 hover:bg-[var(--color-canvas-soft)]"
            >
              <td className="px-4 py-2.5">
                <RankBadge rank={index + 1} />
              </td>
              <td className="px-2 py-2.5">
                <Badge position={row.position} />
              </td>
              <td className="px-2 py-2.5 font-medium text-[var(--color-ink)]">{row.player}</td>
              <td className="px-2 py-2.5 text-[var(--color-ink-soft)]">{row.week || 'TBD'}</td>
              <td className="px-2 py-2.5 text-xs text-[var(--color-ink-faint)]">
                {formatMatchup({
                  awayTeam: row.awayTeam,
                  homeTeam: row.homeTeam,
                  awayTotal: row.awayTotal,
                  homeTotal: row.homeTotal,
                })}
              </td>
              {mode === 'ALL' ? (
                <>
                  <td className="px-2 py-2.5 text-right font-semibold tabular-nums">{fmt(row.ppr)}</td>
                  <td className="px-2 py-2.5 text-right tabular-nums text-[var(--color-ink-soft)]">{fmt(row.halfPpr)}</td>
                  <td className="px-2 py-2.5 text-right tabular-nums text-[var(--color-ink-soft)]">{fmt(row.standard)}</td>
                </>
              ) : (
                <>
                  <td className="px-2 py-2.5 text-right font-semibold tabular-nums text-[var(--color-accent)]">
                    {fmt(row.total)}
                  </td>
                  <td className="px-2 py-2.5 text-right tabular-nums text-[var(--color-ink-soft)]">{fmt1(row.passing)}</td>
                  <td className="px-2 py-2.5 text-right tabular-nums text-[var(--color-ink-soft)]">{fmt1(row.rushing)}</td>
                  <td className="px-2 py-2.5 text-right tabular-nums text-[var(--color-ink-soft)]">{fmt1(row.receiving)}</td>
                </>
              )}
              <td className="px-4 py-2.5 text-right text-[var(--color-ink-faint)]">
                <ChevronRight size={15} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Mobile card list */}
      <ul className="divide-y divide-[var(--color-border)] md:hidden">
        {rows.map((row, index) => (
          <li key={row.player}>
            <button
              type="button"
              onClick={() => onSelectPlayer(row.player)}
              className="flex w-full items-center gap-3 px-4 py-3 text-left active:bg-[var(--color-canvas-soft)]"
            >
              <span className="w-5 shrink-0 text-xs font-medium text-[var(--color-ink-faint)]">{index + 1}</span>
              <Badge position={row.position} />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-[var(--color-ink)]">{row.player}</p>
                <p className="truncate text-xs text-[var(--color-ink-faint)]">
                  {formatMatchup({
                    awayTeam: row.awayTeam,
                    homeTeam: row.homeTeam,
                    awayTotal: row.awayTotal,
                    homeTotal: row.homeTotal,
                    short: true,
                  })}
                </p>
              </div>
              <p className="shrink-0 text-sm font-semibold tabular-nums text-[var(--color-accent)]">
                {fmt(mode === 'ALL' ? row.ppr : row.total)}
              </p>
              <ChevronRight size={16} className="shrink-0 text-[var(--color-ink-faint)]" />
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

function fmt(value) {
  return typeof value === 'number' ? value.toFixed(2) : '–'
}

function fmt1(value) {
  return typeof value === 'number' ? value.toFixed(1) : '–'
}
