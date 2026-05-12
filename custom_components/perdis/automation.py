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
    wakeup_before: str = "",
) -> None:
    """Registriert die Wecker-Automation in HA."""

    automation_id = f"perdis_wecker_{entry.entry_id}"
    offset_h = wakeup_minutes // 60
    offset_m = wakeup_minutes % 60
    offset = f"-{offset_h}:{offset_m:02d}:00"

    # Condition: Ganztages-Einträge überspringen
    conditions = [{
        "condition": "template",
        "value_template": (
            "{% set title = trigger.calendar_event.summary %}"
            "{% set ganztag = ['Urlaub','Frei','Arbeitsbefreiung','Freizeitausgleich','Überstunden','Krank ohne Schein','Streik'] %}"
            "{{ title not in ganztag }}"
        ),
    }]

    # Optionale Condition: nur wecken wenn Dienst vor X Uhr
    if wakeup_before:
        conditions.append({
            "condition": "template",
            "value_template": (
                f"{{% set dienst_start = (trigger.calendar_event.start | as_datetime | as_local) %}}"
                f"{{% set grenze = today_at('{wakeup_before}') %}}"
                "{{ dienst_start < grenze }}"
            ),
        })

    actions = []

    if alexa_entity:
        actions.append({
            "service": "notify.alexa_media",
            "data": {
                "target": alexa_entity,
                "data": {"type": "announce"},
                "message": (
                    f"Guten Morgen! Dein Dienst {{{{ trigger.calendar_event.summary }}}} "
                    f"beginnt in {wakeup_minutes} Minuten um "
                    "{{ (trigger.calendar_event.start | as_datetime | as_local).strftime('%H:%M') }} "
                    "Uhr. Guten Dienst!"
                ),
            },
        })

    if notify_entity:
        # Handy-Benachrichtigung
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

    _LOGGER.info(
        "Perdis: Wecker-Automation '%s' konfiguriert (offset=%s, nur vor=%s).",
        automation_id, offset, wakeup_before or "immer"
    )
