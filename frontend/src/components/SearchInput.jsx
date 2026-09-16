import { Search, X } from 'lucide-react'

export default function SearchInput({ value, onChange, placeholder, className = '' }) {
  return (
    <div className={`relative ${className}`}>
      <Search size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-ink-faint)]" />
      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-canvas)] py-2 pl-9 pr-8 text-base text-[var(--color-ink)] shadow-[var(--shadow-notion-sm)] outline-none transition-colors placeholder:text-[var(--color-ink-faint)] hover:border-[var(--color-border-strong)] focus:border-[var(--color-accent)] sm:text-sm"
      />
      {value && (
        <button
          type="button"
          onClick={() => onChange('')}
          aria-label="Clear search"
          className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-0.5 text-[var(--color-ink-faint)] hover:text-[var(--color-ink)]"
        >
          <X size={14} />
        </button>
      )}
    </div>
  )
}
