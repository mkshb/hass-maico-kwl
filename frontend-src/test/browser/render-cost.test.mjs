// The card renders only when something it shows changed, keeps its DOM and
// animations across a render (no flicker), and still follows the clock.

import assert from "node:assert/strict";
import { after, test } from "node:test";

import { closeBrowser, openCard } from "./harness.mjs";

after(closeBrowser);

/** Count the card's renders from now on. */
const countRenders = (page) =>
  page.evaluate(() => {
    const card = window.kwl.card;
    window.renders = 0;
    const render = Object.getPrototypeOf(card).render;
    card.render = function () {
      window.renders++;
      return render.call(this);
    };
  });
const renders = (page) => page.evaluate(() => window.renders);

/** Hand the card a new hass object, as HA does, with a change elsewhere. */
const pushHass = (page, change) =>
  page.evaluate((change) => {
    const kwl = window.kwl;
    const states = { ...kwl.hass.states };
    if (change) states[change.id] = { entity_id: change.id, state: change.state, attributes: change.attributes ?? {} };
    kwl.hass = { ...kwl.hass, states };
    kwl.card.hass = kwl.hass;
  }, change);

test("changes elsewhere in HA do not render the card", async () => {
  const view = await openCard();
  await countRenders(view.page);
  await pushHass(view.page, { id: "light.kitchen", state: "on" });
  await pushHass(view.page, { id: "sensor.outside", state: "12.3" });
  await pushHass(view.page); // the same states again
  await view.settle();
  assert.equal(await renders(view.page), 0);
  await view.close();
});

test("a change of the unit renders once", async () => {
  const view = await openCard();
  await countRenders(view.page);
  await view.update({ temp_extract_air: { state: "22.9" } });
  assert.equal(await renders(view.page), 1);
  assert.match(await view.card.locator(".schematic").textContent(), /22\.9 °C/);
  await view.close();
});

test("a renamed bus source renders the card", async () => {
  const view = await openCard();
  await countRenders(view.page);
  await pushHass(view.page, {
    id: "sensor.living_room_temperature",
    state: "1",
    attributes: { friendly_name: "Lounge temperature" },
  });
  await view.settle();
  assert.equal(await renders(view.page), 1);
  assert.match(await view.card.locator(".tiles").textContent(), /from Lounge temperature/);
  await view.close();
});

test("a render keeps the elements and the running animations", async () => {
  const view = await openCard();
  const before = await view.page.evaluate(() => {
    const root = window.kwl.card.shadowRoot;
    window.kept = {
      tile: root.querySelector(".tile"),
      rotor: root.querySelector(".rotor"),
      animation: root.getAnimations().find((a) => a.animationName === "kwl-spin"),
    };
    return window.kept.animation.currentTime;
  });
  await view.page.waitForTimeout(200);
  await view.update({ temp_extract_air: { state: "22.9" }, fan_speed_supply: { state: "1700" } });
  const after = await view.page.evaluate(() => {
    const root = window.kwl.card.shadowRoot;
    const animation = root.getAnimations().find((a) => a.effect.target === window.kept.rotor);
    return {
      sameTile: root.querySelector(".tile") === window.kept.tile,
      sameRotor: root.querySelector(".rotor") === window.kept.rotor,
      sameAnimation: animation === window.kept.animation,
      time: animation?.currentTime,
    };
  });
  assert.ok(after.sameTile, "tile element kept");
  assert.ok(after.sameRotor, "rotor element kept");
  assert.ok(after.sameAnimation, "rotor animation kept");
  assert.ok(after.time > before, "rotor animation not restarted");
  await view.close();
});

test("without any update from HA the card still follows the clock", async () => {
  const view = await openCard();
  // The bus values were written 2 minutes before the frozen time.
  assert.equal(await view.card.locator(".badge.stale").count(), 0);
  const calls = (await view.wsCalls()).length;
  await view.page.clock.fastForward(9 * 60_000);
  await view.settle();
  assert.equal(await view.card.locator(".badge.stale").count(), 3, "bus values turned stale");
  assert.ok((await view.wsCalls()).length > calls, "energy read again");
  await view.close();
});
