export default function StatPill({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center gap-2 rounded-md border border-[var(--color-border)] bg-[var(--color-canvas-soft)] px-3 py-1.5">
      {Icon && <Icon size={14} className="text-[var(--color-ink-faint)]" />}
      <span className="text-xs text-[var(--color-ink-faint)]">{label}</span>
      <span className="text-xs font-semibold text-[var(--color-ink)]">{value}</span>
    </div>
  )
}
