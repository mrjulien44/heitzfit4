"""Initialisation du package de l'intégration """
import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .api import Heitzfit4API
from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "calendar"]


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