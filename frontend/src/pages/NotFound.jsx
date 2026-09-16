import { motion } from 'framer-motion'
import { Home } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="flex min-h-[60vh] flex-col items-center justify-center gap-3 text-center"
    >
      <span className="text-4xl">🏈</span>
      <h1 className="text-2xl font-semibold tracking-tight text-[var(--color-ink)]">Incomplete pass</h1>
      <p className="max-w-sm text-sm text-[var(--color-ink-soft)]">
        There's nothing at this page. Fourth down — let's get you back on track.
      </p>
      <Link
        to="/"
        className="mt-2 flex items-center gap-2 rounded-md bg-[var(--color-accent)] px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
      >
        <Home size={15} />
        Back to Projections
      </Link>
    </motion.div>
  )
}
