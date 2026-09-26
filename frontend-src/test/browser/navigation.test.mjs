// Taps and keys that open entities, and the notices and faults in the header.

import assert from "node:assert/strict";
import { after, test } from "node:test";

import { closeBrowser, openCard } from "./harness.mjs";

after(closeBrowser);

/**
 * Tap the middle of an element with the mouse, as a finger would. Playwright's
 * own click aims SVG text differently from the browser's hit testing in WebKit.
 */
async function tap(view, locator) {
  const box = await locator.evaluate((node) => {
    const r = node.getBoundingClientRect();
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
  });
  await view.page.mouse.click(box.x, box.y);
}

test("every value opens its entity, bus values their source", async () => {
  const view = await openCard();
  const svgButton = (label) => view.card.locator(`.schematic [role="button"][aria-label^="${label}"]`);
  await tap(view, svgButton("Outdoor air").locator(".value"));
  await tap(view, svgButton("Heat recovery").locator(".value"));
  await tap(view, svgButton("Bypass closed").locator(".bypass-label"));
  // A point 8 units beside the thin bypass line, which only its wider tap
  // area catches.
  const beside = await view.card.evaluate((el) => {
    const svg = el.shadowRoot.querySelector(".schematic");
    const point = new DOMPoint(210, 30).matrixTransform(svg.getScreenCTM());
    return { x: point.x, y: point.y };
  });
  await view.page.mouse.click(beside.x, beside.y);
  // Between the rotor and its text: the fan's tap area.
  await tap(view, svgButton("1,690 rpm").locator(".hit-box"));
  const tile = (label) =>
    view.card.locator(".tile").filter({ has: view.page.locator(".tile-label", { hasText: new RegExp(`^\\s*${label}`) }) });
  await tile("Room").click();
  await tile("Heat recovery").click();
  await view.card.locator(".filter").click();
  assert.deepEqual(await view.moreInfo(), [
    "sensor.maico_temp_air_intake",
    "sensor.maico_heat_recovery_efficiency",
    "sensor.maico_summer_bypass_open",
    "sensor.maico_summer_bypass_open",
    "sensor.maico_fan_speed_supply",
    "sensor.living_room_temperature",
    "sensor.maico_heat_recovery_power",
    "sensor.maico_filter_remaining_device",
  ]);
  await view.close();
});

test("the diagram works with the keyboard", async () => {
  const view = await openCard();
  const buttons = view.card.locator('.schematic [role="button"]');
  const count = await buttons.count();
  assert.ok(count >= 8, `${count} buttons in the diagram`);
  for (let i = 0; i < count; i++) {
    assert.equal(await buttons.nth(i).getAttribute("tabindex"), "0");
  }
  await buttons.first().focus();
  await view.page.keyboard.press("Enter");
  await buttons.nth(1).focus();
  await view.page.keyboard.press(" ");
  assert.equal((await view.moreInfo()).length, 2);
  await view.close();
});

test("notices: the bypass does not count, the list opens on a tap", async () => {
  let view = await openCard({ states: { notice_code: { state: "16", attributes: { active: ["bypass_active"] } } } });
  assert.equal(await view.card.locator(".chip").count(), 0);
  await view.close();

  view = await openCard({
    states: { notice_code: { state: "528", attributes: { active: ["bypass_active", "device_filter_dirty"] } } },
  });
  const chip = view.card.locator(".chip");
  assert.equal((await chip.textContent()).trim(), "1 notice");
  assert.equal(await chip.getAttribute("aria-expanded"), "false");
  await chip.click();
  assert.equal(await chip.getAttribute("aria-expanded"), "true");
  assert.deepEqual(await view.card.locator(".messages button").allTextContents().then((t) => t.map((s) => s.trim())), [
    "Device filter dirty",
  ]);
  await view.card.locator(".messages button").click();
  assert.deepEqual(await view.moreInfo(), ["sensor.maico_notice_code"]);
  await view.close();
});

test("a fault turns the chip red and comes first", async () => {
  const view = await openCard({
    states: {
      fault_code: { state: "1", attributes: { active: ["supply_fan"] } },
      notice_code: { state: "512", attributes: { active: ["device_filter_dirty"] } },
    },
  });
  const chip = view.card.locator(".chip.fault");
  assert.equal((await chip.textContent()).trim(), "Fault");
  await chip.click();
  assert.deepEqual(
    (await view.card.locator(".messages button").allTextContents()).map((s) => s.trim()),
    ["Supply air fan", "Device filter dirty"],
  );
  await view.close();
});
