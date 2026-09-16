export const POSITION_STYLES = {
  QB: 'bg-[var(--color-pos-qb-bg)] text-[var(--color-pos-qb-text)]',
  RB: 'bg-[var(--color-pos-rb-bg)] text-[var(--color-pos-rb-text)]',
  WR: 'bg-[var(--color-pos-wr-bg)] text-[var(--color-pos-wr-text)]',
  TE: 'bg-[var(--color-pos-te-bg)] text-[var(--color-pos-te-text)]',
  FLEX: 'bg-[var(--color-pos-flex-bg)] text-[var(--color-pos-flex-text)]',
  DEF: 'bg-[var(--color-pos-def-bg)] text-[var(--color-pos-def-text)]',
  K: 'bg-[var(--color-pos-k-bg)] text-[var(--color-pos-k-text)]',
}

export function positionClasses(position) {
  return POSITION_STYLES[position] || 'bg-[var(--color-border)] text-[var(--color-ink-soft)]'
}

export function scoringLabel(rec) {
  const value = parseFloat(rec ?? 0)
  if (value === 1) return 'PPR'
  if (value === 0.5) return 'Half PPR'
  return 'Standard'
}

export function scoringFormatFor(rec) {
  const value = parseFloat(rec ?? 0)
  if (value === 1) return 'PPR'
  if (value === 0.5) return 'HALF_PPR'
  return 'STANDARD'
}
