import logging
from datetime import datetime
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from zoneinfo import ZoneInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the calendar entity for the Heitzfit4 config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([Heitzfit4Calendar(coordinator, config_entry)], False)


@callback
def async_get_calendar_event_from_bookings(planning_data, timezone) -> CalendarEvent:
    """Build a Home Assistant calendar event object from one booked activity."""
    tz = ZoneInfo(timezone)
    activity = planning_data
    return CalendarEvent(
        summary=f"{activity['activity']}",
        description=f"{activity['activity']} - {activity['room']} ({activity['duration']})",
        start=activity["start"],
        end=activity["end"],
        uid=str(activity["idActivity"]),
    )


class Heitzfit4Calendar(CalendarEntity):
    """Calendar entity exposing booked sessions as Home Assistant calendar events."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the calendar entity with the coordinator-backed planning payload."""
        self.coordinator = coordinator
        self.config_entry = entry
        self._attr_unique_id = "Heitzfit4_calendar"
        self._attr_name = "Reservation Heitzfit4"
        self._attr_icon = "mdi:weight-lifter"
        self._attr_device_info = DeviceInfo(
            name="Heitzfit4",
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, "Heitzfit4")},
            manufacturer="Heitzfit4",
            model="Heitzfit4",
        )
        self._event: CalendarEvent | None = None

    @property
    def event(self) -> CalendarEvent | None:
        """Return the currently selected event, if any."""
        return self._event

    @callback
    def _handle_coordinator_update(self) -> None:
        """Respond to a coordinator refresh by making the event list view refreshable."""
        _LOGGER.info("CALENDAR _handle_coordinator_update")
        self.async_write_ha_state()

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range from the coordinator planning payload."""
        new_events = []
        planning = self.coordinator.data.get("Planning", {}) if self.coordinator.data else {}
        for activities in planning.values():
            for activity in activities:
                if activity.get("booked"):
                    new_events.append(activity)
        return [
            async_get_calendar_event_from_bookings(event, hass.config.time_zone)
            for event in new_events
        ]