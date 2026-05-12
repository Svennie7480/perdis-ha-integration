# Perdis Dienstplan – Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Automatisches Scrapen des Perdis WebComm Dienstplans und Anzeige als Home Assistant Kalender – inklusive automatischem Wecker vor Dienstbeginn.

## Features

- 📅 Dienstplan als HA Kalender (3 Monate voraus)
- ⏰ Automatischer Wecker X Minuten vor Dienstbeginn
- 🔔 Alexa-Ansage + Android-Wecker + Handy-Benachrichtigung
- 🏖️ Urlaub, Frei, Arbeitsbefreiung etc. werden angezeigt
- 🔄 Stündliche automatische Aktualisierung

## Installation via HACS

1. HACS öffnen → **Integrationen** → ⋮ → **Benutzerdefinierte Repositories**
2. URL eingeben: `https://github.com/Svennie7480/perdis-ha-integration`
3. Kategorie: **Integration** → Hinzufügen
4. Perdis Dienstplan suchen → Installieren
5. Home Assistant neu starten

## Konfiguration

1. Einstellungen → Integrationen → **+ Hinzufügen** → **Perdis Dienstplan**
2. Zugangsdaten eingeben:
   - **Basis-URL**: `https://perdis.svhl.de/WebComm` (oder deine eigene Instanz)
   - **Benutzername**: dein Perdis-Login
   - **Passwort**: dein Perdis-Passwort
3. Optional: Wecker konfigurieren:
   - **Alexa Entität**: z.B. `media_player.echo_wohnzimmer`
   - **Handy**: z.B. `notify.mobile_app_meinhandy`
   - **Minuten vor Dienstbeginn**: Standard 60

## Unterstützte Abwesenheitstypen

| Kürzel | Bedeutung |
|--------|-----------|
| U | Urlaub |
| F | Frei |
| AB | Arbeitsbefreiung |
| FM | Freizeitausgleich |
| FA | Überstunden |
| KOS | Krank ohne Schein |
| STR | Streik |

## Voraussetzungen

- Home Assistant 2023.1.0 oder neuer
- HACS installiert
- Perdis WebComm Zugangsdaten
- (Optional) Alexa Media Player Integration
- (Optional) Home Assistant Companion App
