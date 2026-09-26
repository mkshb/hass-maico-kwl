import assert from "node:assert/strict";
import { test } from "node:test";

import { formatDay } from "../../src/controls.ts";
import { KwlDevice } from "../../src/device.ts";
import { activeMessages } from "../../src/header.ts";
import { STRINGS, localize } from "../../src/localize.ts";
import { fakeHass } from "./fake-hass.ts";

test("both languages have the same texts with the same placeholders", () => {
  const placeholders = (text: string) => [...text.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort();
  assert.deepEqual(Object.keys(STRINGS.de).sort(), Object.keys(STRINGS.en).sort());
  for (const key of Object.keys(STRINGS.en) as (keyof typeof STRINGS.en)[]) {
    assert.deepEqual(placeholders(STRINGS.de[key]), placeholders(STRINGS.en[key]), key);
  }
});

test("texts fall back to English and fill their placeholders", () => {
  assert.equal(localize(fakeHass({}, "fr"), "fan_off"), "off");
  assert.equal(localize(fakeHass({}, "de-AT"), "fan_off"), "aus");
  assert.equal(localize(fakeHass({}, "de"), "bus_stale", { minutes: 12 }), "seit 12 min kein Wert");
});

test("the next filter change is a short date in the HA language", () => {
  assert.equal(formatDay(fakeHass({}, "de"), "2027-09-27"), "27.09.2027");
  assert.equal(formatDay(fakeHass({}, "en"), "2027-09-27"), "09/27/2027");
  assert.equal(formatDay(fakeHass({}, "de"), "unknown"), undefined);
});

test("messages: faults first, the bypass notice left out", () => {
  const hass = fakeHass({
    fault_code: { state: "1", attributes: { active: ["supply_fan"] } },
    notice_code: { state: "8208", attributes: { active: ["bypass_active", "humidity_protection_active"] } },
  });
  const messages = activeMessages(hass, new KwlDevice(hass, "unit"));
  assert.deepEqual(messages, [
    { kind: "fault", text: "label:supply_fan" },
    { kind: "notice", text: "label:humidity_protection_active" },
  ]);
});
