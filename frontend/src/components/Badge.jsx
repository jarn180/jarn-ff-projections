import { positionClasses } from '../lib/position.js'

export default function Badge({ position, className = '' }) {
  return (
    <span
      className={`inline-flex items-center justify-center rounded px-1.5 py-0.5 text-[11px] font-semibold tracking-wide ${positionClasses(
        position
      )} ${className}`}
    >
      {position}
    </span>
  )
}
