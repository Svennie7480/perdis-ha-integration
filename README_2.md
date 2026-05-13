# Perdis WebComm – Home Assistant Integration

Eine inoffizielle Home Assistant Integration für das Perdis WebComm Personalplanungssystem. Die Integration liest Dienstplandaten, Urlaubssalden, Überstunden, Nachrichten und Dienstversteigerungen direkt aus dem Perdis WebComm Portal und stellt sie als Sensoren in Home Assistant bereit.

> **Hinweis:** Diese Integration ist nicht offiziell von Perdis/IVU Traffic Technologies unterstützt. Sie funktioniert durch Web-Scraping des WebComm-Portals.

---

## Features

### 📆 Dienstplan
- 🚌 **Kalender** – 3 Monate Dienstplan als Home Assistant Kalender
- 📅 **Dienstdetail** – komplette Tagesübersicht mit Linien, Wendezeiten und Pausen (klickbares Pop-up)
- 🏖️ Urlaub, Frei, Arbeitsbefreiung etc. werden im Kalender angezeigt aber **nicht geweckt**
- 🔄 **Stündliche automatische Aktualisierung**

### ⏰ Wecker & Benachrichtigungen
- ⏰ **Automatischer Wecker** X Minuten vor Dienstbeginn (konfigurierbar)
- 🔔 **Alexa-Ansage** + **Android-Wecker** + **Handy-Benachrichtigung**
- 🌅 Wecker optional **nur wenn Dienst vor einer bestimmten Uhrzeit** beginnt
- 🖥️ **Leitstellen-Alarm** – sofortige Benachrichtigung wenn Dienste 800–899 oder „Auslaufdienst Leitstelle" in der Versteigerung erscheinen

### 🏖️ Urlaub & Salden
- **Urlaubssalden** – Rest, Anspruch, Plan, Zusatzurlaub
- **Überstunden & Salden** – Überstunden, Langzeitkonto, TVK Privat, Soll/Ist
- Farbwarnung bei zu vielen Überstunden (grün/orange/rot)
- Farbwarnung bei wenig Resturlaub

### 📬 Nachrichten
- **Letzte Nachricht** – Betreff und Text der neuesten WebComm-Nachricht
- Gesamtanzahl Nachrichten

