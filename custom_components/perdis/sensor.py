"""Perdis Sensoren – Urlaubstage und Überstunden."""
from __future__ import annotations

import logging
import re

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PerdisCoordinator

_LOGGER = logging.getLogger(__name__)


class PerdisMessageSensor(CoordinatorEntity, SensorEntity):
    """Sensor für die neueste Perdis Nachricht."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:message-text"

    def __init__(self, coordinator: PerdisCoordinator, entry: ConfigEntry, key: str, label: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = label
        self._attr_unique_id = f"{entry.entry_id}_msg_{key}"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        msg = self.coordinator.data.get("message", {})
        return msg.get(self._key)

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        msg = self.coordinator.data.get("message", {})
        return {
            "betreff": msg.get("betreff", ""),
            "text":    msg.get("text", ""),
            "header":  msg.get("header", ""),
            "total":   msg.get("total", 0),
        }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensor-Entitäten einrichten."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    # Urlaubstage-Sensoren
    for key, label in [
        ("urlaub_rest",     "Urlaub Rest"),
        ("urlaub_anspruch", "Urlaub Anspruch"),
        ("urlaub_plan",     "Urlaub Plan"),
        ("zusatzurlaub_rest", "Zusatzurlaub Rest"),
    ]:
        entities.append(PerdisSensor(coordinator, entry, key, label, "d", "mdi:beach"))

    # Überstunden-Sensoren
    for key, label in [
        ("ueberstunden",       "Überstunden"),
        ("soll_ist",           "Soll-/Ist-Leistung"),
        ("tvk_privat",         "TVK Privat"),
        ("langzeitkonto",      "Langzeitkonto"),
        ("samstagszuschlag",   "Samstagszuschlag"),
        ("sonntagszuschlag",   "Sonntagszuschlag"),
        ("feiertag_100",       "Feiertag 100%"),
        ("urlaubsaufschlag",   "Urlaubsaufschlag"),
    ]:
        entities.append(PerdisSensor(coordinator, entry, key, label, "h", "mdi:clock-outline"))

    # Nachrichten-Sensoren
    entities.append(PerdisMessageSensor(coordinator, entry, "betreff", "Letzte Nachricht Betreff"))
    entities.append(PerdisMessageSensor(coordinator, entry, "total",   "Nachrichten Anzahl"))

    # Dienstdetail-Sensor
    entities.append(PerdisShiftDetailSensor(coordinator, entry))

    async_add_entities(entities)


class PerdisShiftDetailSensor(CoordinatorEntity, SensorEntity):
    """Sensor für die Dienstdetails des aktuellen Tages."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:bus-clock"
    _attr_name = "Dienstdetail Heute"

    def __init__(self, coordinator: PerdisCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_shift_detail"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        detail = self.coordinator.data.get("shift_detail", {})
        linien = detail.get("linien", [])
        if not linien:
            return "Kein Dienst"
        return f"Linien: {', '.join(linien)}"

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        detail = self.coordinator.data.get("shift_detail", {})
        return {
            "date":             detail.get("date", ""),
            "start_ort":        detail.get("start_ort", ""),
            "end_ort":          detail.get("end_ort", ""),
            "linien":           detail.get("linien", []),
            "wende_total_min":  detail.get("wende_total", 0),
            "pause_bezahlt_min":   detail.get("pause_bezahlt", 0),
            "pause_unbezahlt_min": detail.get("pause_unbezahlt", 0),
            "rows":             detail.get("rows", []),
        }


class PerdisSensor(CoordinatorEntity, SensorEntity):
    """Ein Perdis Sensor für Urlaubstage oder Überstunden."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PerdisCoordinator,
        entry: ConfigEntry,
        key: str,
        label: str,
        unit: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator)
        self._key   = key
        self._label = label
        self._attr_name          = label
        self._attr_unique_id     = f"{entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon          = icon

    @property
    def native_value(self):
        """Aktueller Wert des Sensors."""
        if not self.coordinator.data:
            return None
        balances = self.coordinator.data.get("balances", {})
        return balances.get(self._key)
