// What Home Assistant asks of a custom card: picker entry, stub config, size,
// and the visual editor.

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
  assert.deepEqual(api.stub, { device_id: "unit" });
  assert.ok(api.size > 0);
  await view.close();
});

test("sections view: full width by default, never narrower than 9 columns, own height", async () => {
  const view = await openCard();
  const grid = await view.page.evaluate(() => window.kwl.card.getGridOptions());
  assert.deepEqual(grid, { columns: 12, min_columns: 9, max_columns: 12 });
  assert.ok(!("rows" in grid) && !("min_rows" in grid), "the card sets its own height");
  await view.close();
});

test("the editor picks a unit of this integration and drops an empty one", async () => {
  const view = await openCard();
  const result = await view.page.evaluate(async () => {
    const editor = await customElements.get("maico-kwl-card").getConfigElement();
    editor.hass = window.kwl.hass;
    editor.setConfig({ type: "custom:maico-kwl-card", device_id: "unit" });
    document.body.appendChild(editor);
    await editor.updateComplete;
    const form = editor.shadowRoot.querySelector("ha-form");
    const configs = [];
    editor.addEventListener("config-changed", (ev) => configs.push(ev.detail.config));
    const change = (value) =>
      form.dispatchEvent(new CustomEvent("value-changed", { detail: { value }, bubbles: true, composed: true }));
    change({ type: "custom:maico-kwl-card", device_id: "" });
    change({ type: "custom:maico-kwl-card", device_id: "attic" });
    editor.remove();
    return { schema: form.schema, data: form.data, configs };
  });
  assert.deepEqual(result.schema[0].selector, { device: { filter: { integration: "maico_kwl" } } });
  assert.deepEqual(result.data, { type: "custom:maico-kwl-card", device_id: "unit" });
  assert.deepEqual(result.configs, [
    { type: "custom:maico-kwl-card" },
    { type: "custom:maico-kwl-card", device_id: "attic" },
  ]);
  await view.close();
});
