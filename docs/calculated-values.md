# Calculated values

[README](../README.md) | [Documentation overview](../README.md#documentation)

Some useful values have no register of their own. They are calculated from the registers that are
there, and each is only created when the unit has all the registers it needs.

> [!NOTE]
> *Heat recovery power* and *Heat recovery energy* are **estimates**, not a heat meter reading.
> They rest on the airflow the unit reports, a rounded heat capacity of air (0.34 Wh/(m³·K)), the
> tolerances of the temperature sensors and readings taken once per scan interval. Use them to
> follow trends and compare periods, not for billing or exact energy balances.

## When a value is unavailable

A calculated value is unavailable while one of its inputs is missing from the last poll, or is no
valid measurement: a temperature outside the documented measuring range of −30 to 120 °C (e.g. a
sensor fault), a humidity outside 0 to 100 % or an airflow outside 0 to 1000 m³/h. The sensors of the
registers themselves still show what the unit reports.

## Formulas

| Sensor | Calculation |
|--------|-------------|
| *Heat recovery power* (W), estimated | Supply airflow (653) × 0.34 Wh/(m³·K) × (supply air (704) − air intake temperature (703)). Negative while the exchanger cools the supply air; the value is not clamped. Since the supply air is measured after the fan and any heater, their heat is included. The *Heat recovery energy* sensor below adds it up. |
| *Heat recovery energy* (kWh), estimated | The estimated heat recovery power integrated between polls (trapezoidal rule), as a total that only increases: negative power counts as 0. See [Heat recovery energy](#heat-recovery-energy). |
| *Heat recovery efficiency* (%) | (supply air − air intake) / (extract air (705) − air intake), the temperature efficiency of the exchanger. Unknown while extract and intake air are less than 5 K apart. Close to 0 while the summer bypass is open; fan heat can push it slightly above 100. A slow decline in winter hints at a dirty exchanger or a leaking bypass damper. |
| *Airflow imbalance* (m³/h) | Supply minus exhaust airflow (653 − 654, diagnostic). Positive: more air goes in. A lasting deviation hints at a clogged filter on one side or a calibration that is off. |
| *Absolute humidity extract air* (g/m³), *Dew point extract air* (°C) | From the extract air temperature (705) and humidity (750), Magnus formula (Sonntag 1990). The dew point is unknown at 0 % humidity. The absolute humidity can be compared with an outdoor sensor, e.g. to decide whether more ventilation dries the home. |
| *Filter due device / outdoor / room* (on/off), *Filter next change* (date) | From the remaining filter days (655 to 657): a filter is due once its days reach 0, the date is today plus the smallest number of days left of the fitted filters. Use these for filter change reminders. |

## Heat recovery energy

The *Heat recovery energy* sensor is an estimate of the heat recovered by the exchanger. It
integrates the *Heat recovery power* between polls with the trapezoidal rule. It is a total that only increases: negative power counts as 0. The total is
restored after a restart, and long-term statistics give daily, monthly and yearly values.

Limits of the calculation:

- A gap between two readings longer than 10 minutes, or two scan intervals if that is longer, is
  not counted, and neither is a reading above 10 kW, which no residential unit reaches.
- Only heat from the exchanger counts: readings while the summer bypass is open (802), the PTC
  heater (803) or the ZP1 reheating register (805) is on, while the extract air (705) is less than
  5 K warmer than the air intake (703), or while one of these two temperatures is no valid
  measurement, are treated like a gap between polls, so the first interval after them does not
  count either. Without the extract air register the 5 K check is skipped.
- Registers that are not in use are ignored: the unit does not have them, or their accessory (PTC
  heater, ZP1) is not selected. One that is in use but missing from a poll counts as on.
- A failed poll is no reading: the power is integrated between the readings before and after it,
  as long as the gap rule above allows it. The interval across a restart is never counted.
- *Heat recovery power* is measured after the fan and any heater, so it still includes their heat.
  The energy total leaves out the readings with the bypass open or a heater on, but fan heat during
  the counted readings stays in it.

## Filter due and next change

The *Filter due* sensors and *Filter next change* only cover the fitted filters, see
[Accessories](configuration.md#accessories). Once a filter is overdue, *Filter next change* shows
today. It is unavailable while the remaining days of a fitted filter cannot be read.
