"""Perdis DataUpdateCoordinator – Scraper-Logik für Home Assistant."""
from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone, date

import requests
from bs4 import BeautifulSoup

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9",
}

GANZTAG = {
    "U":   "Urlaub",
    "AB":  "Arbeitsbefreiung",
    "F":   "Frei",
    "FM":  "Freizeitausgleich",
    "FA":  "Überstunden",
    "KOS": "Krank ohne Schein",
    "STR": "Streik",
}


class PerdisCoordinator(DataUpdateCoordinator):
    """Koordiniert das tägliche Abrufen des Perdis Dienstplans."""

    def __init__(self, hass: HomeAssistant, base_url: str, username: str, password: str) -> None:
        self.base_url    = base_url.rstrip("/")
        self.username    = username
        self.password    = password
        self.roster_url  = f"{self.base_url}/roster.aspx"
        self.planbals_url = f"{self.base_url}/planbals.aspx"
        self.balances_url = f"{self.base_url}/balances.aspx"

        super().__init__(
            hass,
            _LOGGER,
            name="Perdis Dienstplan",
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self) -> list[dict]:
        """Wird von HA automatisch stündlich aufgerufen."""
        try:
            result = await self.hass.async_add_executor_job(self._fetch_all_months)
            return result
        except PermissionError as err:
            raise UpdateFailed(f"Login fehlgeschlagen: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Fehler beim Abrufen: {err}") from err

    def _fetch_all_months(self) -> dict:
        """Login + 3 Monate scrapen + Balances laden."""
        session = requests.Session()
        self._login(session)

        all_shifts = []
        now = datetime.now()
        for i in range(3):
            month = (now.month - 1 + i) % 12 + 1
            year  = now.year + (now.month - 1 + i) // 12
            shifts = self._fetch_month(session, year, month)
            all_shifts.extend(shifts)

        # Duplikate entfernen
        seen = set()
        unique = []
        for s in all_shifts:
            key = (str(s["start"]), s["title"])
            if key not in seen:
                seen.add(key)
                unique.append(s)

        _LOGGER.info("Perdis: %d Einträge für 3 Monate geladen.", len(unique))

        # Balances laden
        balances = self._fetch_balances(session)

        return {"shifts": unique, "balances": balances}

    def _login(self, session: requests.Session) -> None:
        """ASP.NET Login mit Cookie-Redirect-Flow."""
        # Schritt 1: roster.aspx → folgt Redirects → Login-Seite
        r = session.get(self.roster_url, headers=HEADERS, timeout=15, allow_redirects=True)
        r.raise_for_status()
        login_url = r.url
        soup = BeautifulSoup(r.text, "html.parser")

        # Hidden Fields sammeln
        fields = {}
        for inp in soup.find_all("input", {"type": "hidden"}):
            name = inp.get("name", "")
            if name:
                fields[name] = inp.get("value", "")

        # Login-Felder finden
        user_field = next((inp.get("name") for inp in soup.find_all("input") if "UserName" in inp.get("name", "")), None)
        pass_field = next((inp.get("name") for inp in soup.find_all("input") if "Password" in inp.get("name", "")), None)

        if not user_field or not pass_field:
            raise UpdateFailed("Login-Felder nicht gefunden")

        # Schritt 2: Login-POST
        payload = {k: v for k, v in fields.items()}
        payload[user_field] = self.username
        payload[pass_field] = self.password
        payload["ctl00$cntMainBody$lgnView$lgnLogin$LoginButton"] = "Anmelden"

        post_headers = {**HEADERS, "Referer": login_url, "Content-Type": "application/x-www-form-urlencoded"}
        r2 = session.post(login_url, data=payload, headers=post_headers, timeout=15, allow_redirects=True)
        r2.raise_for_status()

        # Login-Prüfung
        if "UserName" in r2.text and "LoginButton" in r2.text:
            raise PermissionError("Benutzername oder Passwort falsch")

        # Schritt 3: roster.aspx abrufen um Session zu aktivieren
        if "roster.aspx" not in r2.url:
            session.get(self.roster_url, headers=HEADERS, timeout=15, allow_redirects=True)

    def _fetch_month(self, session: requests.Session, year: int, month: int) -> list[dict]:
        """Einen Monat abrufen und parsen."""
        url = f"{self.roster_url}?{year}-{month:02d}-01"
        r = session.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        r.raise_for_status()
        return self._parse(BeautifulSoup(r.text, "html.parser"))

    def _fetch_balances(self, session: requests.Session) -> dict:
        """Urlaubstage und Überstunden von planbals.aspx und balances.aspx laden."""
        balances = {}

        try:
            # Plansalden (Urlaubstage)
            r = session.get(self.planbals_url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            for row in soup.select("table tbody tr"):
                cells = row.find_all("td")
                if len(cells) >= 5:
                    konto = cells[0].get_text(strip=True)
                    rest     = self._parse_days(cells[3].get_text(strip=True))
                    anspruch = self._parse_days(cells[4].get_text(strip=True))
                    plan     = self._parse_days(cells[5].get_text(strip=True)) if len(cells) > 5 else None

                    if konto.startswith("U Urlaub"):
                        balances["urlaub_rest"]     = rest
                        balances["urlaub_anspruch"] = anspruch
                        balances["urlaub_plan"]     = plan
                    elif konto.startswith("UF"):
                        balances["zusatzurlaub_rest"] = rest

            # Salden (Überstunden etc.)
            r2 = session.get(self.balances_url, headers=HEADERS, timeout=15)
            soup2 = BeautifulSoup(r2.text, "html.parser")
            key_map = {
                "Überstunden":      "ueberstunden",
                "Soll-/Ist":        "soll_ist",
                "TVK Privat":       "tvk_privat",
                "Langzeitkonto":    "langzeitkonto",
                "Samstagszuschlag": "samstagszuschlag",
                "Sonntagszuschlag": "sonntagszuschlag",
                "Feiertag 100%":    "feiertag_100",
                "Urlaubsaufschlag": "urlaubsaufschlag",
            }
            for row in soup2.select("table tbody tr"):
                cells = row.find_all("td")
                if len(cells) >= 4:
                    konto = cells[0].get_text(strip=True)
                    wert  = cells[3].get_text(strip=True)
                    for k, v in key_map.items():
                        if konto.startswith(k):
                            balances[v] = self._parse_hours(wert)
                            break

            _LOGGER.info("Perdis Balances geladen: %s", list(balances.keys()))
        except Exception as err:
            _LOGGER.warning("Perdis: Fehler beim Laden der Balances: %s", err)

        return balances

    def _parse_days(self, val: str) -> float | None:
        """Parst Tageswerte wie '24,00' oder '24.00'."""
        try:
            return float(val.replace(",", "."))
        except (ValueError, AttributeError):
            return None

    def _parse_hours(self, val: str) -> float | None:
        """Parst Stundenwerte wie '90:22' → 90.37 Stunden."""
        try:
            if ":" in val:
                h, m = val.split(":")
                negative = h.startswith("-")
                hours = abs(int(h)) + int(m) / 60
                return -round(hours, 2) if negative else round(hours, 2)
            return float(val.replace(",", "."))
        except (ValueError, AttributeError):
            return None

    def _parse(self, soup: BeautifulSoup) -> list[dict]:
        """Kalender-HTML parsen → Liste von Schicht-Dicts."""
        shifts = []
        cells = soup.find_all("td", class_=lambda c: c and "calDay" in c.split() and "calOther" not in c.split())

        for cell in cells:
            title_attr = cell.get("title", "").strip()
            a_tag = cell.find("a", href=True)
            if not a_tag:
                continue
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", a_tag["href"])
            if not date_match:
                continue
            date_str = date_match.group(1)
            day = datetime.strptime(date_str, "%Y-%m-%d").date()

            # Ganztages-Einträge
            span = cell.find("span")
            kuerzel = span.get_text(strip=True) if span else ""
            if kuerzel in GANZTAG and "Zeit:" not in title_attr:
                shifts.append({
                    "title":  GANZTAG[kuerzel],
                    "start":  day,
                    "end":    day,
                    "allday": True,
                    "location": "",
                })
                continue

            # Normale Schichten
            if "Zeit:" not in title_attr:
                continue

            dienst_match = re.search(r"Dienst:\s*(.+?)\s*•", title_attr)
            dienst_name  = dienst_match.group(1).strip() if dienst_match else "Dienst"

            time_match = re.search(r"Zeit:\s*(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", title_attr)
            if not time_match:
                continue

            start_str = time_match.group(1)
            end_str   = time_match.group(2)

            loc_match   = re.search(r"Anfangsort:\s*(.+?)\s*•", title_attr)
            location    = loc_match.group(1).strip() if loc_match else ""

            desc_match  = re.search(r"Beschreibung:\s*•?\s*(.+?)(?:\s*•|$)", title_attr)
            description = desc_match.group(1).strip() if desc_match else ""

            dt_start = datetime.combine(day, datetime.strptime(start_str, "%H:%M").time())
            dt_end   = datetime.combine(day, datetime.strptime(end_str,   "%H:%M").time())
            if dt_end <= dt_start:
                dt_end += timedelta(days=1)

            summary = dienst_name
            if description and description.lower() != dienst_name.lower():
                summary += f" – {description}"

            shifts.append({
                "title":    summary,
                "start":    dt_start,
                "end":      dt_end,
                "allday":   False,
                "location": location,
            })

        return shifts
