"""Perdis Dienstplan – Home Assistant Integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_BASE_URL, CONF_USERNAME, CONF_PASSWORD, CONF_ALEXA_ENTITY, CONF_NOTIFY_ENTITY, CONF_WAKEUP_MINUTES
from .coordinator import PerdisCoordinator
from .automation import async_setup_automations

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

    # Wecker-Automation einrichten falls konfiguriert
    alexa_entity  = entry.data.get(CONF_ALEXA_ENTITY, "")
    notify_entity = entry.data.get(CONF_NOTIFY_ENTITY, "")
    wakeup_minutes = entry.data.get(CONF_WAKEUP_MINUTES, 60)

    if alexa_entity or notify_entity:
        await async_setup_automations(hass, entry, alexa_entity, notify_entity, wakeup_minutes)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration entladen."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
