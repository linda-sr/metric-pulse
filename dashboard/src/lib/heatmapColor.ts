/**
 * Maps a retention percentage (0-100) to a background color on a
 * red -> yellow -> green gradient. Returns a plain CSS color string.
 */
export function retentionColor(pct: number | null): string {
  if (pct === null) return '#f3f4f6'; // neutral gray for "no data yet"

  // Clamp defensively — retention_pct should already be 0-100 per the
  // Day 13 test (assert_retention_pct_valid), but clamping here costs
  // nothing and protects the UI if that ever regresses.
  const clamped = Math.max(0, Math.min(100, pct));

  if (clamped >= 50) {
    // 50-100 -> yellow to green
    const ratio = (clamped - 50) / 50;
    return interpolate([250, 204, 21], [34, 197, 94], ratio); // yellow -> green
  } else {
    // 0-50 -> red to yellow
    const ratio = clamped / 50;
    return interpolate([239, 68, 68], [250, 204, 21], ratio); // red -> yellow
  }
}

function interpolate(from: number[], to: number[], ratio: number): string {
  const rgb = from.map((start, i) => Math.round(start + (to[i] - start) * ratio));
  return `rgb(${rgb.join(', ')})`;
}