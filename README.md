# Maico KWL for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![Validate][validate-shield]][validate]
[![hacs][hacsbadge]][hacs]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![Project Maintenance][maintenance-shield]][user_profile]
[![Community Forum][forum-shield]][forum]

A **Home Assistant custom integration** for Maico ventilation units (KWL, controlled
residential ventilation with heat recovery), connected over **Modbus TCP**.

The integration is **largely self-configuring**: on setup it probes the device, detects which
Modbus registers are actually implemented and creates entities only for those. A capability
profile of the unit is derived from the registers it finds.

> [!NOTE]
> This is an unofficial community project and is **not affiliated with Maico
> Elektroapparate-Fabrik GmbH**. It is in daily use and covered by automated tests, but so far it
> has only been tested with a single unit. Reports from other units are very welcome, see
> [Contributing](#contributing).

## Features

- **Autonomous discovery** of the available registers at the first setup. Entities are created
  only for registers the device responds to, and only for the accessories the unit actually has
  (filters, sensors, extension module, see [Accessories](#accessories)). You can correct the
  detected accessories in the options. The result is stored, so restarts are fast; a button scans
  the unit again when needed.
- **Capability-based model detection**: since the Maico registers contain no unique model
  identifier, a profile is derived from the registers and features that are present (e.g.
  "Maico KWL (EnOcean, CO2, ZP1)").
- **Dashboard card included**: an airflow diagram with live temperatures, fans and heat recovery,
  room values, level and mode controls and filter status. It comes with the integration and needs
  no extra download or resource, see [Dashboard card](#dashboard-card).
- **Full UI setup** (config flow): host, port, Modbus address and scan interval. The interval can
  be changed later via the options, the connection settings via *Reconfigure*.
- **Read and write**: live sensors plus controllable entities (operating mode, ventilation level,
  setpoint temperature, airflow rates, filter intervals and much more).
- **Feed external values over Modbus**: optionally push a Home Assistant source entity (room
  temperature, humidity or air quality) into the unit's write-only "bus" input registers. It is written
  on every change and refreshed cyclically (~9 min) to satisfy the device's write-cycle
  requirement. No automation needed.
- **Correct decoding** per the Maico Modbus map: ÷10 scaling, signed values, 32-bit counters via
  High-/Low-word pairs, enum states.
- **Readable fault and notice codes**: the set bits are listed by name, and dirty filters and frost
  protection get their own binary sensors.
- **Calculated values** the unit does not report: heat recovery power and efficiency, airflow
  imbalance, absolute humidity and dew point, filter change reminders.
- **Efficient polling**: contiguous registers are read in blocks. If the unit rejects a block, its
  registers are read one by one. If the unit is not reachable, the update fails right away and is
  retried at the next interval.
- **Robust connection handling**: if the unit can't be reached at startup or the connection drops
  during discovery, Home Assistant retries the setup instead of starting with an incomplete set of
  entities. Failed write actions show an error message in the UI.
- **Multilingual**: English and German translations for both entity names and select/enum state
  values. German names are chosen so that related entities group together via shared prefixes.
- **Repair issues** under *Settings > System > Repairs* while the unit reports a fault, a filter is
  due or its clock is off by more than 5 minutes. They disappear on their own once the problem is gone.
- **Diagnostics** download with every discovered register, its value and raw words.
- **Automation blueprints** for demand boost, open windows and summer night cooling.
- **Local**: purely local Modbus communication, no cloud (`iot_class: local_polling`).

### Entity types

| Platform         | Examples |
|------------------|----------|
| `sensor`         | Temperatures (room, supply, extract, exhaust, intake, etc.), humidity, CO2, VOC, fan speeds, airflow rates, filter remaining time, operating hours, fault/notice code (with the active bits as the `active` attribute), current ventilation level, states (brine pump, dampers), EnOcean wireless sensors, deviation of the unit clock from Home Assistant |
| `binary_sensor`  | Supply/exhaust fan active, summer bypass, PTC heater, relays, switch contact, derived "Problem" sensor (from fault code), device/outdoor/room filter dirty and frost protection (from notice code bits) |
| `fan`            | *Ventilation*: operating mode and ventilation level as one fan (levels as speeds, operating modes as presets), for voice assistants, HomeKit and fan cards |
| `number`         | Filter intervals, airflow rates (reduced/nominal/intensive), room temperature setpoint/max/offset, min. supply temperature, allowed filter delta-p, plus write-only **bus inputs** (room temperature / humidity / air quality fed over Modbus) |
| `select`         | Operating mode, ventilation level, season, language, room temperature source |
| `switch`         | Disable off level, lock control panel, boost ventilation |
| `button`         | Reset filter (device/outdoor/room), reset errors, sync the unit clock with Home Assistant, rediscover registers |

Around **100 registers** are mapped in total. Rarely used or duplicated sensors (EnOcean banks,
additional sensor IDs, ZP1 counters) are still discovered but **disabled by default** to keep the
UI tidy. They can be enabled individually when needed.

### Calculated values

Some useful values have no register of their own. They are calculated from the registers that are
there, and each is only created when the unit has all the registers it needs.

| Sensor | Calculation |
|--------|-------------|
| *Heat recovery power* (W) | Supply airflow × 0.34 Wh/(m³·K) × (supply air − air intake temperature), like the vendor app. Negative while the exchanger cools the supply air. Includes the heat of the supply fan and of any heater that is running. The *Heat recovery energy* sensor below adds it up. |
| *Heat recovery energy* (kWh) | The recovered heat added up over time, as a total that only increases (cooling does not count). It survives restarts and skips periods without readings, and it keeps long-term statistics for daily, monthly and yearly values. |
| *Heat recovery efficiency* (%) | (supply air − air intake) / (extract air − air intake), the temperature efficiency of the exchanger. Unknown while extract and intake air are less than 5 K apart. Close to 0 while the summer bypass is open; a slow decline in winter hints at a dirty exchanger or a leaking bypass damper. |
| *Airflow imbalance* (m³/h) | Supply minus exhaust airflow (diagnostic). A lasting deviation hints at a clogged filter on one side or a calibration that is off. |
| *Absolute humidity extract air* (g/m³), *Dew point extract air* (°C) | From the extract air temperature and humidity (Magnus formula). The absolute humidity can be compared with an outdoor sensor, e.g. to decide whether more ventilation dries the home. |
| *Filter due device / outdoor / room* (on/off), *Filter next change* (date) | From the remaining filter days: a filter is due once its days reach 0, the date is when the first filter runs out. Use these for filter change reminders. |

### Fault and notice codes

The *Fault code* and *Notice code* sensors show the raw 32-bit value of registers 401/402 and
403/404. Their `active` attribute lists the bits that are set, e.g. `["bypass_active"]` for notice
code 16; the Home Assistant UI and the [dashboard card](#dashboard-card) show them by name, e.g.
*Bypass active*. Bits without a documented meaning appear as `bit_<n>`. The most useful bits also have their
own binary sensors: *Device filter dirty*, *Outdoor filter dirty*, *Room filter dirty* and *Frost
protection active*. The *Problem* sensor is on whenever any fault bit is set.

The Maico KWL documentation only calls these registers a bitfield. The bit meanings are taken from
the Modbus documentation of another Maico product (Geniovent), which uses the same registers. The
bit numbering was confirmed on a live unit (notice bit 4 follows the summer bypass), the meaning of
the other bits was not. For filter change reminders, the *Filter due* sensors (see
[Calculated values](#calculated-values)) are the simpler choice: they follow the remaining days.

### Accessories

Some parts are not fitted to every unit. Their registers answer on every unit anyway, so the
register probe cannot tell whether they are there. Discovery therefore reads their values once and
decides from those:

| Accessory | Entities | Detected as fitted when |
|---|---|---|
| Outdoor filter, room filter | Interval, reset button, remaining time, *Filter due*, *dirty* binary sensor, repair issue | The filter has days left, or it has run out and the unit reports it as dirty. Without such a filter the unit keeps the days at 0, never reports it as dirty and ignores a filter change. |
| Wired sensors | Humidity, CO2 and VOC sensor 1 to 4 | At least one of them reports a value other than 0. |
| EnOcean wireless sensors | CO2, humidity and VOC of the 8 EnOcean IDs | At least one of them reports a value other than 0. |
| External room temperature sensor | *Temperature room external* | The *Room temperature source* is set to "External". |
| PTC heater | *PTC heater active* | Not detectable, counts as fitted. |
| ZP1 extension module | Reheating relay, brine pump, dampers, their operating hours, outdoor temperature before the air ground heat exchanger | Not detectable, counts as fitted. |

The device filter is always there. Entities of accessories that are not fitted are not created,
and *Filter next change* only covers the fitted filters. If a value does not allow a decision (e.g.
it cannot be read), the accessory counts as fitted.

The detection can be wrong, e.g. when a wireless sensor has not sent anything yet. Under
**Configure** on the integration you can choose the fitted accessories yourself (see
[Options](#options)). If you fit an accessory later, either select it there or press *Rediscover
registers* once it is set up on the unit.

## Requirements

- Home Assistant **2025.10** or newer (developed/tested with 2026.9). Older releases ship a
  pymodbus version that is too old for this integration. The integration's icon and logo are shown
  from Home Assistant 2026.3.
- The Maico unit must be reachable via **Modbus TCP**, directly or through a gateway / Modbus
  proxy.
- `pymodbus` (3.11.2 or newer) is provided by Home Assistant; no separate installation is required.

> Note: this integration speaks **Modbus TCP** only. Modbus RTU (serial) is not currently
> supported.

## Supported devices

- **Maico KWL units with Modbus TCP**, whose register map matches the Maico KWL Modbus
  documentation (`docs/modbus.csv`). According to that documentation, Modbus TCP is available from
  firmware **V1.1.1**.
- Units without some of the optional parts (EnOcean, ZP1, brine ground heat exchanger, extra
  sensors) are supported: registers the unit does not implement get no entity.
- Tested so far with **one unit**, connected through a Modbus TCP proxy. Reports from other models
  are welcome, see [Contributing](#contributing).
- Not supported: Modbus RTU (serial) and other Maico product lines with a different register map.

## Installation

### Via HACS (recommended)

1. In HACS > **Custom repositories**, add `https://github.com/mkshb/hass-maico-kwl` with category
   **Integration**.
2. Install "Maico KWL".
3. Restart Home Assistant.

### Manual

1. Copy the `custom_components/maico_kwl` folder into the `custom_components` directory of your
   Home Assistant configuration.
2. Restart Home Assistant.

## Configuration

1. **Settings > Devices & Services > Add Integration** > "Maico KWL".
2. Enter the connection details:
   - **Host**: IP/hostname of the unit or gateway
   - **Port**: default `502`
   - **Modbus address**: default `10`
   - **Scan interval**: default `30` seconds (changeable later via the options)
3. The integration tests the connection, probes the registers and creates the entities.

To change host, port or Modbus address later, use **Reconfigure** on the integration. The entities
and their history are kept.

### Options

Use **Configure** on the integration to:

- change the **scan interval**,
- choose the **fitted accessories** (see [Accessories](#accessories)), and
- pick a **source entity** for each "bus" input (room temperature, humidity, air quality).

The accessories are preselected with what discovery detected. Only accessories the unit answers to
are listed. A choice that differs from the detected one is kept, also after *Rediscover
registers*; select the detected accessories again to let discovery decide.

When a source entity is selected, its value is written to the matching Modbus register on every
change and refreshed about every 9 minutes, no automation required. The corresponding device
source must be set to **"Bus"** (e.g. the *Room temperature source* select for room temperature).
While a source entity is configured, the manual bus `number` is hidden ("source has priority");
leave the option empty to set the value manually instead.

### How data is updated

- **Polling**: all readable registers are read every *scan interval* (default 30 s, 5 to 3600 s).
  Adjacent registers are read in one request.
- **Writes**: changing a control writes the register right away and then refreshes all values, so
  the new state shows up without waiting for the next poll.
- **Bus inputs**: a configured source entity is written on every change and at least every
  ~9 minutes. Manual bus numbers are rewritten every ~9 minutes as well.
- **Discovery**: the register probe runs once at the first setup and its result is stored in the
  config entry, so restarts are fast. Press the *Rediscover registers* button to probe again, e.g.
  after a firmware update or after adding sensors or filters to the unit. An update that changes
  the discovery rules probes the unit once more on its own. Changing the options reloads the
  integration; entities of accessories that are no longer selected are removed.

## Dashboard card

The integration brings its own dashboard card. It is loaded automatically once the integration is
set up, so there is nothing to download and no dashboard resource to add.

<table>
  <tr>
    <td><img src="https://raw.githubusercontent.com/mkshb/hass-maico-kwl/main/docs/images/card-light.png" alt="Maico KWL card, light theme" width="380"></td>
    <td><img src="https://raw.githubusercontent.com/mkshb/hass-maico-kwl/main/docs/images/card-dark.png" alt="Maico KWL card, dark theme" width="380"></td>
  </tr>
</table>

*The screenshots are rendered by the card's automated test with example values.*

**Adding the card**: edit a dashboard, choose **Add card** and search for **Maico KWL**. The card
picks the unit on its own; with more than one unit, choose it in the card editor. In YAML:

```yaml
type: custom:maico-kwl-card
device_id: 0123456789abcdef0123456789abcdef  # optional, the first unit if left out
```

**What it shows**

- **Airflow diagram**: outdoor air to supply air on top, extract air to exhaust air below, the heat
  exchanger with the heat recovery efficiency in between. The colour of the air follows its
  temperature (blue when cold, grey around room temperature, orange to red when hot), so the heat
  exchange is visible at a glance. With the summer bypass open, the outdoor air takes the arc over
  the exchanger. Fans show their speed and airflow, a PTC heater lights up while it heats. A soft
  sheen moves along the ducts while the fans run; nothing moves with *reduce motion* turned on.
- **Room values**: room temperature, humidity, air quality and heat recovery power. Values that the
  integration feeds to the unit over the bus carry a **BUS** badge and name their source entity;
  the badge turns orange when no value has been written for 10 minutes. Air quality gets a
  coloured dot (up to 800 ppm good, up to 1400 ppm moderate, above poor).
- **Controls**: ventilation level, operating mode and boost. In the auto modes the unit picks the
  level itself, so the level bar is locked there. A change shows at once and pulses until the unit
  reports it, which can take a few seconds.
- **Filters**: remaining days of every fitted filter and the date of the next change.
- **Notices and faults**: a chip in the header while the unit reports any, with the messages by
  name when tapped. The bypass notice is left out, the diagram already shows it.

Parts the unit does not have (accessories, sensors) are simply left out. A unit without a summer
bypass shows it as closed. Tapping a value opens its entity, for bus values the source entity. On narrow screens the
level bar switches to icons.

## Automations

The integration is a clean **control surface**. The control *policy* (when to change mode/level)
is best done with Home Assistant automations, which can react to anything (presence, windows,
schedule, outdoor temperature, electricity price, sensors from other rooms). That is more flexible
than the unit's built-in *Auto-Sensor* mode, which only uses the sensors configured on the device.

**Control (use as actions):** `fan` *Ventilation* (`fan.set_percentage`, `fan.set_preset_mode`, `fan.turn_off`), `select` *Operating mode* and *Ventilation level*, `switch` *Boost
ventilation*, `number` *Room temperature setpoint* / *Ventilation level duration*, `select` *Season*.
Set them with `select.select_option`, `switch.turn_on`, `number.set_value`.

**Boost for a while:** the action `maico_kwl.boost` starts the boost ventilation, e.g. from a button
in the bathroom. With `duration` (minutes), Home Assistant ends the boost when the time is up;
without it, the unit ends it on its own terms. A new call replaces a running timer.

```yaml
action: maico_kwl.boost
target:
  entity_id: fan.maico_kwl_ventilation
data:
  duration: 20
```

**Triggers (read):** temperatures (room, supply, extract, exhaust, air intake), *Current ventilation
level*, fan speeds / airflow, *Summer bypass*, the *Problem* binary sensor, the *Filter due* sensors,
the *Fault code* / *Notice code* sensors and their `active` attribute, and the
[calculated values](#calculated-values), e.g. *Absolute humidity extract air* compared with an
outdoor sensor.

### Example blueprints

Ready-to-import blueprints live in [`blueprints/automation/maico_kwl/`](blueprints/automation/maico_kwl):

| Blueprint | What it does |
|-----------|--------------|
| `summer_night_cooling.yaml` | Switches to a supply-air mode (free cooling) when the outdoor air is cooler than the room after a hot day; reverts when no longer worthwhile. |
| `demand_boost.yaml` | Boosts to intensive when any HA sensor (CO2, humidity, etc.) exceeds a threshold; reverts below the lower threshold (hysteresis). |
| `window_open_reduce.yaml` | Reduces ventilation while a window/door contact is open; restores when all are closed. |

Import via **Settings > Automations & Scenes > Blueprints > Import Blueprint** using the raw URL, e.g.
`https://github.com/mkshb/hass-maico-kwl/blob/main/blueprints/automation/maico_kwl/summer_night_cooling.yaml`.
These are starting points: copy and adapt them to your home.

`demand_boost` and `window_open_reduce` save the current operating mode and ventilation level in a
temporary snapshot scene before they intervene, and restore it afterwards. They leave the unit
alone if it is already in manual mode at the target level, and they keep your setting if you change
the mode or level yourself while they are active. Snapshot scenes do not survive a Home Assistant
restart: if the unit is still in the state the automation set when Home Assistant starts, the
blueprint assumes it made that change and switches to the *Fallback* operating mode once the reason
is gone; with the fallback mode "manual" it also sets the *Fallback* level. All blueprints run
in `queued` mode, so frequent triggers do not log "Already running" warnings.

## Notes & limitations

- **Register addressing** is assumed to be 0-based (documented decimal code = protocol address).
  If all entities show as "unavailable", a central `REGISTER_OFFSET` can be adjusted in
  `register_defs.py`.
- **Humidity** is reported as a whole percentage on this unit (×1, not ×10 as in the docs). CO2/VOC
  remain at ×10 for now, not yet verified against real values.
- **Discovery via proxy**: some Modbus proxies/devices answer *every* address instead of returning
  an error for missing registers. In that case the probe cannot filter anything; the accessory
  detection and the entities disabled by default still keep the overview lean.
- **State values are slugs**: select and enum sensors store internal slugs (e.g. `manual`,
  `reduced`, `summer`) and display the translated text. Automations/templates should compare
  against the **slug**, not the displayed text.
- **Bus feed units**: a source entity's numeric state is sent as-is (assumed to match the
  register unit: °C / % / ppm). Make sure the source reports in the device's unit.

## Troubleshooting

**"Failed to connect" during setup, or the integration keeps retrying**
- Check host, port (default `502`) and Modbus address (default `10`) against the settings of the
  unit or the gateway. Connection settings can be changed later with **Reconfigure** on the
  integration.
- Make sure Modbus TCP is enabled on the unit (firmware V1.1.1 or newer) and that no firewall
  blocks the port.

**All entities are unavailable**
- The unit is not reachable at the moment (see above); entities come back on their own once it
  answers again.
- If the connection works but no values arrive, the unit may count registers from 1 instead of 0.
  Adjust `REGISTER_OFFSET` in `register_defs.py` and open an issue.

**Entities for accessories the unit does not have, or entities of a fitted accessory are missing**
- Choose the fitted accessories under **Configure** on the integration, see
  [Accessories](#accessories).
- Other entities that always show 0: some Modbus proxies answer every address instead of rejecting
  missing registers, so discovery cannot filter them. Disable the ones you don't need.

**The filter reset for the outdoor or room filter has no effect**
- The unit does not monitor this filter. Once it is fitted and enabled on the unit, select it under
  **Configure** or press *Rediscover registers*.

**A bus input has no effect**
- The matching source on the unit must be set to **"Bus"**, e.g. the *Room temperature source*
  select for the room temperature.

**New registers or features are missing after a firmware update**
- Press the *Rediscover registers* button on the device page.

**The dashboard card is missing or shows "Custom element doesn't exist"**
- Reload the page in the browser; in the companion app, reset the frontend cache in the app
  settings. The card is loaded with the rest of the frontend, so a page that was open before the
  integration was set up or updated does not know it yet.
- The card needs the integration to be set up; without a configured unit it is not loaded.

**Collecting information for a bug report**
- Download the diagnostics: **Settings > Devices & Services > Maico KWL > ⋮ > Download
  diagnostics**. They contain every discovered register with its value and raw words; the host
  is removed.
- Enable debug logging on the same page (**⋮ > Enable debug logging**), reproduce the problem, then
  disable it again to download the log.

## Removal

1. **Settings > Devices & Services > Maico KWL > ⋮ > Delete**. This removes the device and all of
   its entities.
2. Delete automations created from the blueprints, and the blueprints themselves under
   **Settings > Automations & Scenes > Blueprints** if you no longer need them.
3. Remove the integration files: in HACS open "Maico KWL" and choose **Remove**, or delete
   `custom_components/maico_kwl` for a manual installation.
4. Restart Home Assistant. Dashboard cards of type `custom:maico-kwl-card` stop working once the
   integration is removed; delete them from your dashboards.

Settings written to the unit (operating mode, ventilation level, airflow rates, etc.) stay on the
unit. Bus inputs are no longer refreshed; if the unit should use its own sensors again, set the
matching source (e.g. *Room temperature source*) away from "Bus" before removing the integration.

## Data source

The register definitions come from the Maico Modbus documentation (`docs/modbus.csv`) and are
modelled in `custom_components/maico_kwl/register_defs.py`. Connection parameters per the docs:
holding registers (FC 03), word order High-Word/Low-Word, byte order High-Byte/Low-Byte.

## Contributing

This project grows from real-world device data. Issues, register corrections and reports
(especially from other Maico models) are highly appreciated. Please open an issue or pull request
at [github.com/mkshb/hass-maico-kwl][repo].

For a bug report or a new model, attach the diagnostics (**Settings > Devices & Services >
Maico KWL > ⋮ > Download diagnostics**). They list every register the unit answers, with its value
and raw words, and make most questions answerable without access to the unit.

Development: `pytest` runs the test suite against a simulated unit, `mypy` checks the types (both
also run in GitHub Actions). The dashboard card lives in `frontend-src` (Lit, TypeScript):
`npm ci`, then `npm run build` writes the bundle to `custom_components/maico_kwl/frontend`, which is
committed so HACS ships it. `npm test` runs the unit tests and renders the built card in
Chromium, which refreshes the screenshots in `docs/images`; `npm run test:webkit` runs the browser
tests in WebKit (Safari and the iOS app). The browser tests need Roboto installed
(`fonts-roboto`).

## License / disclaimer

Unofficial community project, provided as-is and not affiliated with Maico. Use at your own risk:
write operations in particular change real device settings.

<!-- Badges -->
[repo]: https://github.com/mkshb/hass-maico-kwl
[releases-shield]: https://img.shields.io/github/release/mkshb/hass-maico-kwl.svg?style=for-the-badge
[releases]: https://github.com/mkshb/hass-maico-kwl/releases
[validate-shield]: https://img.shields.io/github/actions/workflow/status/mkshb/hass-maico-kwl/validate.yml?branch=main&style=for-the-badge&label=validate
[validate]: https://github.com/mkshb/hass-maico-kwl/actions/workflows/validate.yml
[commits-shield]: https://img.shields.io/github/commit-activity/y/mkshb/hass-maico-kwl.svg?style=for-the-badge
[commits]: https://github.com/mkshb/hass-maico-kwl/commits/main
[license-shield]: https://img.shields.io/github/license/mkshb/hass-maico-kwl.svg?style=for-the-badge
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40mkshb-blue.svg?style=for-the-badge
[user_profile]: https://github.com/mkshb
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
