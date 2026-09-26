// What Home Assistant asks of a custom card: picker entry, stub config, size,
// and the editor form.

import assert from "node:assert/strict";
import { after, test } from "node:test";

import { closeBrowser, openCard } from "./harness.mjs";

after(closeBrowser);

test("card picker entry, stub config and size", async () => {
  const view = await openCard();
  const api = await view.page.evaluate(() => {
    const Card = customElements.get("maico-kwl-card");
    return {
      entry: window.customCards.find((c) => c.type === "maico-kwl-card"),
      stub: Card.getStubConfig(window.kwl.hass),
      size: window.kwl.card.getCardSize(),
    };
  });
  assert.equal(api.entry.name, "Maico KWL");
  assert.equal(api.entry.preview, true);
  assert.ok(api.entry.description);
  assert.equal(api.entry.documentationURL, "https://github.com/mkshb/hass-maico-kwl#dashboard-card");
  assert.deepEqual(api.stub, { device_id: "unit" });
  assert.ok(api.size > 0);
  await view.close();
});

test("the card suggests itself for an entity of a Maico unit", async () => {
  const view = await openCard();
  const suggestions = await view.page.evaluate(() => {
    const hass = window.kwl.hass;
    const entry = window.customCards.find((c) => c.type === "maico-kwl-card");
    return {
      maico: entry.getEntitySuggestion(hass, "sensor.maico_temp_room"),
      foreign: entry.getEntitySuggestion(hass, "sensor.living_room_temperature"),
      unknown: entry.getEntitySuggestion(hass, "light.nowhere"),
    };
  });
  assert.deepEqual(suggestions.maico, { config: { type: "custom:maico-kwl-card", device_id: "unit" } });
  assert.equal(suggestions.foreign, null);
  assert.equal(suggestions.unknown, null);
  await view.close();
});

test("an invalid config is refused with a message and changes nothing", async () => {
  const view = await openCard();
  const results = await view.page.evaluate(() => {
    const card = window.kwl.card;
    const attempt = (config) => {
      try {
        card.setConfig(config);
        return "accepted";
      } catch (err) {
        return err.message;
      }
    };
    return {
      number: attempt({ type: "custom:maico-kwl-card", device_id: 123 }),
      empty: attempt({ type: "custom:maico-kwl-card", device_id: "  " }),
      list: attempt(["device_id"]),
      haKeys: attempt({
        type: "custom:maico-kwl-card",
        grid_options: { columns: 9 },
        visibility: [],
        view_layout: { position: "main" },
      }),
    };
  });
  assert.match(results.number, /device_id must be the id of a Maico KWL unit, got 123/);
  // The form leaves an empty id when the unit is cleared: the first unit.
  assert.equal(results.empty, "accepted");
  assert.match(results.list, /expected an object/);
  assert.equal(results.haKeys, "accepted");
  assert.equal(await view.card.locator(".tile").count(), 4, "still showing the unit");
  await view.close();
});

test("the card size matches its rendered height", async () => {
  const view = await openCard();
  const { size, height, estimate } = await view.page.evaluate(() => {
    const card = window.kwl.card;
    const fresh = document.createElement("maico-kwl-card");
    return { size: card.getCardSize(), height: card.getBoundingClientRect().height, estimate: fresh.getCardSize() };
  });
  assert.equal(size, Math.ceil(height / 50));
  assert.ok(Math.abs(estimate - size) <= 2, `estimate ${estimate} near ${size}`);
  await view.close();
});

test("sections view: full width by default, never narrower than 9 columns, own height", async () => {
  const view = await openCard();
  const grid = await view.page.evaluate(() => window.kwl.card.getGridOptions());
  assert.deepEqual(grid, { columns: 12, min_columns: 9, max_columns: 12 });
  assert.ok(!("rows" in grid) && !("min_rows" in grid), "the card sets its own height");
  await view.close();
});

test("the editor is HA's own form with a unit picker", async () => {
  const view = await openCard();
  const form = await view.page.evaluate(() => {
    const Card = customElements.get("maico-kwl-card");
    const form = Card.getConfigForm();
    const refused = (config) => {
      try {
        form.assertConfig(config);
        return false;
      } catch {
        return true;
      }
    };
    return {
      customEditor: typeof Card.getConfigElement,
      schema: form.schema,
      label: form.computeLabel(form.schema[0]),
      refusesNumber: refused({ type: "custom:maico-kwl-card", device_id: 7 }),
      refusesUnit: refused({ type: "custom:maico-kwl-card", device_id: "unit" }),
    };
  });
  assert.equal(form.customEditor, "undefined", "no custom editor element");
  assert.deepEqual(form.schema, [
    { name: "device_id", selector: { device: { filter: { integration: "maico_kwl" } } } },
  ]);
  assert.equal(form.label, "Unit");
  assert.equal(form.refusesNumber, true);
  assert.equal(form.refusesUnit, false);
  await view.close();
});
