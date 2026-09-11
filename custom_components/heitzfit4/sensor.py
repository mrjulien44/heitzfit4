from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Heitzfit4 sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        Heitzfit4Sensor(coordinator, "heitzfit4_planning", "planning"),
        Heitzfit4TokenSensor(coordinator),
        # Heitzfit4Sensor(coordinator, "heitzfit4_booking", "booking")
    ], True)

class Heitzfit4TokenSensor(CoordinatorEntity, SensorEntity):  # type: ignore[misc]
    """Hidden coordinator-backed sensor used to preserve the token."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_token"
        self._attr_name = "Token"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:key-variant"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_entity_registry_enabled_default = False
        self._attr_native_value = getattr(getattr(coordinator, "api", None), "token", None)

    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = getattr(getattr(self.coordinator, "api", None), "token", None)
        super()._handle_coordinator_update()


class Heitzfit4Sensor(CoordinatorEntity, SensorEntity):  # type: ignore[misc]
    """Representation of a Heitzfit4 sensor."""

    def __init__(self, coordinator, name, attribute):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = name
        self._attribute = attribute
        self._attr_has_entity_name = True
        self._attr_name = "Heitzfit4"
        self._attr_unique_id = "Heitzfit4"
        self._attr_icon = "mdi:weight-lifter"
        self._attr_native_value = self.coordinator.data.get(self._attribute) if self.coordinator.data else None
        self._attr_extra_state_attributes = {
            "planning": self.coordinator.data.get("Planning") if self.coordinator.data else None
        }

    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data.get(self._attribute)
        self._attr_extra_state_attributes = {
            "planning": self.coordinator.data.get("Planning")
        }
        super()._handle_coordinator_update()
