"""Perdis Dienstplan – Home Assistant Integration."""
from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN, CONF_BASE_URL, CONF_USERNAME, CONF_PASSWORD,
    CONF_ALEXA_ENTITY, CONF_NOTIFY_ENTITY, CONF_WAKEUP_MINUTES, CONF_WAKEUP_BEFORE,
)
from .coordinator import PerdisCoordinator
from .automation import async_setup_automations

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["calendar"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration einrichten."""
    coordinator = PerdisCoordinator(
        hass,
        base_url=entry.data[CONF_BASE_URL],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Einstellungen aus data ODER options laden (options überschreiben data)
    opts = {**entry.data, **entry.options}

    alexa_entity   = opts.get(CONF_ALEXA_ENTITY, "")
    notify_entity  = opts.get(CONF_NOTIFY_ENTITY, "")
    wakeup_minutes = int(opts.get(CONF_WAKEUP_MINUTES, 60))
    wakeup_before  = opts.get(CONF_WAKEUP_BEFORE, "")

    if alexa_entity or notify_entity:
        await async_setup_automations(
            hass, entry,
            alexa_entity, notify_entity,
            wakeup_minutes, wakeup_before,
        )

    # Bei Options-Änderungen neu laden
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Integration neu laden wenn Einstellungen geändert werden."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration entladen."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
