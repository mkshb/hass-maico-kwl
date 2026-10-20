# Automations

[README](../README.md) | [Documentation overview](../README.md#documentation)

The integration is a clean **control surface**. The control *policy* (when to change mode/level)
is best done with Home Assistant automations, which can react to anything (presence, windows,
schedule, outdoor temperature, electricity price, sensors from other rooms). That is more flexible
than the unit's built-in *Auto sensor* mode, which only uses the sensors configured on the device.

## Actions

**Control (use as actions):** `fan` *Ventilation* (`fan.set_percentage`, `fan.set_preset_mode`,
`fan.turn_off`), `select` *Operating mode* and *Ventilation level*, `switch` *Boost ventilation*,
`number` *Room temperature setpoint* / *Ventilation level duration*, `select` *Season*. Set them
with `select.select_option`, `switch.turn_on`, `number.set_value`.

How the fan maps speeds and presets onto the unit is described under
[The Ventilation fan](entities.md#the-ventilation-fan). Selects compare and set their state by
slug, see [State values are slugs](entities.md#state-values-are-slugs).

### Boost for a while

The action `maico_kwl.boost` starts the boost ventilation, e.g. from a button in the bathroom. Its
target is the *Ventilation* fan of the unit. The unit ends a boost itself after its *Ventilation
level duration* (5 to 90 minutes). With `duration`, Home Assistant ends it earlier; a `duration`
longer than the unit's *Ventilation level duration* is refused with an error, since it could not
be kept. While the unit's *Ventilation level duration* is unknown, only the limit of 1 to
90 minutes applies. A new call replaces a running timer, a call without `duration` cancels it, and
the timer is dropped when the boost ends some other way (in Home Assistant, at the control panel or
by the unit). The timer does not survive a reload or restart of
Home Assistant; the unit then ends the boost after its own duration. On a unit without the boost
register the action fails with an error.

```yaml
action: maico_kwl.boost
target:
  entity_id: fan.maico_kwl_192_168_1_50_ventilation  # the ID of your unit's fan
data:
  duration: 20
```

## Triggers

**Triggers (read):** temperatures (room, supply, extract, exhaust, air intake), *Current
ventilation level*, fan speeds / airflow, *Summer bypass*, the *Problem* binary sensor, the *Filter
due* sensors, the *Fault code* / *Notice code* sensors and their `active` attribute (see
[Fault and notice codes](entities.md#fault-and-notice-codes)), and the
[calculated values](calculated-values.md), e.g. *Absolute humidity extract air* compared with an
outdoor sensor.

The event `maico_kwl_bus_input` reports what the bus feed sends or skips, see
[Bus inputs](bus-inputs.md#activity-on-the-device-page).

## Example blueprints

Ready-to-import blueprints live in
[`blueprints/automation/maico_kwl/`](../blueprints/automation/maico_kwl):

| Blueprint | What it does |
|-----------|--------------|
| `summer_night_cooling.yaml` | Switches to a cooling mode (default *Eco supply air*, free cooling) when the outdoor air is cooler than the room after a hot day; checks again every 10 minutes and switches to the revert mode when no longer worthwhile, if the cooling mode is still set. Optional enable toggle and notification. |
| `demand_boost.yaml` | Raises the ventilation level (nominal or intensive, default intensive, in manual mode) when any HA sensor (CO2, humidity, etc.) reaches a threshold; reverts below the lower threshold (hysteresis). |
| `window_open_reduce.yaml` | Lowers the ventilation level (off, humidity protection or reduced) while a window/door contact is open; restores when all are closed. |

Import via **Settings > Automations & Scenes > Blueprints > Import Blueprint** using the raw URL,
e.g.
`https://github.com/mkshb/hass-maico-kwl/blob/main/blueprints/automation/maico_kwl/summer_night_cooling.yaml`.
These are starting points: copy and adapt them to your home.

`demand_boost` and `window_open_reduce` save the current operating mode and ventilation level in a
temporary snapshot scene before they intervene, and restore it afterwards. They leave the unit
alone if it is already in manual mode at the target level, and they keep your setting if you change
the mode or level yourself while they are active. Snapshot scenes do not survive a Home Assistant
restart: if the unit is still in the state the automation set when Home Assistant starts, the
blueprint assumes it made that change and switches to the *Fallback* operating mode once the reason
is gone; with the fallback mode "manual" it also sets the *Fallback* level. All blueprints run in
`queued` mode, so frequent triggers do not log "Already running" warnings.

To remove them, delete the automations created from the blueprints, and the blueprints themselves
under **Settings > Automations & Scenes > Blueprints** if you no longer need them.
