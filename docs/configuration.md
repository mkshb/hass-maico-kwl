# Configuration

[README](../README.md) | [Documentation overview](../README.md#documentation)

## Setup

[![Open your Home Assistant instance and start setting up Maico KWL.][config-flow-badge]][config-flow]

1. Start the setup with the button above, or go to **Settings > Devices & Services > Add
   Integration** > "Maico KWL".
2. Enter the connection details:
   - **Host**: IP/hostname of the unit or gateway
   - **Port**: default `502`
   - **Modbus address**: default `10` (1 to 247)
   - **Scan interval**: default `30` seconds, 5 to 3600 (changeable later via the options)
3. The integration checks that a Maico KWL answers (see
   [Discovery and its limits](modbus.md#discovery-and-its-limits)), then probes the registers and
   creates the entities.

A second entry with the same host, port and Modbus address is refused; the host is compared
without regard to upper and lower case.

## Reconfigure

To change host, port or Modbus address later, use **Reconfigure** on the integration. The unit is
probed again; entities that are still found keep their IDs, names and history. If the connection
points somewhere else, a manual accessory choice is dropped and detection decides again. The scan
interval and the bus source entities are kept. The entry title follows the new host, unless you
renamed the entry.

## Options

Use **Configure** on the integration to:

- change the **scan interval**,
- choose the **fitted accessories** (see [Accessories](#accessories)), and
- pick a **source entity** for each "bus" input (room temperature, humidity, air quality).

The accessories are preselected with your own choice, or without one with what discovery detected.
Only accessories the unit answers to are listed; while no discovery result is stored, the choice is
not offered and an earlier choice is kept. A choice that differs from the detected one is kept,
also after *Rediscover registers*; select the detected accessories again to let discovery decide.
The choice only covers the accessories listed when you made it: one the unit answers to only later
(fitted afterwards, or added in a new version of the integration) is detected as usual.

For the bus source entities, see [Bus inputs](bus-inputs.md). Changing the options reloads the
integration.

## Accessories

Some parts are not fitted to every unit. Their registers answer on every unit anyway, so the
register probe cannot tell whether they are there. Discovery therefore reads their values once and
decides from those:

| Accessory | Entities | Detected as fitted when |
|---|---|---|
| Outdoor filter, room filter | Interval, reset button, remaining time, *Filter due*, *dirty* binary sensor, repair issue | The filter has days left, or it has run out and the unit reports it as dirty. Without such a filter the unit keeps the days at 0, never reports it as dirty and ignores a filter change. Some units do not report a filter that ran out as dirty either, so a filter detected before stays fitted when a later discovery (*Rediscover registers*, a reconfigure with the same connection, or the automatic one after an update) finds it at 0 days. |
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
[Options](#options)). If you fit an accessory later, press *Rediscover registers* once it is set up
on the unit. If you chose the accessories yourself and had left this one out, select it there
instead: your choice stays in force for the accessories it covered.

## How data is updated

- **Polling**: all readable registers in use are read every *scan interval* (default 30 s, 5 to
  3600 s); registers of accessories that are not fitted are not read. Directly adjacent registers
  are read in one request of up to 100 registers. If the unit rejects a block, its registers are
  read one by one; a register that still fails is unavailable until the next poll. If the unit is
  not reachable, the whole poll fails right away, all entities are unavailable and the next poll
  tries again.
- **Writes**: changing a control writes the register right away and then asks for a refresh of all
  values, so the new state shows up without waiting for the next poll. Several changes in quick
  succession share one refresh, so the last one may take a moment to show. Failed writes show an
  error message in the UI.
- **Bus inputs**: a configured source entity is written on every change and at least every
  8 minutes, and every minute after a failed write, see [Bus inputs](bus-inputs.md). Inputs without
  a source are not written; the unit uses its own sensor.
- **Discovery**: the register probe runs once at the first setup and its result is stored in the
  config entry, so restarts are fast. Press the *Rediscover registers* button to probe again, e.g.
  after a firmware update or after adding sensors or filters to the unit; the integration reloads,
  so its entities are unavailable for a moment. See
  [Discovery and its limits](modbus.md#discovery-and-its-limits).
- **Cleanup**: after every setup, entities the integration no longer creates are disabled, e.g.
  registers a rediscovery did not find again, accessories that are no longer selected, or the
  *(sent)* sensor of a bus input without a source. They keep their names, areas and entity IDs:
  once they are created again, the integration enables them again and Home Assistant reloads the
  integration once about 30 seconds later. Entities you disabled yourself stay disabled. Delete
  entities you no longer need under *Settings > Devices & Services > Entities*.

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
unit. Bus inputs are no longer refreshed: 10 minutes after the last value the unit uses its internal
room temperature sensor again, while *Room temperature source* still says "Bus". Set it to another
source before removing the integration if the setting should say so as well.

[config-flow-badge]: https://my.home-assistant.io/badges/config_flow_start.svg
[config-flow]: https://my.home-assistant.io/redirect/config_flow_start/?domain=maico_kwl
