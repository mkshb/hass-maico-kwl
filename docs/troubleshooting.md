# Troubleshooting

[README](../README.md) | [Documentation overview](../README.md#documentation)

## Common problems

### "Failed to connect" during setup, or the integration keeps retrying

- Check host, port (default `502`) and Modbus address (default `10`) against the settings of the
  unit or the gateway. Connection settings can be changed later with **Reconfigure** on the
  integration.
- Make sure Modbus TCP is enabled on the unit (firmware V1.1.1 or newer) and that no firewall
  blocks the port.
- The unit accepts only one Modbus TCP connection at a time and ignores further ones: check that no
  other program is connected to it. Integrations that take their connection from the Modbus
  integration share one, a `modbus:` hub in `configuration.yaml` opens its own. The **Modbus** panel
  under **Settings** > **Connectivity** lists both, a hub as a connection of its own. A Modbus TCP
  proxy lets several clients share the one connection, see
  [One connection only](compatibility.md#one-connection-only-use-a-modbus-tcp-proxy).
- *"The Modbus connection to the Maico KWL is already used with other settings"*: another
  integration uses the same host and port with different connection settings. The setup is not
  retried in this case; align the settings or remove the other entry, then reload the integration.

### "The device does not look like a Maico KWL"

- The device at host, port and Modbus address reports a value a Maico KWL does not have; the
  message names the register and the value. Check that the address belongs to the unit (e.g. after
  the router gave its IP address to another device), and correct it with **Reconfigure**.
- At setup, Home Assistant retries until the values look right. While running, the same check
  shows a repair issue, and nothing is written to the device until its values look right again;
  controls show an error instead. See [Discovery and its limits](modbus.md#discovery-and-its-limits).
- If it is your Maico unit, please open an issue with the message: its firmware may use a value
  the documentation does not list.

### All entities are unavailable

- The unit is not reachable at the moment (see above); entities come back on their own once it
  answers again.
- If the connection works but no values arrive, the unit may count registers from 1 instead of 0.
  Adjust `REGISTER_OFFSET` in `register_defs.py` and open an issue, see
  [Register addressing](modbus.md#register-addressing).

### Entities for accessories the unit does not have, or entities of a fitted accessory are missing

- Choose the fitted accessories under **Configure** on the integration, see
  [Accessories](configuration.md#accessories).
- Other entities that always show 0: some Modbus proxies answer every address instead of rejecting
  missing registers, so discovery cannot filter them. Disable the ones you don't need.

### The filter reset for the outdoor or room filter has no effect

- The unit does not monitor this filter. Once it is fitted and enabled on the unit, press
  *Rediscover registers*, or select it under **Configure** if you chose the accessories yourself.

### A bus input has no effect

- The matching source on the unit must be set to **"Bus"**, e.g. the *Room temperature source*
  select for the room temperature.
- Check the source entity: it needs a suitable unit and a value in range, see
  [Bus inputs](bus-inputs.md). The *(sent)* sensor and the **Activity** on the device page show
  what was sent last.

### New registers or features are missing after a firmware update

- Press the *Rediscover registers* button on the device page.

### The dashboard card is missing or shows "Custom element doesn't exist"

- Reload the page in the browser; in the companion app, reset the frontend cache in the app
  settings. The card is loaded with the rest of the frontend, so a page that was open before the
  integration was set up or updated does not know it yet. The card's URL changes with every new
  version, so a reload is enough to get it.
- The card needs the integration to be set up; without a configured unit it is not loaded.

## Repair issues

The integration reports these problems under **Settings > System > Repairs**. They disappear on
their own once the problem is gone, and are removed when the integration is unloaded.

| Issue | When |
|---|---|
| *... reports a fault* | The unit reports a fault; the message lists the active fault bits. Clear it with *Reset errors* once the cause is fixed. See [Fault and notice codes](entities.md#fault-and-notice-codes). |
| *... filter of ... is due* | A fitted filter has no days left. |
| *Clock of ... is off* | The unit clock is off by more than 5 minutes, see [Unit clock](entities.md#unit-clock). |
| *... does not look like a Maico KWL* | See [above](#the-device-does-not-look-like-a-maico-kwl). |
| *Bus source of ... is missing* / *sends no data* | A configured bus source no longer exists, or has given no value that can be sent for more than 30 minutes, see [Bus inputs](bus-inputs.md). |
| *... gets no bus value* | Writing a bus input has failed for 10 minutes, see [Bus inputs](bus-inputs.md). |

## Collecting information for a bug report

- Download the diagnostics: **Settings > Devices & Services > Maico KWL > ⋮ > Download
  diagnostics**. They contain the capability profile, every register in use with its value and the
  raw words it encodes to, the absent registers (including those of accessories that are not in
  use), the last bus writes, the result of the last poll, and the entry data and options
  (including the stored discovery and the bus source entity IDs). Host, title and unique ID are
  removed.
- Enable debug logging on the same page (**⋮ > Enable debug logging**), reproduce the problem, then
  disable it again to download the log.

> [!WARNING]
> Issues on GitHub are public. Look through the diagnostics and the log before you attach them, and
> remove anything you do not want to share, e.g. entity IDs that name rooms or people. The log is
> not redacted and can contain the host of the unit.

Then open an issue, see [Support and contributing](../README.md#support-and-contributing).
