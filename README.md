# Perdis Dienstplan – Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)](https://github.com/Svennie7480/perdis-ha-integration)

Automatisches Scrapen des Perdis WebComm Dienstplans und Anzeige als Home Assistant Kalender – inklusive automatischem Wecker vor Dienstbeginn.

---

## Features

- 📅 Dienstplan als HA Kalender (3 Monate voraus)
- ⏰ Automatischer Wecker X Minuten vor Dienstbeginn
- 🔔 Alexa-Ansage + Android-Wecker + Handy-Benachrichtigung
- 🌅 Wecker optional nur wenn Dienst vor einer bestimmten Uhrzeit beginnt
- 🏖️ Urlaub, Frei, Arbeitsbefreiung etc. werden angezeigt aber nicht geweckt
- 🔄 Stündliche automatische Aktualisierung
- ⚙️ Einstellungen jederzeit nachträglich änderbar
- 👥 Mehrere Mitarbeiter pro HA-Installation möglich

---

## Installation via HACS

1. HACS öffnen → **Integrationen** → ⋮ → **Benutzerdefinierte Repositories**
2. URL eingeben: `https://github.com/Svennie7480/perdis-ha-integration`
3. Kategorie: **Integration** → Hinzufügen
4. **Perdis Dienstplan** suchen → Installieren
5. Home Assistant neu starten

---

## Konfiguration

### Schritt 1 – Verbindung
Einstellungen → Integrationen → **+ Hinzufügen** → **Perdis Dienstplan**

| Feld | Beschreibung | Beispiel |
|------|-------------|---------|
| Basis-URL | URL zu deiner Perdis WebComm Instanz | `https://perdis.svhl.de/WebComm` |
| Benutzername | Dein Perdis-Login | `183` |
| Passwort | Dein Perdis-Passwort | `*****` |

### Schritt 2 – Wecker & Benachrichtigungen (optional)

| Feld | Beschreibung | Beispiel |
|------|-------------|---------|
| Alexa Gerät | Entität des Alexa-Geräts | `media_player.echo_wohnzimmer` |
| Handy Benachrichtigung | Notify-Entität der Companion App | `notify.mobile_app_meinhandy` |
| Minuten vor Dienstbeginn | Wieviel Minuten vorher wecken | `60` (Schieberegler 15–240) |
| Nur wecken vor Uhrzeit | Optional: nur wecken wenn Dienst vor dieser Zeit beginnt | `14:00` |

> **Hinweis:** Lässt du „Nur wecken vor Uhrzeit" leer, wirst du bei jedem Dienst geweckt – egal ob Früh- oder Spätschicht.

### Einstellungen nachträglich ändern
Einstellungen → Integrationen → Perdis → **Konfigurieren**

Dort können alle Wecker-Einstellungen jederzeit angepasst werden ohne die Integration neu einzurichten.

---

## Mehrere Mitarbeiter

Die Integration kann mehrfach eingerichtet werden – einfach nochmal „+ Hinzufügen" und andere Zugangsdaten eingeben. Jeder Mitarbeiter bekommt seinen eigenen Kalender.

---

## Unterstützte Abwesenheitstypen

| Kürzel | Bedeutung | Wecker |
|--------|-----------|--------|
| U | Urlaub | ❌ Kein Wecker |
| F | Frei | ❌ Kein Wecker |
| AB | Arbeitsbefreiung | ❌ Kein Wecker |
| FM | Freizeitausgleich | ❌ Kein Wecker |
| FA | Überstunden | ❌ Kein Wecker |
| KOS | Krank ohne Schein | ❌ Kein Wecker |
| STR | Streik | ❌ Kein Wecker |

---

## Wecker-Logik

```
Dienst beginnt um 07:11 Uhr
Wakeup-Minuten: 60
→ Automation feuert um 06:11 Uhr
→ Alexa-Ansage: "Dein Dienst beginnt in 60 Minuten um 07:11 Uhr"
→ Android-Wecker wird auf 06:11 Uhr gestellt
→ Handy-Benachrichtigung mit hoher Priorität
```

Mit „Nur wecken vor Uhrzeit" = `14:00`:
```
Dienst um 07:11 Uhr → ✅ Wecker wird gestellt
Dienst um 15:00 Uhr → ❌ Kein Wecker
```

---

## Voraussetzungen

- Home Assistant 2023.1.0 oder neuer
- HACS installiert
- Perdis WebComm Zugangsdaten
- (Optional) Alexa Media Player Integration für Ansagen
- (Optional) Home Assistant Companion App für Android-Wecker

---

## Geplante Features

- 🌍 Mehrsprachigkeit (DE/EN/NL/FR)
- 📊 Sensor für Urlaubstage (Gesamt/Verbraucht/Rest)
- 📈 Sensor für Überstunden
- 🔔 Benachrichtigung wenn neuer Dienstplan verfügbar
- 🌤️ Wetterwarnung vor Dienstbeginn

---

## Lizenz

MIT License – freie Nutzung, Änderung und Weitergabe erlaubt.
