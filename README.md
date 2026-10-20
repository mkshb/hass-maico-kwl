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
Modbus registers are actually implemented and creates entities only for those. A dashboard card
comes with it.

> [!NOTE]
> This is an unofficial community project and is **not affiliated with Maico
> Elektroapparate-Fabrik GmbH**. It is in daily use and covered by automated tests, but so far it
> has only been tested with a single unit. Reports from other units are very welcome, see
> [Support and contributing](#support-and-contributing).

<table>
  <tr>
    <td><img src="https://raw.githubusercontent.com/mkshb/hass-maico-kwl/main/docs/images/card-light.png" alt="Maico KWL card, light theme" width="380"></td>
    <td><img src="https://raw.githubusercontent.com/mkshb/hass-maico-kwl/main/docs/images/card-dark.png" alt="Maico KWL card, dark theme" width="380"></td>
  </tr>
</table>

## Features

- **Autonomous discovery**: entities only for the registers the unit answers and the accessories
  it actually has. The result is stored; a button scans the unit again when needed.
- **Read and write**: live temperatures, humidity, air quality, fans, airflow, filters and
  operating hours, plus controls for operating mode, ventilation level, setpoint temperature,
  airflow rates, filter intervals and more. Operating mode and level also come as one fan entity.
- **Dashboard card included**: an airflow diagram with live values and controls, no extra download
  or resource needed.
- **Calculated values** the unit does not report: heat recovery power, energy and efficiency,
  airflow imbalance, absolute humidity and dew point, filter change reminders.
- **Feed external values**: send a room temperature, humidity or air quality sensor from Home
  Assistant to the unit over Modbus, without an automation.
- **Readable fault and notice codes**, repair issues for faults, due filters and a wrong unit clock,
  and a diagnostics download.
- **Automation blueprints** for demand boost, open windows and summer night cooling, plus a
  `maico_kwl.boost` action.
- **Full UI setup**, English and German translations, purely local communication without a cloud.

## Supported devices and requirements

- **Maico KWL units with Modbus TCP** whose register map matches the Maico KWL Modbus
  documentation. Modbus TCP is available from firmware **V1.1.1**.
- **Home Assistant 2026.10** or newer.
- Modbus RTU (serial) and other Maico product lines are **not supported**.
- The integration cannot read the model name; it shows a capability profile of the unit instead.

> [!IMPORTANT]
> The Maico KWL accepts only **one** Modbus TCP connection at a time. Integrations that use the
> Modbus integration of Home Assistant share it, every other Modbus client is locked out. A
> **Modbus TCP proxy** between the unit and its clients is strongly recommended. Details:
> [Compatibility and requirements](docs/compatibility.md).

## Installation

### Via HACS (recommended)

[![Open your Home Assistant instance and open this repository inside HACS.][hacs-repo-badge]][hacs-repo]

1. Open the repository in HACS with the button above, or search HACS for "Maico KWL".
2. Download "Maico KWL". HACS downloads the `maico_kwl.zip` attached to the release.
3. Restart Home Assistant.

### Manual

1. Download `maico_kwl.zip` from the [latest release][releases] and unpack it into
   `custom_components/maico_kwl` of your Home Assistant configuration, or copy the
   `custom_components/maico_kwl` folder of the release source. The `main` branch may contain
   unreleased changes.
2. Restart Home Assistant.

After an update, restart Home Assistant and reload the dashboard in the browser once, so the
browser loads the new card.

## Setup

[![Open your Home Assistant instance and start setting up Maico KWL.][config-flow-badge]][config-flow]

1. Start the setup with the button above, or go to **Settings > Devices & Services > Add
   Integration** > "Maico KWL".
2. Enter **host** (IP/hostname of the unit or gateway), **port** (default `502`), **Modbus
   address** (default `10`) and **scan interval** (default `30` seconds).
3. The integration checks that a Maico KWL answers, probes the registers and creates the entities.

Afterwards:

- **Configure** on the integration changes the scan interval, the fitted accessories and the
  source entities for the bus inputs.
- **Reconfigure** changes host, port or Modbus address.
- Check that the detected accessories (filters, sensors, extension module) are right.

Everything about the options: [Configuration](docs/configuration.md).

## Dashboard card

The card is loaded automatically with the integration. Edit a dashboard, choose **Add card** and
search for **Maico KWL**, or in YAML:

```yaml
type: custom:maico-kwl-card
```

What the card shows and how to choose a unit: [Dashboard card](docs/dashboard-card.md).

## Documentation

| Topic | What you find there |
|---|---|
| [Compatibility and requirements](docs/compatibility.md) | Supported units, Home Assistant versions, the one-connection limit and the Modbus TCP proxy, known limitations |
| [Configuration](docs/configuration.md) | Setup, reconfigure, options, accessory detection, how data is updated, removal |
| [Entities](docs/entities.md) | All entity types, entity IDs, availability, the fan entity, fault and notice codes, unit clock, airflow limits |
| [Calculated values](docs/calculated-values.md) | Heat recovery power, energy and efficiency, humidity values, filter reminders, formulas and limits |
| [Bus inputs](docs/bus-inputs.md) | Feeding room temperature, humidity and air quality from Home Assistant to the unit |
| [Dashboard card](docs/dashboard-card.md) | Adding the card and what it shows |
| [Automations](docs/automations.md) | Actions and triggers, the `maico_kwl.boost` action, example blueprints |
| [Modbus, registers and discovery](docs/modbus.md) | Communication, register map, discovery and its limits, deviations from the Maico documentation |
| [Troubleshooting](docs/troubleshooting.md) | Common problems, repair issues, diagnostics for a bug report |

## Removal

1. **Settings > Devices & Services > Maico KWL > ⋮ > Delete**.
2. In HACS open "Maico KWL" and choose **Remove** (or delete `custom_components/maico_kwl`).
3. Restart Home Assistant and delete Maico KWL cards from your dashboards.

Settings written to the unit stay on the unit. Before removing, read the notes on blueprints and
bus inputs under [Removal](docs/configuration.md#removal).

## Support and contributing

- **Questions and ideas**: [Discussions][discussions].
- **Bugs**: open a [bug report][bug-report] and attach the diagnostics (**Settings > Devices &
  Services > Maico KWL > ⋮ > Download diagnostics**). They list every register in use with its
  value and raw words, and make most questions answerable without access to the unit.
  See also [Troubleshooting](docs/troubleshooting.md).
- **Other units**: this project grows from real-world device data. A
  [unit report][device-report] helps, also when everything works, especially from other Maico
  models. Register corrections are just as welcome.
- **Code and translations**: development setup, adding a register, working on the dashboard card
  and pull requests are described in [CONTRIBUTING.md](CONTRIBUTING.md).

## License / disclaimer

Unofficial community project, provided as-is and not affiliated with Maico. Use at your own risk:
write operations in particular change real device settings. See [LICENSE](LICENSE).

<!-- Badges -->
[discussions]: https://github.com/mkshb/hass-maico-kwl/discussions
[bug-report]: https://github.com/mkshb/hass-maico-kwl/issues/new?template=bug_report.yml
[device-report]: https://github.com/mkshb/hass-maico-kwl/issues/new?template=device_report.yml
[releases-shield]: https://img.shields.io/github/release/mkshb/hass-maico-kwl.svg?style=for-the-badge
[releases]: https://github.com/mkshb/hass-maico-kwl/releases
[validate-shield]: https://img.shields.io/github/actions/workflow/status/mkshb/hass-maico-kwl/validate.yml?branch=main&style=for-the-badge&label=validate
[validate]: https://github.com/mkshb/hass-maico-kwl/actions/workflows/validate.yml
[commits-shield]: https://img.shields.io/github/commit-activity/y/mkshb/hass-maico-kwl.svg?style=for-the-badge
[commits]: https://github.com/mkshb/hass-maico-kwl/commits/main
[license-shield]: https://img.shields.io/github/license/mkshb/hass-maico-kwl.svg?style=for-the-badge
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge
[hacs-repo-badge]: https://my.home-assistant.io/badges/hacs_repository.svg
[hacs-repo]: https://my.home-assistant.io/redirect/hacs_repository/?owner=mkshb&repository=hass-maico-kwl&category=integration
[config-flow-badge]: https://my.home-assistant.io/badges/config_flow_start.svg
[config-flow]: https://my.home-assistant.io/redirect/config_flow_start/?domain=maico_kwl
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40mkshb-blue.svg?style=for-the-badge
[user_profile]: https://github.com/mkshb
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
