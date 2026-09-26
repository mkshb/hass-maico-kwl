// Renders the built card like Home Assistant would, checks that it shows its
// parts without errors, and saves the screenshots the README uses:
// docs/images/card-light.png and docs/images/card-dark.png.
//
// Run with `npm test` after `npm run build`. Uses Playwright's Chromium, or
// the browser at CHROMIUM_PATH.

import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { after, before, test } from "node:test";
import { dirname, extname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "playwright";

import { SOURCES, THEMES, unitStates } from "./fixture.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const FRONTEND = join(ROOT, "custom_components", "maico_kwl", "frontend");
const IMAGES = join(ROOT, "docs", "images");
const STRINGS = JSON.parse(
  await readFile(join(ROOT, "custom_components", "maico_kwl", "strings.json"), "utf-8"),
);
const ORIGIN = "http://card.test";

// What the page runs: a stand-in for ha-card and for the hass object, then
// the card's own loader, exactly as the integration serves it.
const PAGE = `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap">
<style>
  body { margin: 0; font-family: Roboto, sans-serif; background: var(--primary-background-color); }
  #frame { display: inline-block; padding: 24px; background: var(--primary-background-color); }
  maico-kwl-card { display: block; width: 460px; }
</style>
</head>
<body>
<div id="frame"></div>
<script type="module">
  customElements.define("ha-card", class extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: "open" }).innerHTML =
        "<style>:host { display: block; border-radius: 12px; border: 1px solid var(--divider-color);" +
        " background: var(--card-background-color); color: var(--primary-text-color); }</style><slot></slot>";
    }
  });
  const { theme, states: raw, sources, labels } = window.FIXTURE;
  for (const [name, value] of Object.entries(theme)) document.documentElement.style.setProperty(name, value);

  const entities = {};
  const states = {};
  for (const [key, spec] of Object.entries(raw)) {
    const entityId = "sensor.maico_" + key;
    entities[entityId] = { entity_id: entityId, platform: "maico_kwl", device_id: "unit", translation_key: key };
    states[entityId] = {
      entity_id: entityId,
      state: spec.state,
      attributes: {
        friendly_name: key,
        ...(spec.unit ? { unit_of_measurement: spec.unit } : {}),
        ...(spec.options ? { options: spec.options } : {}),
        ...spec.attributes,
      },
      _spec: spec,
      _key: key,
    };
  }
  for (const [entityId, name] of Object.entries(sources)) {
    states[entityId] = { entity_id: entityId, state: "1", attributes: { friendly_name: name } };
  }
  const number = (value, digits) =>
    new Intl.NumberFormat("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(value);
  const hass = {
    language: "en",
    locale: { language: "en" },
    themes: { darkMode: window.FIXTURE.dark },
    entities,
    states,
    devices: { unit: { id: "unit", name: "Maico KWL", name_by_user: null } },
    formatEntityState(stateObj, value = stateObj.state) {
      const spec = stateObj._spec ?? {};
      const label = labels[stateObj._key]?.[value];
      if (label) return label;
      if (spec.date) return new Date(value).toLocaleDateString("en-US", { dateStyle: "medium" });
      if (spec.unit) {
        const text = number(Number(value), spec.precision ?? 0);
        return spec.unit === "%" ? text + " %" : text + " " + spec.unit;
      }
      return value;
    },
    formatEntityAttributeValue: (stateObj, attribute, value) => String(value),
    callService: async () => {},
  };

  customElements.define("home-assistant", class extends HTMLElement {});
  await import("/frontend/maico-kwl-card.js");
  await customElements.whenDefined("maico-kwl-card");
  const card = document.createElement("maico-kwl-card");
  card.setConfig({ type: "custom:maico-kwl-card" });
  card.hass = hass;
  document.getElementById("frame").appendChild(card);
  await card.updateComplete;
  await document.fonts.ready;
  window.READY = true;
</script>
</body>
</html>`;

const TYPES = { ".js": "text/javascript", ".html": "text/html" };

// State labels the integration's translations give to select entities.
const LABELS = Object.fromEntries(
  Object.entries(STRINGS.entity.select).map(([key, entry]) => [key, entry.state ?? {}]),
);

let browser;

before(async () => {
  browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
});

after(async () => {
  await browser?.close();
});

for (const theme of ["light", "dark"]) {
  test(`card renders in the ${theme} theme`, async () => {
    const page = await browser.newPage({ viewport: { width: 520, height: 1200 }, deviceScaleFactor: 2 });
    const errors = [];
    page.on("pageerror", (err) => errors.push(err.message));
    page.on("console", (msg) => msg.type() === "error" && errors.push(msg.text()));

    await page.route(`${ORIGIN}/**`, async (route) => {
      const path = new URL(route.request().url()).pathname;
      if (path === "/") return route.fulfill({ body: PAGE, contentType: "text/html" });
      const file = join(FRONTEND, path.replace(/^\/frontend\//, ""));
      return route.fulfill({ body: await readFile(file), contentType: TYPES[extname(file)] });
    });
    await page.addInitScript(
      (fixture) => (window.FIXTURE = fixture),
      { theme: THEMES[theme], dark: theme === "dark", states: unitStates(), sources: SOURCES, labels: LABELS },
    );
    await page.goto(`${ORIGIN}/`);
    await page.waitForFunction(() => window.READY === true);

    const card = page.locator("maico-kwl-card");
    assert.equal(await card.locator(".schematic").count(), 1, "schematic");
    assert.equal(await card.locator(".tile").count(), 4, "tiles");
    assert.equal(await card.locator(".segment").count(), 5, "level segments");
    assert.equal(await card.locator(".filter").count(), 1, "filters");
    assert.match(await card.locator(".schematic").textContent(), /2\.0 °C/);
    assert.match(await card.locator(".tiles").textContent(), /from Living room temperature/);
    assert.deepEqual(errors, []);

    // Let the fans and the air sheen settle into a steady frame.
    await page.waitForTimeout(500);
    await page.locator("#frame").screenshot({ path: join(IMAGES, `card-${theme}.png`), animations: "disabled" });
    await page.close();
  });
}
