async function request(path, options) {
  const res = await fetch(path, options)
  const data = await res.json().catch(() => null)
  if (!res.ok || !data || data.success === false) {
    throw new Error(data?.error || `Request failed (${res.status})`)
  }
  return data
}

export const api = {
  getProjections: () => request('/api/projections'),
  getSleeperUser: (username) =>
    request(`/api/sleeper/user/${encodeURIComponent(username)}`),
  getSleeperLeagues: (userId, season) =>
    request(`/api/sleeper/user/${userId}/leagues?season=${season}`),
  getSleeperRoster: (leagueId, userId) =>
    request(`/api/sleeper/league/${leagueId}/roster/${userId}`),
  optimizeLineup: (leagueId, userId, scoringFormat) =>
    request('/api/sleeper/optimize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        league_id: leagueId,
        user_id: userId,
        scoring_format: scoringFormat,
      }),
    }),
}
