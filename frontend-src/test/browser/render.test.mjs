// The card renders its parts in both themes without errors. With Chromium it
// saves the screenshots the README uses (docs/images/card-{light,dark}.png);
// other engines write theirs to test/out/ for a look.

import assert from "node:assert/strict";
import { mkdir } from "node:fs/promises";
import { join } from "node:path";
import { after, test } from "node:test";

import { ENGINE, ROOT, closeBrowser, openCard } from "./harness.mjs";

const OUT = ENGINE === "chromium" ? join(ROOT, "docs", "images") : join(ROOT, "frontend-src", "test", "out");

after(closeBrowser);

for (const theme of ["light", "dark"]) {
  test(`renders in the ${theme} theme`, async () => {
    const view = await openCard({ theme });
    const { card } = view;
    assert.equal(await card.locator(".schematic").count(), 1, "schematic");
    assert.equal(await card.locator(".tile").count(), 4, "tiles");
    assert.equal(await card.locator(".segment").count(), 5, "level segments");
    assert.equal(await card.locator(".filter").count(), 1, "filters");
    assert.match(await card.locator(".schematic").textContent(), /2\.0 °C/);
    const tiles = await card.locator(".tiles").textContent();
    assert.match(tiles, /from Living room temperature/);
    assert.match(tiles, /8\.1 g\/m³/);
    assert.match(tiles, /12\.4 kWh today/);
    assert.match(await card.locator(".mode-row").textContent(), /Winter/);
    assert.deepEqual(view.errors, []);

    await mkdir(OUT, { recursive: true });
    const name = ENGINE === "chromium" ? `card-${theme}.png` : `${ENGINE}-${theme}.png`;
    await view.page.locator("#frame").screenshot({ path: join(OUT, name), animations: "disabled" });
    await view.close();
  });
}
