"""Actions of the Maico KWL integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.components.fan import DOMAIN as FAN_DOMAIN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv, service

from .const import DOMAIN

SERVICE_BOOST = "boost"
ATTR_DURATION = "duration"
MAX_BOOST_MINUTES = 720


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register the actions (once, independent of the config entries)."""
    service.async_register_platform_entity_service(
        hass,
        DOMAIN,
        SERVICE_BOOST,
        entity_domain=FAN_DOMAIN,
        schema={
            vol.Optional(ATTR_DURATION): vol.All(
                cv.positive_int, vol.Range(min=1, max=MAX_BOOST_MINUTES)
            )
        },
        func="async_boost",
    )
