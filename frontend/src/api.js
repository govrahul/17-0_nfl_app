const BASE = '/api'

export async function rollTeam(excludeIds, { pinTeam, pinSeason } = {}) {
  const params = new URLSearchParams({ exclude: excludeIds.join(',') })
  if (pinTeam) params.set('team', pinTeam)
  if (pinSeason) params.set('season', pinSeason)
  const res = await fetch(`${BASE}/roll?${params}`)
  if (!res.ok) throw new Error((await res.json()).detail || 'Failed to roll team')
  return res.json()
}

export async function predictRecord(picks) {
  const res = await fetch(`${BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(picks),
  })
  if (!res.ok) throw new Error((await res.json()).detail || 'Failed to predict record')
  return res.json()
}
