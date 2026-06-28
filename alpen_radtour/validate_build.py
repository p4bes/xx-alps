#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GEOJSON = ROOT / "alpen_etappen_varianten.geojson"
HTML = ROOT / "alpen_etappen_karte.html"
GPX_ZIP = ROOT / "alpen_etappen_gpx.zip"
EXPECTED_ROUTE_COUNT = 16

FORBIDDEN_HTML_TEXT = [
    "Zeitraum",
    "Eine Route wählen",
    "Komoot",
    "Strava Route",
    "Plan kopieren",
    "Steckbrief",
    "Planwert",
    "Routing:",
    "Valloire - Briançon",
]

EXPECTED_J5 = {
    "j5-light": ("LIGHT", "via Télégraphe + Galibier"),
    "j5-v2": ("MEDIUM", "via Télégraphe + Galibier + Granon"),
    "j5-v3": ("STRONG", "via Télégraphe + Galibier + Izoard"),
}

EXPECTED_J1 = {
    "j1-v2": ("MEDIUM", "via Colombière + Aravis", False),
    "j1-v2-closure": ("MEDIUM", "via Mont-Saxonnex + Aravis", True),
    "j1-v3": ("STRONG", "via Romme + Colombière + Aravis", False),
    "j1-v3-closure": ("STRONG", "via Mont-Saxonnex + Glières + Aravis", True),
}

EXPECTED_J2 = {
    "j2-v2": ("MEDIUM", "via Saisies + Col du Joly"),
    "j2-v3": ("STRONG", "via Ugine + Saisies/Joly"),
}


def fail(errors: list[str]) -> None:
    if errors:
        print("Build validation failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)


def main() -> None:
    errors: list[str] = []

    for path in [GEOJSON, HTML, GPX_ZIP]:
        if not path.exists():
            errors.append(f"missing file: {path.relative_to(ROOT)}")
    fail(errors)

    geojson = json.loads(GEOJSON.read_text(encoding="utf-8"))
    features = geojson.get("features", [])
    if len(features) != EXPECTED_ROUTE_COUNT:
        errors.append(f"expected {EXPECTED_ROUTE_COUNT} routes, got {len(features)}")

    ids = set()
    for feature in features:
        props = feature.get("properties", {})
        route_id = props.get("id")
        ids.add(route_id)

        if not route_id:
            errors.append("route without id")
            continue
        if props.get("brouter_km") is None:
            errors.append(f"{route_id}: missing brouter_km")
        if props.get("brouter_hm") is None:
            errors.append(f"{route_id}: missing brouter_hm")
        if props.get("brouter_km", 0) <= 0:
            errors.append(f"{route_id}: non-positive brouter_km")
        if props.get("brouter_hm", 0) <= 0:
            errors.append(f"{route_id}: non-positive brouter_hm")
        if "provider" in props:
            errors.append(f"{route_id}: obsolete provider property present")
        if "komoot_import_url" in props:
            errors.append(f"{route_id}: obsolete komoot_import_url property present")
        if "strava_import_url" in props:
            errors.append(f"{route_id}: obsolete strava_import_url property present")

        gpx_file = props.get("gpx_file")
        if not gpx_file or not (ROOT / gpx_file).exists():
            errors.append(f"{route_id}: missing GPX file {gpx_file!r}")

    for route_id, (difficulty, title) in EXPECTED_J5.items():
        feature = next((item for item in features if item.get("properties", {}).get("id") == route_id), None)
        if not feature:
            errors.append(f"missing J5 route: {route_id}")
            continue
        props = feature["properties"]
        if props.get("difficulty") != difficulty:
            errors.append(f"{route_id}: expected difficulty {difficulty}, got {props.get('difficulty')}")
        if props.get("title") != title:
            errors.append(f"{route_id}: expected title {title!r}, got {props.get('title')!r}")
        if props.get("day_label") != "Etappe 5 - St-Michel nach Briançon":
            errors.append(f"{route_id}: unexpected day label {props.get('day_label')!r}")
        if props.get("start") != "St-Michel" or props.get("finish") != "Briançon":
            errors.append(f"{route_id}: wrong start/finish")

    for route_id, (difficulty, title, closure_alternative) in EXPECTED_J1.items():
        feature = next((item for item in features if item.get("properties", {}).get("id") == route_id), None)
        if not feature:
            errors.append(f"missing J1 route: {route_id}")
            continue
        props = feature["properties"]
        if props.get("difficulty") != difficulty:
            errors.append(f"{route_id}: expected difficulty {difficulty}, got {props.get('difficulty')}")
        if props.get("title") != title:
            errors.append(f"{route_id}: expected title {title!r}, got {props.get('title')!r}")
        if bool(props.get("closure_alternative")) != closure_alternative:
            errors.append(f"{route_id}: wrong closure_alternative flag")
        waypoints = props.get("waypoints", [])
        if not waypoints or waypoints[0] != "Hotel Le Chamois d'Or" or waypoints[-1] != "Hôtel Le Mont-Blanc":
            errors.append(f"{route_id}: J1 hotel endpoints missing")

    if any(item.get("properties", {}).get("id") == "j2-alt" for item in features):
        errors.append("j2-alt should be removed")

    for route_id, (difficulty, title) in EXPECTED_J2.items():
        feature = next((item for item in features if item.get("properties", {}).get("id") == route_id), None)
        if not feature:
            errors.append(f"missing J2 route: {route_id}")
            continue
        props = feature["properties"]
        if props.get("difficulty") != difficulty:
            errors.append(f"{route_id}: expected difficulty {difficulty}, got {props.get('difficulty')}")
        if props.get("title") != title:
            errors.append(f"{route_id}: expected title {title!r}, got {props.get('title')!r}")
        waypoints = props.get("waypoints", [])
        if not waypoints or waypoints[0] != "Hôtel Le Mont-Blanc" or waypoints[-1] != "Hotel La Roche":
            errors.append(f"{route_id}: J2 hotel endpoints missing")

    j5_strong = next((item for item in features if item.get("properties", {}).get("id") == "j5-v3"), None)
    if j5_strong:
        pass_names = {item.get("name") for item in j5_strong["properties"].get("passes", [])}
        if "Col d'Izoard" not in pass_names:
            errors.append("j5-v3: Col d'Izoard pass card missing")

    with zipfile.ZipFile(GPX_ZIP) as archive:
        gpx_names = {Path(name).name for name in archive.namelist() if name.endswith(".gpx")}
    expected_gpx = {f"{route_id}.gpx" for route_id in ids if route_id}
    if gpx_names != expected_gpx:
        errors.append("GPX zip contents do not match route ids")

    html = HTML.read_text(encoding="utf-8")
    for text in FORBIDDEN_HTML_TEXT:
        if text in html:
            errors.append(f"forbidden HTML text still present: {text}")
    for required in [
        "mini-profile",
        "Alle GPX",
        "Details",
        "Etappe 5 - St-Michel nach Briançon",
        "Tagesdashboard",
        "Verpflegung & Wasser",
        "Packliste",
        "Anreise",
        "Abreise",
        "Open-Meteo",
        "Forecast ab ca. 16 Tage vorher verfügbar",
    ]:
        if required not in html:
            errors.append(f"required HTML text missing: {required}")

    fail(errors)
    print(f"Build validation passed: {len(features)} routes, {len(gpx_names)} GPX files.")


if __name__ == "__main__":
    main()
