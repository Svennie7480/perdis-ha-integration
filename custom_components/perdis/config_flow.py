"""Config Flow für Perdis Dienstplan Integration."""
from __future__ import annotations

import voluptuous as vol
import requests
from bs4 import BeautifulSoup

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, CONF_BASE_URL, CONF_USERNAME, CONF_PASSWORD, CONF_ALEXA_ENTITY, CONF_NOTIFY_ENTITY, CONF_WAKEUP_MINUTES

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

STEP_USER_SCHEMA = vol.Schema({
    vol.Required(CONF_BASE_URL, default="https://perdis.svhl.de/WebComm"): str,
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
})


def _test_login(base_url: str, username: str, password: str) -> bool:
    """Testet ob Login funktioniert."""
    roster_url = f"{base_url.rstrip('/')}/roster.aspx"
    session = requests.Session()

    r = session.get(roster_url, headers=HEADERS, timeout=15, allow_redirects=True)
    soup = BeautifulSoup(r.text, "html.parser")

    fields = {inp.get("name"): inp.get("value", "") for inp in soup.find_all("input", {"type": "hidden"}) if inp.get("name")}
    user_field = next((inp.get("name") for inp in soup.find_all("input") if "UserName" in inp.get("name", "")), None)
    pass_field = next((inp.get("name") for inp in soup.find_all("input") if "Password" in inp.get("name", "")), None)

    if not user_field or not pass_field:
        return False

    payload = dict(fields)
    payload[user_field] = username
    payload[pass_field] = password
    payload["ctl00$cntMainBody$lgnView$lgnLogin$LoginButton"] = "Anmelden"

    r2 = session.post(r.url, data=payload, headers={**HEADERS, "Referer": r.url}, timeout=15, allow_redirects=True)
    return "UserName" not in r2.text or "LoginButton" not in r2.text


def _get_media_players(hass: HomeAssistant) -> dict:
    """Alle media_player Entitäten als Dropdown-Optionen."""
    registry = er.async_get(hass)
    options = {"": "– Kein Alexa –"}
    for entity in registry.entities.values():
        if entity.domain == "media_player":
            options[entity.entity_id] = entity.entity_id
    return options


def _get_notify_services(hass: HomeAssistant) -> dict:
    """Alle notify.mobile_app_* Services als Dropdown-Optionen."""
    options = {"": "– Keine Benachrichtigung –"}
    for service in hass.services.async_services().get("notify", {}).keys():
        if service.startswith("mobile_app_"):
            entity_id = f"notify.{service}"
            options[entity_id] = entity_id
    return options


class PerdisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für Perdis."""

    VERSION = 1
    _user_data: dict = {}

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Schritt 1: URL + Zugangsdaten."""
        errors = {}

        if user_input is not None:
            try:
                valid = await self.hass.async_add_executor_job(
                    _test_login,
                    user_input[CONF_BASE_URL],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                )
                if valid:
                    self._user_data = user_input
                    return await self.async_step_notifications()
                else:
                    errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def async_step_notifications(self, user_input=None) -> FlowResult:
        """Schritt 2: Benachrichtigungen mit Dropdowns."""
        if user_input is not None:
            data = {**self._user_data, **user_input}
            return self.async_create_entry(
                title=f"Perdis ({self._user_data[CONF_USERNAME]})",
                data=data,
            )

        media_players = await self.hass.async_add_executor_job(_get_media_players, self.hass)
        notify_services = _get_notify_services(self.hass)

        schema = vol.Schema({
            vol.Optional(CONF_ALEXA_ENTITY, default=""): vol.In(media_players),
            vol.Optional(CONF_NOTIFY_ENTITY, default=""): vol.In(notify_services),
            vol.Optional(CONF_WAKEUP_MINUTES, default=60): int,
        })

        return self.async_show_form(
            step_id="notifications",
            data_schema=schema,
        )
