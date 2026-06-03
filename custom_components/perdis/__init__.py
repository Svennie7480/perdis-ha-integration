"""Perdis Dienstplan – Home Assistant Integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN, CONF_BASE_URL, CONF_USERNAME, CONF_PASSWORD,
    CONF_ALEXA_ENTITY, CONF_NOTIFY_ENTITY, CONF_WAKEUP_MINUTES, CONF_WAKEUP_BEFORE,
)
from .coordinator import PerdisCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["calendar", "sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration einrichten."""
    coordinator = PerdisCoordinator(
        hass,
        base_url=entry.data[CONF_BASE_URL],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
    )

    await coordinator.async_config_entry_first_refresh()
    await async_setup_services(hass)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Bei Options-Änderungen neu laden
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Integration neu laden wenn Einstellungen geändert werden."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Registriert Perdis Services."""

    async def handle_accept_auction(call):
        dienst_id = call.data.get("dienst_id")
        action = call.data.get("action", "accept_time")
        for entry_id, coordinator in hass.data[DOMAIN].items():
            result = await hass.async_add_executor_job(
                coordinator.accept_auction, dienst_id, action
            )
            _LOGGER.info("Perdis accept_auction %s %s → %s", dienst_id, action, result)
            await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "accept_auction", handle_accept_auction)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration entladen."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
