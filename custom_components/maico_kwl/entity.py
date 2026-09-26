"""Base entity for the Maico KWL integration."""

from __future__ import annotations

from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER
from .coordinator import MaicoCoordinator
from .modbus_hub import MaicoModbusError
from .register_defs import BUTTON, RegisterDef


class MaicoEntity(CoordinatorEntity[MaicoCoordinator]):
    """Common base: device info, unique id and availability for one register."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MaicoCoordinator,
        entry: ConfigEntry,
        reg: RegisterDef,
    ) -> None:
        super().__init__(coordinator)
        self._reg = reg
        self._attr_unique_id = f"{entry.entry_id}_{reg.key}"
        # Display name comes from the translation files (entity.<platform>.<key>.name),
        # the icon from icons.json; English in translations/en.json is the fallback.
        self._attr_translation_key = reg.key
        self._attr_entity_registry_enabled_default = reg.enabled_default
        if reg.entity_category:
            self._attr_entity_category = EntityCategory(reg.entity_category)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer=MANUFACTURER,
            name=entry.title or DEFAULT_NAME,
            model=coordinator.profile.get("model", DEFAULT_NAME),
        )

    @property
    def available(self) -> bool:
        if not super().available:
            return False
        # Buttons / write-only registers have no polled value.
        if self._reg.platform == BUTTON or not self._reg.readable:
            return True
        return self._reg.key in self.coordinator.data

    @property
    def _value(self):
        """The decoded value for this register, or None if absent this cycle."""
        return self.coordinator.data.get(self._reg.key)

    async def _async_write(self, value: float | datetime) -> None:
        """Write a real-world value to this entity's register.

        Raises HomeAssistantError so the UI shows a clear message instead of
        an unexpected error with a traceback.
        """
        try:
            await self.coordinator.hub.write(
                self._reg.address, self._reg.encode(value)
            )
        except MaicoModbusError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="write_failed",
                translation_placeholders={
                    "entity": self.entity_id,
                    "error": str(err),
                },
            ) from err
