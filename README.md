# Maico KWL – Home Assistant Integration

[![GitHub Release][releases-shield]][releases]
[![Validate][validate-shield]][validate]
[![hacs][hacsbadge]][hacs]
[![Project Stage][stage-shield]][commits]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![Project Maintenance][maintenance-shield]][user_profile]
[![Community Forum][forum-shield]][forum]

A **Home Assistant custom integration** for Maico ventilation units (KWL – controlled
residential ventilation with heat recovery), connected over **Modbus TCP**.

The integration is **largely self-configuring**: on setup it probes the device, detects which
Modbus registers are actually implemented and creates entities only for those. A capability
profile of the unit is derived from the registers it finds.

> [!WARNING]
> **Very young project (alpha, v0.1.0).** This integration is at the very beginning. It has so
> far only been tested against a single unit (through a Modbus-TCP proxy). Expect bugs, missing
> fields and **breaking changes** between versions – entity IDs and stored state values may still
> change. Use at your own risk. This is an unofficial community project and is **not affiliated
> with Maico Elektroapparate-Fabrik GmbH**. Feedback and device logs are very welcome.

## Features

- **Autonomous discovery** of the available registers at setup – entities are created only for
  registers the device responds to.
- **Capability-based model detection**: since the Maico registers contain no unique model
  identifier, a profile is derived from the registers and features that are present (e.g.
  “Maico KWL (EnOcean, CO2, ZP1)”).
- **Full UI setup** (config flow): host, port, Modbus address and scan interval. The interval can
  be changed later via the options.
- **Read and write**: live sensors plus controllable entities (operating mode, ventilation level,
  setpoint temperature, airflow rates, filter intervals and much more).
- **Correct decoding** per the Maico Modbus map: ÷10 scaling, signed values, 32-bit counters via
  High-/Low-word pairs, enum states, bitfield fault codes.
- **Efficient polling**: contiguous registers are read in blocks (with a per-register fallback on
  errors).
- **Multilingual**: English and German translations – both entity names and select/enum state
  values. German names are chosen so that related entities group together via shared prefixes.
- **Local**: purely local Modbus communication, no cloud (`iot_class: local_polling`).

### Entity types

| Platform         | Examples |
|------------------|----------|
| `sensor`         | Temperatures (room, supply, extract, exhaust, intake …), humidity, CO2, VOC, fan speeds, airflow rates, filter remaining time, operating hours, fault/notice code, current ventilation level, states (brine pump, dampers), EnOcean wireless sensors |
| `binary_sensor`  | Supply/exhaust fan active, summer bypass, PTC heater, relays, switch contact, derived “Problem” sensor (from fault code) |
| `number`         | Filter intervals, airflow rates (reduced/nominal/intensive), room temperature setpoint/max/offset, min. supply temperature, allowed filter delta-p |
| `select`         | Operating mode, ventilation level, season, language, room temperature source |
| `switch`         | Disable off level, lock control panel, boost ventilation |
| `button`         | Reset filter (device/outdoor/room), reset errors |

Around **100 registers** are mapped in total. Rarely used or duplicated sensors (EnOcean banks,
additional sensor IDs, ZP1 counters) are still discovered but **disabled by default** to keep the
UI tidy – they can be enabled individually when needed.

## Requirements

- Home Assistant **2024.1** or newer (developed/tested with 2026.4).
- The Maico unit must be reachable via **Modbus TCP** – directly or through a gateway / Modbus
  proxy.
- `pymodbus` (3.11) is provided by Home Assistant; no separate installation is required.

> Note: this integration speaks **Modbus TCP** only. Modbus RTU (serial) is not currently
> supported.

## Installation

### Via HACS (recommended)

1. In HACS → **Custom repositories**, add `https://github.com/mkshb/hass-maico-kwl` with category
   **Integration**.
2. Install “Maico KWL”.
3. Restart Home Assistant.

### Manual

1. Copy the `custom_components/maico_kwl` folder into the `custom_components` directory of your
   Home Assistant configuration.
2. Restart Home Assistant.

## Configuration

1. **Settings → Devices & Services → Add Integration** → “Maico KWL”.
2. Enter the connection details:
   - **Host**: IP/hostname of the unit or gateway
   - **Port**: default `502`
   - **Modbus address**: default `10`
   - **Scan interval**: default `30` seconds (changeable later via the options)
3. The integration tests the connection, probes the registers and creates the entities.

## Notes & limitations

- **Register addressing** is assumed to be 0-based (documented decimal code = protocol address).
  If all entities show as “unavailable”, a central `REGISTER_OFFSET` can be adjusted in
  `register_defs.py`.
- **Humidity** is reported as a whole percentage on this unit (×1, not ×10 as in the docs). CO2/VOC
  remain at ×10 for now – not yet verified against real values.
- **Discovery via proxy**: some Modbus proxies/devices answer *every* address instead of returning
  an error for missing registers. In that case automatic filtering cannot kick in; the overview
  still stays lean thanks to the entities disabled by default.
- **State values are slugs**: select and enum sensors store internal slugs (e.g. `manual`,
  `reduced`, `summer`) and display the translated text. Automations/templates should compare
  against the **slug**, not the displayed text.

## Data source

The register definitions come from the Maico Modbus documentation (`docs/modbus.csv`) and are
modelled in `custom_components/maico_kwl/register_defs.py`. Connection parameters per the docs:
holding registers (FC 03), word order High-Word/Low-Word, byte order High-Byte/Low-Byte.

## Contributing

This project is in an early stage and grows from real-world device data. Issues, register
corrections and logs (especially from other Maico models) are highly appreciated – please open an
issue or pull request at [github.com/mkshb/hass-maico-kwl][repo].

## License / disclaimer

Unofficial community project, provided as-is and not affiliated with Maico. Use at your own risk –
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
[stage-shield]: https://img.shields.io/badge/project%20stage-alpha-orange.svg?style=for-the-badge
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40mkshb-blue.svg?style=for-the-badge
[user_profile]: https://github.com/mkshb
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
