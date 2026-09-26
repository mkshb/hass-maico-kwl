# Changelog

What changed in each version of the Maico KWL integration, newest first. The text of each
[GitHub release](https://github.com/mkshb/hass-maico-kwl/releases) is taken from here.

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
