// Widths, motion and escaping: how the card fits and what it may not do.

import assert from "node:assert/strict";
import { after, test } from "node:test";

import { closeBrowser, openCard } from "./harness.mjs";

after(closeBrowser);

/** Elements of the card that stick out of it on the left or right. */
const overflowing = (card) =>
  card.evaluate((el) => {
    const box = el.getBoundingClientRect();
    return [...el.shadowRoot.querySelectorAll("*")]
      .map((node) => [node, node.getBoundingClientRect()])
      .filter(([, r]) => r.width > 0 && (r.left < box.left - 0.5 || r.right > box.right + 0.5))
      .map(([node]) => node.localName + (node.getAttribute("class") ? "." + node.getAttribute("class") : ""));
  });

for (const width of [300, 328, 460]) {
  test(`fits into ${width} px`, async () => {
    const view = await openCard({ width });
    assert.deepEqual(await overflowing(view.card), []);
    const narrow = width < 400;
    assert.equal(await view.card.locator(".segment .level-icon").count(), narrow ? 5 : 0, "level icons");
    const levels = await view.card.locator(".control").first().textContent();
    // With icons, the running level is named below the bar.
    assert.equal(/Nominal ·/.test(levels), narrow);
    assert.equal(await view.card.locator(".mode-row .button span").count(), narrow ? 0 : 2, "button labels");
    assert.deepEqual(view.errors, []);
    await view.close();
  });
}

test("the card is a block, so its resize observer fires", async () => {
  // The test page sets no display on the card: this has to come from the card.
  const view = await openCard();
  assert.equal(await view.card.evaluate((el) => getComputedStyle(el).display), "block");
  await view.close();
});

test("fans turn and the air shimmers, but not with reduced motion", async () => {
  const running = (card) => card.evaluate((el) => el.shadowRoot.getAnimations().length);
  let view = await openCard();
  assert.ok((await running(view.card)) >= 3, "rotors and sheen animate");
  await view.close();
  view = await openCard({ reducedMotion: true });
  assert.equal(await running(view.card), 0);
  await view.close();
});

test("names from HA reach the card as text", async () => {
  const evil = '<img src="x" id="injected">';
  const view = await openCard({
    devices: { unit: { id: "unit", name: "Maico KWL", name_by_user: evil } },
    sources: {
      "sensor.living_room_temperature": evil,
      "sensor.bathroom_humidity": "Bath",
      "sensor.living_room_co2": "CO2",
    },
  });
  assert.equal(await view.card.locator("#injected").count(), 0);
  assert.match(await view.card.locator(".title").textContent(), /<img src="x" id="injected">/);
  assert.match(await view.card.locator(".tiles").textContent(), /from <img/);
  await view.close();
});
