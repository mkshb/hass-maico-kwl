import assert from "node:assert/strict";
import { test } from "node:test";

import { neutralColor, temperatureColor, temperatureSteps } from "../../src/colors.ts";

const BLUES = ["#0d47a1", "#1976d2", "#64b5f6", "#1e88e5", "#42a5f5", "#90caf9"];
const REDS_AND_ORANGES = ["#ffb74d", "#f57c00", "#d32f2f", "#ff9800", "#ef5350"];

for (const dark of [false, true]) {
  test(`blue and red never mix (${dark ? "dark" : "light"})`, () => {
    for (let celsius = -20; celsius <= 45; celsius += 0.5) {
      const color = temperatureColor(celsius, dark);
      const blue = BLUES.some((c) => color.includes(c));
      const warm = REDS_AND_ORANGES.some((c) => color.includes(c));
      assert.ok(!(blue && warm), `${celsius} °C mixes ${color}`);
    }
  });
}

test("the scale ends at its outer stops", () => {
  assert.equal(temperatureColor(-30, false), "#0d47a1");
  assert.equal(temperatureColor(50, false), "#d32f2f");
  assert.equal(temperatureColor(undefined, false), neutralColor(false));
});

test("gradient steps follow the scale", () => {
  const steps = temperatureSteps(0, 30, false);
  assert.equal(steps.length, 5);
  assert.equal(steps[0], temperatureColor(0, false));
  assert.equal(steps[2], temperatureColor(15, false));
  assert.equal(steps[4], temperatureColor(30, false));
});
