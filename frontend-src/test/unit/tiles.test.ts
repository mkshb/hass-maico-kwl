import assert from "node:assert/strict";
import { test } from "node:test";

import { KwlDevice } from "../../src/device.ts";
import { airQualityTile, buildTiles, humidityTile, roomTile } from "../../src/tiles.ts";
import { localize } from "../../src/localize.ts";
import { fakeHass, type Spec } from "./fake-hass.ts";

const NOW = Date.parse("2026-01-15T10:00:00Z");
const minutesAgo = (minutes: number) => new Date(NOW - minutes * 60_000).toISOString();
const bus = (state: string, minutes: number | null): Spec => ({
  state,
  attributes: { source_entity: "sensor.source", ...(minutes === null ? {} : { last_written: minutesAgo(minutes) }) },
});

function setup(specs: Record<string, Spec>) {
  const hass = fakeHass(specs);
  const device = new KwlDevice(hass, "unit");
  const t = (key: Parameters<typeof localize>[1], values?: Record<string, string | number>) =>
    localize(hass, key, values);
  return { hass, device, t };
}

test("room temperature follows the source set on the unit", () => {
  const specs = {
    temp_room: { state: "21.0" },
    temp_room_external: { state: "20.0" },
    room_temp_bus_sent: bus("22.0", 2),
  };
  for (const [source, expected] of [["bus", "22.0"], ["external", "20.0"], ["internal", "21.0"]]) {
    const { hass, device, t } = setup({ ...specs, room_temp_source: { state: source } });
    assert.equal(roomTile(hass, device, t, NOW)?.value, expected, source);
  }
});

test("a bus source without a sent value falls back to the unit's sensor", () => {
  const { hass, device, t } = setup({ room_temp_source: { state: "bus" }, temp_room: { state: "21.0" } });
  const tile = roomTile(hass, device, t, NOW);
  assert.equal(tile?.value, "21.0");
  assert.equal(tile?.bus, undefined);
});

test("a bus value turns stale after 10 minutes", () => {
  for (const [minutes, stale] of [[9, false], [10, true]] as const) {
    const { hass, device, t } = setup({ room_temp_source: { state: "bus" }, room_temp_bus_sent: bus("22.0", minutes) });
    const tile = roomTile(hass, device, t, NOW)!;
    assert.equal(tile.bus?.stale, stale, `${minutes} min`);
    assert.equal(tile.moreInfo, "sensor.source", "a bus value opens its source");
  }
  const { hass, device, t } = setup({ room_temp_source: { state: "bus" }, room_temp_bus_sent: bus("22.0", 14) });
  assert.equal(roomTile(hass, device, t, NOW)?.sub, "no value for 14 min");
  const fresh = setup({ room_temp_source: { state: "bus" }, room_temp_bus_sent: bus("22.0", 2) });
  assert.equal(roomTile(fresh.hass, fresh.device, fresh.t, NOW)?.sub, "from Living room");
});

test("a bus source that never delivered: no value, and no fallback", () => {
  // What the integration reports before the first write: unknown, with the
  // source but without last_written.
  const { hass, device, t } = setup({
    room_temp_source: { state: "bus" },
    room_temp_bus_sent: { state: "unknown", attributes: { source_entity: "sensor.source" } },
    temp_room: { state: "21.0" },
  });
  const tile = roomTile(hass, device, t, NOW)!;
  assert.equal(tile.value, "no value");
  assert.equal(tile.sub, "from Living room");
  assert.deepEqual(tile.bus, { stale: true });
  assert.equal(tile.moreInfo, "sensor.source");
});

test("an unavailable bus sensor (integration down) counts as no bus value", () => {
  const { hass, device, t } = setup({
    room_temp_source: { state: "bus" },
    room_temp_bus_sent: { state: "unavailable", attributes: { source_entity: "sensor.source" } },
    temp_room: { state: "21.0" },
  });
  assert.equal(roomTile(hass, device, t, NOW)?.value, "21.0");
});

test("humidity: bus value, then the highest room sensor, then the extract air", () => {
  const room = { humidity_sensor_1: { state: "48" }, enocean_humidity_id3: { state: "61" } };
  let s = setup({ humidity_bus_sent: bus("51", 1), ...room, humidity_exhaust: { state: "40" } });
  assert.equal(humidityTile(s.hass, s.device, s.t, NOW)?.value, "51");
  s = setup({ ...room, humidity_exhaust: { state: "40" } });
  assert.equal(humidityTile(s.hass, s.device, s.t, NOW)?.value, "61");
  s = setup({ humidity_exhaust: { state: "40" }, absolute_humidity_extract: { state: "7.9" } });
  const tile = humidityTile(s.hass, s.device, s.t, NOW)!;
  assert.equal(tile.value, "40");
  assert.equal(tile.sub, "extract air");
  assert.equal(tile.extra?.value, "7.9");
});

test("air quality: dot by CO2 level, sensors before the bus value", () => {
  for (const [ppm, air] of [["800", "good"], ["801", "moderate"], ["1400", "moderate"], ["1401", "poor"]]) {
    const { hass, device, t } = setup({ co2_sensor_2: { state: ppm } });
    assert.equal(airQualityTile(hass, device, t, NOW)?.air, air, ppm);
  }
  const s = setup({ co2_sensor_1: { state: "700" }, air_quality_bus_sent: bus("450", 1) });
  assert.equal(airQualityTile(s.hass, s.device, s.t, NOW)?.value, "700");
});

test("no data, no tiles; unavailable counts as no data", () => {
  let s = setup({});
  assert.deepEqual(buildTiles(s.hass, s.device, undefined, NOW), []);
  s = setup({ temp_room: { state: "unavailable" }, heat_recovery_power: { state: "unknown" } });
  assert.deepEqual(buildTiles(s.hass, s.device, undefined, NOW), []);
});

test("recovered energy today on the heat recovery tile", () => {
  const s = setup({ heat_recovery_power: { state: "903" } });
  assert.equal(buildTiles(s.hass, s.device, 3.456, NOW)[0].sub, "3.46 kWh today");
  assert.equal(buildTiles(s.hass, s.device, 12.44, NOW)[0].sub, "12.4 kWh today");
  assert.equal(buildTiles(s.hass, s.device, undefined, NOW)[0].sub, undefined);
});
