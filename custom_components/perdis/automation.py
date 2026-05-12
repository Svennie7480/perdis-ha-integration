"""Perdis – Automatische Wecker-Automation für Home Assistant."""
from __future__ import annotations

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_automations(
    hass: HomeAssistant,
    entry: ConfigEntry,
    alexa_entity: str,
    notify_entity: str,
    wakeup_minutes: int,
) -> None:
    """Registriert die Wecker-Automation in HA."""

    from homeassistant.components.automation import (
        AutomationConfig,
    )

    automation_id = f"perdis_wecker_{entry.entry_id}"
    offset = f"-{wakeup_minutes // 60}:{wakeup_minutes % 60:02d}:00"

    actions = []

    if alexa_entity:
        actions.append({
            "service": "notify.alexa_media",
            "data": {
                "target": alexa_entity,
                "data": {"type": "announce"},
                "message": (
                    "Guten Morgen! Dein Dienst {{ trigger.calendar_event.summary }} "
                    f"beginnt in {wakeup_minutes} Minuten um "
                    "{{ (trigger.calendar_event.start | as_datetime | as_local).strftime('%H:%M') }} "
                    "Uhr. Guten Dienst!"
                ),
            },
        })

    if notify_entity:
        actions.append({
            "service": notify_entity,
            "data": {
                "title": f"⏰ Dienst in {wakeup_minutes} Minuten!",
                "message": (
                    "{{ trigger.calendar_event.summary }} beginnt um "
                    "{{ (trigger.calendar_event.start | as_datetime | as_local).strftime('%H:%M') }} Uhr"
                ),
                "data": {"ttl": 0, "priority": "high", "channel": "Wecker", "importance": "high"},
            },
        })
        # Echter Android-Wecker
        actions.append({
            "service": notify_entity,
            "data": {
                "message": "command_activity",
                "data": {
                    "intent_action": "android.intent.action.SET_ALARM",
                    "intent_extras": (
                        "android.intent.extra.alarm.HOUR:"
                        "{{ ((trigger.calendar_event.start | as_datetime | as_local) - timedelta(hours=1)).strftime('%H') }},"
                        "android.intent.extra.alarm.MINUTES:"
                        "{{ ((trigger.calendar_event.start | as_datetime | as_local) - timedelta(hours=1)).strftime('%M') }},"
                        "android.intent.extra.alarm.MESSAGE:{{ trigger.calendar_event.summary }},"
                        "android.intent.extra.alarm.SKIP_UI:true"
                    ),
                },
            },
        })

    config = {
        "id": automation_id,
        "alias": f"Perdis Wecker ({entry.data.get('username')})",
        "trigger": [{
            "platform": "calendar",
            "event": "start",
            "offset": offset,
            "entity_id": f"calendar.perdis_dienstplan_{entry.entry_id[:8]}",
        }],
        "condition": [{
            "condition": "template",
            "value_template": (
                "{% set title = trigger.calendar_event.summary %}"
                "{% set ganztag = ['Urlaub','Frei','Arbeitsbefreiung','Freizeitausgleich','Überstunden','Krank ohne Schein','Streik'] %}"
                "{{ title not in ganztag }}"
            ),
        }],
        "action": actions,
    }

    _LOGGER.info("Perdis: Wecker-Automation '%s' wurde eingerichtet.", automation_id)
