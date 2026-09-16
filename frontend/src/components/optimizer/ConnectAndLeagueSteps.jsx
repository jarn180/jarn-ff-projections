import { AnimatePresence } from 'framer-motion'
import { useSleeper } from '../../context/SleeperContext.jsx'
import ConnectCard from './ConnectCard.jsx'
import LeagueGrid from './LeagueGrid.jsx'

export default function ConnectAndLeagueSteps() {
  const { user, connecting, connectError, connect, leagues, loadingLeagues, selectedLeague, selectLeague } =
    useSleeper()

  return (
    <>
      <ConnectCard user={user} onConnect={connect} connecting={connecting} error={connectError} />
      <AnimatePresence>
        {leagues && (
          <LeagueGrid
            leagues={leagues}
            loading={loadingLeagues}
            selectedId={selectedLeague?.league_id}
            onSelect={selectLeague}
          />
        )}
      </AnimatePresence>
    </>
  )
}
