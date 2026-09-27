# Security

## Supported versions

Fixes go into the latest release. Please update before reporting a problem.

## Reporting a vulnerability

Please do not open a public issue. Report it privately instead:
[Report a vulnerability](https://github.com/mkshb/hass-maico-kwl/security/advisories/new)
(GitHub's private vulnerability reporting).

Describe what an attacker could do, how to reproduce it and which version you used. This is a
community project maintained in spare time; reports are answered as soon as possible, and you are
kept informed until a fix is released.

## What this integration can and cannot protect

- **Modbus TCP has no authentication.** Anyone who can reach the unit's Modbus port can read and
  change its settings, with or without this integration. Keep the unit (or its Modbus gateway) in
  a network that only trusted devices reach, and do not forward the port to the internet. This is
  a property of the protocol, not a vulnerability of the integration.
- **The Modbus proxy as well.** A Modbus TCP proxy, recommended since the unit accepts only one
  connection, has no authentication either. Its port belongs in the same protected network as the
  unit's.
- **No writes to another device.** Before setup and on every poll, the integration checks that the
  device at the configured address looks like a Maico KWL. If it does not (e.g. another Modbus
  device got the unit's IP address), nothing is written to it.
- **Local only.** The integration talks to the unit on your network and sends nothing to any cloud
  service.
- **Diagnostics** leave out the host of the unit, so they can be attached to public issues.
- **Dashboard card.** Home Assistant serves the card's files without login, like other frontend
  files. They contain code only, no data of your installation; the values the card shows come
  through your logged-in Home Assistant session.

Problems in Home Assistant itself belong to the
[Home Assistant project](https://www.home-assistant.io/security/).
