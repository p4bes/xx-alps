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
EXPECTED_ROUTE_COUNT = 17

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

EXPECTED_J3 = {
    "j3-v2": ("LIGHT", "via Pré + Roselend + Tra"),
    "j3-v3": ("MEDIUM", "via Pré + Roselend"),
    "j3-loze": ("STRONG", "via Pré + Roselend + Tra + Loze"),
}

EXPECTED_J4 = {
    "j4-v2": ("LIGHT", "via Madeleine", 84, 86),
    "j4-alt": ("MEDIUM", "via Madeleine + Chaussy", 100, 103),
    "j4-v3": ("STRONG", "via Madeleine + Lacets + Chaussy", 112, 116),
    "j4-super": ("SUPER STRONG", "via Madeleine + Lacets + Chaussy + Sapey", 131, 134),
}

EXPECTED_J3_UPDATE = "2026-06-29 16:55 CEST"
EXPECTED_J4_UPDATE = "2026-06-29 21:26 CEST"
EXPECTED_J4_SUPER_UPDATE = "2026-06-29 21:41 CEST"


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

    for route_id, (difficulty, title) in EXPECTED_J3.items():
        feature = next((item for item in features if item.get("properties", {}).get("id") == route_id), None)
        if not feature:
            errors.append(f"missing J3 route: {route_id}")
            continue
        props = feature["properties"]
        if props.get("difficulty") != difficulty:
            errors.append(f"{route_id}: expected difficulty {difficulty}, got {props.get('difficulty')}")
        if props.get("title") != title:
            errors.append(f"{route_id}: expected title {title!r}, got {props.get('title')!r}")
        waypoints = props.get("waypoints", [])
        if not waypoints or waypoints[0] != "Hotel La Roche" or waypoints[-1] != "B&B Home Brides-les-Bains":
            errors.append(f"{route_id}: J3 hotel endpoints missing")
        pass_names = {item.get("name") for item in props.get("passes", [])}
        if route_id == "j3-v2" and "Col du Tra" not in pass_names:
            errors.append("j3-v2: Col du Tra pass card missing")
        if route_id == "j3-loze" and "Col de la Loze" not in pass_names:
            errors.append("j3-loze: Col de la Loze pass card missing")
        if route_id == "j3-loze" and props.get("brouter_hm", 0) < 4000:
            errors.append(f"j3-loze: elevation gain unexpectedly low ({props.get('brouter_hm')} hm)")
        if props.get("updated_at") != EXPECTED_J3_UPDATE:
            errors.append(f"{route_id}: missing today's update timestamp")

    for route_id, (difficulty, title, min_km, max_km) in EXPECTED_J4.items():
        feature = next((item for item in features if item.get("properties", {}).get("id") == route_id), None)
        if not feature:
            errors.append(f"missing J4 route: {route_id}")
            continue
        props = feature["properties"]
        if props.get("difficulty") != difficulty:
            errors.append(f"{route_id}: expected difficulty {difficulty}, got {props.get('difficulty')}")
        if props.get("title") != title:
            errors.append(f"{route_id}: expected title {title!r}, got {props.get('title')!r}")
        waypoints = props.get("waypoints", [])
        if not waypoints or waypoints[0] != "B&B Home Brides-les-Bains" or waypoints[-1] != "Hôtel Le Marintan":
            errors.append(f"{route_id}: J4 hotel endpoints missing")
        if props.get("source_label") != "GPX":
            errors.append(f"{route_id}: expected GPX source label")
        distance = props.get("brouter_km", 0)
        if not (min_km <= distance <= max_km):
            errors.append(f"{route_id}: unexpected distance {distance} km")
        pass_names = {item.get("name") for item in props.get("passes", [])}
        if "Col de la Madeleine" not in pass_names:
            errors.append(f"{route_id}: Col de la Madeleine pass card missing")
        if route_id in {"j4-alt", "j4-v3", "j4-super"} and "Col du Chaussy" not in pass_names:
            errors.append(f"{route_id}: Col du Chaussy pass card missing")
        if route_id == "j4-super" and "Col du Sapey" not in pass_names:
            errors.append("j4-super: Col du Sapey pass card missing")
        expected_update = EXPECTED_J4_SUPER_UPDATE if route_id == "j4-super" else EXPECTED_J4_UPDATE
        if props.get("updated_at") != expected_update:
            errors.append(f"{route_id}: missing J4 update timestamp")

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
