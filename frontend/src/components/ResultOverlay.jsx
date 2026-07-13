import './ResultOverlay.css'

export default function ResultOverlay({ predicting, result, onPlayAgain }) {
  return (
    <div className="result-overlay">
      <div className="result-card">
        {predicting && <div className="result-status">Simulating your season...</div>}
        {result && !predicting && (
          <>
            <div className="result-label">Projected record</div>
            <div className="result-record">{result.record}</div>
            <div className="result-winpct">{Math.round(result.win_pct * 100)}% win rate</div>
            <button className="play-again-btn" onClick={onPlayAgain}>
              Draft a new team
            </button>
          </>
        )}
      </div>
    </div>
  )
}
