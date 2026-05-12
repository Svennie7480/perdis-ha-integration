"""Konstanten für Perdis Dienstplan Integration."""

DOMAIN = "perdis"

CONF_BASE_URL        = "base_url"
CONF_USERNAME        = "username"
CONF_PASSWORD        = "password"
CONF_ALEXA_ENTITY    = "alexa_entity"
CONF_NOTIFY_ENTITY   = "notify_entity"
CONF_WAKEUP_MINUTES  = "wakeup_minutes"
CONF_WAKEUP_BEFORE   = "wakeup_before"  # Optional: nur wecken wenn Dienst vor X Uhr

GANZTAG_TITLES = [
    "Urlaub", "Frei", "Arbeitsbefreiung", "Freizeitausgleich",
    "Überstunden", "Krank ohne Schein", "Streik"
]
