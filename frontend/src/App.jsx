import { useEffect, useState } from 'react'
import { rollTeam, predictRecord } from './api'
import { SLOT_ORDER, eligibleSlots } from './slots'
import TopBar from './components/TopBar'
import ListPanel from './components/ListPanel'
import FieldPanel from './components/FieldPanel'
import ResultOverlay from './components/ResultOverlay'
import './App.css'

const emptySlots = () => ({ TEAM: null, QB: null, RB: null, WR1: null, WR2: null, FLEX: null })
const MAX_BASE_ROLLS = 5
const MAX_REROLLS = 2

export default function App() {
  const [round, setRound] = useState(1)
  const [usedTeamIds, setUsedTeamIds] = useState([])
  const [pool, setPool] = useState(null)
  const [slots, setSlots] = useState(emptySlots())
  const [selectedPlayerId, setSelectedPlayerId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [predicting, setPredicting] = useState(false)
  const [baseRollsUsed, setBaseRollsUsed] = useState(1)
  const [bonusRerollsUsed, setBonusRerollsUsed] = useState(0)

  const gameComplete = Object.values(slots).filter(Boolean).length === SLOT_ORDER.length
  const baseRollsRemaining = Math.max(0, MAX_BASE_ROLLS - baseRollsUsed)
  const bonusRerollsRemaining = Math.max(0, MAX_REROLLS - bonusRerollsUsed)

  async function loadNextTeam(excludeIds, pinOptions) {
    setLoading(true)
    setError(null)
    setSelectedPlayerId(null)
    try {
      const data = await rollTeam(excludeIds, pinOptions)
      setPool(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadNextTeam([])
  }, [])

  function handleRerollCombo() {
    if (loading || bonusRerollsRemaining === 0) return

    setBonusRerollsUsed((count) => count + 1)
    loadNextTeam(usedTeamIds)
  }

  function commitPick(slotKey, value) {
    const nextSlots = { ...slots, [slotKey]: value }
    const nextUsed = [...usedTeamIds, pool.team.id]
    setSlots(nextSlots)
    setUsedTeamIds(nextUsed)
    setRound((r) => r + 1)

    if (baseRollsUsed < MAX_BASE_ROLLS) {
      setBaseRollsUsed((count) => count + 1)
    }

    const nextFilledCount = Object.values(nextSlots).filter(Boolean).length
    if (nextFilledCount === SLOT_ORDER.length) {
      runPrediction(nextSlots)
    } else {
      loadNextTeam(nextUsed)
    }
  }

  function pickTeam() {
    commitPick('TEAM', { ...pool.team, position: 'TEAM' })
  }

  function pickPlayerSlot(player, slotKey) {
    commitPick(slotKey, player)
  }

  async function runPrediction(finalSlots) {
    setPredicting(true)
    setError(null)
    try {
      const picks = {
        base_team_id: finalSlots.TEAM.id,
        qb_id: finalSlots.QB.id,
        rb_id: finalSlots.RB.id,
        wr1_id: finalSlots.WR1.id,
        wr2_id: finalSlots.WR2.id,
        flex_id: finalSlots.FLEX.id,
      }
      const data = await predictRecord(picks)
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setPredicting(false)
    }
  }

  function handlePlayNewGame() {
    setRound(1)
    setUsedTeamIds([])
    setSlots(emptySlots())
    setResult(null)
    setBaseRollsUsed(1)
    setBonusRerollsUsed(0)
    loadNextTeam([])
  }

  return (
    <div className="app-root">
      <TopBar round={round} />

      <div className="content-row">
        <ListPanel
          pool={pool}
          slots={slots}
          loading={loading}
          error={error}
          selectedPlayerId={selectedPlayerId}
          onSelectPlayer={setSelectedPlayerId}
          onPickSlot={pickPlayerSlot}
          onPickTeam={pickTeam}
          eligibleSlots={eligibleSlots}
          onRerollCombo={handleRerollCombo}
          rerollDisabled={loading || gameComplete || bonusRerollsRemaining === 0}
          baseRollsRemaining={baseRollsRemaining}
          bonusRerollsRemaining={bonusRerollsRemaining}
        />
        <FieldPanel slots={slots} />
      </div>

      {(predicting || result) && (
        <ResultOverlay predicting={predicting} result={result} onPlayAgain={handlePlayNewGame} />
      )}
    </div>
  )
}
