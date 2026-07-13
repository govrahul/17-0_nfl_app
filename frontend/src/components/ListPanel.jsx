import { useMemo, useState } from 'react'
import { SLOT_LABELS } from '../slots'
import './ListPanel.css'

const TABS = ['All', 'QB', 'RB', 'WR', 'TE', 'TEAM']

export default function ListPanel({
  pool,
  slots,
  loading,
  error,
  selectedPlayerId,
  onSelectPlayer,
  onPickSlot,
  onPickTeam,
  eligibleSlots,
  onRerollTeam,
  onRerollDecade,
  rerollDisabled,
}) {
  const [tab, setTab] = useState('All')
  const [search, setSearch] = useState('')

  const players = useMemo(() => {
    if (!pool) return []
    let list = pool.players
    if (tab !== 'All' && tab !== 'TEAM') {
      list = list.filter((p) => p.position === tab)
    }
    if (search.trim()) {
      const q = search.trim().toLowerCase()
      list = list.filter((p) => p.name.toLowerCase().includes(q))
    }
    return [...list].sort((a, b) => b.total_yards - a.total_yards)
  }, [pool, tab, search])

  const teamAlreadyPicked = !!slots.TEAM
  const teamSlotOpen = !teamAlreadyPicked

  const teamMatchesSearch =
    !search.trim() ||
    pool?.team.team_name.toLowerCase().includes(search.trim().toLowerCase()) ||
    pool?.team.team.toLowerCase().includes(search.trim().toLowerCase())
  const showTeamRow = pool && (tab === 'All' || tab === 'TEAM') && teamMatchesSearch

  return (
    <div className="list-panel">
      <div className="filter-row">
        {TABS.map((t) => (
          <button key={t} className={`filter-tab ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>
            {t}
          </button>
        ))}
        <input
          className="search-box"
          placeholder="Look for..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        {pool && (
          <>
            <div className="team-pill" style={{ background: pool.team.color }}>
              {pool.team.team}
            </div>
            <div className="decade-pill">&lsquo;{String(pool.team.season).slice(-2)}</div>
            <button className="reroll-chip" onClick={onRerollTeam} disabled={rerollDisabled}>
              &#8635; Team
            </button>
            <button className="reroll-chip" onClick={onRerollDecade} disabled={rerollDisabled}>
              &#8635; Decade
            </button>
          </>
        )}
      </div>

      {error && <div className="panel-error">{error}</div>}
      {loading && <div className="panel-status">Rolling next team...</div>}

      {!loading && pool && (
        <>
          <div className="player-count">
            {tab === 'TEAM'
              ? '1 base team available'
              : `${players.length} players available${showTeamRow ? ' + base team' : ''}`}
          </div>

          <div className="rows">
            {showTeamRow && <TeamRow team={pool.team} disabled={!teamSlotOpen} onPick={onPickTeam} />}
            {tab !== 'TEAM' &&
              players.map((p) => (
                <PlayerRow
                  key={p.id}
                  player={p}
                  expanded={selectedPlayerId === p.id}
                  eligible={eligibleSlots(p.position, slots)}
                  onClick={() => onSelectPlayer(selectedPlayerId === p.id ? null : p.id)}
                  onPickSlot={(slotKey) => onPickSlot(p, slotKey)}
                />
              ))}
          </div>
        </>
      )}
    </div>
  )
}

function statColumns(player) {
  const yds = Math.round(player.total_yards).toLocaleString()
  const td = Math.round(player.total_tds)
  if (player.position === 'QB') {
    return [
      { value: player.completions, label: 'CMP' },
      { value: yds, label: 'YDS' },
      { value: td, label: 'TD' },
      { value: player.interceptions, label: 'INT' },
      { value: player.games, label: 'GP' },
    ]
  }
  if (player.position === 'RB') {
    const ypc = player.carries > 0 ? (player.total_yards / player.carries).toFixed(1) : '0.0'
    return [
      { value: Math.round(player.carries), label: 'ATT' },
      { value: yds, label: 'YDS' },
      { value: td, label: 'TD' },
      { value: ypc, label: 'YPC' },
      { value: player.games, label: 'GP' },
    ]
  }
  const ypr = player.receptions > 0 ? (player.total_yards / player.receptions).toFixed(1) : '0.0'
  return [
    { value: player.receptions, label: 'REC' },
    { value: yds, label: 'YDS' },
    { value: td, label: 'TD' },
    { value: ypr, label: 'YPR' },
    { value: player.games, label: 'GP' },
  ]
}

function PlayerRow({ player, expanded, eligible, onClick, onPickSlot }) {
  const noSlots = eligible.length === 0
  return (
    <div className={`player-row ${noSlots ? 'disabled' : ''}`}>
      <button className="row-main" onClick={onClick} disabled={noSlots}>
        <div className="name-block">
          <div className="name">{player.name}</div>
          <div className="sub">
            {player.position} &middot; {player.team} &middot; {player.season}
          </div>
        </div>
        <div className="stats-group">
          {statColumns(player).map((s) => (
            <Stat key={s.label} value={s.value} label={s.label} />
          ))}
        </div>
      </button>
      {expanded && !noSlots && (
        <div className="slot-picker">
          {eligible.map((slotKey) => (
            <button key={slotKey} className="slot-choice" onClick={() => onPickSlot(slotKey)}>
              Draft to {SLOT_LABELS[slotKey]}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function TeamRow({ team, disabled, onPick }) {
  return (
    <div className={`player-row ${disabled ? 'disabled' : ''}`}>
      <button className="row-main" onClick={onPick} disabled={disabled}>
        <div className="name-block">
          <div className="name">{team.team_name}</div>
          <div className="sub">
            {team.team} &middot; {team.season} &middot; base team
          </div>
        </div>
        <div className="stats-group">
          <Stat value={Math.round(team.actual_win_pct * 100)} label="WIN%" />
          <Stat value={Math.round(team.base_team_strength * 100)} label="STR" />
        </div>
      </button>
    </div>
  )
}

function Stat({ value, label }) {
  return (
    <div className="stat-col">
      <div className="stat-val">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}
