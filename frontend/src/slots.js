// Mirrors Server/game.py SLOT_ELIGIBILITY -- keep these in sync.
export const SLOT_ORDER = ['TEAM', 'QB', 'RB', 'WR1', 'WR2', 'FLEX']

export const SLOT_LABELS = {
  TEAM: 'Base team',
  QB: 'QB',
  RB: 'RB',
  WR1: 'WR',
  WR2: 'WR',
  FLEX: 'FLEX',
}

export const SLOT_ELIGIBILITY = {
  QB: ['QB'],
  RB: ['RB'],
  WR1: ['WR'],
  WR2: ['WR'],
  FLEX: ['RB', 'WR', 'TE'],
}

export function eligibleSlots(position, filledSlots) {
  return SLOT_ORDER.filter((slot) => {
    if (slot === 'TEAM') return false
    if (filledSlots[slot]) return false
    return SLOT_ELIGIBILITY[slot].includes(position)
  })
}
