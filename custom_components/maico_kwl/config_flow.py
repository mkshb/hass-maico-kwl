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

from .const import (
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

            await self.async_set_unique_id(f"{host}:{port}:{slave}")
            self._abort_if_unique_id_configured()

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
            return self.async_create_entry(title="", data=user_input)

        current = self._entry.options.get(
            CONF_SCAN_INTERVAL,
            self._entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        schema = vol.Schema(
            {
                vol.Optional(CONF_SCAN_INTERVAL, default=current): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=3600)
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
