"""Initialisation du package de l'intégration """
import asyncio
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .api import Heitzfit4API
from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "calendar"]

SERVICE_SCHEMA = vol.Schema({vol.Required("activity_id"): cv.string})


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register Home Assistant services exposed by this integration."""

    async def _book_activity(call: ServiceCall) -> None:
        activity_id = str(call.data["activity_id"])
        await _dispatch_activity_action(hass, activity_id, "book")

    async def _delete_activity(call: ServiceCall) -> None:
        activity_id = str(call.data["activity_id"])
        await _dispatch_activity_action(hass, activity_id, "delete")

    # Register integration domain services.
    if not hass.services.has_service(DOMAIN, "book_activity"):
        hass.services.async_register(DOMAIN, "book_activity", _book_activity, schema=SERVICE_SCHEMA)
    if not hass.services.has_service(DOMAIN, "delete_activity"):
        hass.services.async_register(DOMAIN, "delete_activity", _delete_activity, schema=SERVICE_SCHEMA)

    # Register compatibility aliases for the service domain used by the card.
    if not hass.services.has_service("heitzfit", "book_activity"):
        hass.services.async_register("heitzfit", "book_activity", _book_activity, schema=SERVICE_SCHEMA)
    if not hass.services.has_service("heitzfit", "delete_activity"):
        hass.services.async_register("heitzfit", "delete_activity", _delete_activity, schema=SERVICE_SCHEMA)

    # Alias names requested by the custom Lovelace card style.
    if not hass.services.has_service("heitzfit", "heitzfit_book"):
        hass.services.async_register("heitzfit", "heitzfit_book", _book_activity, schema=SERVICE_SCHEMA)
    if not hass.services.has_service("heitzfit", "heitzfit_book_delete"):
        hass.services.async_register("heitzfit", "heitzfit_book_delete", _delete_activity, schema=SERVICE_SCHEMA)

    # Optional alias names matching the requested card action names.
    if not hass.services.has_service(DOMAIN, "heitzfit_book"):
        hass.services.async_register(DOMAIN, "heitzfit_book", _book_activity, schema=SERVICE_SCHEMA)
    if not hass.services.has_service(DOMAIN, "heitzfit_book_delete"):
        hass.services.async_register(DOMAIN, "heitzfit_book_delete", _delete_activity, schema=SERVICE_SCHEMA)

    return True


async def _dispatch_activity_action(hass: HomeAssistant, activity_id: str, action: str) -> None:
    """Route a booking/cancellation request to the first loaded coordinator API."""
    entries = hass.data.get(DOMAIN, {})
    if not entries:
        raise HomeAssistantError("No heitzfit4 config entry is loaded. Cannot dispatch booking service.")

    coordinator = next(iter(entries.values()))
    api = getattr(coordinator, "api", None)
    if api is None:
        raise HomeAssistantError("Heitzfit4 API client is not available on the loaded coordinator.")

    if action == "book":
        await api.async_book_activity(activity_id)
    elif action == "delete":
        await api.async_delete_activity(activity_id)
    else:
        raise HomeAssistantError(f"Unsupported heitzfit4 activity action: {action}")


async def async_migrate_entry(hass, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:

        new = {**config_entry.data}
        new["club"] = "club"

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new)

    _LOGGER.debug("Migration to version %s successful", config_entry.version)

    return True

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry
):  # pylint: disable=unused-argument
    """Initialisation de l'intégration"""
    # _LOGGER.info(
    #     "Initializing %s integration with plaforms: %s with config: %s",
    #     DOMAIN,
    #     PLATFORMS,
    #     config,
    # )
    coordinator = Heitzfit4DataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.info("Coordinator initialized")
    _LOGGER.info(coordinator)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    #for platform in PLATFORMS:
    #    # await hass.async_add_executor_job(  KO TypeError: 'coroutine' object is not callable)
    #    hass.async_add_job(
    #        hass.config_entries.async_forward_entry_setup(entry, platform)
    #    )
    #    _LOGGER.info("Forwarding entry setup for %s", platform)

    # Envoie toutes les plateformes d'un coup de manière moderne
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.info("Forwarding entry setups for %s", PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)

class Heitzfit4DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Heitzfit4 data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize."""
        self.hass = hass
        self.entry = entry
        self.api = Heitzfit4API(entry.data["club"], entry.data["username"], entry.data["password"], entry.data["nbdays"])
        # self._attr_name = entry.get("name")
        # self._attr_unique_id = entry.get("entity_id")
        self._attr_has_entity_name = True

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=120),
        )

    async def _async_update_data(self):
        """Update data via library."""
        await self.api.async_sign_in()
        # await self.api.async_get_planning()
        return await self.api.async_get_planning()