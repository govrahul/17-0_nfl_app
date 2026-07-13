import { SLOT_LABELS } from '../slots'
import './PlayerCard.css'

export default function PlaceholderCard({ slotKey }) {
  return (
    <div className="player-card placeholder">
      <div className="top-row">
        <div className="photo-area" />
        <div className="stats-area default">
          <div className="position-chip">{SLOT_LABELS[slotKey]}</div>
          <div className="stat-chip">
            <div className="stat-value">XXX</div>
            <div className="stat-label">YDS</div>
          </div>
          <div className="stat-chip">
            <div className="stat-value">XX</div>
            <div className="stat-label">TDS</div>
          </div>
        </div>
      </div>
      <div className="name-banner">Player Name</div>
    </div>
  )
}
