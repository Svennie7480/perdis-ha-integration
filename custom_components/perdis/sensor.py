"""Perdis Sensoren – Urlaubstage und Überstunden."""
from __future__ import annotations

import logging
import re
from datetime import datetime

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

    # Versteigerungs-Sensor
    entities.append(PerdisAuctionSensor(coordinator, entry))

    # Monatszusammenfassung
    entities.append(PerdisMonthlySummarySensor(coordinator, entry))

    # Jahresübersicht & Rekorde
    entities.append(PerdisAbsencesSensor(coordinator, entry))
    entities.append(PerdisRecordsSensor(coordinator, entry))

    async_add_entities(entities)


class PerdisAbsencesSensor(CoordinatorEntity, SensorEntity):
    """Sensor für die Jahresübersicht."""

    _attr_has_entity_name = True
    _attr_name = "Jahresübersicht"
    _attr_icon = "mdi:calendar-year"

    def __init__(self, coordinator: PerdisCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_absences"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        absences = self.coordinator.data.get("absences", {})
        counts = absences.get("counts", {})
        return counts.get("urlaub", 0)

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        absences = self.coordinator.data.get("absences", {})
        counts = absences.get("counts", {})
        return {
            "year":               absences.get("year", ""),
            "urlaub_tage":        counts.get("urlaub", 0),
            "krank_tage":         counts.get("krank", 0),
            "arbeitsbefreiung":   counts.get("arbeitsbefreiung", 0),
            "freizeitausgleich":  counts.get("freizeitausgleich", 0),
            "streik_tage":        counts.get("streik", 0),
            "ueberstunden_abbau": counts.get("ueberstunden_abbau", 0),
            "summary":            absences.get("summary", []),
        }


class PerdisRecordsSensor(CoordinatorEntity, SensorEntity):
    """Sensor für Rekorde aus dem Dienstplan."""

    _attr_has_entity_name = True
    _attr_name = "Rekorde"
    _attr_icon = "mdi:trophy"

    def __init__(self, coordinator: PerdisCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_records"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        shifts = self.coordinator.data.get("shifts", [])
        ganztag = ["Urlaub","Frei","Arbeitsbefreiung","Freizeitausgleich",
                   "Überstunden","Krank ohne Schein","Streik"]
        work = [s for s in shifts if s.get("title") not in ganztag and s.get("start") and s.get("end")]
        return len(work)

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        shifts = self.coordinator.data.get("shifts", [])
        ganztag = ["Urlaub","Frei","Arbeitsbefreiung","Freizeitausgleich",
                   "Überstunden","Krank ohne Schein","Streik"]

        longest_minutes = 0
        longest_dienst = ""
        longest_date = ""
        earliest_start = "23:59"
        earliest_date = ""
        latest_end = "00:00"
        latest_date = ""

        for s in shifts:
            if not s.get("title") or s["title"] in ganztag:
                continue
            if not s.get("start") or not s.get("end"):
                continue

            try:
                start_dt = s["start"] if isinstance(s["start"], datetime) else datetime.fromisoformat(str(s["start"]))
                end_dt   = s["end"]   if isinstance(s["end"],   datetime) else datetime.fromisoformat(str(s["end"]))
            except Exception:
                continue
            minutes  = int((end_dt - start_dt).total_seconds() / 60)
            start_time = start_dt.strftime("%H:%M")
            end_time   = end_dt.strftime("%H:%M")
            date_str   = start_dt.strftime("%d.%m.%Y")

            if minutes > longest_minutes:
                longest_minutes = minutes
                longest_dienst  = s["title"]
                longest_date    = date_str

            if start_time < earliest_start:
                earliest_start = start_time
                earliest_date  = date_str

            if end_time > latest_end:
                latest_end  = end_time
                latest_date = date_str

        return {
            "laengster_dienst_min":  longest_minutes,
            "laengster_dienst_h":    round(longest_minutes / 60, 1),
            "laengster_dienst_name": longest_dienst,
            "laengster_dienst_datum": longest_date,
            "fruehester_start":      earliest_start,
            "fruehester_start_datum": earliest_date,
            "spaetestes_ende":       latest_end,
            "spaetestes_ende_datum": latest_date,
        }


class PerdisMonthlySummarySensor(CoordinatorEntity, SensorEntity):
    """Sensor für die monatliche Zusammenfassung."""

    _attr_has_entity_name = True
    _attr_name = "Monatsübersicht"
    _attr_icon = "mdi:calendar-month"

    def __init__(self, coordinator: PerdisCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_monthly_summary"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        shifts = self.coordinator.data.get("shifts", [])
        now = datetime.now()
        month_shifts = []
        for s in shifts:
            if not s.get("start"):
                continue
            try:
                dt = s["start"] if isinstance(s["start"], datetime) else datetime.fromisoformat(str(s["start"]))
                if dt.month == now.month and dt.year == now.year and not s.get("allday", False):
                    month_shifts.append(s)
            except Exception:
                pass
        return len(month_shifts)

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        shifts = self.coordinator.data.get("shifts", [])
        now = datetime.now()

        # Dienste diesen Monat
        month_shifts = []
        ganztag = ["Urlaub","Frei","Arbeitsbefreiung","Freizeitausgleich",
                   "Überstunden","Krank ohne Schein","Streik"]

        total_minutes = 0
        dienst_count = 0
        frueh_count = 0   # Dienste die vor 09:00 beginnen
        spaet_count = 0   # Dienste die nach 18:00 enden
        nacht_count = 0   # Dienste die nach 22:00 enden

        for s in shifts:
            if not s.get("start"):
                continue
            start_dt = as_datetime(s["start"])
            if start_dt.month != now.month or start_dt.year != now.year:
                continue
            title = s.get("title", "")
            if title in ganztag:
                continue

            end_dt = as_datetime(s["end"]) if s.get("end") else None
            dienst_count += 1

            if end_dt:
                minutes = int((end_dt - start_dt).total_seconds() / 60)
                total_minutes += minutes
                if end_dt.hour >= 22:
                    nacht_count += 1
                elif end_dt.hour >= 18:
                    spaet_count += 1

            if start_dt.hour < 9:
                frueh_count += 1

        avg_minutes = int(total_minutes / dienst_count) if dienst_count > 0 else 0

        return {
            "dienste_gesamt":  dienst_count,
            "stunden_gesamt":  round(total_minutes / 60, 1),
            "durchschnitt_h":  round(avg_minutes / 60, 1),
            "fruehschichten":  frueh_count,
            "spaetschichten":  spaet_count,
            "nachtschichten":  nacht_count,
            "monat":           now.strftime("%B %Y"),
        }


class PerdisAuctionSensor(CoordinatorEntity, SensorEntity):
    """Sensor für die Dienstversteigerung."""

    _attr_has_entity_name = True
    _attr_name = "Dienstversteigerung"

    def __init__(self, coordinator: PerdisCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_auction"
        self._prev_has_leitstelle = False

    @property
    def icon(self):
        auction = (self.coordinator.data or {}).get("auction", {})
        if auction.get("has_leitstelle"):
            return "mdi:alert-decagram"
        return "mdi:gavel"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return "Keine Dienste in der Versteigerung"
        auction = self.coordinator.data.get("auction", {})
        total = auction.get("total", 0)
        leitstelle = len(auction.get("leitstelle_items", []))
        if total == 0:
            return "Keine Dienste in der Versteigerung"
        if leitstelle > 0:
            return f"⚠️ {leitstelle} Leitstellen-Dienst | {total} gesamt"
        return f"{total} Dienste verfügbar"

    @property
    def extra_state_attributes(self):
        auction = (self.coordinator.data or {}).get("auction", {})
        return {
            "items":            auction.get("items", []),
            "has_leitstelle":   auction.get("has_leitstelle", False),
            "leitstelle_items": auction.get("leitstelle_items", []),
            "total":            auction.get("total", 0),
        }


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
