"""Tests for the config flow and the options flow."""

from __future__ import annotations

import pytest

from homeassistant.config_entries import SOURCE_USER, ConfigEntryState
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.maico_kwl.const import (
    CONF_ACCESSORIES,
    CONF_ACCESSORIES_OFFERED,
    CONF_DISCOVERY,
    CONF_HOST,
    CONF_PORT,
    CONF_ROOM_TEMP_SOURCE_ENTITY,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE,
    DOMAIN,
)

from .conftest import HOST, PORT, SLAVE, FakeDevice
from .helpers import entity_id, setup_entry

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


async def test_user_flow_unit_without_one_identity_register(
    hass: HomeAssistant, device: FakeDevice
) -> None:
    """A unit may lack a register; discovery allows for that."""
    device.absent.add(650)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


@pytest.mark.parametrize(
    ("absent", "registers", "details"),
    [
        (
            set(range(0, 1000)),
            {},
            "none of its registers 108, 109, 550 to 554 and 650 can be read",
        ),
        (set(), {550: 7}, "register 550 reads 7, expected 0 to 5"),
        (set(), {108: 1234}, "register 108 reads 1234, expected 0 to 3"),
    ],
)
async def test_user_flow_rejects_another_device(
    hass: HomeAssistant,
    device: FakeDevice,
    absent: set[int],
    registers: dict[int, int],
    details: str,
) -> None:
    """E.g. an inverter at the address: not set up, and why is shown."""
    device.absent = absent
    device.registers.update(registers)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unsupported_device"}
    assert result["description_placeholders"] == {"details": details}
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


async def test_user_flow_normalizes_the_host(
    hass: HomeAssistant, device: FakeDevice
) -> None:
    """Spaces and upper case must not make the same unit a second entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**USER_INPUT, CONF_HOST: " KWL.Local "}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_HOST] == "kwl.local"
    assert result["title"] == "Maico KWL (kwl.local)"

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**USER_INPUT, CONF_HOST: "KWL.LOCAL"}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_user_flow_matches_an_older_entry_in_upper_case(
    hass: HomeAssistant, device: FakeDevice
) -> None:
    """Entries stored before the host was normalized are found as well."""
    MockConfigEntry(
        domain=DOMAIN, data={**USER_INPUT, CONF_HOST: "KWL.local"}
    ).add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**USER_INPUT, CONF_HOST: "kwl.local"}
    )
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


async def test_options_flow_accessories(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """The detected accessories are preselected, a different choice is kept."""
    device.registers[656] = 0  # no outdoor filter detected
    await setup_entry(hass, config_entry)
    detected = config_entry.data[CONF_DISCOVERY]["accessories"]
    assert "outdoor_filter" not in detected

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    marker = next(key for key in result["data_schema"].schema if key == CONF_ACCESSORIES)
    assert marker.default() == detected
    options = result["data_schema"].schema[marker].config["options"]
    assert options[:2] == ["outdoor_filter", "room_filter"]  # in definition order
    assert "enocean" not in options  # the unit rejects these registers

    # The user knows better: an outdoor filter is fitted.
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CONF_SCAN_INTERVAL: 30, CONF_ACCESSORIES: [*detected, "outdoor_filter"]},
    )
    await hass.async_block_till_done()
    assert set(config_entry.options[CONF_ACCESSORIES]) == {*detected, "outdoor_filter"}
    assert config_entry.options[CONF_ACCESSORIES_OFFERED] == sorted(options)
    assert "filter_remaining_outdoor" in config_entry.runtime_data.coordinator.present
    assert entity_id(hass, config_entry, "button", "filter_reset_outdoor")

    # Back to the detected set: nothing stored, a rediscovery applies again.
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 30, CONF_ACCESSORIES: detected}
    )
    await hass.async_block_till_done()
    assert CONF_ACCESSORIES not in config_entry.options
    assert CONF_ACCESSORIES_OFFERED not in config_entry.options
    present = config_entry.runtime_data.coordinator.present
    assert "filter_remaining_outdoor" not in present
    ent_reg = er.async_get(hass)
    button = ent_reg.async_get_entity_id(
        "button", DOMAIN, f"{config_entry.entry_id}_filter_reset_outdoor"
    )
    assert ent_reg.async_get(button).disabled_by is er.RegistryEntryDisabler.INTEGRATION


async def test_accessory_fitted_after_the_choice_is_detected(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Rediscover finds an accessory the choice could not cover yet."""
    await setup_entry(hass, config_entry)
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 30, CONF_ACCESSORIES: ["outdoor_filter"]}
    )
    await hass.async_block_till_done()
    assert "enocean" not in config_entry.options[CONF_ACCESSORIES_OFFERED]

    device.absent -= set(range(350, 374))  # EnOcean module fitted
    device.registers[350] = 4500  # 450 ppm
    button = entity_id(hass, config_entry, "button", "rediscover")
    await hass.services.async_call(
        "button", "press", {ATTR_ENTITY_ID: button}, blocking=True
    )
    await hass.async_block_till_done()

    present = config_entry.runtime_data.coordinator.present
    assert "enocean_co2_id0" in present
    # The room filter was offered and left out: it stays out.
    assert "filter_remaining_room" not in present
    assert "filter_remaining_outdoor" in present


