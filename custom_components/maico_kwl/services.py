"""Actions of the Maico KWL integration."""

from __future__ import annotations

import probatio

from homeassistant.components.fan.const import DOMAIN as FAN_DOMAIN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv, service

from .const import DOMAIN
from .register_defs import REGISTERS_BY_KEY

SERVICE_BOOST = "boost"
ATTR_DURATION = "duration"
# The unit ends a boost after its "ventilation level duration" (153), at most
# 90 minutes; a longer duration could not be kept. See MaicoFan.async_boost.
MAX_BOOST_MINUTES = int(REGISTERS_BY_KEY["vent_level_duration"].native_max or 90)


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register the actions (once, independent of the config entries)."""
    service.async_register_platform_entity_service(
        hass,
        DOMAIN,
        SERVICE_BOOST,
        entity_domain=FAN_DOMAIN,
        schema={
            probatio.Optional(ATTR_DURATION): probatio.All(
                cv.positive_int, probatio.Range(min=1, max=MAX_BOOST_MINUTES)
            )
        },
        func="async_boost",
    )
