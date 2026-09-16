export function formatMatchup({ awayTeam, homeTeam, awayTotal, homeTotal, short = false }) {
  if (!awayTeam || !homeTeam) return 'TBD'

  const teamName = (full) => (short ? full.trim().split(' ').pop() : full)
  const withTotal = (full, total) =>
    typeof total === 'number' ? `${teamName(full)} ${total.toFixed(1)}` : teamName(full)

  return `${withTotal(awayTeam, awayTotal)} @ ${withTotal(homeTeam, homeTotal)}`
}
