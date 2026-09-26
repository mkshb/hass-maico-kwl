// Colour of air by its temperature, on a fixed scale like a weather map:
// deep blue when freezing, neutral grey around room temperature, orange to
// red when hot. Only neighbouring stops are mixed, so blue and red never
// meet (that would give purple).

type Stop = [celsius: number, color: string];

const LIGHT: Stop[] = [
  [-10, "#0d47a1"], [0, "#1976d2"], [10, "#64b5f6"], [20, "#b8b8b8"],
  [25, "#ffb74d"], [30, "#f57c00"], [35, "#d32f2f"],
];

const DARK: Stop[] = [
  [-10, "#1e88e5"], [0, "#42a5f5"], [10, "#90caf9"], [20, "#a8a8a8"],
  [25, "#ffb74d"], [30, "#ff9800"], [35, "#ef5350"],
];

export function neutralColor(dark: boolean): string {
  return (dark ? DARK : LIGHT)[3][1];
}

export function temperatureColor(celsius: number | undefined, dark: boolean): string {
  const stops = dark ? DARK : LIGHT;
  if (celsius === undefined) return neutralColor(dark);
  if (celsius <= stops[0][0]) return stops[0][1];
  for (let i = 1; i < stops.length; i++) {
    const [t1, c1] = stops[i];
    const [t0, c0] = stops[i - 1];
    if (celsius <= t1) {
      const amount = Math.round(((celsius - t0) / (t1 - t0)) * 100);
      return `color-mix(in oklab, ${c1} ${amount}%, ${c0})`;
    }
  }
  return stops[stops.length - 1][1];
}

/**
 * Colours for a gradient from one temperature to another, taken from the
 * scale at even steps, so the gradient follows the scale instead of blending
 * its two ends directly.
 */
export function temperatureSteps(
  from: number | undefined,
  to: number | undefined,
  dark: boolean,
  steps = 5,
): string[] {
  if (from === undefined || to === undefined) {
    return Array.from({ length: steps }, (_, i) =>
      temperatureColor(i < steps / 2 ? from ?? to : to ?? from, dark),
    );
  }
  return Array.from({ length: steps }, (_, i) =>
    temperatureColor(from + ((to - from) * i) / (steps - 1), dark),
  );
}
