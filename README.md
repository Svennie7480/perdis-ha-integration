# Perdis WebComm – Home Assistant Integration

Eine inoffizielle Home Assistant Integration für das Perdis WebComm Personalplanungssystem. Die Integration liest Dienstplandaten, Urlaubssalden, Überstunden, Nachrichten, Dienstversteigerungen und Jahresübersichten direkt aus dem Perdis WebComm Portal und stellt sie als Sensoren in Home Assistant bereit.

> **Hinweis:** Diese Integration ist nicht offiziell von Perdis/IVU Traffic Technologies unterstützt. Sie funktioniert durch Web-Scraping des WebComm-Portals.

---

## Version 1.2.0

### Neu in 1.2.0
- 📅 **Dienstdetail** – komplette Tagesübersicht mit Wendezeiten und Pausen (Pop-up)
- 🔨 **Dienstversteigerung** – verfügbare Dienste mit Leitstellen-Alarm
- 📬 **Nachrichten-Sensor** – neueste Perdis Nachricht mit Betreff und Text
- 📊 **Monatsübersicht** – Dienste, Stunden, Früh-/Spät-/Nachtschichten
- 📅 **Jahresübersicht** – Urlaub (geplant + genommen), Krank (K/KOS), AB, FM, ET, Streik
- 🏆 **Rekorde** – Frühester Start, Spätestes Ende, Längster Dienst des laufenden Jahres
- 🔔 **Automationen** – Benachrichtigung bei neuer Nachricht, neuem Dienstplan, Leitstellen-Dienst
- 🌤️ **Wetter** im Dashboard
- 🎨 **Perdis Dark Theme** mit Hintergrundbild
- ⏰ **Zeitfenster für Wecker** – Wecker nur zwischen konfigurierbaren Uhrzeiten erlaubt
- 🕐 **Dienste bis 28:xx Uhr** werden korrekt verarbeitet
- 🌿 **Entlastungstage (ET)** werden erkannt und gezählt
- 📆 **Komplettes Jahres-Laden** – Januar bis aktueller Monat + 2 Monate voraus

---

## Features

### 📆 Dienstplan
- 🚌 **Kalender** – Dienstplan als Home Assistant Kalender (Jan bis aktuell +2 Monate)
- 📅 **Dienstdetail** – komplette Tagesübersicht mit Linien, Wendezeiten und Pausen (klickbares Pop-up)
- 🏖️ Urlaub, Frei, AB, FM, ET, Streik etc. werden im Kalender angezeigt aber **nicht geweckt**
- 🕐 Dienste die nach Mitternacht enden (z.B. 28:08 Uhr) werden korrekt verarbeitet
- 🔄 **Stündliche automatische Aktualisierung**

### ⏰ Wecker & Benachrichtigungen
- ⏰ **Automatischer Wecker** X Minuten vor Dienstbeginn (konfigurierbar)
- 🔔 **Alexa-Ansage** + **Android-Wecker** + **Handy-Benachrichtigung**
- 🕐 Wecker nur innerhalb eines **konfigurierbaren Zeitfensters** (z.B. 21:00–09:30)
- 🖥️ **Leitstellen-Alarm** – sofortige Benachrichtigung wenn Dienste 800–899 oder „Auslaufdienst Leitstelle" in der Versteigerung erscheinen
- 📬 **Neue Nachricht** – Benachrichtigung bei neuer Perdis-Nachricht
- 📅 **Neuer Dienstplan** – Benachrichtigung wenn sich der Kalender ändert

### 🏖️ Urlaub & Salden
- Urlaubssalden – Rest, Anspruch, Plan, Zusatzurlaub
- Überstunden & Salden – Überstunden, Langzeitkonto, TVK Privat, Soll/Ist
- Farbwarnung bei zu vielen Überstunden (grün/orange/rot)
- Farbwarnung bei wenig Resturlaub

### 📊 Statistiken
- **Monatsübersicht** – Dienste, Stunden, Durchschnitt, Früh-/Spät-/Nachtschichten
- **Jahresübersicht** – Urlaub (geplant + genommen), Krank (K + KOS getrennt), AB, FM, ET, Streik, Überstundenabbau
- **Rekorde** – Frühester Start, Spätestes Ende, Längster Dienst des laufenden Jahres

### 📬 Nachrichten
- Neueste Nachricht mit Betreff und Text
- Gesamtanzahl Nachrichten

