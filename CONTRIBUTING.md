# Contributing

Thanks for helping. The integration grows from real units, so reports matter as much as code.

## Ways to help

- **Report your unit.** Open a [unit report](https://github.com/mkshb/hass-maico-kwl/issues/new?template=device_report.yml),
  also when everything works. The diagnostics it asks for list every register your unit answers,
  which is how support for other models comes about.
- **Report a bug** with the [bug form](https://github.com/mkshb/hass-maico-kwl/issues/new?template=bug_report.yml)
  and the diagnostics attached.
- **Ask or discuss** in [Discussions](https://github.com/mkshb/hass-maico-kwl/discussions).
- **Contribute code or translations** as described below.

## Development setup

### Integration (Python)

Python 3.14, as in the CI:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements_test.txt
pytest --cov --cov-fail-under=95   # tests against a simulated unit
mypy                               # strict type check
```

The tests run a simulated unit behind a fake pymodbus client (`tests/conftest.py`), so the real
hub, discovery, coordinator and entities are exercised without a device.

### Dashboard card (TypeScript)

The card lives in `frontend-src` (Lit, TypeScript, Rollup). Node 20:

```bash
cd frontend-src
npm ci
npx playwright install chromium webkit   # once; Linux also needs fonts-roboto
npm run build          # writes custom_components/maico_kwl/frontend
npm test               # unit tests, then the card in Chromium
npm run test:webkit    # the card in WebKit (Safari and the iOS app)
```

- The build output in `custom_components/maico_kwl/frontend` is **committed**, because HACS ships
  the repository as it is. Run `npm run build` and commit the result with every card change; the
  CI fails when the committed build does not match the sources.
- `npm test` also refreshes the README screenshots in `docs/images` from example data. Commit them
  when the card looks different.
- `frontend-src/test/browser` renders the card against a simulated `hass` object, in both engines.
  Prefer `settle()` over fixed waits; see the comments in `harness.mjs`.

### On a real Home Assistant

Link or copy `custom_components/maico_kwl` into the `custom_components` folder of a test instance,
restart Home Assistant and add the integration. The card is loaded with the integration; after a
rebuild a normal reload of the browser page is enough.

## Adding or fixing a register

`docs/modbus.csv` is the source of truth for the register map. A register is one `RegisterDef` in
`custom_components/maico_kwl/register_defs.py`: address, data type, scaling, unit, device class,
platform and, for enums, the options. Everything else (discovery, polling, entities) follows from
it. Then:

1. Name the entity in `strings.json` and the same in `translations/en.json`, with the German name
   in `translations/de.json`. Enum options and attribute values need their states translated too.
2. Give it an icon in `icons.json` if the default does not fit.
3. Add or extend a test, e.g. in `tests/test_register_defs.py` for decoding.
4. If the card should show it, add its key to `frontend-src/src/keys.ts`.
   `tests/test_frontend.py` checks that every key there exists.

`tests/test_translations.py` and `tests/test_icons.py` check that the translation files have the
same keys and that icons belong to existing entities.

## Card rules

- Entities are found by their `translation_key` on the chosen device, never by entity id.
- The card is loaded before the frontend has set up its element registry, so nothing may define an
  element at the top level of a module; `src/loader.ts` waits for the frontend first.
- The card renders only when an entity it shows changed (`shouldUpdate`). Time-based parts run on
  the card's own clock. Keep new data inside this: read entities through `KwlDevice`.
- Colours come from Home Assistant's theme variables; air colours from `src/colors.ts`.

## Commits and pull requests

- One change per commit, with a short lowercase prefix: `add:` for new things, `fix:` for bugs,
  `update:` for changes to existing behaviour, `bump:` for the version.
- Open the pull request against `main`. The checks (tests, types, hassfest, HACS, card in both
  engines) have to pass.
- Describe what changes for users; that text goes into the release notes.

## Releases

Each version is prepared on a branch `release/x.y.z`. Its first commit sets the version in
`custom_components/maico_kwl/manifest.json`, and `CHANGELOG.md` gets a section for it at the top,
marked `(unreleased)` until the release. The maintainer merges the pull request, sets the date in
the changelog and publishes the release with that section as its text.
