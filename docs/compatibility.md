# Compatibility and requirements

[README](../README.md) | [Documentation overview](../README.md#documentation)

## Supported devices

- **Maico KWL units with Modbus TCP**, whose register map matches the Maico KWL Modbus
  documentation ([`modbus.csv`](modbus.csv)). According to that documentation, Modbus TCP is
  available from firmware **V1.1.1**.
- Units without some of the optional parts (EnOcean, ZP1, brine ground heat exchanger, extra
  sensors) are supported: registers the unit does not implement get no entity, and accessories that
  answer anyway are left out as described under [Accessories](configuration.md#accessories).
- Tested so far with **one unit**, connected through a Modbus TCP proxy. Reports from other models
  are welcome, see [Support and contributing](../README.md#support-and-contributing).
- Not supported: Modbus RTU (serial) and other Maico product lines with a different register map.
  The register lists of other Maico products in this folder are reference material only, see
  [Register map files](modbus.md#register-map-files).

The integration cannot tell which model it talks to, since the Maico register map has neither a
model nor a serial number. It shows a capability profile instead, see
[Discovery and its limits](modbus.md#discovery-and-its-limits).

## Requirements

- Home Assistant **2026.10** or newer (the minimum in `hacs.json`). The automated tests run on
  every pull request and every day, against this minimum and against the newest release (in the
  week before a release, its beta when a test package for it is available). The run against the
  newest release only reports and does not block a change. Releases in between are not tested on
  their own.
- The Maico unit must be reachable via **Modbus TCP**, directly or through a gateway / Modbus
  proxy.
- The connection is made by the Modbus integration of Home Assistant (a dependency in
  `manifest.json`). It comes with Home Assistant; nothing to install and no `modbus:` entry in
  `configuration.yaml` is needed.

> [!NOTE]
> This integration speaks **Modbus TCP** only. Modbus RTU (serial) is not currently supported.

## One connection only

The Maico KWL accepts only **one** Modbus TCP connection at a time; it silently ignores a second one
(checked on a live unit). Whether you need a Modbus TCP proxy depends on who else talks to the unit:

- **Home Assistant is the only Modbus client**: connect it directly. Home Assistant holds the one
  connection, and integrations that take their connection from the Modbus integration of Home
  Assistant share it.
- **Other Modbus clients as well**: a `modbus:` hub in `configuration.yaml`, an integration with a
  Modbus client of its own, a diagnostic tool, a second Home Assistant or a script cannot connect
  at all, or block Home Assistant while they are connected. Put a **Modbus TCP proxy** between the
  unit and its clients: it keeps the one connection to the unit and lets several clients share it.

> [!NOTE]
> The integration is developed and tested behind such a proxy. Reports from units connected
> directly are welcome.

Entries of this integration and other integrations that take their connection from the Modbus
integration of Home Assistant share one connection for the same host and port. It shows up in the
**Modbus** panel under **Settings** > **Connectivity**. If another integration already uses the
same host and port with different connection settings, the setup fails with an error and is not
retried, see [Troubleshooting](troubleshooting.md#failed-to-connect-during-setup-or-the-integration-keeps-retrying).

## Known limitations

- **No model detection**: the device model shown in Home Assistant is a capability profile, not a
  model name, see [Discovery and its limits](modbus.md#discovery-and-its-limits).
- **Airflow limits** depend on the unit type, which the integration cannot read, see
  [Airflow limits](entities.md#airflow-limits).
- **Register addressing** is assumed to be 0-based, see
  [Register addressing](modbus.md#register-addressing).
- **Proxies can hide missing registers**, so discovery cannot filter them, see
  [Discovery and its limits](modbus.md#discovery-and-its-limits).
- **Accessories are guessed from values**, the PTC heater and the ZP1 module cannot be detected at
  all, see [Accessories](configuration.md#accessories).
- **Bus inputs**: how the unit selects the bus for humidity and air quality is not documented, see
  [Bus inputs](bus-inputs.md).
- **Fault and notice bits**: only the bit numbering was confirmed on a unit, not the meaning of
  every bit, see [Fault and notice codes](entities.md#fault-and-notice-codes).
- **Scaling**: some registers deliberately differ from the Maico documentation, see
  [Scaling and deviations](modbus.md#scaling-and-deviations-from-the-maico-documentation).
