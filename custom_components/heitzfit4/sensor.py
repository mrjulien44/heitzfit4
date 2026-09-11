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

class Heitzfit4TokenSensor(CoordinatorEntity, SensorEntity):
    """Hidden coordinator-backed sensor used to preserve the token."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_token"
        self._attr_name = "Token"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:key-variant"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self):
        """Return the current token stored by the coordinator API."""
        return self.coordinator.api.token


class Heitzfit4Sensor(CoordinatorEntity, SensorEntity):
    """Representation of a Heitzfit4 sensor."""

    def __init__(self, coordinator, name, attribute):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = name
        self._attribute = attribute
        self._attr_native_value = 6
        """Initisalisation de notre entité"""
        self._attr_has_entity_name = True
        self._attr_name = "Heitzfit4"
        self._attr_unique_id = "Heitzfit4"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
    
    @property
    def icon(self) -> str | None:
        """Return the icon of the sensor."""
        return "mdi:weight-lifter"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._attribute)
    
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "planning": self.coordinator.data.get("Planning")
        }