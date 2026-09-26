"""Config flow for the Maico KWL integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig

from .const import (
    BUS_FEEDS,
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE,
    DOMAIN,
)
from .modbus_hub import MaicoModbusError, MaicoModbusHub

_LOGGER = logging.getLogger(__name__)

# A holding register that every Maico KWL implements (current ventilation
# level), used to confirm the target really answers FC 03.
_VALIDATION_REGISTER = 650


async def _validate(host: str, port: int, slave: int) -> None:
    """Raise MaicoModbusError if the device can't be reached / read."""
    hub = MaicoModbusHub(host, port, slave)
    try:
        if not await hub.connect():
            raise MaicoModbusError(f"cannot connect to {host}:{port}")
        await hub.read_block(_VALIDATION_REGISTER, 1)
    finally:
        await hub.close()


class MaicoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the user-initiated setup flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            slave = user_input[CONF_SLAVE]

            # The unit has no serial number to use as unique_id, and an IP
            # address is not a stable one, so match on the connection instead.
            self._async_abort_entries_match(
                {CONF_HOST: host, CONF_PORT: port, CONF_SLAVE: slave}
            )

            try:
                await _validate(host, port, slave)
            except MaicoModbusError as err:
                _LOGGER.debug("Validation failed: %s", err)
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"{DEFAULT_NAME} ({host})", data=user_input
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST, default=(user_input or {}).get(CONF_HOST, "")
                ): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=65535)
                ),
                vol.Optional(CONF_SLAVE, default=DEFAULT_SLAVE): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=247)
                ),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ):
        """Change host, port or Modbus address of an existing entry."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            slave = user_input[CONF_SLAVE]

            # Keeping the current values must not match the entry itself.
            if any(
                other.entry_id != entry.entry_id
                and other.data.get(CONF_HOST) == host
                and other.data.get(CONF_PORT) == port
                and other.data.get(CONF_SLAVE) == slave
                for other in self._async_current_entries(include_ignore=False)
            ):
                return self.async_abort(reason="already_configured")

            try:
                await _validate(host, port, slave)
            except MaicoModbusError as err:
                _LOGGER.debug("Validation failed: %s", err)
                errors["base"] = "cannot_connect"
            else:
                # Keep a custom title, follow the host in the default one.
                title = entry.title
                if title == f"{DEFAULT_NAME} ({entry.data[CONF_HOST]})":
                    title = f"{DEFAULT_NAME} ({host})"
                return self.async_update_reload_and_abort(
                    entry,
                    title=title,
                    # Drop the host based unique_id of entries created before 0.2.0.
                    unique_id=None,
                    data_updates={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_SLAVE: slave,
                    },
                )

        current = user_input or entry.data
        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current[CONF_HOST]): str,
                vol.Required(
                    CONF_PORT, default=current.get(CONF_PORT, DEFAULT_PORT)
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
                vol.Required(
                    CONF_SLAVE, default=current.get(CONF_SLAVE, DEFAULT_SLAVE)
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=247)),
            }
        )
        return self.async_show_form(
            step_id="reconfigure", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return MaicoOptionsFlow(config_entry)


class MaicoOptionsFlow(OptionsFlow):
    """Allow changing the scan interval after setup."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            # Keys left empty are omitted -> the corresponding feed is cleared.
            return self.async_create_entry(title="", data=user_input)

        opts = self._entry.options
        scan_current = opts.get(
            CONF_SCAN_INTERVAL,
            self._entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        fields: dict = {
            vol.Optional(CONF_SCAN_INTERVAL, default=scan_current): vol.All(
                vol.Coerce(int), vol.Range(min=5, max=3600)
            )
        }
        for _reg_key, conf_key, device_class in BUS_FEEDS:
            config = (
                EntitySelectorConfig(domain="sensor", device_class=device_class)
                if device_class
                else EntitySelectorConfig(domain="sensor")
            )
            current = opts.get(conf_key)
            marker = (
                vol.Optional(conf_key, description={"suggested_value": current})
                if current
                else vol.Optional(conf_key)
            )
            fields[marker] = EntitySelector(config)

        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(fields)
        )