async def test_options_flow_without_discovery_keeps_accessories(
    hass: HomeAssistant, config_entry
) -> None:
    """Without a stored discovery there is nothing to choose from."""
    config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        config_entry, options={CONF_ACCESSORIES: ["zp1"]}
    )
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert CONF_ACCESSORIES not in result["data_schema"].schema
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 30}
    )
    assert config_entry.options[CONF_ACCESSORIES] == ["zp1"]

    hass.config_entries.async_update_entry(config_entry, options={})
    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 30}
    )
    assert CONF_ACCESSORIES not in config_entry.options


# --- Reconfigure ----------------------------------------------------------

NEW_HOST = "192.0.2.20"


async def test_reconfigure_changes_connection(
    hass: HomeAssistant, device: FakeDevice, config_entry, caplog
) -> None:
    """A new host is validated, stored and the entry reloads once."""
    await setup_entry(hass, config_entry)

    result = await config_entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"
    device.reads = 0

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
    # The new connection was discovered again, not taken from the old one.
    assert device.reads > len(config_entry.runtime_data.coordinator._blocks)
    # Only the update listener reloads (HA reports a second reload by the flow).
    assert "should use it for scheduling a reload" not in caplog.text


async def test_reconfigure_recovers_an_entry_that_failed_to_set_up(
    hass: HomeAssistant, device: FakeDevice, config_entry, caplog
) -> None:
    """Fixing the connection of a retrying entry sets it up right away."""
    device.online = False
    await setup_entry(hass, config_entry)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY

    device.online = True
    result = await config_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: NEW_HOST, CONF_PORT: PORT, CONF_SLAVE: SLAVE}
    )
    await hass.async_block_till_done()
    assert result["reason"] == "reconfigure_successful"
    assert config_entry.state is ConfigEntryState.LOADED
    assert "should use it for scheduling a reload" not in caplog.text


async def test_reconfigure_drops_the_accessory_choice_of_another_unit(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    """Another connection may be another unit: detection decides again."""
    await setup_entry(hass, config_entry)
    hass.config_entries.async_update_entry(
        config_entry,
        options={
            **config_entry.options,
            CONF_ACCESSORIES: ["room_filter"],
            CONF_ACCESSORIES_OFFERED: ["room_filter"],
        },
    )
    await hass.async_block_till_done()

    result = await config_entry.start_reconfigure_flow(hass)
    await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: NEW_HOST, CONF_PORT: PORT, CONF_SLAVE: SLAVE}
    )
    await hass.async_block_till_done()
    assert CONF_ACCESSORIES not in config_entry.options
    assert CONF_ACCESSORIES_OFFERED not in config_entry.options


async def test_reconfigure_with_the_same_connection_keeps_the_accessories(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    await setup_entry(hass, config_entry)
    hass.config_entries.async_update_entry(
        config_entry, options={**config_entry.options, CONF_ACCESSORIES: ["room_filter"]}
    )
    await hass.async_block_till_done()

    result = await config_entry.start_reconfigure_flow(hass)
    await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: HOST, CONF_PORT: PORT, CONF_SLAVE: SLAVE}
    )
    await hass.async_block_till_done()
    assert config_entry.options[CONF_ACCESSORIES] == ["room_filter"]


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


async def test_reconfigure_normalizes_the_host(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    await setup_entry(hass, config_entry)
    MockConfigEntry(
        domain=DOMAIN, data={**USER_INPUT, CONF_HOST: "Other.Unit"}
    ).add_to_hass(hass)
    result = await config_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: " other.unit", CONF_PORT: PORT, CONF_SLAVE: SLAVE}
    )
    assert result["reason"] == "already_configured"

    result = await config_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: " KWL.Local ", CONF_PORT: PORT, CONF_SLAVE: SLAVE}
    )
    await hass.async_block_till_done()
    assert result["reason"] == "reconfigure_successful"
    assert config_entry.data[CONF_HOST] == "kwl.local"


async def test_reconfigure_rejects_another_device(
    hass: HomeAssistant, device: FakeDevice, config_entry
) -> None:
    await setup_entry(hass, config_entry)
    result = await config_entry.start_reconfigure_flow(hass)
    device.registers[554] = 9
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: NEW_HOST, CONF_PORT: PORT, CONF_SLAVE: SLAVE}
    )
    assert result["errors"] == {"base": "unsupported_device"}
    assert config_entry.data[CONF_HOST] == HOST


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
