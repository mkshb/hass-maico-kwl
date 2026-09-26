// Drives the card in a real browser against the mock hass (mock-hass.mjs).
//
// Speed: one browser and one context per test file (node runs the files in
// parallel), pages are reused from a pool, and settle() waits for the card
// instead of for the clock. The browser clock is frozen at FIXED_TIME.
//
// KWL_BROWSER=chromium|webkit picks the engine (default chromium).

import { readFile } from "node:fs/promises";
import { dirname, extname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium, webkit } from "playwright";

import { ENERGY_TODAY_KWH, FIXED_TIME, SOURCES, THEMES, unitStates } from "./fixture.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
export const ROOT = join(HERE, "..", "..", "..");
const FRONTEND = join(ROOT, "custom_components", "maico_kwl", "frontend");
const STRINGS = JSON.parse(
  await readFile(join(ROOT, "custom_components", "maico_kwl", "strings.json"), "utf-8"),
);
const ORIGIN = "http://card.test";
const TYPES = { ".js": "text/javascript", ".mjs": "text/javascript", ".html": "text/html" };

export const ENGINE = process.env.KWL_BROWSER ?? "chromium";
export { FIXED_TIME };

// State labels of select entities and the names of the code bits, as the
// integration's translations give them.
const LABELS = Object.fromEntries(
  Object.entries(STRINGS.entity.select).map(([key, entry]) => [key, entry.state ?? {}]),
);
const ATTRIBUTE_LABELS = Object.fromEntries(
  ["fault_code", "notice_code"].map((key) => [
    key,
    { active: STRINGS.entity.sensor[key].state_attributes.active.state },
  ]),
);

let browser;
let context;
const pool = [];
const fixtures = new Map();
let nextFixture = 0;

async function context_() {
  if (context) return context;
  browser = await (ENGINE === "webkit" ? webkit : chromium).launch();
  context = await browser.newContext({ viewport: { width: 560, height: 1400 }, deviceScaleFactor: 2 });
  await context.route(`${ORIGIN}/**`, async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path === "/") {
      return route.fulfill({ body: await readFile(join(HERE, "page.html")), contentType: "text/html" });
    }
    if (path.startsWith("/fixture/")) {
      const fixture = fixtures.get(path.slice("/fixture/".length, -".json".length));
      return route.fulfill({ json: fixture });
    }
    const file = path.startsWith("/frontend/")
      ? join(FRONTEND, path.slice("/frontend/".length))
      : join(HERE, path.slice("/test/".length));
    return route.fulfill({ body: await readFile(file), contentType: TYPES[extname(file)] });
  });
  return context;
}

export async function closeBrowser() {
  await browser?.close();
  browser = undefined;
  context = undefined;
  pool.length = 0;
}

/**
 * Open a card on a pooled page.
 *
 * options: theme ("light"|"dark"), width (px), language ("en"|"de"),
 * states (patch by translation_key; null removes an entity), config,
 * energyToday (kWh, undefined = no statistics), failServices, devices,
 * sources (friendly names of the bus source entities), reducedMotion,
 * failDelay (ms before a refused call fails). A states key "key@name" adds
 * the same kind of entity again, e.g. for a second unit.
 */
export async function openCard(options = {}) {
  const ctx = await context_();
  let page = pool.pop();
  if (!page) {
    page = await ctx.newPage();
    await page.clock.install({ time: FIXED_TIME });
  } else {
    await page.clock.setSystemTime(FIXED_TIME);
  }
  await page.emulateMedia({ reducedMotion: options.reducedMotion ? "reduce" : "no-preference" });
  const errors = [];
  const onError = (err) => errors.push(err.message);
  const onConsole = (msg) => msg.type() === "error" && errors.push(msg.text());
  page.on("pageerror", onError);
  page.on("console", onConsole);

  const theme = options.theme ?? "light";
  const states = unitStates(FIXED_TIME);
  for (const [key, spec] of Object.entries(options.states ?? {})) {
    states[key] = spec === null ? null : { ...states[key], ...spec };
  }
  const id = String(nextFixture++);
  fixtures.set(id, {
    theme: THEMES[theme],
    dark: theme === "dark",
    width: options.width ?? 460,
    language: options.language ?? "en",
    states,
    sources: options.sources ?? SOURCES,
    labels: LABELS,
    attributeLabels: ATTRIBUTE_LABELS,
    devices: options.devices ?? { unit: { id: "unit", name: "Maico KWL", name_by_user: null } },
    config: options.config ?? {},
    energyToday: "energyToday" in options ? options.energyToday : ENERGY_TODAY_KWH,
    failServices: options.failServices ?? false,
    failDelay: options.failDelay ?? 0,
  });

  await page.goto(`${ORIGIN}/?fixture=${id}`);
  await page.waitForFunction(() => window.kwl?.ready === true);
  await settle(page);

  const card = page.locator("maico-kwl-card");
  return {
    page,
    card,
    errors,
    /** What the card sent to HA so far. */
    serviceCalls: () => page.evaluate(() => window.kwl.serviceCalls),
    wsCalls: () => page.evaluate(() => window.kwl.wsCalls),
    moreInfo: () => page.evaluate(() => window.kwl.moreInfo),
    /** Report changed entities, as HA does with a new hass object. */
    update: async (patch) => {
      await page.evaluate((p) => window.kwl.update(p), patch);
      await settle(page);
    },
    settle: () => settle(page),
    close: async () => {
      page.off("pageerror", onError);
      page.off("console", onConsole);
      fixtures.delete(id);
      await page.goto("about:blank");
      pool.push(page);
    },
  };
}

/**
 * Wait until the card is idle: no update pending, no call to HA open, and a
 * frame drawn. Use it instead of a fixed wait after anything that renders.
 */
export async function settle(page) {
  await page.waitForFunction(async () => {
    const card = window.kwl?.card;
    if (!card) return false;
    await card.updateComplete;
    await new Promise((resolve) => requestAnimationFrame(() => resolve()));
    return !card.isUpdatePending && window.kwl.pending === 0;
  });
}
