import { ChevronDown } from 'lucide-react'

export default function Select({ value, onChange, options, label, className = '' }) {
  return (
    <label className={`flex flex-col gap-1.5 text-xs font-medium text-[var(--color-ink-faint)] ${className}`}>
      {label}
      <div className="relative">
        <select
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className="w-full cursor-pointer appearance-none rounded-md border border-[var(--color-border)] bg-[var(--color-canvas)] py-2 pl-3 pr-9 text-sm font-medium text-[var(--color-ink)] shadow-[var(--shadow-notion-sm)] outline-none transition-colors hover:border-[var(--color-border-strong)] focus:border-[var(--color-accent)]"
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <ChevronDown
          size={15}
          className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-[var(--color-ink-faint)]"
        />
      </div>
    </label>
  )
}
