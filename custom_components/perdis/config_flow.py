"""Config Flow und Options Flow für Perdis Dienstplan Integration."""
from __future__ import annotations

import voluptuous as vol
import requests
from bs4 import BeautifulSoup

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    TimeSelector,
    TimeSelectorConfig,
)

from .const import (
    DOMAIN,
    CONF_BASE_URL, CONF_USERNAME, CONF_PASSWORD,
    CONF_ALEXA_ENTITY, CONF_NOTIFY_ENTITY,
    CONF_WAKEUP_MINUTES, CONF_WAKEUP_BEFORE,
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

STEP_USER_SCHEMA = vol.Schema({
    vol.Required(CONF_BASE_URL): TextSelector(
        TextSelectorConfig(type=TextSelectorType.URL)
    ),
    vol.Required(CONF_USERNAME): TextSelector(
        TextSelectorConfig(type=TextSelectorType.TEXT)
    ),
    vol.Required(CONF_PASSWORD): TextSelector(
        TextSelectorConfig(type=TextSelectorType.PASSWORD)
    ),
})


def _notifications_schema(defaults: dict = {}) -> vol.Schema:
    """Schema für Benachrichtigungen – mit optionalen Defaults."""
    return vol.Schema({
        vol.Optional(CONF_ALEXA_ENTITY, default=defaults.get(CONF_ALEXA_ENTITY, "")): EntitySelector(
            EntitySelectorConfig(domain="media_player")
        ),
        vol.Optional(CONF_NOTIFY_ENTITY, default=defaults.get(CONF_NOTIFY_ENTITY, "")): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
        vol.Optional(CONF_WAKEUP_MINUTES, default=defaults.get(CONF_WAKEUP_MINUTES, 60)): NumberSelector(
            NumberSelectorConfig(min=15, max=240, step=15, mode=NumberSelectorMode.SLIDER)
        ),
        vol.Optional(CONF_WAKEUP_BEFORE, default=defaults.get(CONF_WAKEUP_BEFORE, "")): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT)
        ),
    })


def _test_login(base_url: str, username: str, password: str) -> bool:
    """Testet ob Login funktioniert."""
    roster_url = f"{base_url.rstrip('/')}/roster.aspx"
    session = requests.Session()

    r = session.get(roster_url, headers=HEADERS, timeout=15, allow_redirects=True)
    soup = BeautifulSoup(r.text, "html.parser")

    fields = {
        inp.get("name"): inp.get("value", "")
        for inp in soup.find_all("input", {"type": "hidden"})
        if inp.get("name")
    }
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
        """Schritt 2: Benachrichtigungen konfigurieren."""
        if user_input is not None:
            data = {**self._user_data, **user_input}
            return self.async_create_entry(
                title=f"Perdis ({self._user_data[CONF_USERNAME]})",
                data=data,
            )

        return self.async_show_form(
            step_id="notifications",
            data_schema=_notifications_schema(),
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return PerdisOptionsFlow(config_entry)


class PerdisOptionsFlow(config_entries.OptionsFlow):
    """Options Flow – Einstellungen nachträglich ändern."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Einstellungen anzeigen und speichern."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Aktuelle Werte als Defaults laden
        current = {**self.config_entry.data, **self.config_entry.options}

        return self.async_show_form(
            step_id="init",
            data_schema=_notifications_schema(current),
        )
