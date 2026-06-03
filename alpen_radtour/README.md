# Alpen Radtour 2026

Statische Karte für die Rennrad-Etappenreise in den französischen Alpen.

## Lokal bauen

```bash
python3 alpen_radtour/build_alpen_map.py
python3 alpen_radtour/validate_build.py
python3 alpen_radtour/build_pages_artifact.py
python3 -m http.server 8787 --directory alpen_radtour
```

Dann im Browser öffnen:

```text
http://127.0.0.1:8787/alpen_etappen_karte.html
```

## GitHub Pages

Der Workflow `.github/workflows/deploy-alpen-pages.yml` baut die Karte bei jedem Push auf `main` neu und deployt sie als GitHub-Pages-Site.

Einmalig in GitHub aktivieren:

1. Repository öffnen.
2. `Settings -> Pages`.
3. Unter `Build and deployment` die Source `GitHub Actions` wählen.
4. Auf `main` pushen oder den Workflow manuell über `Actions -> Deploy Alpen Route Map -> Run workflow` starten.

Das Deployment-Artefakt enthält:

- `index.html`
- `alpen_etappen_karte.html`
- `alpen_etappen_varianten.geojson`
- `alpen_etappen_gpx.zip`
- `assets/`
- `gpx/`

## Änderungen

Routen, Texte und Highlights werden in `build_alpen_map.py` gepflegt. Die erzeugten Dateien sind bewusst nicht für Git gedacht und werden im CI frisch gebaut.

Wenn BRouter nicht erreichbar ist oder eine Route keine echten km/hm liefert, schlägt der Build fehl. Dadurch geht keine Fallback- oder Wegpunktlinie live.

Tagesdashboard, Hotel-/Gepäckhinweise, Verpflegungspunkte und Packliste werden ebenfalls in `build_alpen_map.py` gepflegt:

- `TRIP_DAYS`: Datum, Start-/Ziel-Hotel-Platzhalter, Gepäck, Support, Wetterpunkt
- `SUPPLY_POINTS`: Verpflegung/Wasserpunkte und Kartenmarker
- `PACKING_LIST`: allgemeine Packliste

Das Wetter-Widget nutzt clientseitig die Open-Meteo Forecast API. Für die Reiseetappen erscheinen echte Prognosen, sobald die jeweiligen Tage im Forecast-Fenster liegen; vorher zeigt die App einen entsprechenden Hinweis.
