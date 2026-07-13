// Computes the minimum darkening needed on a team color so that both the
// bold white stat value and the muted Gray/300 label clear WCAG AA (4.5:1)
// against it -- rather than always stacking a fixed opaque chip behind
// every stat regardless of whether the team's color actually needs it.

function hexToRgb(hex) {
  const h = hex.replace('#', '')
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16))
}

function relativeLuminance([r, g, b]) {
  const lin = (c) => {
    c /= 255
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  }
  const [rl, gl, bl] = [r, g, b].map(lin)
  return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl
}

function contrastRatio(rgb1, rgb2) {
  const l1 = relativeLuminance(rgb1)
  const l2 = relativeLuminance(rgb2)
  const [hi, lo] = l1 > l2 ? [l1, l2] : [l2, l1]
  return (hi + 0.05) / (lo + 0.05)
}

function darken(rgb, amount) {
  return rgb.map((c) => c * (1 - amount))
}

const WHITE = [255, 255, 255]
const GRAY_300 = hexToRgb('#B4BDCC')

// Returns 0 (no darkening needed) up to ~0.6 in 0.05 steps.
export function minDarkenNeeded(hexColor) {
  const rgb = hexToRgb(hexColor)
  for (let amount = 0; amount <= 0.6; amount += 0.05) {
    const bg = darken(rgb, amount)
    if (contrastRatio(WHITE, bg) >= 4.5 && contrastRatio(GRAY_300, bg) >= 4.5) {
      return Math.round(amount * 100) / 100
    }
  }
  return 0.6
}

export function darkenedColor(hexColor, amount) {
  if (amount <= 0) return null
  const [r, g, b] = darken(hexToRgb(hexColor), amount)
  return `rgb(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)})`
}
