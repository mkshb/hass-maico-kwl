"""Config flow for the Maico KWL integration."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigEntryState,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    BUS_FEEDS,
    CONF_ACCESSORIES,
    CONF_ACCESSORIES_OFFERED,
    CONF_DISCOVERY,
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
from .discovery import (
    active_accessories,
    async_check_identity,
    data_without_discovery,
    offered_accessories,
    present_from_cache,
)
from .modbus_hub import MaicoModbusError, MaicoModbusHub
from .register_defs import ACCESSORIES

_LOGGER = logging.getLogger(__name__)

def _host(value: str) -> str:
    """The host as stored and compared: without spaces, names in lower case.

    DNS names are case-insensitive, so "KWL.local" and "kwl.local " are the
    same unit and must not become two entries.
    """
    return value.strip().lower()


def _connection(data: Mapping[str, Any]) -> tuple[str, int, int]:
    """Host, port and Modbus address of an entry, for finding duplicates."""
    return (
        _host(data.get(CONF_HOST, "")),
        data.get(CONF_PORT, DEFAULT_PORT),
        data.get(CONF_SLAVE, DEFAULT_SLAVE),
    )


def _running_hub(entry: ConfigEntry, host: str, port: int) -> MaicoModbusHub | None:
    """The hub of a loaded entry, if it is connected to host and port."""
    if entry.state is not ConfigEntryState.LOADED:
        return None
    if _connection(entry.data)[:2] != (host, port):
        return None
    hub: MaicoModbusHub = entry.runtime_data.hub
    return hub


class UnsupportedDevice(Exception):
    """The device answers, but does not look like a Maico KWL."""


async def _validate(
    host: str, port: int, slave: int, running: MaicoModbusHub | None = None
) -> None:
    """Check that a Maico KWL answers at the address.

    With the hub of a running entry for the same host and port, its connection
    is used: the unit accepts only one Modbus TCP connection at a time and
    ignores a second one. Raises MaicoModbusError if it cannot be reached,
    UnsupportedDevice if the device there reports values a Maico KWL does not
    have.
    """
    hub = running.with_slave(slave) if running else MaicoModbusHub(host, port, slave)
    try:
        if running is None and not await hub.connect():
            raise MaicoModbusError(f"cannot connect to {host}:{port}")
        if problem := await async_check_identity(hub):
            raise UnsupportedDevice(problem)
    finally:
        await hub.close()


class MaicoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the user-initiated setup flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        placeholders: dict[str, str] = {}
        if user_input is not None:
            host = _host(user_input[CONF_HOST])
            port = user_input[CONF_PORT]
            slave = user_input[CONF_SLAVE]
            user_input = {**user_input, CONF_HOST: host}

            # The unit has no serial number to use as unique_id, and an IP
            # address is not a stable one, so match on the connection instead.
            if any(
                _connection(other.data) == (host, port, slave)
                for other in self._async_current_entries(include_ignore=False)
            ):
                return self.async_abort(reason="already_configured")

            try:
                await _validate(host, port, slave)
            except MaicoModbusError as err:
                _LOGGER.debug("Validation failed: %s", err)
                errors["base"] = "cannot_connect"
            except UnsupportedDevice as err:
                errors["base"] = "unsupported_device"
                placeholders["details"] = str(err)
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
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders=placeholders,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change host, port or Modbus address of an existing entry."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        placeholders: dict[str, str] = {}
        if user_input is not None:
            host = _host(user_input[CONF_HOST])
            port = user_input[CONF_PORT]
            slave = user_input[CONF_SLAVE]

            # Keeping the current values must not match the entry itself.
            if any(
                other.entry_id != entry.entry_id
                and _connection(other.data) == (host, port, slave)
                for other in self._async_current_entries(include_ignore=False)
            ):
                return self.async_abort(reason="already_configured")

            try:
                await _validate(host, port, slave, _running_hub(entry, host, port))
            except MaicoModbusError as err:
                _LOGGER.debug("Validation failed: %s", err)
                errors["base"] = "cannot_connect"
            except UnsupportedDevice as err:
                errors["base"] = "unsupported_device"
                placeholders["details"] = str(err)
            else:
                # Keep a custom title, follow the host in the default one.
                title = entry.title
                if title == f"{DEFAULT_NAME} ({entry.data[CONF_HOST]})":
                    title = f"{DEFAULT_NAME} ({host})"
                # A new connection may lead to another unit: the accessories
                # chosen for the old one no longer apply, detection decides.
                options = dict(entry.options)
                same_unit = (host, port, slave) == _connection(entry.data)
                if not same_unit:
                    options.pop(CONF_ACCESSORIES, None)
                    options.pop(CONF_ACCESSORIES_OFFERED, None)
                # A loaded entry is reloaded by its update listener; reloading
                # here as well would set the unit up twice. An entry that
                # failed to set up (retrying, or in error) has no listener, so
                # it is reloaded here, which also ends a pending retry.
                self.hass.config_entries.async_update_entry(
                    entry,
                    title=title,
                    # Drop the host based unique_id of entries created before 0.2.0.
                    unique_id=None,
                    # A new connection may lead to another unit: discover again.
                    data={
                        **data_without_discovery(entry.data, same_unit),
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_SLAVE: slave,
                    },
                    options=options,
                )
                if entry.state in (
                    ConfigEntryState.SETUP_RETRY,
                    ConfigEntryState.SETUP_ERROR,
                ):
                    self.hass.config_entries.async_schedule_reload(entry.entry_id)
                return self.async_abort(reason="reconfigure_successful")

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
            step_id="reconfigure",
            data_schema=schema,
            errors=errors,
            description_placeholders=placeholders,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return MaicoOptionsFlow(config_entry)


class MaicoOptionsFlow(OptionsFlow):
    """Scan interval, fitted accessories and bus feed sources."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        cache = self._entry.data.get(CONF_DISCOVERY) or {}
        offered = offered_accessories(present_from_cache(cache) or set())
        opts = self._entry.options

        if user_input is not None:
            # Keys left empty are omitted -> the corresponding feed is cleared.
            data = dict(user_input)
            if not offered:
                # No stored discovery to choose from: keep the last choice.
                for key in (CONF_ACCESSORIES, CONF_ACCESSORIES_OFFERED):
                    if key in opts:
                        data[key] = opts[key]
            elif set(data.get(CONF_ACCESSORIES, [])) == set(
                cache.get("accessories", [])
            ):
                # Same as detected: store nothing, a rediscovery still applies.
                data.pop(CONF_ACCESSORIES, None)
            else:
                # The choice covers what was offered; see active_accessories.
                data[CONF_ACCESSORIES_OFFERED] = sorted(offered)
            return self.async_create_entry(title="", data=data)

        scan_current = opts.get(
            CONF_SCAN_INTERVAL,
            self._entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        fields: dict[vol.Marker, Any] = {
            vol.Optional(CONF_SCAN_INTERVAL, default=scan_current): vol.All(
                vol.Coerce(int), vol.Range(min=5, max=3600)
            )
        }
        if offered:
            fields[
                vol.Optional(
                    CONF_ACCESSORIES,
                    default=sorted(active_accessories(cache, opts) & offered),
                )
            ] = SelectSelector(
                SelectSelectorConfig(
                    options=[acc.key for acc in ACCESSORIES if acc.key in offered],
                    multiple=True,
                    mode=SelectSelectorMode.LIST,
                    translation_key="accessory",
                )
            )
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