### 🔨 Dienstversteigerung
- **Alle verfügbaren Dienste** auf einen Blick
- **Leitstellen-Dienste** (800–899 + „Auslaufdienst Leitstelle") werden rot hervorgehoben
- Sofortige Benachrichtigung auf Alexa + Handy bei Leitstellen-Diensten

### ⚙️ Konfiguration
- ⚙️ **Einstellungen jederzeit nachträglich änderbar** (Weckzeit, Offset, Benachrichtigungsgeräte)
- 👥 **Mehrere Mitarbeiter** pro HA-Installation möglich
- 🏢 **Optionale Ortskonfiguration** – eigene Kürzel für Betriebshof, ZOB etc. definierbar

---

## Voraussetzungen

- Home Assistant 2024.1 oder neuer
- Zugang zu einem Perdis WebComm Portal (z.B. `https://perdis.beispiel.de/WebComm`)
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
cd perdis
wget https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/__init__.py
wget https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/coordinator.py
wget https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/sensor.py
wget https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/calendar.py
wget https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/config_flow.py
wget https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/const.py
wget https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/manifest.json
wget https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/strings.json
```

Home Assistant neu starten.

---

## Einrichtung

1. **Einstellungen** → **Integrationen** → **+ Hinzufügen**
2. Nach **Perdis WebComm** suchen
3. Folgende Daten eingeben:

| Feld | Beschreibung | Beispiel |
|------|-------------|---------|
| WebComm URL | URL des Perdis Portals | `https://perdis.beispiel.de/WebComm` |
| Benutzername | Deine Mitarbeiternummer | `183` |
| Passwort | Dein WebComm Passwort | |

> **Hinweis bei Sonderzeichen im Passwort:** Im Terminal einfache Anführungszeichen verwenden: `export PASS='mein!passwort'`

---

## Verfügbare Entitäten

### Kalender
| Entität | Beschreibung |
|---------|-------------|
| `calendar.dienstplan` | Alle Dienste als Kalendereinträge (3 Monate) |

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
| `sensor.samstagszuschlag` | Samstagszuschlag dieser Periode |
| `sensor.sonntagszuschlag` | Sonntagszuschlag dieser Periode |
| `sensor.feiertag_100` | Feiertagszuschlag 100% |
| `sensor.urlaubsaufschlag` | Urlaubsaufschlag |

### Sensoren – Nachrichten
| Entität | Beschreibung | Attribute |
|---------|-------------|-----------|
| `sensor.letzte_nachricht_betreff` | Betreff der neuesten Nachricht | `header`, `text`, `total` |
| `sensor.nachrichten_anzahl` | Gesamtanzahl Nachrichten | |

### Sensoren – Dienstdetail
| Entität | Beschreibung | Attribute |
|---------|-------------|-----------|
| `sensor.dienstdetail_heute` | Dienstdetails für heute | `rows`, `start_ort`, `end_ort`, `linien`, `wende_total_min`, `pause_bezahlt_min`, `pause_unbezahlt_min` |

### Sensoren – Dienstversteigerung
| Entität | Beschreibung | Attribute |
|---------|-------------|-----------|
| `sensor.dienstversteigerung` | Verfügbare Dienste in der Versteigerung | `items`, `has_leitstelle`, `leitstelle_items`, `total` |

---

## Ganztages-Einträge im Kalender

Folgende Einträge werden als Ganztags-Ereignisse dargestellt:

| Kürzel | Bedeutung |
|--------|-----------|
| `U` | Urlaub |
| `AB` | Arbeitsbefreiung |
| `F` | Frei |
| `FM` | Freizeitausgleich |
| `FA` | Überstundenabbau |
| `KOS` | Krank ohne Schein |
| `STR` | Streik |

---

## Dashboard

Im Repository liegt eine fertige Dashboard-Konfiguration (`dashboard/perdis_dashboard.yaml`) mit:

- **3-Spalten-Layout** (Sections View)
- **Nächster Dienst** mit dynamischem Icon je nach Diensttyp
- **Dienstdetail** als Pop-up mit farbiger Tabelle (Wenden 🟢, Bezahlte Pause 🟡, Unbezahlte Pause 🔵)
- **Urlaubsübersicht** mit Farbwarnung bei wenig Resturlaub
- **Überstunden** mit dynamischer Farbcodierung (grün/orange/rot)
- **Dienstversteigerung** mit Leitstellen-Alarm (rote Kachel)
- **Kalender** der nächsten 7 Tage (benötigt Atomic Calendar Revive)
- **Letzte Nachricht** mit lila Rahmen

### Benötigte HACS Frontend-Pakete

- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom)
- [Atomic Calendar Revive](https://github.com/totaldebug/atomic-calendar-revive)
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod)
- [Browser Mod](https://github.com/thomasloven/lovelace-browser-mod)

---

## Alarm-Automation: Leitstellen-Dienst

Wenn ein Dienst zwischen 800–899 oder ein „Auslaufdienst Leitstelle" in der Versteigerung erscheint, kann eine Benachrichtigung ausgelöst werden.

Einstellungen → Automationen → + Hinzufügen → Als YAML bearbeiten:

```yaml
alias: "Perdis Leitstellen-Alarm"
triggers:
  - trigger: state
    entity_id: sensor.dienstversteigerung
conditions:
  - condition: template
    value_template: >
      {{ state_attr('sensor.dienstversteigerung', 'has_leitstelle') == true }}
actions:
  - action: notify.mobile_app_dein_handy
    data:
      title: "🖥️ Leitstellen-Dienst verfügbar!"
      message: >
        {% set items = state_attr('sensor.dienstversteigerung', 'leitstelle_items') %}
        {% for i in items %}{{ i.dienst }} am {{ i.betriebstag }} ({{ i.dienstzeit }}) {% endfor %}
      data:
        priority: high
```

---

## Theme

Im Repository liegt ein passendes dunkles Theme (`themes/perdis/perdis.yaml`):
- Fast-schwarzer Hintergrund
- Orange Akzente (passend zum Stadtbus-Design)
- Türkis für Highlights

Installation:
```bash
mkdir -p /homeassistant/themes/perdis
# Datei aus Repository kopieren nach /homeassistant/themes/perdis/perdis.yaml
```

In `configuration.yaml`:
```yaml
frontend:
  themes: !include_dir_merge_named themes
```

---

## Bekannte Einschränkungen

- Die Integration funktioniert nur mit dem Perdis WebComm Portal (ASP.NET)
- Passwörter mit Sonderzeichen müssen in einfachen Anführungszeichen gesetzt werden
- Der Options Flow (Einstellungen nachträglich ändern) funktioniert bei bestehenden Installationen nicht – Integration neu einrichten bei Änderungen
- Im Urlaub werden keine Dienste in der Versteigerung angezeigt (Perdis-seitige Einschränkung)

---

## Updateanleitung

```bash
cd /homeassistant/custom_components/perdis
wget -O coordinator.py https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/coordinator.py
wget -O sensor.py https://raw.githubusercontent.com/Svennie7480/perdis-ha-integration/main/custom_components/perdis/sensor.py
# HA neu starten
```

---

## Lizenz

MIT License – Nutzung auf eigene Gefahr. Diese Integration ist nicht offiziell von IVU Traffic Technologies / Perdis unterstützt.

---

*Entwickelt mit ❤️ und vielen Tassen Kaffee – und mit Hilfe von Claude (Anthropic)*
