import { createContext, useContext, useState } from 'react'
import { api } from '../lib/api.js'

const SleeperContext = createContext(null)

const SEASONS = ['2026', '2025']

export function SleeperProvider({ children }) {
  const [user, setUser] = useState(null)
  const [connecting, setConnecting] = useState(false)
  const [connectError, setConnectError] = useState('')

  const [leagues, setLeagues] = useState(null)
  const [loadingLeagues, setLoadingLeagues] = useState(false)
  const [selectedLeague, setSelectedLeague] = useState(null)
  const [record, setRecord] = useState('')

  async function connect(username) {
    setConnecting(true)
    setConnectError('')
    setLeagues(null)
    setSelectedLeague(null)
    setRecord('')
    try {
      const data = await api.getSleeperUser(username)
      setUser(data.user)
      setLoadingLeagues(true)
      let found = []
      for (const season of SEASONS) {
        const leaguesData = await api.getSleeperLeagues(data.user.user_id, season)
        if (leaguesData.leagues.length > 0) {
          found = leaguesData.leagues
          break
        }
      }
      setLeagues(found)
    } catch (error) {
      setConnectError(error.message)
      setUser(null)
    } finally {
      setConnecting(false)
      setLoadingLeagues(false)
    }
  }

  function selectLeague(league) {
    setSelectedLeague(league)
    setRecord('')

    api
      .getSleeperRoster(league.league_id, user.user_id)
      .then((data) => {
        const { wins = 0, losses = 0, ties = 0 } = data.roster.settings || {}
        setRecord(`${wins}-${losses}${ties > 0 ? `-${ties}` : ''}`)
      })
      .catch(() => setRecord(''))
  }

  const value = {
    user,
    connecting,
    connectError,
    connect,
    leagues,
    loadingLeagues,
    selectedLeague,
    selectLeague,
    record,
  }

  return <SleeperContext.Provider value={value}>{children}</SleeperContext.Provider>
}

export function useSleeper() {
  const ctx = useContext(SleeperContext)
  if (!ctx) {
    throw new Error('useSleeper must be used within a SleeperProvider')
  }
  return ctx
}
