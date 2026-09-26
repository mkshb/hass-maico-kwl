// Units without some entities, today's energy from the statistics, and the
// card being taken off and put back on a dashboard.

import assert from "node:assert/strict";
import { after, test } from "node:test";

import { closeBrowser, openCard } from "./harness.mjs";
import { unitStates } from "./fixture.mjs";

after(closeBrowser);

const without = (...keys) => Object.fromEntries(keys.map((key) => [key, null]));

test("parts the unit does not have are left out", async () => {
  const view = await openCard({
    states: {
      ...without(
        "summer_bypass_open", "room_temp_bus_sent", "humidity_bus_sent", "air_quality_bus_sent",
        "filter_remaining_device", "filter_next_change", "boost_ventilation", "season",
      ),
      temp_supply_air: { state: "unavailable" },
    },
  });
  const { card } = view;
  assert.doesNotMatch(await card.locator(".schematic").textContent(), /Bypass|Supply air/);
  assert.equal(await card.locator(".tile").count(), 3, "room, humidity, heat recovery");
  assert.doesNotMatch(await card.locator(".tiles").textContent(), /BUS/);
  assert.equal(await card.locator(".filter").count(), 0);
  assert.equal(await card.locator(".mode-row .button").count(), 0);
  assert.deepEqual(view.errors, []);
  await view.close();
});

test("no unit, or the configured one is gone", async () => {
  let view = await openCard({ states: without(...Object.keys(unitStates())) });
  assert.match(await view.card.locator(".empty").textContent(), /No Maico KWL unit found/);
  await view.close();
  view = await openCard({ config: { device_id: "gone" } });
  assert.match(await view.card.locator(".empty").textContent(), /The selected unit no longer exists/);
  await view.close();
});

test("the configured unit, not the first one", async () => {
  const view = await openCard({
    devices: {
      unit: { id: "unit", name: "Maico KWL", name_by_user: null },
      attic: { id: "attic", name: "Attic unit", name_by_user: null },
    },
    states: { temp_room_external: { state: "19.0", unit: "°C", precision: 1, device: "attic" } },
    config: { device_id: "attic" },
  });
  assert.equal((await view.card.locator(".title").textContent()).trim(), "Attic unit");
  assert.equal(await view.card.locator(".tile").count(), 0);
  await view.close();
});

test("today's energy is read from the statistics, at most every 5 minutes", async () => {
  const view = await openCard();
  const expected = {
    type: "recorder/statistic_during_period",
    statistic_id: "sensor.maico_heat_recovery_energy",
    calendar: { period: "day" },
    types: ["change"],
  };
  assert.deepEqual(await view.wsCalls(), [expected]);
  await view.update({ temp_room: { state: "21.7" } });
  assert.equal((await view.wsCalls()).length, 1);
  await view.page.clock.fastForward(5 * 60_000 + 1_000);
  await view.update({ temp_room: { state: "21.8" } });
  assert.equal((await view.wsCalls()).length, 2);
  await view.close();
});

test("without statistics the energy line stays away", async () => {
  const view = await openCard({ energyToday: undefined });
  assert.doesNotMatch(await view.card.locator(".tiles").textContent(), /today/);
  assert.deepEqual(view.errors, []);
  await view.close();
});

test("taken off and put back, the card measures and resets its changes", async () => {
  const view = await openCard({ states: { operating_mode: { state: "manual" } } });
  await view.card.getByRole("button", { name: "Reduced", exact: true }).click();
  await view.page.evaluate(() => {
    const card = window.kwl.card;
    const frame = card.parentElement;
    card.remove();
    card.style.width = "300px";
    frame.appendChild(card);
  });
  await view.settle();
  await view.page.waitForFunction(
    () => window.kwl.card.shadowRoot.querySelectorAll(".level-icon").length === 5,
  );
  // A pending change does not survive the card leaving the page.
  assert.equal(await view.card.locator(".segment.pending").count(), 0);
  assert.equal(await view.card.locator(".segment.active").getAttribute("aria-label"), "Nominal");
  assert.deepEqual(view.errors, []);
  await view.close();
});

test("air colours follow the temperature, not the unit it is shown in", async () => {
  const dot = (card) => card.evaluate((el) =>
    getComputedStyle(el.shadowRoot.querySelector('.schematic [aria-label^="Outdoor air"] circle')).fill);
  let view = await openCard();
  const celsius = await dot(view.card);
  await view.close();
  view = await openCard({ states: { temp_air_intake: { state: "35.6", unit: "°F", precision: 1 } } });
  assert.match(await view.card.locator(".schematic").textContent(), /35\.6 °F/);
  assert.equal(await dot(view.card), celsius);
  await view.close();
});

test("filter days in another duration unit", async () => {
  const view = await openCard({ states: { filter_remaining_device: { state: "5088", unit: "h", precision: 0 } } });
  assert.match(await view.card.locator(".filter").textContent(), /212 days/);
  await view.close();
});

test("a bus source that never delivered shows no value, in orange", async () => {
  const view = await openCard({
    states: {
      humidity_bus_sent: {
        state: "unknown",
        attributes: { source_entity: "sensor.bathroom_humidity" },
      },
    },
  });
  const tile = view.card.locator(".tile").filter({ has: view.page.locator(".tile-label", { hasText: /^\s*Humidity/ }) });
  assert.match(await tile.textContent(), /no value/);
  assert.match(await tile.textContent(), /from Bathroom humidity/);
  assert.equal(await tile.locator(".badge.stale").count(), 1);
  await tile.click();
  assert.deepEqual(await view.moreInfo(), ["sensor.bathroom_humidity"]);
  await view.close();
});
