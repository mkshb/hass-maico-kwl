// What the controls send to HA, and how a change shows before the unit
// confirms it.

import assert from "node:assert/strict";
import { after, test } from "node:test";

import { closeBrowser, openCard } from "./harness.mjs";

after(closeBrowser);

const MANUAL = { operating_mode: { state: "manual" } };
const segment = (card, name) => card.getByRole("button", { name, exact: true });
const active = (card) => card.locator(".segment.active").getAttribute("aria-label");
const isPending = (card) => card.locator(".segment.active.pending").count();

test("a level tap selects the option", async () => {
  const view = await openCard({ states: MANUAL });
  await segment(view.card, "Reduced").click();
  assert.deepEqual(await view.serviceCalls(), [
    { domain: "select", service: "select_option", data: { entity_id: "sensor.maico_ventilation_level", option: "reduced" } },
  ]);
  await view.close();
});

test("the level bar is locked in the auto modes, off when the unit locks it", async () => {
  let view = await openCard();
  assert.equal(await view.card.locator(".segment:disabled").count(), 5, "auto sensor");
  await view.close();
  view = await openCard({ states: { ...MANUAL, off_lock: { state: "on" } } });
  assert.equal(await segment(view.card, "Off").isDisabled(), true);
  assert.equal(await view.card.locator(".segment:disabled").count(), 1);
  await view.close();
});

test("the level bar is locked while the unit is off or boosting", async () => {
  const hint = (card) => card.locator(".levels").locator(".hint").textContent();
  for (const [states, text] of [
    [{ operating_mode: { state: "off" } }, "The unit is off"],
    [{ ...MANUAL, boost_ventilation: { state: "on" } }, "Boost is running"],
  ]) {
    const view = await openCard({ states });
    assert.equal(await view.card.locator(".segment:disabled").count(), 5, text);
    assert.equal((await hint(view.card)).trim(), text);
    await view.close();
  }
});

test("starting a boost locks the level bar at once", async () => {
  const view = await openCard({ states: MANUAL });
  assert.equal(await view.card.locator(".segment:disabled").count(), 0);
  await view.card.getByRole("button", { name: "Boost" }).click();
  await view.settle();
  assert.equal(await view.card.locator(".segment:disabled").count(), 5);
  await view.close();
});

test("mode, boost and season", async () => {
  const view = await openCard();
  await view.card.locator("select").selectOption("manual");
  await view.card.getByRole("button", { name: "Boost" }).click();
  await view.card.getByRole("button", { name: "Winter" }).click();
  assert.deepEqual(await view.serviceCalls(), [
    { domain: "select", service: "select_option", data: { entity_id: "sensor.maico_operating_mode", option: "manual" } },
    { domain: "switch", service: "turn_on", data: { entity_id: "sensor.maico_boost_ventilation" } },
  ]);
  // The season is not switched by a tap, the tap opens its entity.
  assert.deepEqual(await view.moreInfo(), ["sensor.maico_season"]);
  await view.close();
});

test("a change shows at once and waits for the unit", async () => {
  const view = await openCard({ states: MANUAL });
  await segment(view.card, "Reduced").click();
  await view.settle();
  assert.equal(await active(view.card), "Reduced");
  assert.equal(await isPending(view.card), 1);
  // The setpoint alone is not enough: the running level has to follow.
  await view.update({ ventilation_level: { state: "reduced" } });
  assert.equal(await isPending(view.card), 1);
  await view.update({ current_vent_level: { state: "reduced" } });
  assert.equal(await active(view.card), "Reduced");
  assert.equal(await isPending(view.card), 0);
  await view.close();
});

test("a refused change goes back at once", async () => {
  const view = await openCard({ states: MANUAL, failServices: true });
  await segment(view.card, "Reduced").click();
  await view.settle();
  assert.equal(await active(view.card), "Nominal");
  assert.equal(await isPending(view.card), 0);
  await view.close();
});

test("a refused tap on the level that already runs raises no error", async () => {
  const view = await openCard({ states: MANUAL, failServices: true });
  await segment(view.card, "Nominal").click();
  await view.settle();
  assert.equal(await active(view.card), "Nominal");
  assert.deepEqual(view.errors, []);
  await view.close();
});

test("a failing earlier tap does not undo a later one", async () => {
  // The first call fails after 100 ms, when the second tap is already out.
  const view = await openCard({ states: MANUAL, failServices: 1, failDelay: 100 });
  await view.page.evaluate(() => {
    const buttons = [...window.kwl.card.shadowRoot.querySelectorAll(".segment")];
    buttons.find((b) => b.getAttribute("aria-label") === "Reduced").click();
    buttons.find((b) => b.getAttribute("aria-label") === "Intensive").click();
  });
  await view.page.waitForTimeout(300);
  await view.settle();
  assert.equal(await active(view.card), "Intensive");
  assert.equal(await isPending(view.card), 1);
  await view.close();
});

test("a change the unit never confirms goes back after 35 s", async () => {
  const view = await openCard({ states: MANUAL });
  await segment(view.card, "Reduced").click();
  await view.page.clock.fastForward(34_000);
  await view.settle();
  assert.equal(await active(view.card), "Reduced");
  await view.page.clock.fastForward(2_000);
  await view.settle();
  assert.equal(await active(view.card), "Nominal");
  await view.close();
});
