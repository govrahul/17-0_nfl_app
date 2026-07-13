import field from '../assets/field.jpg'
import PlayerCard from './PlayerCard'
import PlaceholderCard from './PlaceholderCard'
import './FieldPanel.css'

// Symmetric formation within the 872px-wide FieldStage (card width 170px):
// left/right columns sit 88px from their edge, center column is dead-center.
const FORMATION = {
  WR1: { top: '30px', left: '88px' },
  WR2: { top: '30px', left: '614px' },
  QB: { top: '280px', left: '351px' },
  RB: { top: '530px', left: '88px' },
  FLEX: { top: '530px', left: '614px' },
}

export default function FieldPanel({ slots }) {
  const baseTeam = slots.TEAM

  return (
    <div className="field-panel">
      <div className="field-stage" style={{ backgroundImage: `url(${field})` }}>
        <div className="base-team-block">
          {baseTeam ? (
            <>
              <h1 className="base-team-title">
                {Math.round(baseTeam.actual_win_pct * 100)}% WIN &middot; {Math.round(baseTeam.base_team_strength * 100)} STR
              </h1>
              <h1 className="base-team-title">
                &lsquo;{String(baseTeam.season).slice(-2)} {baseTeam.team_name}
              </h1>
            </>
          ) : (
            <h1 className="base-team-title muted">Base team not yet drafted</h1>
          )}
        </div>
        {Object.entries(FORMATION).map(([slotKey, pos]) => (
          <div key={slotKey} className="slot-anchor" style={pos}>
            {slots[slotKey] ? (
              <PlayerCard player={slots[slotKey]} slotKey={slotKey} />
            ) : (
              <PlaceholderCard slotKey={slotKey} />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
