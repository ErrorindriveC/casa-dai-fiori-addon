# Casa dai Fiori – Ferienhaus Kalender

Buchungskalender für das Ferienhaus
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



## Personen anpassen

In `ferienhaus_kalender/config.yaml` kannst du Personen und Farben ändern.
Danach Add-on neu starten.

## Daten

Die Buchungsdaten werden gespeichert unter:
`/share/ferienhaus_kalender_data.json`

Das ist der HA Share-Ordner – bleibt bei Updates erhalten.

---

## Farben

- 🟢 Fam.1 – Waldgrün `#4A7C59`
- 🟠 Fam.2 – Terrakotta `#C0622A`
- 🟣 Person       – Violett `#7B5EA7`
