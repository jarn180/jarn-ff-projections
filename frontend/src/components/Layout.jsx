import { AnimatePresence, motion } from 'framer-motion'
import { ArrowLeftRight, Menu, Trophy, UserPlus, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/', label: 'Projections', icon: Trophy, end: true },
  { to: '/optimizer', label: 'Start/Sit Optimizer', icon: ArrowLeftRight, end: false },
  { to: '/waiver-wire', label: 'Waiver Wire', icon: UserPlus, end: false },
]

function NavItems({ onNavigate }) {
  return (
    <nav className="flex flex-col gap-0.5 px-2">
      {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          onClick={onNavigate}
          className={({ isActive }) =>
            [
              'flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors',
              isActive
                ? 'bg-[var(--color-accent-soft)] text-[var(--color-accent)]'
                : 'text-[var(--color-ink-soft)] hover:bg-[var(--color-border)] hover:text-[var(--color-ink)]',
            ].join(' ')
          }
        >
          <Icon size={17} strokeWidth={2} />
          {label}
        </NavLink>
      ))}
    </nav>
  )
}

export default function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  return (
    <div className="flex min-h-dvh bg-[var(--color-canvas)] text-[var(--color-ink)]">
      {/* Desktop sidebar */}
      <aside className="hidden w-64 shrink-0 border-r border-[var(--color-border)] bg-[var(--color-sidebar)] md:flex md:flex-col">
        <div className="flex items-center gap-2 px-5 py-5">
          <span className="text-xl">🏈</span>
          <div className="leading-tight">
            <p className="text-sm font-semibold">JarnFF</p>
            <p className="text-xs text-[var(--color-ink-faint)]">Vegas Props Projections</p>
          </div>
        </div>
        <NavItems />
        <div className="mt-auto px-5 py-4 text-xs text-[var(--color-ink-faint)]">
          Data from The Odds API &amp; Sleeper
        </div>
      </aside>

      {/* Mobile top bar */}
      <div className="fixed inset-x-0 top-0 z-30 flex items-center gap-3 border-b border-[var(--color-border)] bg-[var(--color-canvas)]/90 px-4 py-3 backdrop-blur md:hidden">
        <button
          type="button"
          onClick={() => setMobileOpen(true)}
          aria-label="Open menu"
          className="-ml-1 rounded-md p-1.5 text-[var(--color-ink-soft)] active:bg-[var(--color-border)]"
        >
          <Menu size={22} />
        </button>
        <span className="text-lg">🏈</span>
        <p className="text-sm font-semibold">JarnFF</p>
      </div>

      {/* Mobile drawer */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              className="fixed inset-0 z-40 bg-black/30 md:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileOpen(false)}
            />
            <motion.aside
              className="fixed inset-y-0 left-0 z-50 flex w-72 flex-col bg-[var(--color-sidebar)] shadow-[var(--shadow-notion-lg)] md:hidden"
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'tween', duration: 0.22, ease: 'easeOut' }}
            >
              <div className="flex items-center justify-between px-5 py-5">
                <div className="flex items-center gap-2">
                  <span className="text-xl">🏈</span>
                  <p className="text-sm font-semibold">JarnFF</p>
                </div>
                <button
                  type="button"
                  onClick={() => setMobileOpen(false)}
                  aria-label="Close menu"
                  className="rounded-md p-1.5 text-[var(--color-ink-soft)] active:bg-[var(--color-border)]"
                >
                  <X size={20} />
                </button>
              </div>
              <NavItems onNavigate={() => setMobileOpen(false)} />
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      <main className="min-w-0 flex-1 pt-14 md:pt-0">
        <div className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 md:px-10 md:py-10">
          {children}
        </div>
      </main>
    </div>
  )
}
