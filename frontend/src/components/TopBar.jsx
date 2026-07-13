import { SLOT_ORDER } from '../slots'
import './TopBar.css'

export default function TopBar({ round }) {
  const displayRound = Math.min(round, SLOT_ORDER.length)

  return (
    <div className="top-bar">
      <div className="round-label">Round {displayRound}/{SLOT_ORDER.length}</div>
    </div>
  )
}
