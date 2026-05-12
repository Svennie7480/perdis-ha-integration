"""Perdis Kalender-Entität für Home Assistant."""
from __future__ import annotations

from datetime import datetime, date, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import homeassistant.util.dt as dt_util

from .const import DOMAIN
from .coordinator import PerdisCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Kalender-Entität einrichten."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PerdisCalendar(coordinator, entry)])


class PerdisCalendar(CoordinatorEntity, CalendarEntity):
    """Perdis Dienstplan als HA Kalender."""

    _attr_has_entity_name = True
    _attr_name = "Dienstplan"

    def __init__(self, coordinator: PerdisCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_calendar"

    @property
    def event(self) -> CalendarEvent | None:
        """Gibt das nächste/aktuelle Event zurück."""
        now = dt_util.now()
        for shift in self._get_sorted_shifts():
            end = self._to_dt(shift["end"], shift["allday"], end=True)
            if end >= now:
                return self._to_event(shift)
        return None

    async def async_get_events(self, hass: HomeAssistant, start_date: datetime, end_date: datetime) -> list[CalendarEvent]:
        """Gibt alle Events in einem Zeitraum zurück."""
        events = []
        for shift in self.coordinator.data or []:
            start = self._to_dt(shift["start"], shift["allday"])
            end   = self._to_dt(shift["end"],   shift["allday"], end=True)
            if start < end_date and end > start_date:
                events.append(self._to_event(shift))
        return events

    def _get_sorted_shifts(self) -> list[dict]:
        return sorted(self.coordinator.data or [], key=lambda s: str(s["start"]))

    def _to_dt(self, val, allday: bool, end: bool = False) -> datetime:
        if allday:
            d = val if isinstance(val, date) else val.date()
            if end:
                d = d + timedelta(days=1)
            return dt_util.start_of_local_day(datetime(d.year, d.month, d.day))
        if val.tzinfo is None:
            return dt_util.as_local(val)
        return val

    def _to_event(self, shift: dict) -> CalendarEvent:
        if shift["allday"]:
            d = shift["start"] if isinstance(shift["start"], date) else shift["start"].date()
            return CalendarEvent(
                summary=shift["title"],
                start=d,
                end=d + timedelta(days=1),
                location=shift.get("location", ""),
            )
        return CalendarEvent(
            summary=shift["title"],
            start=self._to_dt(shift["start"], False),
            end=self._to_dt(shift["end"], False),
            location=shift.get("location", ""),
        )
