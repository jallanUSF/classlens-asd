/**
 * Format seconds as MM:SS for media progress bars.
 * Negative or NaN values return "0:00".
 */
export function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const whole = Math.floor(seconds);
  const m = Math.floor(whole / 60);
  const s = whole % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}
