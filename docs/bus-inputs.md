# Bus inputs

[README](../README.md) | [Documentation overview](../README.md#documentation)

The unit can take room temperature, humidity and air quality from the Modbus master instead of its
own sensors. The integration can feed these "bus" inputs from a Home Assistant source entity, with
no automation needed.

## How it works

The three bus input registers are **write-only**, and a value written to them is only valid for
10 minutes (the Maico documentation: "Schreibzyklus min. 10 min"). If no new room temperature
arrives within that time, the unit falls back to its internal sensor. The integration therefore
writes every 8 minutes, and after a failed write it tries again every minute until one succeeds:
the retries at 9 and 10 minutes still come before the value expires. The unit sets no upper limit
on how often the values may be written.

| Register | Source entity in the options | Source units accepted | Range | Resolution |
|---|---|---|---|---|
| 707 room temperature | `sensor` with device class `temperature` | °C, °F, K (converted to °C) | 0 to 40 °C | 0.1 °C |
| 763 humidity | `sensor` with device class `humidity` | % | 0 to 100 % | 1 % |
| 764 air quality | any `sensor` | ppm, ppb (converted to ppm) | 0 to 5000 ppm | 1 ppm |

## Setting a source

Under **Configure** on the integration, pick a **source entity** for each bus input you want to
feed (see [Options](configuration.md#options)). Changing the options reloads the integration.

> [!IMPORTANT]
> - **Only with a source.** With a source entity configured, its value is written right after
>   setup, on every state change that changes the value sent (after rounding) and every
>   **8 minutes**. Without a source, nothing is sent and
>   the unit uses its own sensor. For a fixed value, use a template sensor with the device class
>   and unit above as the source.
> - **Only suitable values are sent.** The source needs one of the units above; a source without
>   a unit (e.g. an air quality index) or in another unit (e.g. µg/m³) is not sent. Values are
>   rounded to the resolution above, e.g. 55.4 % is sent as 55 %. A value outside the range is
>   not sent either, instead of sending the limit: a faulty sensor must not look like a real
>   reading to the unit.
> - **Invalid states are skipped.** `unknown`, `unavailable`, empty, non-numeric, `nan` and
>   `inf` states are not written.
> - **Skipped values are logged.** While nothing is sent, no new value reaches the unit; 10 minutes
>   after the last one it uses its internal room temperature sensor again. For a value in an
>   unsuitable unit, out of range or not numeric, the log says once why the source is not sent,
>   and again when it is sent again. `unknown`, `unavailable` and empty states are skipped without
>   a log entry; the repair issue after 30 minutes (below) reports them.
> - **Renamed sources are followed.** If you change the entity ID of a source, the option is
>   updated and the integration reloads once.
> - **Repair issues for a configured source**: one when the source no longer exists, and one when
>   it has given no value that can be sent for more than 30 minutes (e.g. it stays unavailable,
>   has the wrong unit or is out of range; counted from the setup at the latest). They are checked
>   every 8 minutes once Home Assistant has started; the first one also appears right away when the
>   source is removed from the entity registry. Both disappear with the next value that can be
>   sent. Inputs without a source get no issue.
> - **The unit has to use the bus value.** For room temperature set the *Room temperature source*
>   select to **"Bus"**. Humidity and air quality have no such register in the Maico map; how the
>   unit selects the bus for them is not documented there.
> - **Failed writes are retried every minute** and logged once. If writes have failed for
>   10 minutes since the last successful one, a repair issue says so until the next write
>   succeeds. A source that gives no value that can be sent does not write at all, so it gets the
>   30-minute issue above instead.
> - **No writes to a device that is not a Maico KWL.** While the identity check fails (see
>   [Discovery and its limits](modbus.md#discovery-and-its-limits)), bus writes count as failed
>   writes.

## Activity on the device page

What is sent to the bus shows up under **Activity** on the device page and in the logbook, e.g.
*"Maico KWL sent humidity 49 % to the bus (source sensor.bathroom_humidity)"*: the first value
after a start, then a changed value, at most one entry per input every 8 minutes (with the latest
value). The regular refresh of an unchanged value is not listed. Also listed: a source whose value
is not sent (with the reason, for the cases the log names), a write that failed, writes that
succeed again, and writes that have failed for 10 minutes since the last successful one.

The entries are the event `maico_kwl_bus_input` (data: `entry_id`, `device_id`, `input`,
`kind` = `sent`, `skipped`, `failed`, `recovered` or `expired`, plus `value`, `unit`, `source`,
`reason` or `error` depending on the kind), which can also trigger automations. They are in German or English, following the
language of Home Assistant.

## Sent value sensors

With a source entity configured, a sensor *Room temperature bus (sent)*, *Humidity bus (sent)* or
*Air quality bus (sent)* shows the value the unit last received, as encoded on the wire. It is
unknown until the first successful write and keeps the previous value while writes fail. Its
attributes `source_entity` and `last_written` (time of the last successful write) tell where the
value comes from and how old it is. The value is not restored: after a restart or reload it is
unknown again until the next successful write. The [dashboard card](dashboard-card.md) marks a bus value as
stale from 10 minutes on.

The bus inputs have no `number` entity of their own; they are only fed from a source entity.

## Discovery of the bus inputs

Write-only registers cannot be probed. The bus inputs 707, 763 and 764 are assumed to exist when
*Room temperature source* (109) answers, see
[Discovery and its limits](modbus.md#discovery-and-its-limits). If it does not answer, a source
set for a bus input is not used.

## Removing the integration

Without the integration, bus inputs are no longer refreshed: 10 minutes after the last value the
unit uses its internal room temperature sensor again. Set *Room temperature source* to another source first if the setting
should say so as well, see [Removal](configuration.md#removal).

## Troubleshooting

See [A bus input has no effect](troubleshooting.md#a-bus-input-has-no-effect).