### 🔨 Dienstversteigerung
- Alle verfügbaren Dienste auf einen Blick
- Leitstellen-Dienste (800–899 + „Auslaufdienst Leitstelle") werden rot hervorgehoben
- Sofortige Benachrichtigung auf Alexa + Handy bei Leitstellen-Diensten

### ⚙️ Konfiguration
- Einstellungen jederzeit nachträglich änderbar
- Mehrere Mitarbeiter pro HA-Installation möglich
- Zeitfenster für Wecker konfigurierbar

---

## Voraussetzungen

- Home Assistant 2024.1 oder neuer
- Zugang zu einem Perdis WebComm Portal
- HACS (für einfache Installation)

---

## Installation

### Via HACS (empfohlen)

1. HACS → Integrationen → ⋮ → **Benutzerdefinierte Repositories**
2. URL: `https://github.com/Svennie7480/perdis-ha-integration`
3. Kategorie: **Integration**
4. Hinzufügen → **Perdis WebComm** installieren
5. Home Assistant neu starten

### Manuell

```bash
cd /homeassistant/custom_components
mkdir perdis
wget -O /homeassistant/custom_components/perdis/coordinator.py https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/coordinator.py
wget -O /homeassistant/custom_components/perdis/sensor.py https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/sensor.py
wget -O /homeassistant/custom_components/perdis/calendar.py https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/calendar.py
wget -O /homeassistant/custom_components/perdis/config_flow.py https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/config_flow.py
wget -O /homeassistant/custom_components/perdis/const.py https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/const.py
wget -O /homeassistant/custom_components/perdis/__init__.py https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/__init__.py
wget -O /homeassistant/custom_components/perdis/manifest.json https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/manifest.json
wget -O /homeassistant/custom_components/perdis/strings.json https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/strings.json
```

---

## Einrichtung

1. **Einstellungen** → **Integrationen** → **+ Hinzufügen**
2. Nach **Perdis WebComm** suchen
3. Folgende Daten eingeben:

| Feld | Beschreibung | Beispiel |
|------|-------------|---------|
| WebComm URL | URL des Perdis Portals | `https://perdis.svhl.de/WebComm` |
| Benutzername | Mitarbeiternummer | `183` |
| Passwort | WebComm Passwort | |
| Alexa Gerät | Optional | `media_player.echo_show` |
| Handy | Optional | `notify.mobile_app_meinhandy` |
| Weckzeit (Minuten) | Minuten vor Dienst | `75` |
| Wecker ab | Früheste Weckzeit | `21:00` |
| Wecker bis | Späteste Weckzeit | `09:30` |

---

## Verfügbare Entitäten

### Kalender
| Entität | Beschreibung |
|---------|-------------|
| `calendar.dienstplan` | Alle Dienste als Kalendereinträge |

### Sensoren – Urlaub
| Entität | Beschreibung |
|---------|-------------|
| `sensor.urlaub_rest` | Verbleibende Urlaubstage |
| `sensor.urlaub_anspruch` | Gesamter Urlaubsanspruch |
| `sensor.urlaub_plan` | Geplante Urlaubstage |
| `sensor.zusatzurlaub_rest` | Verbleibender Zusatzurlaub |

### Sensoren – Überstunden & Salden
| Entität | Beschreibung |
|---------|-------------|
| `sensor.uberstunden` | Aktuelle Überstunden |
| `sensor.langzeitkonto` | Langzeitkonto-Saldo |
| `sensor.tvk_privat` | TVK Privat-Saldo |
| `sensor.soll_ist_leistung` | Soll-/Ist-Leistung |
| `sensor.samstagszuschlag` | Samstagszuschlag |
| `sensor.sonntagszuschlag` | Sonntagszuschlag |
| `sensor.feiertag_100` | Feiertagszuschlag 100% |
| `sensor.urlaubsaufschlag` | Urlaubsaufschlag |

### Sensoren – Statistiken
| Entität | Beschreibung |
|---------|-------------|
| `sensor.monatsubersicht` | Monatsstatistik mit Attributen |
| `sensor.jahresubersicht` | Jahresstatistik mit Attributen |
| `sensor.rekorde` | Rekorde des laufenden Jahres |

### Sensoren – Nachrichten & Dienste
| Entität | Beschreibung |
|---------|-------------|
| `sensor.letzte_nachricht_betreff` | Neueste Nachricht |
| `sensor.nachrichten_anzahl` | Anzahl Nachrichten |
| `sensor.dienstdetail_heute` | Dienstdetails heute |
| `sensor.dienstversteigerung` | Verfügbare Dienste |

---

## Ganztags-Einträge

| Kürzel | Bedeutung |
|--------|-----------|
| `U` | Urlaub |
| `AB` | Arbeitsbefreiung |
| `F` | Frei |
| `FM` | Freizeitausgleich / Frei Mehrleistung |
| `FA` | Überstundenabbau |
| `K` | Krank mit Schein |
| `KOS` | Krank ohne Schein |
| `STR` | Streik |
| `ET` | Entlastungstag |

---

## Dashboard

Im Repository liegt eine fertige Dashboard-Konfiguration (`dashboard/perdis_dashboard.yaml`) mit 3-Spalten-Layout:

- **Spalte 1:** Nächster Dienst + Dienstdetail + Dienstversteigerung + Dieser Monat
- **Spalte 2:** Urlaub + Wetter + Jahresübersicht + Rekorde
- **Spalte 3:** Kalender + Überstunden & Salden + Letzte Nachricht

### Benötigte HACS Frontend-Pakete
- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom)
- [Atomic Calendar Revive](https://github.com/totaldebug/atomic-calendar-revive)
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod)
- [Browser Mod](https://github.com/thomasloven/lovelace-browser-mod)

---

## Theme

```bash
mkdir -p /homeassistant/themes/perdis
# perdis.yaml nach /homeassistant/themes/perdis/perdis.yaml kopieren
```

In `configuration.yaml`:
```yaml
frontend:
  themes: !include_dir_merge_named themes
```

---

## Updateanleitung

```bash
wget -O /homeassistant/custom_components/perdis/coordinator.py https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/coordinator.py
wget -O /homeassistant/custom_components/perdis/sensor.py https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/sensor.py
wget -O /homeassistant/custom_components/perdis/const.py https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/const.py
```

HA neu starten.

---

## Bekannte Einschränkungen

- Nur für Perdis WebComm (ASP.NET) getestet
- Im Urlaub werden keine Dienste in der Versteigerung angezeigt
- Options Flow funktioniert nur bei Neuinstallationen korrekt

---

## Lizenz

MIT License – Nutzung auf eigene Gefahr. Nicht offiziell von IVU Traffic Technologies unterstützt.

---

*Entwickelt mit ❤️ und Claude (Anthropic)*
