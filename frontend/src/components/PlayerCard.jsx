import { SLOT_LABELS } from '../slots'
import { minDarkenNeeded, darkenedColor } from '../contrast'
import './PlayerCard.css'

export default function PlayerCard({ player, slotKey }) {
  const chipBg = darkenedColor(player.color, minDarkenNeeded(player.color))

  return (
    <div className="player-card">
      <div className="top-row">
        <div className="photo-area" />
        <div className="stats-area" style={{ background: player.color }}>
          <div className="position-chip" style={{ background: chipBg ?? 'transparent' }}>
            {SLOT_LABELS[slotKey]}
          </div>
          <StatChip value={Math.round(player.total_yards).toLocaleString()} label="YDS" chipBg={chipBg} />
          <StatChip value={Math.round(player.total_tds)} label="TDS" chipBg={chipBg} />
        </div>
      </div>
      <div className="name-banner">{player.name}</div>
    </div>
  )
}

function StatChip({ value, label, chipBg }) {
  return (
    <div className="stat-chip" style={{ background: chipBg ?? 'transparent' }}>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}
