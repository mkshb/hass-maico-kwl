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
  only for registers the device responds to. The result is stored, so restarts are fast; a button
  scans the unit again when needed.
- **Capability-based model detection**: since the Maico registers contain no unique model
  identifier, a profile is derived from the registers and features that are present (e.g.
  "Maico KWL (EnOcean, CO2, ZP1)").
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
- **Diagnostics** download with every discovered register, its value and raw words.
- **Automation blueprints** for demand boost, open windows and summer night cooling.
- **Local**: purely local Modbus communication, no cloud (`iot_class: local_polling`).

### Entity types

| Platform         | Examples |
|------------------|----------|
| `sensor`         | Temperatures (room, supply, extract, exhaust, intake, etc.), humidity, CO2, VOC, fan speeds, airflow rates, filter remaining time, operating hours, fault/notice code (with the active bits as the `active` attribute), current ventilation level, states (brine pump, dampers), EnOcean wireless sensors, deviation of the unit clock from Home Assistant |
| `binary_sensor`  | Supply/exhaust fan active, summer bypass, PTC heater, relays, switch contact, derived "Problem" sensor (from fault code), device/outdoor/room filter dirty and frost protection (from notice code bits) |
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
| *Heat recovery power* (W) | Supply airflow × 0.34 Wh/(m³·K) × (supply air − air intake temperature), like the vendor app. Negative while the exchanger cools the supply air. Includes the heat of the supply fan and of any heater that is running. Feed it into an *Integral* helper to get the recovered energy in kWh. |
| *Heat recovery efficiency* (%) | (supply air − air intake) / (extract air − air intake), the temperature efficiency of the exchanger. Unknown while extract and intake air are less than 5 K apart. Close to 0 while the summer bypass is open; a slow decline in winter hints at a dirty exchanger or a leaking bypass damper. |
| *Airflow imbalance* (m³/h) | Supply minus exhaust airflow (diagnostic). A lasting deviation hints at a clogged filter on one side or a calibration that is off. |
| *Absolute humidity extract air* (g/m³), *Dew point extract air* (°C) | From the extract air temperature and humidity (Magnus formula). The absolute humidity can be compared with an outdoor sensor, e.g. to decide whether more ventilation dries the home. |
| *Filter due device / outdoor / room* (on/off), *Filter next change* (date) | From the remaining filter days: a filter is due once its days reach 0, the date is when the first filter runs out. Use these for filter change reminders. |

### Fault and notice codes

The *Fault code* and *Notice code* sensors show the raw 32-bit value of registers 401/402 and
403/404. Their `active` attribute lists the bits that are set, e.g. `["bypass_active"]` for notice
code 16. Bits without a documented meaning appear as `bit_<n>`. The most useful bits also have their
own binary sensors: *Device filter dirty*, *Outdoor filter dirty*, *Room filter dirty* and *Frost
protection active*. The *Problem* sensor is on whenever any fault bit is set.

The Maico KWL documentation only calls these registers a bitfield. The bit meanings are taken from
the Modbus documentation of another Maico product (Geniovent), which uses the same registers. The
bit numbering was confirmed on a live unit (notice bit 4 follows the summer bypass), the meaning of
the other bits was not. On the test unit the filter bits stay off even when the remaining filter
time is 0 days, so use the *Filter due* sensors (see [Calculated values](#calculated-values)) for filter
change reminders.

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

### Options (cyclic bus feed)

Use **Configure** on the integration to:

- change the **scan interval**, and
- pick a **source entity** for each "bus" input (room temperature, humidity, air quality).

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
  after a firmware update or after adding sensors to the unit.

## Automations

The integration is a clean **control surface**. The control *policy* (when to change mode/level)
is best done with Home Assistant automations, which can react to anything (presence, windows,
schedule, outdoor temperature, electricity price, sensors from other rooms). That is more flexible
than the unit's built-in *Auto-Sensor* mode, which only uses the sensors configured on the device.

**Control (use as actions):** `select` *Operating mode* and *Ventilation level*, `switch` *Boost
ventilation*, `number` *Room temperature setpoint* / *Ventilation level duration*, `select` *Season*.
Set them with `select.select_option`, `switch.turn_on`, `number.set_value`.

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
is gone. All blueprints run
in `queued` mode, so frequent triggers do not log "Already running" warnings.

## Notes & limitations

- **Register addressing** is assumed to be 0-based (documented decimal code = protocol address).
  If all entities show as "unavailable", a central `REGISTER_OFFSET` can be adjusted in
  `register_defs.py`.
- **Humidity** is reported as a whole percentage on this unit (×1, not ×10 as in the docs). CO2/VOC
  remain at ×10 for now, not yet verified against real values.
- **Discovery via proxy**: some Modbus proxies/devices answer *every* address instead of returning
  an error for missing registers. In that case automatic filtering cannot kick in; the overview
  still stays lean thanks to the entities disabled by default.
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

**Entities for features the unit does not have**
- Some Modbus proxies answer every address instead of rejecting missing registers, so discovery
  cannot filter them. These entities usually show 0; disable the ones you don't need.

**A bus input has no effect**
- The matching source on the unit must be set to **"Bus"**, e.g. the *Room temperature source*
  select for the room temperature.

**New registers or features are missing after a firmware update**
- Press the *Rediscover registers* button on the device page.

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
4. Restart Home Assistant.

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
also run in GitHub Actions).

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
