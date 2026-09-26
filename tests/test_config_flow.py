"""Tests for the config flow and the options flow."""

from __future__ import annotations

from homeassistant.config_entries import SOURCE_USER, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.maico_kwl.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_ROOM_TEMP_SOURCE_ENTITY,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE,
    DOMAIN,
)

from .conftest import HOST, PORT, SLAVE, FakeDevice
from .helpers import setup_entry

USER_INPUT = {
    CONF_HOST: HOST,
    CONF_PORT: PORT,
    CONF_SLAVE: SLAVE,
    CONF_SCAN_INTERVAL: 30,
}


async def test_user_flow_creates_entry(hass: HomeAssistant, device: FakeDevice) -> None:
    """A reachable unit creates an entry and leaves no connection open."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == f"Maico KWL ({HOST})"
    assert result["data"] == USER_INPUT
    assert result["result"].unique_id is None
    await hass.async_block_till_done()
    # Only the connection of the loaded entry stays open, not the validation one.
    assert device.open_connections == 1


async def test_user_flow_cannot_connect(hass: HomeAssistant, device: FakeDevice) -> None:
    """An unreachable unit shows an error and the flow can be retried."""
    device.online = False
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
    assert device.open_connections == 0

    device.online = True
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_user_flow_validation_register_rejected(
    hass: HomeAssistant, device: FakeDevice
) -> None:
    """A device that rejects the validation register is not accepted."""
    device.absent.add(650)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
    assert device.open_connections == 0


async def test_user_flow_already_configured(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """The same host, port and Modbus address can't be added twice."""
    config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_user_flow_other_modbus_address_allowed(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A second unit behind the same gateway (other address) can be added."""
    config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**USER_INPUT, CONF_SLAVE: SLAVE + 1}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_options_flow_saves_and_reloads(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Saving the options stores them and reloads the entry."""
    hass.states.async_set("sensor.room", "21.0", {"device_class": "temperature"})
    await setup_entry(hass, config_entry)

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CONF_SCAN_INTERVAL: 60, CONF_ROOM_TEMP_SOURCE_ENTITY: "sensor.room"},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    assert config_entry.options == {
        CONF_SCAN_INTERVAL: 60,
        CONF_ROOM_TEMP_SOURCE_ENTITY: "sensor.room",
    }
    assert config_entry.state is ConfigEntryState.LOADED
    assert config_entry.runtime_data.coordinator.update_interval.total_seconds() == 60


async def test_options_flow_suggests_current_source(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A configured source entity is suggested when the options open again."""
    config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        config_entry, options={CONF_ROOM_TEMP_SOURCE_ENTITY: "sensor.room"}
    )
    await setup_entry(hass, config_entry)

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    schema = result["data_schema"].schema
    marker = next(key for key in schema if key == CONF_ROOM_TEMP_SOURCE_ENTITY)
    assert marker.description == {"suggested_value": "sensor.room"}

    # Leaving the field empty clears the feed.
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 30}
    )
    await hass.async_block_till_done()
    assert CONF_ROOM_TEMP_SOURCE_ENTITY not in config_entry.options


# --- Reconfigure ----------------------------------------------------------

NEW_HOST = "192.0.2.20"


async def test_reconfigure_changes_connection(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """A new host is validated, stored and the entry reloads."""
    await setup_entry(hass, config_entry)

    result = await config_entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: NEW_HOST, CONF_PORT: PORT, CONF_SLAVE: SLAVE}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert config_entry.data[CONF_HOST] == NEW_HOST
    assert config_entry.data[CONF_SCAN_INTERVAL] == 30  # untouched
    assert config_entry.title == f"Maico KWL ({NEW_HOST})"
    assert config_entry.unique_id is None  # legacy host based id dropped
    assert config_entry.state is ConfigEntryState.LOADED


async def test_reconfigure_keeps_custom_title_and_same_values(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Saving unchanged values works and a renamed entry keeps its title."""
    config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(config_entry, title="Basement KWL")
    await setup_entry(hass, config_entry)

    result = await config_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: HOST, CONF_PORT: PORT, CONF_SLAVE: SLAVE}
    )
    await hass.async_block_till_done()
    assert result["reason"] == "reconfigure_successful"
    assert config_entry.title == "Basement KWL"


async def test_reconfigure_cannot_connect(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """An unreachable new host shows an error and keeps the old data."""
    await setup_entry(hass, config_entry)
    result = await config_entry.start_reconfigure_flow(hass)

    device.online = False
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: NEW_HOST, CONF_PORT: PORT, CONF_SLAVE: SLAVE}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
    assert config_entry.data[CONF_HOST] == HOST

    device.online = True
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: NEW_HOST, CONF_PORT: PORT, CONF_SLAVE: SLAVE}
    )
    await hass.async_block_till_done()
    assert result["reason"] == "reconfigure_successful"


async def test_reconfigure_to_other_entry_aborts(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Pointing an entry at a unit that is already configured is refused."""
    other = MockConfigEntry(
        domain=DOMAIN,
        data={**USER_INPUT, CONF_HOST: NEW_HOST},
    )
    other.add_to_hass(hass)
    await setup_entry(hass, config_entry)

    result = await config_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: NEW_HOST, CONF_PORT: PORT, CONF_SLAVE: SLAVE}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert config_entry.data[CONF_HOST] == HOST
