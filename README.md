# Casa dai Fiori – Ferienhaus Kalender

Buchungskalender für das Ferienhaus in Calonico, Tessin.
Läuft als Home Assistant Add-on (HAOS).

---

## Installation (Schritt für Schritt)

### 1. GitHub Repository erstellen

1. Gehe zu https://github.com/new
2. Repository Name: `casa-dai-fiori-addon`
3. Auf **Public** stellen (wichtig für HA!)
4. **Create repository** klicken

### 2. Dateien hochladen

Lade alle Dateien aus diesem Ordner in dein GitHub Repo hoch.
Struktur muss so aussehen:

```
casa-dai-fiori-addon/
├── repository.json
└── ferienhaus_kalender/
    ├── config.yaml
    ├── Dockerfile
    └── rootfs/
        ├── usr/bin/kalender.py
        └── etc/services.d/kalender/run
```

### 3. In Home Assistant einbinden

1. HA öffnen → **Einstellungen** → **Add-ons**
2. Unten rechts **Add-on Store** öffnen
3. Oben rechts die **drei Punkte** → **Repositories**
4. URL eingeben: `https://github.com/DEIN_USERNAME/casa-dai-fiori-addon`
5. **Hinzufügen** klicken
6. Seite neu laden – das Add-on erscheint unten im Store
7. **Installieren** → **Starten**

### 4. Zugriff von aussen (Tailscale Funnel)

Im HA Terminal (SSH Add-on) oder auf dem PC:

```bash
tailscale funnel 5050
```

Tailscale gibt dir eine URL wie:
`https://deinname.ts.net`

Diese URL an Mutter und Mischa/ADI schicken – fertig!

---

## Personen anpassen

In `ferienhaus_kalender/config.yaml` kannst du Personen und Farben ändern.
Danach Add-on neu starten.

## Daten

Die Buchungsdaten werden gespeichert unter:
`/share/ferienhaus_kalender_data.json`

Das ist der HA Share-Ordner – bleibt bei Updates erhalten.

---

## Versionierung & Updates

Jede Änderung am Add-on braucht eine neue Versionsnummer in `config.yaml` (`version: "1.1.0"` → `"1.2.0"` usw.).

Sobald du eine neue Version auf GitHub hochlädst:
1. In HA → Add-on Store → oben rechts **Reload** klicken
2. Im Add-on selbst erscheint automatisch ein **Update verfügbar** Button
3. Klick drauf → HA baut das Add-on neu

Empfehlung: **Semantic Versioning** nutzen — `MAJOR.MINOR.PATCH`
- PATCH (1.0.**1**) – kleine Bugfixes
- MINOR (1.**1**.0) – neue Funktionen (z.B. PIN-Schutz, Header-Bild)
- MAJOR (**2**.0.0) – grössere Umbrüche

### Changelog

- **1.1.0** – PIN-Schutz (optional, ein PIN für alle), Hintergrundbild im Header (Calonico), Login-Seite
- **1.0.0** – Erste Version: Monats-/Jahresansicht, Buchungen pro Person

---

## PIN einrichten

In HA → Add-on → **Konfiguration**:

```yaml
pin: "1234"
```

Leer lassen (`pin: ""`) = kein Passwortschutz, jeder mit Link kommt direkt rein.
Mit PIN: alle Familienmitglieder geben einmal den gleichen PIN ein (bleibt im Browser gespeichert).

