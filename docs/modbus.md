# Modbus, registers and discovery

[README](../README.md) | [Documentation overview](../README.md#documentation)

This page is for advanced users and developers: how the integration talks to the unit, how it finds
out what the unit has, and where it deliberately differs from the Maico documentation.

## Communication

- **Modbus TCP** only, through the Modbus integration of Home Assistant, which keeps one shared
  connection per host and port (see
  [One connection only](compatibility.md#one-connection-only)).
- All registers are **holding registers**, read with FC 03, written with FC 06 (single register)
  or FC 16 (several registers, e.g. the clock).
- Word order **High-Word/Low-Word**, byte order **High-Byte/Low-Byte**, as documented by Maico.
- Default Modbus address of the unit: **10**.
- Purely local communication, no cloud (`iot_class: local_polling`).

How often values are read and written is described under
[How data is updated](configuration.md#how-data-is-updated). A response with fewer registers than
requested counts as a rejection: polling then reads the registers one by one, discovery probes
them one by one.

## Register map files

The register definitions come from the Maico KWL Modbus documentation, [`modbus.csv`](modbus.csv),
and are modelled in
[`custom_components/maico_kwl/register_defs.py`](../custom_components/maico_kwl/register_defs.py).
Some registers deliberately differ from the CSV, see
[Scaling and deviations](#scaling-and-deviations-from-the-maico-documentation).

The other CSV files in this folder are the Modbus lists of other Maico products. They are kept as
reference only; these products are **not supported**:

| File | Product |
|---|---|
| [`geniovent-modbus.csv`](geniovent-modbus.csv) | Maico GVX (Geniovent). Source of the fault and notice bit meanings, see [Fault and notice codes](entities.md#fault-and-notice-codes). |
| [`ws75-modbus.csv`](ws75-modbus.csv) | Maico WS 75 K |
| [`pp45-modbus.csv`](pp45-modbus.csv) | Maico RLS 45 K |
| [`rlt-flat-modbus.csv`](rlt-flat-modbus.csv) | Register list with a different structure (coils, input registers) |

## Register addressing

Register addressing is assumed to be 0-based (documented decimal code = protocol address). If all
entities show as "unavailable" although the connection works, a central `REGISTER_OFFSET` can be
adjusted in `register_defs.py`; please open an issue in that case.

## Discovery and its limits

At the first setup the integration probes every documented register and creates entities only for
the registers the unit answers. Registers next to each other are probed as one block; if the unit
rejects the block, each register is probed on its own.

> [!IMPORTANT]
> Discovery tells which registers **answer**, not which model you have. Keep these limits in mind:
>
> - **No model or serial number.** The Maico register map has neither. The device model shown in
>   Home Assistant is a capability profile built from the registers in use, e.g.
>   *Maico KWL (EnOcean, CO2, VOC, Summer bypass, ZP1)*. It is not a model name. The
>   type-dependent airflow limits (154 to 156) are not used for it; the airflow numbers always
>   allow 80 to 300 m³/h.
> - **One device per config entry.** Since there is no serial number, the device is identified by
>   its config entry, and a second entry with the same host, port and Modbus address is refused.
> - **Is it a Maico KWL at all?** Before every setup, and on every poll, a few registers every
>   Maico KWL has are checked against the values its documentation allows: language (108), room
>   temperature source (109), operating mode, boost, season and ventilation level (550 to 554) and
>   current ventilation level (650). If a value is out of range, or at setup none of them can be
>   read, the device is not taken for a Maico KWL: it is not set up (Home Assistant retries), and
>   while running **nothing is written to it** (neither bus values nor your own changes) and a
>   repair issue says why. Its entities keep showing the values read. This protects another Modbus
>   device that got the unit's IP address. It cannot tell one Maico KWL from another.
> - **Proxies can hide missing registers.** A register counts as missing only when the unit answers
>   with Modbus exception 1, 2 or 3 (e.g. *Illegal Data Address*). Some gateways and proxies answer
>   every address, then nothing is filtered; the accessory detection and the entities disabled by
>   default still keep the overview lean.
> - **Accessories are guessed from values** (see [Accessories](configuration.md#accessories)), and
>   the PTC heater and the ZP1 module cannot be detected at all.
> - **Write-only registers cannot be probed.** The bus inputs 707, 763 and 764 are assumed to exist
>   when *Room temperature source* (109) answers, the error reset (405) when the fault code answers,
>   the clock sync when the clock answers.
>
> If the unit answers with exception 5 or 6 (*Acknowledge*, *Device Busy*), a gateway reports its
> target as unreachable (exception 10 or 11), or the connection drops, discovery stops and Home
> Assistant retries the setup instead of storing an incomplete result. A discovery that finds no
> register at all is not stored either. A single register that answers with any other exception
> (e.g. 4, *Slave Device Failure*) is asked three times, one second apart; if the exception stays,
> it is left out and a warning names it in the log.

The discovery result is stored in the config entry. The unit is probed again when you press
*Rediscover registers*, after **Reconfigure**, and when the stored result does not fit this version
of the integration: it lacks registers this version knows, was stored in another format (also
after a downgrade), is damaged or holds no register.

## Scaling and deviations from the Maico documentation

Values are decoded as the Maico documentation describes: ÷10 scaling, signed values, 32-bit
counters from High-/Low-word pairs and enum states. A few registers deliberately differ from the
documentation after checks on a real unit:

| Registers | Maico documentation | Integration | Status |
|---|---|---|---|
| 300, 302, 553, 700 to 707 (temperatures) | signed, ×10 | signed 16 bit, ÷10 | as documented |
| 301 *Supply temp min cooling* | Format °C, comment "step 1 (= 0.1 °C)" | **not scaled**, whole °C (8 to 29) | deviates; a live unit reports 14 |
| 701 *Temperature room external* | writable | read-only sensor | deviates |
| 750 to 754 (humidity) | ×10 | **not scaled**, whole % | deviates; checked on a live unit |
| 358 to 365 (EnOcean humidity) | raw 0 to 1000 for 0 to 100 % | **not scaled**, whole % | deviates by analogy with 750; not checked on a unit |
| 350 to 357, 366 to 373, 755 to 762 (CO2, VOC) | ×10 | ÷10 | as documented; not checked against real readings |
| 763, 764 (humidity and air quality bus) | 0 to 100 %, 0 to 5000 ppm | not scaled | as documented |
| 401/402, 403/404, 850 to 869 | High-Word / Low-Word | one unsigned 32-bit value each | as documented |
| 154 to 156 (airflow setpoints) | limits depend on the unit type | fixed 80 to 300 m³/h | see [Airflow limits](entities.md#airflow-limits) |

## Diagnostics

The diagnostics download lists every register in use with its decoded value and the raw words it
encodes to, so scaling questions can be answered from a report. What else it contains is described
under [Collecting information for a bug report](troubleshooting.md#collecting-information-for-a-bug-report).
