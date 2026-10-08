# Changelog

What changed in each version of the Maico KWL integration, newest first. The text of each
[GitHub release](https://github.com/mkshb/hass-maico-kwl/releases) is taken from here.

## Unreleased

### What changed

- **Heat recovery energy counts only the exchanger.** Until now every bit of warming of the supply
  air was added up, also heat that does not come from the exchanger: with the summer bypass open,
  the fan heat of 0.5 to 1.5 K alone added up to about 2 kWh a day, and a running PTC heater or
  ZP1 reheating register was counted as recovered heat as well. Readings while the bypass is
  open, one of the heaters is on, or extract and intake air are less than 5 K apart are now left
  out like a gap between polls. *Heat recovery power* and *Heat recovery efficiency* still show
  what is measured and did not change.

### Do I need to do anything?

- **Nothing.** The energy total keeps its value and its entity. What was counted too much before
  cannot be told apart afterwards, so it stays in the total and in the long-term statistics.

## 0.5.0 (2026-10-08)

One connection to the unit, shared with the rest of Home Assistant. Needs Home Assistant
2026.10.

### What's new

- **The unit's single connection is shared.** The integration no longer opens a Modbus connection
  of its own, it asks the Modbus integration of Home Assistant for one. Everything that takes its
  connection from there and uses the same host and port shares it, which is what the unit needs:
  it accepts only one Modbus TCP connection at a time and silently ignores a second one. A second
  entry on the same host and port (a second unit behind one gateway), another integration that
  also asks the Modbus integration, and the connection check in the setup and reconfigure dialog
  now all go through that one connection instead of competing for it. The **Modbus** panel under
  **Settings** > **Connectivity** shows the connection and which entries are using it.

### What changed

- **Home Assistant 2026.10 or newer** is required, up from 2025.10. The shared connection does
  not exist before 2026.9, and 2026.10 is where the Modbus and validation interfaces this
  release builds on have settled, so it is the oldest release it is built and tested against.
  HACS does not offer the update while your Home Assistant is older.
- **No pymodbus any more.** The integration installs nothing of its own. Opening the connection,
  reopening it after a drop and closing it behind the last user are the Modbus integration's job
  now, which also means this integration no longer closes a connection another one is still using.
  Nothing needs to go into `configuration.yaml`.
- **A clear message when settings collide.** If another integration already talks to the same host
  and port with different connection settings, the entry now says that the connection is already
  used with other settings, instead of just failing to connect.
- **A `modbus:` hub in `configuration.yaml` is not part of the sharing.** It keeps a connection of
  its own, so it still occupies the unit's one slot, and the same goes for an integration that
  brings its own Modbus client instead of using the Modbus integration. The YAML hub is listed in
  the **Modbus** panel, but as a separate connection. Point it and this integration at a Modbus TCP
  proxy, or do without the YAML hub.

What is read, discovered and written did not change, and neither did your entities.

### Do I need to do anything?

- **Make sure Home Assistant is 2026.10 or newer, then update and restart.** Entities, settings
  and the stored discovery result stay as they are.
- **Running a `modbus:` hub in YAML for the same unit?** It does not share the connection, see
  above.
- **Connected directly, without a proxy?** A diagnostic tool or a second Home Assistant on the
  same unit still blocks the one connection. A Modbus TCP proxy remains the recommended setup.

## 0.4.2 (2026-09-29)

Bus values only go to the unit when you chose a source for them, and you can see what was sent.
Plus two fixes for the fan and the filters.

### What's new

- **Bus activity on the device page.** What is sent to the bus inputs shows up under **Activity**
  on the device page: the first value after a start and every changed value (at most one entry
  per input every 8 minutes), a source whose value is not sent and why, failed writes, writes
  that work again, and a unit that has had no valid value for 10 minutes. The event
  `maico_kwl_bus_input` behind it can also trigger automations.

### What changed

- **Bus inputs need a source.** Room temperature, humidity and air quality are only sent to the
  unit when a source entity is set for them under **Configure**. Without a source, nothing is sent
  and the unit uses its own sensor. The manual *Room temperature (bus)*, *Humidity (bus)* and
  *Air quality (bus)* numbers are gone: once set, they kept sending their stored value every
  8 minutes, also from a second Home Assistant instance (e.g. a test instance) on the same unit.
  In our case such a stored 80 % humidity switched the unit's over-humidity protection on and off
  every 8 minutes. Existing manual numbers are disabled and send nothing.
- **A fan speed in Auto-Sensor mode.** Setting a speed on the *Ventilation* fan no longer switches
  the unit from *Auto-Sensor* to manual mode. The unit runs the new level at once and keeps its
  sensor control, so it may choose another level later. In the other automatic and eco modes the
  unit still switches to manual mode first.
- **A filter that ran out stays.** *Rediscover registers* or a reconfigure with the same
  connection no longer takes an outdoor or room filter at 0 days for a filter that is not fitted,
  if it was detected before. Its entities, the *Filter due* sensor and the repair issue stay.

### Do I need to do anything?

- **Update and restart.**
- **Used the manual bus numbers?** Set a source entity for that input under **Configure**. For a
  fixed value, use a template sensor with the matching device class and unit.
- **A second Home Assistant instance on the same unit?** Update it as well, or remove its bus
  sources, so it does not send its own values.

## 0.4.1 (2026-09-27)

A careful look at everything that can go wrong: bus values that reach the unit reliably, no writes
to a device that is not a Maico KWL, and entities that keep your settings.

### What's new

- **Bus values the unit can use.** A source for room temperature, humidity or air quality now
  needs a unit: °F and K are converted to °C, ppb to ppm. A source without a unit (e.g. an air
  quality index) or in another unit (e.g. µg/m³) is not sent, and neither is a value outside the
  range of the input, instead of sending its limit. The log says once why a source is not sent.
- **Repair issues for bus inputs.** When a configured source no longer exists, when it has sent
  nothing usable for 30 minutes, or when the unit has had no valid bus value for 10 minutes
  (e.g. the connection is down), a repair issue says so. Inputs without a source get none.
- **Renamed sources are followed.** If you change the entity ID of a bus source, the option
  follows it.
- **Only a Maico KWL is set up and written to.** Setup, reconfigure and every poll check a few
  registers every Maico KWL has. If the device at the address reports values a Maico KWL does not
  have (e.g. another Modbus device got its IP address), it is not set up, nothing is written to it,
  and a repair issue names the register and the value.
- **Entities keep your settings.** Entities the integration no longer creates (a register a
  rediscovery did not find, an accessory you deselected) are now disabled instead of deleted.
  When they come back, their names, areas and entity IDs are still there.

### What changed

- **Bus values are refreshed every 8 minutes** instead of 9, and a failed write is retried every
  minute. The unit keeps a bus value for 10 minutes and then uses its own sensor again, so a
  single missed refresh no longer means minutes without the bus value.
- **A source reporting `nan` or `inf`** no longer stops the whole integration.
- **Boost with a duration.** The unit ends a boost itself after its *Ventilation level duration*.
  A longer `duration` is now refused with a message instead of being cut short without notice;
  the maximum is 90 minutes. A timed boost no longer ends a boost started after it.
- **Recovered heat** no longer counts a failed poll, a sensor fault (e.g. a temperature of
  3276.7 °C) or a reading above 10 kW. Calculated values are unavailable while an input is outside
  its measuring range.
- **Modbus answers** that lack registers are no longer read as 0, and a register that answers
  with an unexpected error is asked three times before it is left out.
- **A manual accessory choice** no longer hides an accessory that was fitted later or that a new
  version adds; your choice only covers the accessories it listed.
- **One Modbus connection.** The unit accepts only one Modbus TCP connection at a time. Reconfigure
  now checks over the running connection, so it also works without a proxy, and the connection
  messages say what to check. A Modbus TCP proxy is strongly recommended, see the README.
- **The same unit twice.** A host written with spaces or in other letter case is recognized as the
  same unit.
- **Robustness.** A damaged or newer stored discovery is probed again instead of failing the setup;
  a setup that fails late closes its connection; a change in Home Assistant's frontend functions
  only costs the dashboard card; a value a register cannot hold is refused instead of cut to its
  width; values are rounded as Home Assistant shows them (54.5 % is sent as 55 %).

### Do I need to do anything?

- **Update and restart.**
- **Bus sources need a unit.** Check that your sources report °C, °F or K for the room
  temperature, % for the humidity and ppm or ppb for the air quality. A template sensor without a
  unit needs `unit_of_measurement`. A repair issue appears after 30 minutes if a source sends
  nothing usable.
- **Boost automations:** a `duration` longer than the *Ventilation level duration* of your unit
  now fails. Shorten it, or raise the *Ventilation level duration*.
- **Connected directly without a proxy?** Only one program can talk to the unit at a time; consider
  a Modbus TCP proxy.

## 0.4.0 (2026-09-27)

Your ventilation at a glance: a dashboard card made for the unit, included with the integration.

### What's new

- **A dashboard card for your unit.** Edit a dashboard, choose *Add card* and search for
  *Maico KWL*. From Home Assistant 2026.6 on, the card is also suggested when you pick any entity
  of your unit in the card picker. There is nothing to download and no dashboard resource to add:
  the card comes with the integration. It shows:
  - **The airflow through your unit**: outdoor air to supply air, extract air to exhaust air, and
    the heat exchanger in between with its efficiency. The colour of the air follows its
    temperature, from blue when cold over grey around room temperature to orange and red when hot,
    so you see the heat exchange at a glance. With the summer bypass open, the outdoor air takes the
    arc over the exchanger. Fans show their speed and airflow, a PTC heater lights up while it heats.
  - **Room values**: temperature, humidity with its absolute value, air quality with a coloured dot,
    and the heat recovered right now and today.
  - **Controls**: operating mode, boost, summer or winter, and the ventilation level. A change shows
    at once and waits for the unit to confirm it, so a tap never seems to do nothing. Where the unit
    picks the level itself (auto modes, off, boost) the level bar is locked and says why.
  - **Filters** with the days left and the date of the next change, and **notices and faults** by
    name in the header.

  Values the integration feeds to the unit over the bus carry a *BUS* badge and name their source.
  The badge turns orange when no value has arrived for 10 minutes, or when the source never
  delivered one. Parts your unit does not have are left out, a tap on a value opens its entity, and
  the card works in English and German, in light and dark themes, on phones (Android and iPhone)
  and with a screen reader. In a sections dashboard it takes the full width of a section by default
  and cannot be made narrower than 9 of its 12 columns, where the diagram would get too small.

- **Faults and notices by name everywhere.** The active bits of the fault and notice codes now read
  as text in every language, e.g. *Bypass active* instead of `bypass_active`, also in the entity's
  attributes.

### What changed

- **Recovered heat with long poll intervals.** With a scan interval of 10 minutes or more, *Heat
  recovery energy* stayed at 0. It now counts with any interval.
- **Entities keep their names.** If one entity type failed to set up (e.g. after an unexpected
  error), all its entities were removed, and with them your names and areas. They now stay.
- **Reconfigure fixes a failed setup right away.** Correcting the host of a unit that could not be
  reached now sets it up at once instead of waiting for the next retry or a restart.
- **Reconfigure to another unit.** Your accessory choice belonged to the old unit; after pointing
  the integration at another unit, its accessories are detected anew.
- **Blueprints after a restart.** With the fallback mode *manual*, the window and demand boost
  blueprints left the unit off or at the boost level after a Home Assistant restart. A new
  *Fallback level* input (default *nominal*) sets the level as well.

### Do I need to do anything?

- **Update and restart.** Then reload the dashboard in your browser once, so it loads the new card.
  In the companion app, reset the frontend cache in the app settings if the card does not show up.
- **Add the card** to a dashboard: *Add card*, search for *Maico KWL*.
- **Blueprints:** import `demand_boost` and `window_open_reduce` again to get the fallback level.
  Your automations keep their settings.

## 0.3.1 (2026-09-26)

Only the accessories your unit has.

### What changed

- **Accessories are detected.** Outdoor filter, room filter, wired sensors, EnOcean wireless
  sensors and the external room sensor answer on every unit, so their entities showed up
  everywhere: filters stuck at 0 days with a reset button that did nothing and a repair notice that
  never went away, sensors that always read 0. The integration now checks which of them your unit
  actually has and leaves out the entities of the others. The device filter is always there.

- **You have the last word.** Under *Configure* on the integration you can choose the fitted
  accessories yourself, preselected with what was detected. This also covers the PTC heater and
  the ZP1 extension module, which cannot be detected.

### Do I need to do anything?

- **Update and restart.** The unit is scanned once more after the update, and the entities of
  accessories it does not have are removed.
- If something is missing or too much, correct it under *Configure*.

## 0.3.0 (2026-09-26)

New ways to control your unit and to keep an eye on it.

### What's new

- **Your unit as a fan.** A new *Ventilation* entity combines operating mode and ventilation level:
  the levels are the fan speeds, the operating modes are presets. Voice assistants, HomeKit and the
  standard fan cards now work out of the box. "Set the ventilation to 100 %" switches to manual
  mode at intensive level, turning it on again returns to the mode it was in before.

- **Home Assistant tells you when something needs attention.** Under *Settings > System > Repairs*
  you now get a notice when the unit reports a fault, when a filter is due, or when its clock is off
  by more than five minutes. Each notice explains what to do, and it disappears on its own once the
  problem is gone.

- **Boost for as long as you want.** The new action *Boost* starts the boost ventilation, for
  example from a button in the bathroom. Give it a duration in minutes and Home Assistant ends the
  boost when the time is up.

- **Recovered heat in kWh.** The new *Heat recovery energy* sensor adds up the heat your unit wins
  back, survives restarts and keeps long-term statistics, so you can see how much it recovered per
  day, month or year. No helper needed anymore.

### Do I need to do anything?

- **Update and restart.** The new entities appear on their own.
- If you built an *Integral* helper on *Heat recovery power*, you can replace it with the new
  *Heat recovery energy* sensor.
- If a filter is already due on your unit, you will see a repair notice right after the update.

## 0.2.1 (2026-09-26)

A maintenance release with fixes found in a review of v0.2.0.

### What changed

- **Blueprints finish what they started, even after a restart.** If Home Assistant restarted while
  the demand boost or the window blueprint was active, the unit could stay boosted or reduced for
  good. Now the blueprint notices this at startup and returns to your fallback mode once the reason
  is gone.
- **Your own changes win.** If you change the mode or level yourself while a blueprint is active,
  it no longer boosts again on the next sensor update and no longer restores over your setting.
- **More robust first scan.** If the unit or a Modbus gateway answers "busy" while it is scanned,
  the scan is retried later instead of leaving entities out for good.
- **Reconfigure reloads once.** Changing host, port or Modbus address no longer sets the unit up
  twice, and it keeps working with Home Assistant 2026.12 and newer.
- **Steady clock deviation.** The clock deviation no longer flips by one second on every poll, so
  it stays out of your history unless the clock really drifts.
- **No more leftover entities.** Entities the unit or your options no longer provide are removed,
  e.g. after *Rediscover registers* finds fewer registers, or when you remove a bus source entity.

### Do I need to do anything?

- **Update and restart.**
- **Blueprints:** import `demand_boost` and `window_open_reduce` again to get the fixes. Your
  automations keep their settings.
- Entities that were left over as "unavailable" disappear after the update.

## 0.2.0 (2026-09-26)

The biggest update so far: new values your unit never reported, clearer fault messages, smarter
blueprints and a much faster start.

### What's new

- **Values the vendor app shows, and more.** The integration now calculates values that have no
  register of their own:
  - **Heat recovery power** in watts, how much heat the exchanger wins back right now. Feed it into
    an *Integral* helper and you get the recovered energy in kWh. Thanks to Felix Bechstein
    (@felixb) for the idea and the formula!
  - **Heat recovery efficiency** in percent. A slow decline over the winter hints at a dirty
    exchanger or a bypass damper that does not close properly.
  - **Airflow imbalance** between supply and exhaust air, handy to spot a filter clogged on one side.
  - **Absolute humidity and dew point** of the air leaving your rooms, e.g. to compare with an
    outdoor sensor and decide whether airing out dries your home.
  - **Filter change reminders**: one "filter due" sensor per filter and the date of the next
    filter change.

- **Know what your unit is telling you.** Fault and notice codes are no longer just numbers. The
  sensors now list what is active (for example "bypass active"), and dirty filters and frost
  protection have their own sensors.

- **Blueprints that respect your choices.** The demand boost and window blueprints now remember the
  operating mode and ventilation level before they step in and restore exactly that afterwards. If
  you had set the unit to manual yourself, they leave it alone.

- **Keep the unit's clock right.** A new sensor shows how far the unit's clock is off, and a button
  sets it to Home Assistant's time.

- **Starts much faster.** Your unit is scanned once and the result is remembered, so restarts no
  longer wait for every register to be checked. A new *Rediscover registers* button scans again,
  e.g. after a firmware update or a retrofitted module.

- **Easier to live with.** Change host, port or Modbus address without removing the integration
  (*Reconfigure*), download diagnostics for bug reports, and see its own icon and logo in Home
  Assistant 2026.3 and newer.

- **More reliable.** Bus values are only written when they change, a lost connection is logged
  once instead of flooding the log, and a long list of smaller fixes. Behind the scenes, over 200
  automated tests now check every change.

### Do I need to do anything?

- **Update and restart.** The first start after the update scans your unit once, which takes a
  moment. After that, starts are quick.
- **Blueprints:** to get the new behaviour, import them again from the repository and check your
  automations.
- **Filter reminders:** on some units the filter bits of the notice code never switch on, even when a
  filter is due. Use the new *Filter due* sensors for reminders.
- The new values appear on their own. Settings and existing entities are not affected.

## 0.1.1 (2026-07-10)

A small compatibility fix so the integration keeps loading on recent Home Assistant releases.

### What changed

- **Fixed setup failure on Home Assistant 2026.6 and newer.** On these versions the integration
  refused to start with an error like `Requirements for maico_kwl not found: ['pymodbus==3.11.2']`.
  Home Assistant now ships a newer pymodbus of its own, and the integration insisted on one exact
  older version that Home Assistant would not install. It now accepts the version that Home
  Assistant already provides, so setup works again.

### Do I need to do anything?

If your unit was already set up and working, no. If setup was failing with the error above, update
to this version and reload the integration (or restart Home Assistant). No settings or entities are
affected, and the way the integration talks to your unit is unchanged.

## 0.1.0 (2026-05-25), first release

Bring your Maico KWL ventilation unit into Home Assistant. Fully local, no cloud, and almost no
setup work.

### Why you'll like it

- **Set up in a minute.** Enter how your unit is reached and the integration figures out the rest
  on its own. It detects what your specific model can do and creates the right entities for you, with
  no tinkering through long device lists.

- **See everything at a glance.** Indoor and outdoor temperatures, humidity, air quality, fan
  speeds, airflow, remaining filter life, operating hours and fault status. All of it shows up as
  proper Home Assistant sensors you can put on dashboards and chart over time.

- **Control it the way you like.** Operating mode, ventilation level, boost, target temperature and
  filter resets, straight from dashboards, voice assistants or automations.

- **Feed in your own values.** Got a better room temperature, humidity or air quality sensor
  elsewhere in your home? Point the integration at it and it keeps your unit supplied with that value
  automatically.

- **Smarter than the built-in modes.** Ready-to-use automation blueprints are included, for example
  free cooling on a cool summer night, a demand boost when CO₂ or humidity rises, and turning
  ventilation down while a window is open.

- **Private by design.** Communication stays on your local network. Available in English and German,
  and installable through HACS.

### Good to know

This is an early **alpha** release and a young project. It has so far been tested with a single unit,
so expect rough edges and occasional changes between versions. It is an unofficial community project
and not affiliated with Maico. Feedback, ideas and reports are very welcome and directly shape where
this goes next.

Enjoy fresh air, on your terms. 🌬️
