import { motion } from 'framer-motion'

export default function PageHeader({ title, subtitle, action }) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="mb-6 flex flex-wrap items-start justify-between gap-4"
    >
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-[var(--color-ink)] sm:text-3xl">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-[var(--color-ink-soft)]">{subtitle}</p>}
      </div>
      {action}
    </motion.header>
  )
}
