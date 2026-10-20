# Entities

[README](../README.md) | [Documentation overview](../README.md#documentation)

The integration creates one entity per register the unit answers, on the platform that fits the
register's access: read-only registers become sensors or binary sensors, writable ones numbers,
selects or switches. Entities for accessories the unit does not have are left out, see
[Accessories](configuration.md#accessories).

## Entity types

| Platform         | Examples |
|------------------|----------|
| `sensor`         | Temperatures (room, supply, extract, exhaust, intake, etc.), humidity, CO2, VOC, fan speeds, airflow rates, filter remaining time, operating hours, fault/notice code (with the active bits as the `active` attribute), current ventilation level, states (brine pump, dampers), EnOcean wireless sensors, deviation of the unit clock from Home Assistant, the [calculated values](calculated-values.md), and per fed bus input a *(sent)* sensor with the value last written (see [Bus inputs](bus-inputs.md#sent-value-sensors)) |
| `binary_sensor`  | Supply/exhaust fan active, summer bypass, PTC heater, reheating relay, base board contact, derived "Problem" sensor (from fault code), device/outdoor/room filter dirty and frost protection (from notice code bits), *Filter due* per fitted filter |
| `fan`            | *Ventilation*: operating mode and ventilation level as one fan (levels as speeds, operating modes as presets), for voice assistants, HomeKit and fan cards. Only created when both registers are present. See [The Ventilation fan](#the-ventilation-fan). |
| `number`         | Filter intervals, ventilation level duration, airflow rates (reduced/nominal/intensive), room temperature setpoint/max/offset, min. supply temperature for cooling, allowed filter delta-p. The write-only **bus inputs** have no `number`; they are fed from a source entity, see [Bus inputs](bus-inputs.md) |
| `select`         | Operating mode, ventilation level, season, language, room temperature source |
| `switch`         | Disable off level, lock control panel, boost ventilation |
| `button`         | Reset filter (device/outdoor/room), reset errors, sync the unit clock with Home Assistant, rediscover registers |

Around **100 registers** are mapped in total. Rarely used or duplicated sensors are still
discovered but
**disabled by default** to keep the UI tidy: the EnOcean sensors, wired sensors 1 to 4, external
room temperature (701), the ZP1 values (outdoor temperature before the air ground heat exchanger
(702), states 805 to 808 and operating hours 860 to 867) and the operating hours of the base board
contact (868/869). They can be enabled individually when needed.

Entity names are translated into English and German, including the states of selects and enum
sensors. German names are chosen so that related entities group together via shared prefixes.

## Entity IDs

The device is named after the config entry, by default *Maico KWL (&lt;host&gt;)*. Entity IDs
therefore contain the host, e.g. `fan.maico_kwl_192_168_1_50_ventilation` for host
`192.168.1.50`. Rename the device before you write automations if you want shorter IDs.

## Availability

An entity is unavailable while its register could not be read in the last poll, and all entities
are unavailable while the unit is not reachable. Buttons stay available as long as the connection
works.

When a later setup no longer creates an entity (e.g. after a rediscovery or a changed accessory
choice), it is disabled instead of deleted, see
[How data is updated](configuration.md#how-data-is-updated).

## State values are slugs

Select and enum sensors store internal slugs (e.g. `manual`, `reduced`, `summer`) and display the
translated text. Automations and templates should compare against the **slug**, not the displayed
text.

## The Ventilation fan

The fan has four speeds (humidity protection, reduced, nominal, intensive; 25 % steps) and the
operating modes except *Off* as presets. In *Manual* and *Auto sensor* a speed is set as it is, and
*Auto sensor* keeps its sensor control. In the other modes setting a speed switches the unit to
manual mode first. The percentage shows the level that is actually running (*Current ventilation
level*). `fan.set_percentage` with 0 switches the unit off (operating mode *Off*). `fan.turn_on`
without arguments returns to the last mode, or to *Manual* if no other mode was seen since the
integration was loaded; it does nothing while the fan is on.

How to use the fan and the other controls in automations is described in
[Automations](automations.md).

## Fault and notice codes

The *Fault code* and *Notice code* sensors show the raw 32-bit value of registers 401/402 and
403/404. Their `active` attribute lists the bits that are set, e.g. `["bypass_active"]` for notice
code 16; the Home Assistant UI and the [dashboard card](dashboard-card.md) show them by name, e.g.
*Bypass active*. Bits without a documented meaning appear as `bit_<n>`. The most useful bits also
have their own binary sensors: *Device filter dirty*, *Outdoor filter dirty*, *Room filter dirty*
and *Frost protection active*. The *Problem* sensor is on whenever any fault bit is set.

The Maico KWL documentation only calls these registers a bitfield. The bit meanings are taken from
the Modbus documentation of another Maico product (Geniovent), which uses the same registers. The
bit numbering was confirmed on a live unit (notice bit 4 follows the summer bypass), the meaning of
the other bits was not. For filter change reminders, the *Filter due* sensors (see
[Calculated values](calculated-values.md)) are the simpler choice: they follow the remaining days.

While the unit reports a fault, a repair issue lists the active fault bits, see
[Repair issues](troubleshooting.md#repair-issues).

## Unit clock

The unit keeps local time without a time zone. *Clock deviation* is the unit's time minus Home
Assistant's time in seconds (positive: the unit is ahead); changes below 2 s are not shown. *Sync
clock with Home Assistant* writes Home Assistant's local time to registers 100 to 105 in one request. A repair issue
appears at a deviation of more than 5 minutes.

## Airflow limits

The *Airflow reduced / nominal / intensive* numbers allow 80 to 300 m³/h, the general limits of the
Maico Modbus documentation. According to it the limits depend on the unit type, and there is no
register that tells them, so your unit may allow less. Set the airflows within the limits the
manufacturer or your installer gives for your unit. Whether the unit refuses a value outside its
own limits, cuts it to them or takes it as it is, has not been checked yet; if a value springs back
after the next update, the unit did not take it.

> [!CAUTION]
> Writable entities change real settings on the unit. Settings written to the unit stay there,
> also after the integration is removed.
