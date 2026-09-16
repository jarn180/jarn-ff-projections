import { motion } from 'framer-motion'

export default function SegmentedTabs({ options, value, onChange, layoutId }) {
  return (
    <div className="flex w-max min-w-full gap-1 overflow-x-auto rounded-lg bg-[var(--color-sidebar)] p-1 sm:min-w-0">
      {options.map((option) => {
        const active = option.value === value
        return (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={[
              'relative shrink-0 rounded-md px-3.5 py-1.5 text-sm font-medium transition-colors',
              active ? 'text-[var(--color-ink)]' : 'text-[var(--color-ink-faint)] hover:text-[var(--color-ink-soft)]',
            ].join(' ')}
          >
            {active && (
              <motion.span
                layoutId={layoutId}
                className="absolute inset-0 rounded-md bg-[var(--color-canvas)] shadow-[var(--shadow-notion-sm)]"
                transition={{ type: 'spring', stiffness: 500, damping: 35 }}
              />
            )}
            <span className="relative">{option.label}</span>
          </button>
        )
      })}
    </div>
  )
}
