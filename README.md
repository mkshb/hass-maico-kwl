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
  on every change and refreshed every 8 minutes, since the unit only keeps a bus value for 10.
  No automation needed. Values in an unsuitable unit or outside the register's range are not
  sent, see [Bus inputs](#bus-inputs).
- **Decoding** based on the Maico Modbus map: ÷10 scaling, signed values, 32-bit counters via
  High-/Low-word pairs, enum states. A few registers deliberately differ from the documentation
  after checks on a real unit, see [Scaling and deviations](#scaling-and-deviations-from-the-maico-documentation).
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
- **Repair issues** under *Settings > System > Repairs* while the unit reports a fault (listing the
  active fault bits), a fitted filter is due or its clock is off by more than 5 minutes. They
  disappear on their own once the problem is gone, and are removed when the integration is unloaded.
- **Diagnostics** download with every discovered register, its value and raw words.
- **Automation blueprints** for demand boost, open windows and summer night cooling.
- **Local**: purely local Modbus communication, no cloud (`iot_class: local_polling`).

### Entity types

| Platform         | Examples |
|------------------|----------|
| `sensor`         | Temperatures (room, supply, extract, exhaust, intake, etc.), humidity, CO2, VOC, fan speeds, airflow rates, filter remaining time, operating hours, fault/notice code (with the active bits as the `active` attribute), current ventilation level, states (brine pump, dampers), EnOcean wireless sensors, deviation of the unit clock from Home Assistant, the [calculated values](#calculated-values), and per fed bus input a *(sent)* sensor with the value last written (see [Bus inputs](#bus-inputs)) |
| `binary_sensor`  | Supply/exhaust fan active, summer bypass, PTC heater, relays, switch contact, derived "Problem" sensor (from fault code), device/outdoor/room filter dirty and frost protection (from notice code bits), *Filter due* per fitted filter |
| `fan`            | *Ventilation*: operating mode and ventilation level as one fan (levels as speeds, operating modes as presets), for voice assistants, HomeKit and fan cards. Only created when both registers are present. |
| `number`         | Filter intervals, ventilation level duration, airflow rates (reduced/nominal/intensive), room temperature setpoint/max/offset, min. supply temperature for cooling, allowed filter delta-p, plus write-only **bus inputs** (room temperature / humidity / air quality fed over Modbus) |
| `select`         | Operating mode, ventilation level, season, language, room temperature source |
| `switch`         | Disable off level, lock control panel, boost ventilation |
| `button`         | Reset filter (device/outdoor/room), reset errors, sync the unit clock with Home Assistant, rediscover registers |

Around **100 registers** are mapped in total. Rarely used or duplicated sensors (EnOcean banks,
wired sensors 1 to 4, external room temperature, ZP1 states and counters) are still discovered but
**disabled by default** to keep the UI tidy. They can be enabled individually when needed.

**Entity IDs**: the device is named after the config entry, by default *Maico KWL (&lt;host&gt;)*.
Entity IDs therefore contain the host, e.g. `fan.maico_kwl_192_168_1_50_ventilation` for host
`192.168.1.50`. Rename the device before you write automations if you want shorter IDs.

**Availability**: an entity is unavailable while its register could not be read in the last poll,
and all entities are unavailable while the unit is not reachable. Buttons and write-only bus inputs
stay available as long as the connection works.

### Calculated values

Some useful values have no register of their own. They are calculated from the registers that are
there, and each is only created when the unit has all the registers it needs. A calculated value is
unavailable while one of its inputs is missing from the last poll, or is no valid measurement: a
temperature outside the documented measuring range of −30 to 120 °C (e.g. a sensor fault), a
humidity outside 0 to 100 % or an airflow above 1000 m³/h. The sensors of the registers themselves
still show what the unit reports.

| Sensor | Calculation |
|--------|-------------|
| *Heat recovery power* (W) | Supply airflow (653) × 0.34 Wh/(m³·K) × (supply air (704) − air intake temperature (703)). Negative while the exchanger cools the supply air; the value is not clamped. Since the supply air is measured after the fan and any heater, their heat is included. The *Heat recovery energy* sensor below adds it up. |
| *Heat recovery energy* (kWh) | The heat recovery power integrated between polls (trapezoidal rule), as a total that only increases: negative power counts as 0. The total is restored after a restart. A gap between two readings longer than 10 minutes, or two scan intervals if that is longer, is not counted, and neither is a reading above 10 kW, which no residential unit reaches. Long-term statistics give daily, monthly and yearly values. |
| *Heat recovery efficiency* (%) | (supply air − air intake) / (extract air (705) − air intake), the temperature efficiency of the exchanger. Unknown while extract and intake air are less than 5 K apart. Close to 0 while the summer bypass is open; fan heat can push it slightly above 100. A slow decline in winter hints at a dirty exchanger or a leaking bypass damper. |
| *Airflow imbalance* (m³/h) | Supply minus exhaust airflow (653 − 654, diagnostic). Positive: more air goes in. A lasting deviation hints at a clogged filter on one side or a calibration that is off. |
| *Absolute humidity extract air* (g/m³), *Dew point extract air* (°C) | From the extract air temperature (705) and humidity (750), Magnus formula (Sonntag 1990). The dew point is unknown at 0 % humidity. The absolute humidity can be compared with an outdoor sensor, e.g. to decide whether more ventilation dries the home. |
| *Filter due device / outdoor / room* (on/off), *Filter next change* (date) | From the remaining filter days (655 to 657): a filter is due once its days reach 0, the date is today plus the smallest number of days left of the fitted filters. Use these for filter change reminders. |

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
[Options](#options)). If you fit an accessory later, press *Rediscover registers* once it is set up
on the unit. If you chose the accessories yourself and had left this one out, select it there
instead: your choice stays in force for the accessories it covered.

### Discovery and its limits

> [!IMPORTANT]
> Discovery tells which registers **answer**, not which model you have. Keep these limits in mind:
>
> - **No model or serial number.** The Maico register map has neither. The device model shown in
>   Home Assistant is a capability profile built from the registers in use, e.g.
>   *Maico KWL (EnOcean, CO2, ZP1)*. It is not a model name. The type-dependent airflow limits
>   (154 to 156) are not used for it; the airflow numbers always allow 80 to 300 m³/h.
> - **One device per config entry.** Since there is no serial number, the device is identified by
>   its config entry, and a second entry with the same host, port and Modbus address is refused.
> - **Is it a Maico KWL at all?** Before setup, and on every poll, a few registers every Maico KWL
>   has are checked against the values its documentation allows: language (108), room temperature
>   source (109), operating mode, boost, season and ventilation level (550 to 554) and current
>   ventilation level (650). If a value is out of range, or none of them can be read, the device is
>   not taken for a Maico KWL: it is not set up (Home Assistant retries), and while running
>   **nothing is written to it** (neither bus values nor your own changes) and a repair issue says
>   why. This protects another Modbus device that got the unit's IP address. It cannot tell one
>   Maico KWL from another.
> - **Proxies can hide missing registers.** A register counts as missing only when the unit answers
>   with Modbus exception 1, 2 or 3 (e.g. *Illegal Data Address*). Some gateways and proxies answer
>   every address, then nothing is filtered.
> - **Accessories are guessed from values** (see [Accessories](#accessories)), and the PTC heater and
>   the ZP1 module cannot be detected at all.
> - **Write-only registers cannot be probed.** The bus inputs 707, 763 and 764 are assumed to exist
>   when *Room temperature source* (109) answers, the error reset (405) when the fault code answers,
>   the clock sync when the clock answers.
>
> If the unit is busy or a gateway reports its target as unreachable (exception 5, 6, 10 or 11), or
> the connection drops, discovery stops and Home Assistant retries the setup instead of storing an
> incomplete result. A register that answers with any other exception (e.g. 4, *Slave Device
> Failure*) is asked three times; if the exception stays, it is left out and a warning names it
> in the log.

The discovery result is stored in the config entry. The unit is probed again when you press
*Rediscover registers*, after **Reconfigure**, and after an update that knows registers the stored
result does not cover or that stores the result in a newer format.

## Requirements

- Home Assistant **2025.10** or newer (the minimum in `hacs.json`). Development and the automated
  tests use the current Home Assistant release; older releases within the supported range are not
  tested automatically. The integration's icon and logo are shown from Home Assistant 2026.3.
- The Maico unit must be reachable via **Modbus TCP**, directly or through a gateway / Modbus
  proxy.

> [!IMPORTANT]
> **A Modbus TCP proxy is strongly recommended.** The Maico KWL accepts only **one** Modbus TCP
> connection at a time; it silently ignores a second one (checked on a live unit). Connected
> directly, Home Assistant holds that one connection, and any other Modbus program (a diagnostic
> tool, a second Home Assistant, a script) cannot connect, or blocks Home Assistant while it is
> connected. A Modbus TCP proxy between the unit and its clients keeps the one connection to the
> unit and lets several clients share it. The integration is developed and tested behind such a
> proxy.
- `pymodbus` 3.11.2 or newer (`manifest.json`). Home Assistant installs it when needed; no separate
  installation is required. The integration passes the Modbus address as `device_id`, which older
  pymodbus versions do not accept.

> Note: this integration speaks **Modbus TCP** only. Modbus RTU (serial) is not currently
> supported.

## Supported devices

- **Maico KWL units with Modbus TCP**, whose register map matches the Maico KWL Modbus
  documentation (`docs/modbus.csv`). According to that documentation, Modbus TCP is available from
  firmware **V1.1.1**.
- Units without some of the optional parts (EnOcean, ZP1, brine ground heat exchanger, extra
  sensors) are supported: registers the unit does not implement get no entity, and accessories that
  answer anyway are left out as described under [Accessories](#accessories).
- Tested so far with **one unit**, connected through a Modbus TCP proxy. Reports from other models
  are welcome, see [Contributing](#contributing).
- Not supported: Modbus RTU (serial) and other Maico product lines with a different register map.

## Installation

### Via HACS (recommended)

1. In HACS > **Custom repositories**, add `https://github.com/mkshb/hass-maico-kwl` with category
   **Integration**.
2. Install "Maico KWL". HACS downloads the `maico_kwl.zip` attached to the release.
3. Restart Home Assistant.

### Manual

1. Download `maico_kwl.zip` from the [latest release][releases] and unpack it into
   `custom_components/maico_kwl` of your Home Assistant configuration, or copy the
   `custom_components/maico_kwl` folder of the release source. The `main` branch may contain
   unreleased changes.
2. Restart Home Assistant.

After an update, restart Home Assistant and reload the dashboard in the browser once, so the
browser loads the new card.

## Configuration

1. **Settings > Devices & Services > Add Integration** > "Maico KWL".
2. Enter the connection details:
   - **Host**: IP/hostname of the unit or gateway
   - **Port**: default `502`
   - **Modbus address**: default `10` (1 to 247)
   - **Scan interval**: default `30` seconds, 5 to 3600 (changeable later via the options)
3. The integration checks that a Maico KWL answers (see
   [Discovery and its limits](#discovery-and-its-limits)), then probes the registers and creates
   the entities.

To change host, port or Modbus address later, use **Reconfigure** on the integration. The unit is
probed again; entities that are still found keep their IDs, names and history. If the connection
points somewhere else, a manual accessory choice is dropped and detection decides again.

### Options

Use **Configure** on the integration to:

- change the **scan interval**,
- choose the **fitted accessories** (see [Accessories](#accessories)), and
- pick a **source entity** for each "bus" input (room temperature, humidity, air quality).

The accessories are preselected with what discovery detected. Only accessories the unit answers to
are listed. A choice that differs from the detected one is kept, also after *Rediscover
registers*; select the detected accessories again to let discovery decide. The choice only covers
the accessories listed when you made it: one the unit answers to only later (fitted afterwards, or
added in a new version of the integration) is detected as usual.

For the bus source entities, see [Bus inputs](#bus-inputs). Changing the options reloads the
integration.

### Bus inputs

The unit can take room temperature, humidity and air quality from the Modbus master instead of its
own sensors. These three registers are **write-only**, and a value written to them is only valid
for 10 minutes (the Maico documentation: "Schreibzyklus min. 10 min"). If no new room temperature
arrives within that time, the unit falls back to its internal sensor. The integration therefore
writes every 8 minutes, and after a failed write it tries again every minute until one succeeds:
the retries at 9 and 10 minutes still come before the value expires. The unit sets no upper limit
on how often the values may be written.

| Register | Number entity (manual) | Source entity in the options | Source units accepted | Range | Resolution |
|---|---|---|---|---|---|
| 707 room temperature | *Room temperature (bus)* | `sensor` with device class `temperature` | °C, °F, K (converted to °C) | 0 to 40 °C | 0.1 °C |
| 763 humidity | *Humidity (bus)* | `sensor` with device class `humidity` | % | 0 to 100 % | 1 % |
| 764 air quality | *Air quality (bus)* | any `sensor` | ppm, ppb (converted to ppm) | 0 to 5000 ppm | 1 ppm |

> [!IMPORTANT]
> - **Source has priority.** With a source entity configured, its value is written right after
>   setup, on every state change and every **8 minutes**. The manual `number` for that input is
>   not created then; leave the option empty to set the value manually instead.
> - **Manual numbers** keep their value across restarts, write it again after a restart and every
>   8 minutes.
> - **Only suitable values are sent.** The source needs one of the units above; a source without
>   a unit (e.g. an air quality index) or in another unit (e.g. µg/m³) is not sent. Values are
>   rounded to the resolution above, e.g. 55.4 % is sent as 55 %. A value outside the range is
>   not sent either, instead of sending the limit: a faulty sensor must not look like a real
>   reading to the unit.
> - **Invalid states are skipped.** `unknown`, `unavailable`, empty, non-numeric, `nan` and
>   `inf` states are not written.
> - **Skipped values are logged.** While nothing is sent, no new value reaches the unit; 10 minutes
>   after the last one it uses its internal room temperature sensor again. The log says once why a
>   source is not sent, and again when it is sent again.
> - **Renamed sources are followed.** If you change the entity ID of a source, the option is
>   updated and the integration reloads once.
> - **Repair issues for a configured source**: one when the source no longer exists, and one when
>   it has given no value that can be sent for more than 30 minutes (e.g. it stays unavailable,
>   has the wrong unit or is out of range). They are checked every 8 minutes once Home Assistant
>   has started, and disappear with the next value sent. Inputs without a source get no issue.
> - **The unit has to use the bus value.** For room temperature set the *Room temperature source*
>   select to **"Bus"**. Humidity and air quality have no such register in the Maico map; how the
>   unit selects the bus for them is not documented there.
> - **Failed writes are retried every minute** and logged once. If a bus input has had no valid
>   value for 10 minutes, a repair issue says so until the next write succeeds; this applies to
>   manual numbers as well.

With a source entity configured, a sensor *Room temperature bus (sent)*, *Humidity bus (sent)* or
*Air quality bus (sent)* shows the value the unit last received, as encoded on the wire. It is
unknown until the first successful write and keeps the previous value while writes fail. Its
attributes `source_entity` and `last_written` (time of the last successful write) tell where the
value comes from and how old it is. The [dashboard card](#dashboard-card) marks a bus value as
stale from 10 minutes on.

### How data is updated

- **Polling**: all readable registers in use are read every *scan interval* (default 30 s, 5 to
  3600 s); registers of accessories that are not fitted are not read. Directly adjacent registers
  are read in one request of up to 100 registers. If the unit rejects a block, its registers are
  read one by one; a register that still fails is unavailable until the next poll.
- **Writes**: changing a control writes the register right away and then refreshes all values, so
  the new state shows up without waiting for the next poll.
- **Bus inputs**: a configured source entity is written on every change and at least every
  8 minutes, and every minute after a failed write. Manual bus numbers are rewritten the same way,
  see [Bus inputs](#bus-inputs).
- **Discovery**: the register probe runs once at the first setup and its result is stored in the
  config entry, so restarts are fast. Press the *Rediscover registers* button to probe again, e.g.
  after a firmware update or after adding sensors or filters to the unit, see
  [Discovery and its limits](#discovery-and-its-limits).
- **Cleanup**: after every setup, entities the integration no longer creates are disabled, e.g.
  registers a rediscovery did not find again, accessories that are no longer selected, or the
  *(sent)* sensor of a bus input without a source. They keep their names, areas and entity IDs:
  once they are created again, the integration enables them again and Home Assistant reloads the
  integration once about 30 seconds later. Entities you disabled yourself stay disabled. Delete
  entities you no longer need under *Settings > Devices & Services > Entities*.

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
- **Controls**: operating mode, boost, season and, below them, the ventilation level. The level bar
  shows the level that runs; where the unit picks it itself (auto modes) or runs another one (off,
  boost) it is locked. A change shows at once and pulses until the unit reports it, which can take
  a few seconds. A tap on the season opens its entity to switch between summer and winter.
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

The fan has four speeds (humidity protection, reduced, nominal, intensive; 25 % steps) and the
operating modes except *off* as presets. Setting a speed switches the unit to manual mode first,
since the auto modes pick the level themselves. The percentage shows the level that is actually
running (*Current ventilation level*). `fan.turn_on` without arguments returns to the last mode.

**Boost for a while:** the action `maico_kwl.boost` starts the boost ventilation, e.g. from a button
in the bathroom. Its target is the *Ventilation* fan of the unit. The unit ends a boost itself after
its *Ventilation level duration* (5 to 90 minutes). With `duration`, Home Assistant ends it earlier;
a `duration` longer than the unit's *Ventilation level duration* is refused with an error, since it
could not be kept. A new call replaces a running timer. The timer does not survive a reload or
restart of Home Assistant; the unit then ends the boost after its own duration. On a unit without
the boost register the action fails with an error.

```yaml
action: maico_kwl.boost
target:
  entity_id: fan.maico_kwl_192_168_1_50_ventilation  # the ID of your unit's fan
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
- **Discovery via proxy**: some Modbus proxies/devices answer *every* address instead of returning
  an error for missing registers. In that case the probe cannot filter anything; the accessory
  detection and the entities disabled by default still keep the overview lean. See
  [Discovery and its limits](#discovery-and-its-limits).
- **Airflow limits**: the *Airflow reduced / nominal / intensive* numbers allow 80 to 300 m³/h, the
  general limits of the Maico Modbus documentation. According to it the limits depend on the unit
  type, and there is no register that tells them, so your unit may allow less. Set the airflows
  within the limits the manufacturer or your installer gives for your unit. Whether the unit
  refuses a value outside its own limits, cuts it to them or takes it as it is, has not been
  checked yet; if a value springs back after the next update, the unit did not take it.
- **State values are slugs**: select and enum sensors store internal slugs (e.g. `manual`,
  `reduced`, `summer`) and display the translated text. Automations/templates should compare
  against the **slug**, not the displayed text.
- **Unit clock**: the unit keeps local time without a time zone. *Clock deviation* is the unit's
  time minus Home Assistant's time in seconds (positive: the unit is ahead); changes below 2 s are
  not shown. *Sync clock* writes Home Assistant's local time to registers 100 to 105 in one request.
  A repair issue appears at a deviation of more than 5 minutes.
- **Bus feed units**: see [Bus inputs](#bus-inputs); °F, K and ppb are converted, other units are
  not sent.

### Scaling and deviations from the Maico documentation

| Registers | Maico documentation | Integration | Status |
|---|---|---|---|
| 300, 302, 553, 700 to 707 (temperatures) | signed, ×10 | signed 16 bit, ÷10 | as documented |
| 301 *Supply temp min cooling* | Format °C, comment "step 1 (= 0.1 °C)" | **not scaled**, whole °C (8 to 29) | deviates; a live unit reports 14 |
| 750 to 754 (humidity) | ×10 | **not scaled**, whole % | deviates; checked on a live unit |
| 358 to 365 (EnOcean humidity) | raw 0 to 1000 for 0 to 100 % | **not scaled**, whole % | deviates by analogy with 750; not checked on a unit |
| 350 to 357, 366 to 373, 755 to 762 (CO2, VOC) | ×10 | ÷10 | as documented; not checked against real readings |
| 763, 764 (humidity and air quality bus) | 0 to 100 %, 0 to 5000 ppm | not scaled | as documented |
| 401/402, 403/404, 850 to 869 | High-Word / Low-Word | one unsigned 32-bit value each | as documented |
| 154 to 156 (airflow setpoints) | limits depend on the unit type | fixed 80 to 300 m³/h | see *Airflow limits* above |

## Troubleshooting

**"Failed to connect" during setup, or the integration keeps retrying**
- Check host, port (default `502`) and Modbus address (default `10`) against the settings of the
  unit or the gateway. Connection settings can be changed later with **Reconfigure** on the
  integration.
- Make sure Modbus TCP is enabled on the unit (firmware V1.1.1 or newer) and that no firewall
  blocks the port.
- The unit accepts only one Modbus TCP connection at a time and ignores further ones: check that
  no other program (or a second entry of this integration) is connected to it. A Modbus TCP proxy
  lets several clients share the one connection, see [Requirements](#requirements).

**"The device does not look like a Maico KWL"**
- The device at host, port and Modbus address reports a value a Maico KWL does not have; the
  message names the register and the value. Check that the address belongs to the unit (e.g. after
  the router gave its IP address to another device), and correct it with **Reconfigure**.
- If it is your Maico unit, please open an issue with the message: its firmware may use a value
  the documentation does not list.

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
- The unit does not monitor this filter. Once it is fitted and enabled on the unit, press
  *Rediscover registers*, or select it under **Configure** if you chose the accessories yourself.

**A bus input has no effect**
- The matching source on the unit must be set to **"Bus"**, e.g. the *Room temperature source*
  select for the room temperature.

**New registers or features are missing after a firmware update**
- Press the *Rediscover registers* button on the device page.

**The dashboard card is missing or shows "Custom element doesn't exist"**
- Reload the page in the browser; in the companion app, reset the frontend cache in the app
  settings. The card is loaded with the rest of the frontend, so a page that was open before the
  integration was set up or updated does not know it yet. The card's URL changes with every new
  version, so a reload is enough to get it.
- The card needs the integration to be set up; without a configured unit it is not loaded.

**Collecting information for a bug report**
- Download the diagnostics: **Settings > Devices & Services > Maico KWL > ⋮ > Download
  diagnostics**. They contain the capability profile, every discovered register with its value
  and raw words, the absent registers and the last bus writes; host and title are removed.
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
unit. Bus inputs are no longer refreshed: 10 minutes after the last value the unit uses its internal
room temperature sensor again, while *Room temperature source* still says "Bus". Set it to another
source before removing the integration if the setting should say so as well.

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

How to set up a development environment, add a register, work on the dashboard card and open a
pull request is described in [CONTRIBUTING.md](CONTRIBUTING.md).

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
