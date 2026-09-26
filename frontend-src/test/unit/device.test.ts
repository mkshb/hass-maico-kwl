import assert from "node:assert/strict";
import { test } from "node:test";

import { KwlDevice } from "../../src/device.ts";
import { fakeHass } from "./fake-hass.ts";

const device = (state: string, unit?: string) =>
  new KwlDevice(fakeHass({ temp_air_intake: { state, attributes: unit ? { unit_of_measurement: unit } : {} } }), "unit");

test("temperatures in any unit HA offers become °C", () => {
  assert.equal(device("2.0", "°C").numberIn("temp_air_intake", "°C"), 2);
  assert.ok(Math.abs(device("35.6", "°F").numberIn("temp_air_intake", "°C")! - 2) < 1e-9);
  assert.ok(Math.abs(device("275.15", "K").numberIn("temp_air_intake", "°C")! - 2) < 1e-9);
});

test("durations become days, flows become m³/h", () => {
  assert.equal(device("5088", "h").numberIn("temp_air_intake", "d"), 212);
  assert.equal(device("2", "w").numberIn("temp_air_intake", "d"), 14);
  assert.ok(Math.abs(device("50", "L/s").numberIn("temp_air_intake", "m³/h")! - 180) < 1e-9);
});

test("an unknown unit gives no number, a missing one the value as it is", () => {
  assert.equal(device("2.0", "°Ré").numberIn("temp_air_intake", "°C"), undefined);
  assert.equal(device("2.0").numberIn("temp_air_intake", "°C"), 2);
});
