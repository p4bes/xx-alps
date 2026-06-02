#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import zipfile
import time
import urllib.parse
import urllib.request
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
GPX_DIR = OUT_DIR / "gpx"
GPX_ZIP_OUT = OUT_DIR / "alpen_etappen_gpx.zip"
GEOJSON_OUT = OUT_DIR / "alpen_etappen_varianten.geojson"
HTML_OUT = OUT_DIR / "alpen_etappen_karte.html"


POINTS = {
    "Cordon": (45.9221674, 6.6105436),
    "Sallanches": (45.9814, 6.6369),
    "Combloux": (45.8960, 6.6440),
    "Cluses": (46.0603171, 6.5804218),
    "Nancy-sur-Cluses": (46.0433318, 6.5777368),
    "Col de Romme": (46.0300458, 6.5745849),
    "Le Reposoir": (46.0114414, 6.5348232),
    "Col de la Colombière": (45.9922392, 6.4756850),
    "Le Grand-Bornand": (45.9418675, 6.4271457),
    "Saint-Jean-de-Sixt": (45.9227059, 6.4106366),
    "La Clusaz": (45.9043659, 6.4239011),
    "Col des Aravis": (45.8722790, 6.4648689),
    "La Giettaz": (45.8772410, 6.5198231),
    "Flumet": (45.8175946, 6.5143172),
    "Praz-sur-Arly": (45.8379186, 6.5704514),
    "Megève": (45.8567089, 6.6179320),
    "Notre-Dame-de-Bellecombe": (45.8084045, 6.5171548),
    "Crest-Voland": (45.7930981, 6.5022718),
    "Col des Saisies": (45.7615643, 6.5333569),
    "Hauteluce": (45.7506448, 6.5853758),
    "Col du Joly": (45.7839174, 6.6740143),
    "Beaufort": (45.7174453, 6.5732569),
    "Villard-sur-Doron": (45.7261125, 6.5274970),
    "Ugine": (45.7490363, 6.4205158),
    "Arêches": (45.6629892, 6.5663191),
    "Col du Pré": (45.6903011, 6.5979747),
    "Lac de Roselend": (45.6819037, 6.6228569),
    "Cormet de Roselend": (45.6913293, 6.6906249),
    "Les Chapieux": (45.6966794, 6.7335808),
    "Bourg-Saint-Maurice": (45.6186105, 6.7695277),
    "Aime-la-Plagne": (45.5660919, 6.6121397),
    "Notre-Dame-du-Pré": (45.5114000, 6.5942800),
    "Col du Tra": (45.5154458, 6.5959758),
    "Moûtiers": (45.4849883, 6.5340061),
    "Brides-les-Bains": (45.4525213, 6.5667816),
    "Les Allues": (45.4307976, 6.5563846),
    "Méribel Centre": (45.3974188, 6.5660571),
    "Altiport Méribel": (45.3995796, 6.5836693),
    "Col de la Loze": (45.4050808, 6.6016031),
    "Aigueblanche": (45.5205568, 6.5120836),
    "La Léchère": (45.5262762, 6.4503940),
    "Celliers": (45.4679709, 6.3939532),
    "Col de la Madeleine": (45.4349516, 6.3755223),
    "Saint-François-Longchamp": (45.4172599, 6.3620514),
    "La Chambre": (45.3575951, 6.3009670),
    "Col du Chaussy": (45.3432158, 6.3571629),
    "Montvernier": (45.3208772, 6.3442934),
    "Lacets de Montvernier": (45.3177817, 6.3369100),
    "Pontamafrey": (45.3102142, 6.3298469),
    "Saint-Jean-de-Maurienne": (45.2775475, 6.3451720),
    "Col du Sapey": (45.2926037, 6.3816028),
    "Montdenis": (45.2814984, 6.4067547),
    "Saint-Michel-de-Maurienne": (45.2178751, 6.4750846),
    "Col du Télégraphe": (45.2026999, 6.4446143),
    "Valloire": (45.1650000, 6.4296372),
    "Plan Lachat": (45.0888292, 6.4361289),
    "Col du Galibier": (45.0641384, 6.4078570),
    "Col du Lautaret": (45.0352314, 6.4051088),
    "Le Monêtier-les-Bains": (44.9760855, 6.5098787),
    "Saint-Chaffrey": (44.9262808, 6.6070868),
    "Col du Granon": (44.9627837, 6.6109055),
    "Cervières": (44.8705556, 6.7225000),
    "Col d'Izoard": (44.8200267, 6.7350408),
    "Briançon": (44.8984037, 6.6436313),
}


DAY_COLORS = {
    "J1": "#1f78b4",
    "J2": "#2ca25f",
    "J3": "#d95f02",
    "J4": "#7b3294",
    "J5": "#e31a1c",
}


DAY_LABELS = {
    "J1": "Etappe 1",
    "J2": "Etappe 2",
    "J3": "Etappe 3",
    "J4": "Etappe 4",
    "J5": "Etappe 5",
}


DAY_ENDPOINTS = {
    "J1": ("Cordon", "Flumet"),
    "J2": ("Flumet", "Beaufort"),
    "J3": ("Beaufort", "Brides-les-Bains"),
    "J4": ("Brides-les-Bains", "St-Michel"),
    "J5": ("St-Michel", "Briançon"),
}


DIFFICULTY_ORDER = {"LIGHT": 1, "MEDIUM": 2, "STRONG": 3}


ROUTE_DETAILS = {
    "j1-alt": {
        "difficulty": "LIGHT",
        "title": "via Megève",
        "description": "Die ruhige Ankommenslinie durch das Arve-Tal und über Megève. Gute Wahl bei später Anreise, müden Beinen oder unsicherem Wetter.",
        "highlights": ["Combloux", "Megève", "Praz-sur-Arly", "Blick Richtung Mont Blanc"],
        "photo_spots": ["Combloux", "Megève", "Praz-sur-Arly"],
    },
    "j1-v2": {
        "difficulty": "MEDIUM",
        "title": "via Colombière + Aravis",
        "description": "Der saubere Auftakt mit zwei echten Klassikern. Erst über die Colombière ins Aravis-Massiv, danach über La Clusaz und den Col des Aravis nach Flumet.",
        "highlights": ["Col de la Colombière", "Le Grand-Bornand", "La Clusaz", "Col des Aravis"],
        "photo_spots": ["Col de la Colombière", "Le Grand-Bornand", "Col des Aravis"],
    },
    "j1-v3": {
        "difficulty": "STRONG",
        "title": "via Romme + Colombière + Aravis",
        "description": "Die sportliche Eröffnung: Col de Romme nimmt früh Körner, macht die Zufahrt zur Colombière aber deutlich ruhiger und charaktervoller.",
        "highlights": ["Col de Romme", "Le Reposoir", "Col de la Colombière", "Col des Aravis"],
        "photo_spots": ["Col de Romme", "Le Reposoir", "Col des Aravis"],
    },
    "j2-alt": {
        "difficulty": "LIGHT",
        "title": "via Saisies direkt",
        "description": "Kurze Regenerationsvariante über den Col des Saisies ohne Joly-Stichfahrt. Ideal, wenn J3 und J4 voll gefahren werden sollen.",
        "highlights": ["Notre-Dame-de-Bellecombe", "Crest-Voland", "Col des Saisies", "Hauteluce"],
        "photo_spots": ["Crest-Voland", "Col des Saisies", "Hauteluce"],
    },
    "j2-v2": {
        "difficulty": "MEDIUM",
        "title": "via Saisies + Col du Joly",
        "description": "Kompakte Panoramatour mit starker Mont-Blanc-Perspektive. Der Col du Joly ist eine Stichfahrt, lohnt sich aber landschaftlich klar.",
        "highlights": ["Col des Saisies", "Hauteluce", "Col du Joly", "Beaufortain"],
        "photo_spots": ["Col des Saisies", "Col du Joly", "Beaufort"],
    },
    "j2-v3": {
        "difficulty": "STRONG",
        "title": "via Ugine + Saisies/Joly",
        "description": "Die lange Beaufortain-Variante mit Zusatzschleife über Ugine und Crest-Voland. Deutlich mehr Strecke, dafür eine rundere Tagesroute.",
        "highlights": ["Ugine", "Crest-Voland", "Col des Saisies", "Col du Joly"],
        "photo_spots": ["Crest-Voland", "Col du Joly", "Beaufort"],
    },
    "j3-v2": {
        "difficulty": "LIGHT",
        "title": "via Roselend direkt",
        "description": "Die kontrollierteste Linie des Tages: Roselend bleibt als landschaftlicher Höhepunkt drin, Col du Pré und Col du Tra werden ausgelassen.",
        "highlights": ["Lac de Roselend", "Cormet de Roselend", "Les Chapieux", "Bourg-Saint-Maurice"],
        "photo_spots": ["Lac de Roselend", "Cormet de Roselend", "Les Chapieux"],
    },
    "j3-v3": {
        "difficulty": "MEDIUM",
        "title": "via Pré + Roselend",
        "description": "Die landschaftliche Königslinie durch das Beaufortain mit Col du Pré, Lac de Roselend und Cormet de Roselend.",
        "highlights": ["Col du Pré", "Lac de Roselend", "Cormet de Roselend", "Bourg-Saint-Maurice"],
        "photo_spots": ["Lac de Roselend", "Cormet de Roselend", "Bourg-Saint-Maurice"],
    },
    "j3-loze": {
        "difficulty": "STRONG",
        "title": "via Pré + Roselend + Loze",
        "description": "Die Eskalation: Pré, Roselend und danach die brutale Loze-Schleife ab Brides. Nur bei stabilem Wetter und sehr guter Tagesform sinnvoll.",
        "highlights": ["Col du Pré", "Cormet de Roselend", "Méribel", "Col de la Loze"],
        "photo_spots": ["Lac de Roselend", "Méribel", "Col de la Loze"],
    },
    "j4-v2": {
        "difficulty": "LIGHT",
        "title": "via Madeleine",
        "description": "Der belastbare Standard nach dem langen Vortag: ein großer Pass, danach direkter Transfer durch die Maurienne.",
        "highlights": ["La Léchère", "Celliers", "Col de la Madeleine", "Maurienne"],
        "photo_spots": ["Celliers", "Col de la Madeleine", "Saint-Jean-de-Maurienne"],
    },
    "j4-alt": {
        "difficulty": "MEDIUM",
        "title": "via Madeleine + Chaussy",
        "description": "Die Anbieterlinie als mittlere J4-Option: Madeleine plus Chaussy, mit den Lacets eher in der Abfahrtsrichtung.",
        "highlights": ["Col de la Madeleine", "Col du Chaussy", "Montvernier", "Lacets de Montvernier"],
        "photo_spots": ["Col de la Madeleine", "Col du Chaussy", "Lacets de Montvernier"],
    },
    "j4-v3": {
        "difficulty": "STRONG",
        "title": "via Madeleine + Lacets + Chaussy",
        "description": "Die schönere, aber harte Richtung: Lacets bergauf fahren, danach Chaussy und zurück ins Maurienne-Tal.",
        "highlights": ["Col de la Madeleine", "Lacets de Montvernier", "Col du Chaussy", "Saint-Michel-de-Maurienne"],
        "photo_spots": ["Lacets de Montvernier", "Col du Chaussy", "Maurienne"],
    },
    "j5-light": {
        "difficulty": "LIGHT",
        "title": "via Télégraphe + Galibier",
        "description": "Der klassische Abschluss ab Saint-Michel mit Télégraphe und Galibier. In der neuen Staffelung ist das die leichteste vollständige Radetappe bis Briançon.",
        "highlights": ["Col du Télégraphe", "Valloire", "Col du Galibier", "Col du Lautaret"],
        "photo_spots": ["Col du Télégraphe", "Plan Lachat", "Col du Galibier"],
    },
    "j5-v2": {
        "difficulty": "MEDIUM",
        "title": "via Télégraphe + Galibier + Granon",
        "description": "Galibier plus der steile Granon als Stichfahrt vor Briançon. Das ist die mittlere J5-Option für Gruppen, die am Finaltag noch einen harten Zusatzanstieg wollen.",
        "highlights": ["Col du Télégraphe", "Col du Galibier", "Col du Granon", "Briançon"],
        "photo_spots": ["Col du Galibier", "Col du Granon", "Briançon"],
    },
    "j5-v3": {
        "difficulty": "STRONG",
        "title": "via Télégraphe + Galibier + Izoard",
        "description": "Die neue Topvariante ohne Granon: erst Télégraphe und Galibier, dann ab Briançon/Cervières noch die ikonische Nordrampe zum Col d'Izoard als finales Monument.",
        "highlights": ["Col du Télégraphe", "Col du Galibier", "Cervières", "Col d'Izoard"],
        "photo_spots": ["Col du Galibier", "Cervières", "Col d'Izoard"],
    },
}


PASS_INFO = {
    "Col de Romme": {
        "status": "steiler Auftaktklassiker",
        "palmares": "Tour-de-France-Bergwertung; oft in Kombination mit der Colombière gefahren.",
        "segment_query": "Col de Romme climb",
    },
    "Col de la Colombière": {
        "status": "Tour-Klassiker",
        "palmares": "Großer Aravis-Pass mit langer Profi-Historie und vielen Strava-Climb-Varianten.",
        "segment_query": "Col de la Colombiere climb",
    },
    "Col des Aravis": {
        "status": "Aravis-Klassiker",
        "palmares": "Bekannter Übergang zwischen La Clusaz und Flumet; starker Social-/Foto-Pass.",
        "segment_query": "Col des Aravis climb",
    },
    "Col des Saisies": {
        "status": "Beaufortain-Pass",
        "palmares": "Regelmäßiger Rennrad- und Tour-de-France-Ort im Beaufortain.",
        "segment_query": "Col des Saisies climb",
    },
    "Col du Joly": {
        "status": "Panorama-Stichfahrt",
        "palmares": "Weniger Profi-Palmarès, aber sehr stark für Aussicht und Segment-Jagd.",
        "segment_query": "Col du Joly climb",
    },
    "Col du Pré": {
        "status": "Beaufortain-Juwel",
        "palmares": "Einer der schönsten Zufahrten zum Lac de Roselend; klare Kletter-Etappe.",
        "segment_query": "Col du Pre Beaufortain climb",
    },
    "Cormet de Roselend": {
        "status": "Tour-Klassiker",
        "palmares": "Großer Alpenpass über dem Lac de Roselend; sehr bekannter Rennrad- und Tour-Pass.",
        "segment_query": "Cormet de Roselend climb",
    },
    "Col du Tra": {
        "status": "ruhige Nebenlinie",
        "palmares": "Eher lokale Alternative zur Talroute; interessant für ruhige Gruppenlinien.",
        "segment_query": "Col du Tra climb",
    },
    "Col de la Loze": {
        "status": "moderner Mythos",
        "palmares": "Extrem steiler, moderner Tour-de-France-Schlussanstieg mit brutalen Rampen.",
        "segment_query": "Col de la Loze Meribel climb",
    },
    "Col de la Madeleine": {
        "status": "Monument",
        "palmares": "Einer der großen Alpenklassiker der Tour de France und Dauphiné.",
        "segment_query": "Col de la Madeleine climb",
    },
    "Lacets de Montvernier": {
        "status": "Social-Highlight",
        "palmares": "Ikonische Serpentinen, eher kurz, aber extrem fotogen und sehr segmenttauglich.",
        "segment_query": "Lacets de Montvernier climb",
    },
    "Col du Chaussy": {
        "status": "Maurienne-Klassiker",
        "palmares": "Ruhiger, harter Maurienne-Pass; oft mit den Lacets kombiniert.",
        "segment_query": "Col du Chaussy climb",
    },
    "Col du Télégraphe": {
        "status": "Galibier-Zubringer",
        "palmares": "Klassischer Auftakt zum Galibier; historischer Bestandteil vieler Tour-Etappen.",
        "segment_query": "Col du Telegraphe climb",
    },
    "Col du Galibier": {
        "status": "Monument",
        "palmares": "Einer der berühmtesten Alpenpässe überhaupt; Tour-de-France-Mythos.",
        "segment_query": "Col du Galibier climb",
    },
    "Col du Lautaret": {
        "status": "Hochalpen-Übergang",
        "palmares": "Wichtiger Übergang am Galibier-Fuß; oft Teil großer Alpenetappen.",
        "segment_query": "Col du Lautaret climb",
    },
    "Col du Granon": {
        "status": "brutaler Stich",
        "palmares": "Steiler Abschlussanstieg über Briançon; starkes Finale für die Topgruppe.",
        "segment_query": "Col du Granon climb",
    },
    "Col d'Izoard": {
        "status": "Tour-Monument",
        "palmares": "Ikonischer Tour-de-France-Pass im Queyras; von Briançon/Cervières als harte Nordrampe gefahren.",
        "segment_query": "Col d'Izoard Briancon climb",
    },
}


ROUTES = [
    {
        "id": "j1-v2",
        "day": "J1",
        "variant": "V2",
        "name": "J1 V2: Cordon - Flumet via Colombière + Aravis",
        "waypoints": [
            "Cordon",
            "Cluses",
            "Le Reposoir",
            "Col de la Colombière",
            "Le Grand-Bornand",
            "Saint-Jean-de-Sixt",
            "La Clusaz",
            "Col des Aravis",
            "Flumet",
        ],
        "default": True,
        "note": "Solide Eröffnungsetappe mit zwei Klassikern.",
    },
    {
        "id": "j1-v3",
        "day": "J1",
        "variant": "V3",
        "name": "J1 V3: Cordon - Flumet via Romme + Colombière + Aravis",
        "waypoints": [
            "Cordon",
            "Cluses",
            "Nancy-sur-Cluses",
            "Col de Romme",
            "Le Reposoir",
            "Col de la Colombière",
            "Le Grand-Bornand",
            "Saint-Jean-de-Sixt",
            "La Clusaz",
            "Col des Aravis",
            "Flumet",
        ],
        "default": False,
        "note": "Die sportlichere Eröffnung; Romme ist steiler und ruhiger.",
    },
    {
        "id": "j1-alt",
        "day": "J1",
        "variant": "Alt",
        "name": "J1 Alt: Wetter-/Anreiseoption via Megève",
        "waypoints": ["Cordon", "Sallanches", "Combloux", "Megève", "Praz-sur-Arly", "Flumet"],
        "default": False,
        "note": "Rettungsoption bei Gewitter, verspäteter Anreise oder müden Gruppen.",
    },
    {
        "id": "j2-v2",
        "day": "J2",
        "variant": "V2",
        "name": "J2 V2: Flumet - Beaufort via Saisies + Joly",
        "waypoints": [
            "Flumet",
            "Notre-Dame-de-Bellecombe",
            "Crest-Voland",
            "Col des Saisies",
            "Hauteluce",
            "Col du Joly",
            "Hauteluce",
            "Beaufort",
        ],
        "default": True,
        "note": "Joly als Stichfahrt; sehr gute Mont-Blanc-Aussicht.",
    },
    {
        "id": "j2-v3",
        "day": "J2",
        "variant": "V3",
        "name": "J2 V3: Flumet - Beaufort, große Saisies/Joly-Schleife",
        "waypoints": [
            "Flumet",
            "Ugine",
            "Crest-Voland",
            "Notre-Dame-de-Bellecombe",
            "Col des Saisies",
            "Hauteluce",
            "Col du Joly",
            "Hauteluce",
            "Beaufort",
        ],
        "default": False,
        "note": "Längerer Anlauf über Ugine/Crest-Voland; schöner, aber deutlich zäher.",
    },
    {
        "id": "j2-alt",
        "day": "J2",
        "variant": "Alt",
        "name": "J2 Alt: Saisies direkt, Joly auslassen",
        "waypoints": [
            "Flumet",
            "Notre-Dame-de-Bellecombe",
            "Crest-Voland",
            "Col des Saisies",
            "Hauteluce",
            "Beaufort",
        ],
        "default": False,
        "note": "Gute Regenerationsvariante, wenn J3/J4 hart gefahren werden sollen.",
    },
    {
        "id": "j3-v2",
        "day": "J3",
        "variant": "V2",
        "name": "J3 Light: Beaufort - Brides via Roselend direkt",
        "waypoints": [
            "Beaufort",
            "Lac de Roselend",
            "Cormet de Roselend",
            "Les Chapieux",
            "Bourg-Saint-Maurice",
            "Aime-la-Plagne",
            "Moûtiers",
            "Brides-les-Bains",
        ],
        "default": True,
        "note": "Leichteste Roselend-Linie ohne Col du Pré und ohne Col du Tra.",
    },
    {
        "id": "j3-v3",
        "day": "J3",
        "variant": "V3",
        "name": "J3 Medium: Beaufort - Brides via Pré + Roselend",
        "waypoints": [
            "Beaufort",
            "Arêches",
            "Col du Pré",
            "Lac de Roselend",
            "Cormet de Roselend",
            "Les Chapieux",
            "Bourg-Saint-Maurice",
            "Aime-la-Plagne",
            "Moûtiers",
            "Brides-les-Bains",
        ],
        "default": False,
        "note": "Landschaftlich Königsetappe im Beaufortain; Tarentaise-Abschnitte früh fahren.",
    },
    {
        "id": "j3-loze",
        "day": "J3",
        "variant": "Option",
        "name": "J3 Strong: Beaufort - Brides plus Col de la Loze",
        "waypoints": [
            "Beaufort",
            "Arêches",
            "Col du Pré",
            "Lac de Roselend",
            "Cormet de Roselend",
            "Les Chapieux",
            "Bourg-Saint-Maurice",
            "Aime-la-Plagne",
            "Moûtiers",
            "Brides-les-Bains",
            "Les Allues",
            "Méribel Centre",
            "Altiport Méribel",
            "Col de la Loze",
            "Altiport Méribel",
            "Méribel Centre",
            "Les Allues",
            "Brides-les-Bains",
        ],
        "default": False,
        "note": "Brutale Rampe mit Passagen um 20%; nur bei sehr stabilem Wetter und guter Tagesform.",
    },
    {
        "id": "j4-v2",
        "day": "J4",
        "variant": "V2",
        "name": "J4 V2: Brides - St-Michel via Madeleine pur",
        "waypoints": [
            "Brides-les-Bains",
            "Moûtiers",
            "Aigueblanche",
            "La Léchère",
            "Celliers",
            "Col de la Madeleine",
            "Saint-François-Longchamp",
            "La Chambre",
            "Saint-Jean-de-Maurienne",
            "Saint-Michel-de-Maurienne",
        ],
        "default": True,
        "note": "Belastbarer Standard nach einem langen J3: Madeleine als großer Pass, danach direkter Transfer durch die Maurienne.",
    },
    {
        "id": "j4-v3",
        "day": "J4",
        "variant": "V3",
        "name": "J4 V3: Brides - St-Michel via Madeleine + Lacets bergauf + Chaussy",
        "waypoints": [
            "Brides-les-Bains",
            "Moûtiers",
            "Aigueblanche",
            "La Léchère",
            "Celliers",
            "Col de la Madeleine",
            "Saint-François-Longchamp",
            "La Chambre",
            "Pontamafrey",
            "Lacets de Montvernier",
            "Montvernier",
            "Col du Chaussy",
            "Saint-Jean-de-Maurienne",
            "Saint-Michel-de-Maurienne",
        ],
        "default": False,
        "note": "Schönere Richtung: die Lacets werden bergauf gefahren, danach Chaussy und Rückweg ins Maurienne-Tal.",
    },
    {
        "id": "j4-alt",
        "day": "J4",
        "variant": "Alt",
        "name": "J4 Alt: Originale Anbieterlinie mit Chaussy + Lacets abwärts",
        "waypoints": [
            "Brides-les-Bains",
            "Moûtiers",
            "Aigueblanche",
            "La Léchère",
            "Celliers",
            "Col de la Madeleine",
            "Saint-François-Longchamp",
            "La Chambre",
            "Col du Chaussy",
            "Montvernier",
            "Lacets de Montvernier",
            "Pontamafrey",
            "Saint-Jean-de-Maurienne",
            "Saint-Michel-de-Maurienne",
        ],
        "default": False,
        "note": "Zum Vergleich behalten; landschaftlich gut, aber die Lacets liegen hier in der weniger ikonischen Abfahrtsrichtung.",
    },
    {
        "id": "j5-light",
        "day": "J5",
        "variant": "Light",
        "name": "J5 Light: St-Michel - Briançon via Télégraphe + Galibier",
        "waypoints": [
            "Saint-Michel-de-Maurienne",
            "Col du Télégraphe",
            "Valloire",
            "Plan Lachat",
            "Col du Galibier",
            "Col du Lautaret",
            "Le Monêtier-les-Bains",
            "Saint-Chaffrey",
            "Briançon",
        ],
        "default": True,
        "note": "Leichteste vollständige J5-Variante. Früh starten, weil Galibier-Wetter schnell kippt.",
    },
    {
        "id": "j5-v2",
        "day": "J5",
        "variant": "V2",
        "name": "J5 Medium: St-Michel - Briançon plus Col du Granon",
        "waypoints": [
            "Saint-Michel-de-Maurienne",
            "Col du Télégraphe",
            "Valloire",
            "Plan Lachat",
            "Col du Galibier",
            "Col du Lautaret",
            "Le Monêtier-les-Bains",
            "Saint-Chaffrey",
            "Col du Granon",
            "Saint-Chaffrey",
            "Briançon",
        ],
        "default": False,
        "note": "Granon ist steil, exponiert und als Stichfahrt perfekt für eine stärkere Finalgruppe.",
    },
    {
        "id": "j5-v3",
        "day": "J5",
        "variant": "V3",
        "name": "J5 Strong: St-Michel - Briançon plus Col d'Izoard",
        "waypoints": [
            "Saint-Michel-de-Maurienne",
            "Col du Télégraphe",
            "Valloire",
            "Plan Lachat",
            "Col du Galibier",
            "Col du Lautaret",
            "Le Monêtier-les-Bains",
            "Saint-Chaffrey",
            "Briançon",
            "Cervières",
            "Col d'Izoard",
            "Cervières",
            "Briançon",
        ],
        "default": False,
        "note": "Neue Topvariante: Izoard als ikonischer Zusatzanstieg nach Galibier und Lautaret.",
    },
]


MAJOR_STOPS = [
    "Cordon",
    "Flumet",
    "Beaufort",
    "Brides-les-Bains",
    "Saint-Michel-de-Maurienne",
    "Briançon",
]


COLS = [
    "Col de Romme",
    "Col de la Colombière",
    "Col des Aravis",
    "Col des Saisies",
    "Col du Joly",
    "Col du Pré",
    "Cormet de Roselend",
    "Col du Tra",
    "Col de la Loze",
    "Col de la Madeleine",
    "Col du Chaussy",
    "Lacets de Montvernier",
    "Col du Télégraphe",
    "Col du Galibier",
    "Col du Lautaret",
    "Col du Granon",
    "Col d'Izoard",
]


def brouter_route(route: dict) -> dict:
    lonlats = "|".join(
        f"{POINTS[name][1]:.7f},{POINTS[name][0]:.7f}" for name in route["waypoints"]
    )
    params = urllib.parse.urlencode(
        {
            "lonlats": lonlats,
            "profile": "fastbike",
            "alternativeidx": 0,
            "format": "geojson",
        }
    )
    url = f"https://brouter.de/brouter?{params}"
    request = urllib.request.Request(url, headers={"User-Agent": "CodexRoutePlanning/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.load(response)
    feature = data["features"][0]
    props = feature.get("properties", {})
    feature["properties"] = route_properties(
        route,
        brouter_km=round(float(props.get("track-length", 0)) / 1000, 1),
        brouter_hm=int(float(props.get("filtered ascend", 0))),
    )
    return feature


def brouter_route_with_retries(route: dict, attempts: int = 3) -> dict:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            feature = brouter_route(route)
            props = feature["properties"]
            if props["brouter_km"] is None or props["brouter_hm"] is None:
                raise RuntimeError("BRouter returned incomplete metrics")
            return feature
        except Exception as exc:
            last_error = exc
            if attempt < attempts:
                print(f"  retry {attempt}/{attempts - 1} for {route['id']}: {exc}", flush=True)
                time.sleep(1.2 * attempt)
    raise RuntimeError(f"Routing failed for {route['id']} after {attempts} attempts") from last_error


def route_properties(route: dict, brouter_km: float | None, brouter_hm: int | None) -> dict:
    details = ROUTE_DETAILS[route["id"]]
    difficulty = details["difficulty"]
    start, finish = DAY_ENDPOINTS[route["day"]]
    day_label = f"{DAY_LABELS[route['day']]} - {start} nach {finish}"
    passes = []
    seen_passes = set()
    for waypoint in route["waypoints"]:
        if waypoint in PASS_INFO and waypoint not in seen_passes:
            passes.append({"name": waypoint, **PASS_INFO[waypoint]})
            seen_passes.add(waypoint)
    return {
        "id": route["id"],
        "day": route["day"],
        "day_label": day_label,
        "base_day_label": DAY_LABELS[route["day"]],
        "start": start,
        "finish": finish,
        "day_number": int(route["day"][1:]),
        "difficulty": difficulty,
        "difficulty_order": DIFFICULTY_ORDER[difficulty],
        "variant": route["variant"],
        "title": details["title"],
        "name": f"{day_label} {difficulty}: {details['title']}",
        "note": route["note"],
        "description": details["description"],
        "highlights": details["highlights"],
        "photo_spots": details["photo_spots"],
        "passes": passes,
        "default": difficulty == "MEDIUM",
        "color": DAY_COLORS[route["day"]],
        "waypoints": route["waypoints"],
        "brouter_km": brouter_km,
        "brouter_hm": brouter_hm,
    }

def build_geojson() -> dict:
    features = []
    for index, route in enumerate(ROUTES, 1):
        print(f"[{index}/{len(ROUTES)}] Routing {route['id']} ...", flush=True)
        features.append(brouter_route_with_retries(route))
        time.sleep(0.4)
    missing = [
        feature["properties"]["id"]
        for feature in features
        if feature["properties"]["brouter_km"] is None or feature["properties"]["brouter_hm"] is None
    ]
    if missing:
        raise RuntimeError(f"Routing incomplete for: {', '.join(missing)}")
    return {"type": "FeatureCollection", "features": features}


def gpx_text(feature: dict) -> str:
    props = feature["properties"]
    name = html.escape(props["name"], quote=True)
    points = []
    for coord in feature["geometry"]["coordinates"]:
        lon, lat = coord[:2]
        point = f'      <trkpt lat="{lat:.7f}" lon="{lon:.7f}">'
        if len(coord) > 2 and coord[2] is not None:
            point += f"<ele>{float(coord[2]):.1f}</ele>"
        point += "</trkpt>"
        points.append(point)
    return "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<gpx version="1.1" creator="Codex Alpen Radtour" xmlns="http://www.topografix.com/GPX/1/1">',
            "  <trk>",
            f"    <name>{name}</name>",
            "    <trkseg>",
            *points,
            "    </trkseg>",
            "  </trk>",
            "</gpx>",
            "",
        ]
    )


def write_gpx_files(geojson: dict) -> None:
    GPX_DIR.mkdir(exist_ok=True)
    with zipfile.ZipFile(GPX_ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for feature in geojson["features"]:
            props = feature["properties"]
            filename = f"{props['id']}.gpx"
            rel_path = f"gpx/{filename}"
            path = GPX_DIR / filename
            path.write_text(gpx_text(feature), encoding="utf-8")
            props["gpx_file"] = rel_path
            archive.write(path, arcname=filename)


def marker_payload(names: list[str], kind: str) -> list[dict]:
    return [
        {"name": name, "kind": kind, "lat": POINTS[name][0], "lon": POINTS[name][1]}
        for name in names
    ]


def make_html(geojson: dict) -> str:
    route_json = json.dumps(geojson, ensure_ascii=False)
    markers_json = json.dumps(
        marker_payload(MAJOR_STOPS, "stop") + marker_payload(COLS, "col"), ensure_ascii=False
    )
    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Französische Alpen Rennrad-Etappen 27.06.-03.07.2026</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    @font-face {{
      font-family: "Bandeins Strange";
      src: url("assets/fonts/BandeinsStrange-Bold.otf") format("opentype");
      font-weight: 700;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: "Bandeins Strange Extended";
      src: url("assets/fonts/BandeinsStrange-BoldExtendedHalf.otf") format("opentype");
      font-weight: 700;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: "Sen";
      src: url("assets/fonts/Sen-Regular.ttf") format("truetype");
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: "Sen";
      src: url("assets/fonts/Sen-Bold.ttf") format("truetype");
      font-weight: 700;
      font-style: normal;
      font-display: swap;
    }}
    :root {{
      color-scheme: light;
      --black: #000000;
      --white: #ffffff;
      --grey-950: #151515;
      --grey-800: #333333;
      --grey-600: #666666;
      --grey-300: #d6d6d6;
      --grey-150: #eeeeee;
      --grey-075: #f7f7f7;
      --panel: var(--white);
      --ink: var(--black);
      --muted: var(--grey-600);
      --line: var(--black);
      --bg: var(--white);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Sen", Arial, sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    .app {{
      display: grid;
      grid-template-columns: minmax(340px, 430px) 1fr;
      min-height: 100vh;
    }}
    aside {{
      background: var(--white);
      border-right: 4px solid var(--black);
      padding: 0;
      overflow: auto;
      max-height: 100vh;
    }}
    .brand-panel {{
      background: var(--black);
      color: var(--white);
      padding: 22px 18px 20px;
      border-bottom: 4px solid var(--black);
      position: relative;
      overflow: hidden;
    }}
    .brand-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 20px;
    }}
    .brand-logo {{
      display: block;
      width: 92px;
      height: auto;
    }}
    .brand-tag {{
      border: 1px solid var(--white);
      color: var(--white);
      font-size: 11px;
      font-weight: 700;
      line-height: 1;
      padding: 7px 8px;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 0 0 4px;
      font-family: "Bandeins Strange", Arial, sans-serif;
      font-size: 35px;
      line-height: 0.96;
      letter-spacing: 0;
      font-weight: 700;
    }}
    .sub {{
      margin: 12px 0 0;
      color: var(--white);
      font-size: 13px;
      line-height: 1.45;
      max-width: 34em;
      position: relative;
      z-index: 1;
    }}
    .ride-art {{
      position: absolute;
      right: 14px;
      bottom: 10px;
      width: 118px;
      height: 58px;
      color: var(--white);
      opacity: 0.22;
      pointer-events: none;
    }}
    .ride-art svg,
    .bike-icon svg {{
      display: block;
      width: 100%;
      height: 100%;
      fill: none;
      stroke: currentColor;
      stroke-width: 2;
      stroke-linecap: square;
      stroke-linejoin: miter;
    }}
    .toolbar {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0;
      border-bottom: 2px solid var(--black);
      background: var(--white);
    }}
    button,
    .button-link {{
      min-height: 42px;
      border: 0;
      border-right: 1px solid var(--black);
      border-bottom: 1px solid var(--black);
      background: var(--white);
      color: var(--ink);
      font: inherit;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      text-align: center;
      padding: 0 12px;
      gap: 7px;
    }}
    .button-link svg {{
      width: 16px;
      height: 16px;
      fill: none;
      stroke: currentColor;
      stroke-width: 2;
      stroke-linecap: square;
      stroke-linejoin: miter;
      flex: 0 0 auto;
    }}
    button:hover,
    .button-link:hover {{
      background: var(--black);
      color: var(--white);
    }}
    .filters {{
      border-bottom: 2px solid var(--black);
      padding: 12px 16px 14px;
      background: var(--white);
    }}
    .filters-title {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .bike-icon {{
      width: 22px;
      height: 16px;
      flex: 0 0 auto;
    }}
    .filter-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      border: 1px solid var(--black);
    }}
    .filter-grid button {{
      border: 0;
      border-right: 1px solid var(--black);
      border-bottom: 0;
      min-height: 54px;
      padding: 0 8px;
      font-size: 11px;
      flex-direction: column;
      gap: 3px;
    }}
    .filter-grid button:last-child {{
      border-right: 0;
    }}
    .filter-grid button.active {{
      background: var(--black);
      color: var(--white);
    }}
    .preset-name {{
      display: block;
      font-weight: 700;
      line-height: 1;
    }}
    .preset-total {{
      display: block;
      font-size: 10px;
      font-weight: 400;
      line-height: 1.15;
    }}
    .current-total {{
      border: 1px solid var(--black);
      border-top: 0;
      padding: 7px 8px;
      display: flex;
      justify-content: space-between;
      gap: 8px;
      font-size: 11px;
      line-height: 1.2;
    }}
    .current-total strong {{
      white-space: nowrap;
    }}
    .day {{
      border-bottom: 2px solid var(--black);
      padding: 0;
    }}
    .day-title {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0;
      padding: 11px 16px;
      font-weight: 700;
      font-size: 14px;
      border-bottom: 1px solid var(--black);
      text-transform: uppercase;
    }}
    .swatch {{
      width: 12px;
      height: 12px;
      border: 1px solid var(--black);
      flex: 0 0 auto;
    }}
    label.route {{
      display: grid;
      grid-template-columns: 20px 1fr;
      gap: 8px;
      align-items: start;
      padding: 12px 16px;
      font-size: 13px;
      line-height: 1.3;
      border-bottom: 1px solid var(--grey-300);
    }}
    label.route.selected {{
      background: var(--grey-075);
    }}
    label.route:last-child {{ border-bottom: 0; }}
    label.route input {{ margin-top: 2px; }}
    input[type="radio"] {{
      accent-color: var(--black);
    }}
    .route strong {{
      display: block;
      font-size: 13px;
      line-height: 1.28;
    }}
    .difficulty {{
      display: inline-flex;
      align-items: center;
      border: 1px solid var(--black);
      font-size: 10px;
      line-height: 1;
      padding: 3px 5px 2px;
      margin: 0 6px 3px 0;
      min-width: 50px;
      justify-content: center;
      vertical-align: 1px;
    }}
    .difficulty-medium {{
      background: var(--black);
      color: var(--white);
    }}
    .meta {{
      display: block;
      color: var(--muted);
      margin-top: 2px;
    }}
    .mini-profile {{
      display: block;
      width: 100%;
      height: 38px;
      margin-top: 7px;
      border: 1px solid var(--grey-300);
      background: var(--white);
      overflow: hidden;
    }}
    .mini-profile svg {{
      display: block;
      width: 100%;
      height: 100%;
    }}
    .route-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 6px;
    }}
    .route-actions a,
    .route-actions button {{
      border: 1px solid var(--black);
      color: var(--ink);
      background: var(--white);
      font-size: 12px;
      line-height: 1;
      padding: 6px 7px;
      text-decoration: none;
      font-family: inherit;
      min-height: 0;
    }}
    .route-actions a:hover,
    .route-actions button:hover {{
      background: var(--black);
      color: var(--white);
    }}
    .detail-panel {{
      border-bottom: 2px solid var(--black);
      padding: 0;
      background: var(--white);
    }}
    .detail-panel[hidden] {{
      display: none;
    }}
    .detail-head {{
      border-bottom: 1px solid var(--black);
      padding: 14px 16px 12px;
    }}
    .detail-kicker {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .detail-head h2 {{
      font-family: "Bandeins Strange", Arial, sans-serif;
      font-size: 23px;
      line-height: 1;
      margin: 0;
      letter-spacing: 0;
    }}
    .detail-body {{
      padding: 12px 16px 16px;
    }}
    .detail-description {{
      margin: 0 0 12px;
      color: var(--grey-800);
      font-size: 13px;
      line-height: 1.45;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      border: 1px solid var(--black);
      margin: 0 0 12px;
    }}
    .metric {{
      padding: 8px;
      border-right: 1px solid var(--black);
    }}
    .metric:last-child {{
      border-right: 0;
    }}
    .metric span {{
      display: block;
      color: var(--grey-600);
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .metric strong {{
      display: block;
      margin-top: 2px;
      font-size: 15px;
      line-height: 1.1;
    }}
    .profile-wrap {{
      border: 1px solid var(--black);
      margin-bottom: 12px;
      padding: 8px;
    }}
    .profile-title {{
      display: flex;
      justify-content: space-between;
      gap: 8px;
      color: var(--grey-600);
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      margin-bottom: 4px;
    }}
    .profile-svg {{
      display: block;
      width: 100%;
      height: 118px;
    }}
    .detail-block-title {{
      margin: 12px 0 6px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .highlight-list {{
      list-style: none;
      padding: 0;
      margin: 0;
      border-top: 1px solid var(--grey-300);
    }}
    .highlight-list li {{
      border-bottom: 1px solid var(--grey-300);
      padding: 6px 0;
      font-size: 12px;
    }}
    .pass-list {{
      display: grid;
      gap: 8px;
      margin: 0;
    }}
    .pass-card {{
      border: 1px solid var(--black);
      padding: 8px;
      background: var(--white);
    }}
    .pass-card strong {{
      display: block;
      font-size: 13px;
      line-height: 1.15;
    }}
    .pass-card span {{
      display: inline-block;
      margin: 4px 0 6px;
      border: 1px solid var(--black);
      padding: 3px 5px 2px;
      font-size: 9px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .pass-card p {{
      margin: 0 0 7px;
      color: var(--grey-800);
      font-size: 12px;
      line-height: 1.35;
    }}
    .segment-link {{
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      border: 1px solid var(--black);
      color: var(--black);
      padding: 0 7px;
      font-size: 11px;
      font-weight: 700;
      text-decoration: none;
    }}
    .segment-link:hover {{
      background: var(--black);
      color: var(--white);
    }}
    .photo-strip {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 6px;
      margin-top: 6px;
    }}
    .photo-tile {{
      min-height: 72px;
      border: 1px solid var(--black);
      background: var(--grey-150);
      color: var(--black);
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding: 7px;
      overflow: hidden;
    }}
    .photo-tile span {{
      font-size: 9px;
      font-weight: 700;
      text-transform: uppercase;
      color: var(--grey-600);
    }}
    .photo-tile strong {{
      font-size: 11px;
      line-height: 1.1;
      margin-top: 2px;
    }}
    .detail-actions {{
      display: grid;
      grid-template-columns: 1fr;
      border-top: 1px solid var(--black);
      margin-top: 12px;
    }}
    .detail-actions a,
    .detail-actions button {{
      border-bottom: 0;
    }}
    .modal-backdrop {{
      position: fixed;
      inset: 0;
      z-index: 10000;
      background: rgba(0, 0, 0, 0.72);
      display: grid;
      place-items: center;
      padding: 22px;
    }}
    .modal-backdrop[hidden] {{
      display: none;
    }}
    .route-modal {{
      width: min(920px, 100%);
      max-height: min(860px, 92vh);
      background: var(--white);
      color: var(--black);
      border: 4px solid var(--black);
      overflow: auto;
      box-shadow: 0 0 0 2px var(--white);
    }}
    .modal-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      border-bottom: 2px solid var(--black);
      padding: 10px 12px;
      position: sticky;
      top: 0;
      background: var(--white);
      z-index: 1;
    }}
    .modal-title {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .modal-close {{
      width: 34px;
      min-height: 34px;
      border: 1px solid var(--black);
      border-bottom: 1px solid var(--black);
      border-right: 1px solid var(--black);
      padding: 0;
      font-size: 20px;
      line-height: 1;
    }}
    .modal-body {{
      padding: 0;
    }}
    .route-modal .detail-head {{
      padding: 18px 20px 14px;
    }}
    .route-modal .detail-body {{
      padding: 16px 20px 20px;
    }}
    .route-modal .profile-svg {{
      height: 152px;
    }}
    .note {{
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
      margin: 0;
      border-top: 0;
      padding: 14px 16px 18px;
    }}
    #map {{ min-height: 100vh; }}
    .leaflet-tile-pane {{
      filter: grayscale(1) contrast(0.92) brightness(1.05);
    }}
    .popup-title {{
      font-weight: 700;
      margin-bottom: 4px;
    }}
    .popup-meta {{
      color: var(--grey-800);
      line-height: 1.35;
    }}
    .leaflet-bar a {{
      border-radius: 0 !important;
      color: var(--black);
    }}
    .leaflet-popup-content-wrapper,
    .leaflet-popup-tip {{
      border-radius: 0;
    }}
    .map-marker {{
      display: block;
      width: 13px;
      height: 13px;
      border: 2px solid var(--black);
      background: var(--white);
      box-shadow: 0 0 0 2px var(--white);
    }}
    .map-marker.stop {{
      background: var(--black);
      border-color: var(--white);
      box-shadow: 0 0 0 2px var(--black);
    }}
    .map-marker.col {{
      background: var(--white);
      border-color: var(--black);
    }}
    .leaflet-div-icon {{
      background: transparent;
      border: 0;
    }}
    @media (max-width: 800px) {{
      .app {{ grid-template-columns: 1fr; }}
      aside {{
        max-height: none;
        border-right: 0;
        border-bottom: 4px solid var(--black);
      }}
      h1 {{ font-size: 28px; }}
      #map {{ min-height: 68vh; }}
    }}
  </style>
</head>
<body>
  <div class="app">
    <aside>
      <section class="brand-panel" aria-label="Exxeta Route Desk">
        <div class="brand-row">
          <img class="brand-logo" src="assets/exxeta_logo_negativ_RGB.png" alt="Exxeta">
          <span class="brand-tag">Route Desk</span>
        </div>
        <h1>Rennrad-Etappen Französische Alpen</h1>
        <div class="ride-art" aria-hidden="true">
          <svg viewBox="0 0 120 60">
            <circle cx="28" cy="42" r="13"></circle>
            <circle cx="91" cy="42" r="13"></circle>
            <path d="M28 42 L48 24 L62 42 L38 42 L51 42 L73 20 L91 42 L62 42"></path>
            <path d="M47 24 L43 15 M38 15 L49 15 M73 20 L80 13 M77 13 L88 13"></path>
          </svg>
        </div>
      </section>
      <div class="toolbar">
        <button id="fit">Auf Route zoomen</button>
        <a class="button-link" href="alpen_etappen_gpx.zip" download>
          <svg aria-hidden="true" viewBox="0 0 24 24">
            <path d="M12 3v10m0 0 4-4m-4 4-4-4M5 17v3h14v-3"></path>
          </svg>
          Alle GPX
        </a>
      </div>
      <section class="filters" aria-label="Routenfilter">
        <div class="filters-title">
          <span class="bike-icon" aria-hidden="true">
            <svg viewBox="0 0 32 20">
              <circle cx="7" cy="14" r="5"></circle>
              <circle cx="25" cy="14" r="5"></circle>
              <path d="M7 14 L13 6 L17 14 L11 14 L16 14 L22 5 L25 14 L17 14"></path>
              <path d="M13 6 L12 2 M10 2 L15 2"></path>
            </svg>
          </span>
          Variantenfilter
        </div>
        <div class="filter-grid">
          <button id="preset-light" type="button" data-preset="LIGHT" aria-pressed="false"><span class="preset-name">LIGHT</span><span class="preset-total"></span></button>
          <button id="preset-medium" type="button" data-preset="MEDIUM" aria-pressed="true"><span class="preset-name">MEDIUM</span><span class="preset-total"></span></button>
          <button id="preset-strong" type="button" data-preset="STRONG" aria-pressed="false"><span class="preset-name">STRONG</span><span class="preset-total"></span></button>
        </div>
        <div class="current-total"><span>Aktuelle Auswahl</span><strong id="current-total">-</strong></div>
      </section>
      <div id="layers"></div>
    </aside>
    <main id="map"></main>
  </div>
  <div class="modal-backdrop" id="route-modal" hidden>
    <article class="route-modal" role="dialog" aria-modal="true" aria-labelledby="route-modal-title">
      <header class="modal-head">
        <div class="modal-title" id="route-modal-title">Details</div>
        <button class="modal-close" id="route-modal-close" type="button" aria-label="Details schließen">×</button>
      </header>
      <section class="modal-body" id="route-modal-body"></section>
    </article>
  </div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const routeData = {route_json};
    const markerData = {markers_json};
    const dayColors = {json.dumps(DAY_COLORS)};

    const map = L.map("map", {{ preferCanvas: true }}).setView([45.55, 6.42], 9);
    L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);

    const layers = new Map();
    const allBounds = L.latLngBounds([]);
    const selectedByDay = new Map();

    function popupHtml(props) {{
      return `<div class="popup-title">${{props.day_label}} · ${{props.difficulty}}<br>${{props.title}}</div>
        <div class="popup-meta">${{props.brouter_km}} km / ${{props.brouter_hm}} hm<br>${{props.description}}</div>`;
    }}

    function styleFor(props) {{
      return {{
        color: props.color,
        weight: props.difficulty === "MEDIUM" ? 5 : 4,
        opacity: 1,
        dashArray: props.difficulty === "MEDIUM" ? null : props.difficulty === "STRONG" ? "8 6" : "3 7",
        lineCap: "round",
        lineJoin: "round"
      }};
    }}

    for (const feature of routeData.features) {{
      const props = feature.properties;
      const layer = L.geoJSON(feature, {{
        style: () => styleFor(props),
        onEachFeature: (_, routeLayer) => routeLayer.bindPopup(popupHtml(props))
      }});
      layer.eachLayer(line => allBounds.extend(line.getBounds()));
      layers.set(props.id, layer);
    }}

    const markerLayer = L.layerGroup().addTo(map);
    for (const marker of markerData) {{
      const icon = L.divIcon({{
        className: "",
        html: `<span class="map-marker ${{marker.kind}}"></span>`,
        iconSize: [13, 13],
        iconAnchor: [6, 6]
      }});
      L.marker([marker.lat, marker.lon], {{ icon }})
        .bindTooltip(marker.name, {{ direction: "top", offset: [0, -4] }})
        .addTo(markerLayer);
    }}

    function setRouteVisibility(id, visible) {{
      const layer = layers.get(id);
      if (!layer) return;
      if (visible && !map.hasLayer(layer)) layer.addTo(map);
      if (!visible && map.hasLayer(layer)) layer.removeFrom(map);
      const input = document.querySelector(`input[data-route-id="${{id}}"]`);
      if (input) input.checked = visible;
      const routeLabel = input?.closest("label.route");
      if (routeLabel) routeLabel.classList.toggle("selected", visible);
    }}

    function setActiveFilter(activeId) {{
      for (const button of document.querySelectorAll(".filter-grid button")) {{
        const isActive = button.id === activeId;
        button.classList.toggle("active", isActive);
        button.setAttribute("aria-pressed", String(isActive));
      }}
    }}

    function featuresForDay(day) {{
      return routeData.features
        .filter(feature => feature.properties.day === day)
        .sort((a, b) => a.properties.difficulty_order - b.properties.difficulty_order);
    }}

    function selectedFeatures() {{
      return Array.from(selectedByDay.values())
        .map(id => featureById(id))
        .filter(Boolean)
        .sort((a, b) => a.properties.day_number - b.properties.day_number);
    }}

    function formatTotal(km, hm) {{
      return `${{km.toFixed(1)}} km / ${{Math.round(hm).toLocaleString("de-DE")}} hm`;
    }}

    function totalForFeatures(features) {{
      return features.reduce((total, feature) => {{
        const props = feature.properties;
        total.km += Number(props.brouter_km || 0);
        total.hm += Number(props.brouter_hm || 0);
        return total;
      }}, {{ km: 0, hm: 0 }});
    }}

    function updatePresetTotals() {{
      for (const button of document.querySelectorAll(".filter-grid button[data-preset]")) {{
        const difficulty = button.dataset.preset;
        const features = routeData.features.filter(feature => feature.properties.difficulty === difficulty);
        const total = totalForFeatures(features);
        const target = button.querySelector(".preset-total");
        if (target) target.textContent = formatTotal(total.km, total.hm);
      }}
    }}

    function updateCurrentTotal() {{
      const total = totalForFeatures(selectedFeatures());
      const target = document.getElementById("current-total");
      if (target) target.textContent = formatTotal(total.km, total.hm);
    }}

    function updateActivePresetFromSelection() {{
      const selected = selectedFeatures().map(feature => feature.properties.difficulty);
      const unique = new Set(selected);
      const dayCount = new Set(routeData.features.map(feature => feature.properties.day)).size;
      if (selected.length === dayCount && unique.size === 1) {{
        setActiveFilter(`preset-${{selected[0].toLowerCase()}}`);
      }} else {{
        setActiveFilter("");
      }}
    }}

    function selectRoute(id, options = {{ updatePreset: true }}) {{
      const feature = featureById(id);
      if (!feature) return;
      const day = feature.properties.day;
      for (const routeFeature of featuresForDay(day)) {{
        setRouteVisibility(routeFeature.properties.id, routeFeature.properties.id === id);
      }}
      selectedByDay.set(day, id);
      if (options.updatePreset) updateActivePresetFromSelection();
      updateCurrentTotal();
    }}

    function selectPreset(difficulty) {{
      setActiveFilter(`preset-${{difficulty.toLowerCase()}}`);
      const days = [...new Set(routeData.features.map(feature => feature.properties.day))];
      for (const day of days) {{
        const feature = featuresForDay(day).find(candidate => candidate.properties.difficulty === difficulty);
        if (feature) selectRoute(feature.properties.id, {{ updatePreset: false }});
      }}
      updateCurrentTotal();
    }}

    function fitRoutes() {{
      const selectedBounds = L.latLngBounds([]);
      for (const feature of selectedFeatures()) {{
        const layer = layers.get(feature.properties.id);
        if (layer) layer.eachLayer(line => selectedBounds.extend(line.getBounds()));
      }}
      const bounds = selectedBounds.isValid() ? selectedBounds : allBounds;
      if (bounds.isValid()) map.fitBounds(bounds.pad(0.05));
    }}

    function routeById(id) {{
      return routeData.features.find(feature => feature.properties.id === id)?.properties;
    }}

    function featureById(id) {{
      return routeData.features.find(feature => feature.properties.id === id);
    }}

    function difficultyClass(difficulty) {{
      return `difficulty difficulty-${{difficulty.toLowerCase()}}`;
    }}

    function haversineKm(a, b) {{
      const radius = 6371;
      const toRad = value => value * Math.PI / 180;
      const dLat = toRad(b[1] - a[1]);
      const dLon = toRad(b[0] - a[0]);
      const lat1 = toRad(a[1]);
      const lat2 = toRad(b[1]);
      const h = Math.sin(dLat / 2) ** 2
        + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
      return 2 * radius * Math.asin(Math.sqrt(h));
    }}

    function elevationStats(feature) {{
      const coords = feature.geometry.coordinates.filter(coord => Number.isFinite(coord[2]));
      if (!coords.length) return null;
      let distance = 0;
      const points = coords.map((coord, index) => {{
        if (index > 0) distance += haversineKm(coords[index - 1], coord);
        return {{ distance, elevation: coord[2] }};
      }});
      const elevations = points.map(point => point.elevation);
      return {{
        points,
        distance,
        min: Math.round(Math.min(...elevations)),
        max: Math.round(Math.max(...elevations))
      }};
    }}

    function profileSvg(feature) {{
      const stats = elevationStats(feature);
      if (!stats) return `<div class="profile-wrap">Keine Profildaten</div>`;
      const width = 360;
      const height = 118;
      const padX = 10;
      const padY = 12;
      const range = Math.max(1, stats.max - stats.min);
      const step = Math.max(1, Math.floor(stats.points.length / 110));
      const sampled = stats.points.filter((_, index) => index % step === 0);
      if (sampled[sampled.length - 1] !== stats.points[stats.points.length - 1]) {{
        sampled.push(stats.points[stats.points.length - 1]);
      }}
      const xy = point => {{
        const x = padX + (point.distance / Math.max(1, stats.distance)) * (width - padX * 2);
        const y = height - padY - ((point.elevation - stats.min) / range) * (height - padY * 2);
        return `${{x.toFixed(1)}},${{y.toFixed(1)}}`;
      }};
      const line = sampled.map(xy).join(" ");
      const area = `${{padX}},${{height - padY}} ${{line}} ${{width - padX}},${{height - padY}}`;
      return `<div class="profile-wrap">
        <div class="profile-title"><span>Streckenprofil</span><span>${{stats.min}}-${{stats.max}} m</span></div>
        <svg class="profile-svg" viewBox="0 0 ${{width}} ${{height}}" role="img" aria-label="Höhenprofil">
          <polygon points="${{area}}" fill="#eeeeee"></polygon>
          <polyline points="${{line}}" fill="none" stroke="#000000" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"></polyline>
          <line x1="${{padX}}" y1="${{height - padY}}" x2="${{width - padX}}" y2="${{height - padY}}" stroke="#000000" stroke-width="1"></line>
        </svg>
      </div>`;
    }}

    function miniProfileSvg(feature) {{
      const stats = elevationStats(feature);
      if (!stats) return "";
      const width = 260;
      const height = 38;
      const padX = 5;
      const padY = 5;
      const range = Math.max(1, stats.max - stats.min);
      const step = Math.max(1, Math.floor(stats.points.length / 64));
      const sampled = stats.points.filter((_, index) => index % step === 0);
      if (sampled[sampled.length - 1] !== stats.points[stats.points.length - 1]) {{
        sampled.push(stats.points[stats.points.length - 1]);
      }}
      const xy = point => {{
        const x = padX + (point.distance / Math.max(1, stats.distance)) * (width - padX * 2);
        const y = height - padY - ((point.elevation - stats.min) / range) * (height - padY * 2);
        return `${{x.toFixed(1)}},${{y.toFixed(1)}}`;
      }};
      const line = sampled.map(xy).join(" ");
      const area = `${{padX}},${{height - padY}} ${{line}} ${{width - padX}},${{height - padY}}`;
      return `<span class="mini-profile" aria-hidden="true">
        <svg viewBox="0 0 ${{width}} ${{height}}">
          <polygon points="${{area}}" fill="#eeeeee"></polygon>
          <polyline points="${{line}}" fill="none" stroke="#000000" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"></polyline>
        </svg>
      </span>`;
    }}

    function metricValue(value, suffix) {{
      return value === null || value === undefined ? "offen" : `${{value}} ${{suffix}}`;
    }}

    function stravaSegmentUrl(query) {{
      return `https://www.strava.com/segments/search?keywords=${{encodeURIComponent(query)}}`;
    }}

    function passCardsHtml(passes) {{
      if (!passes || !passes.length) return "";
      return `<div class="detail-block-title">Pässe & Segmente</div>
        <div class="pass-list">
          ${{passes.map(pass => `<article class="pass-card">
            <strong>${{htmlEscape(pass.name)}}</strong>
            <span>${{htmlEscape(pass.status)}}</span>
            <p>${{htmlEscape(pass.palmares)}}</p>
            <a class="segment-link" href="${{htmlEscape(stravaSegmentUrl(pass.segment_query))}}" target="_blank" rel="noopener">Strava Segmente suchen</a>
          </article>`).join("")}}
        </div>`;
    }}

    function showRouteDetail(id) {{
      const feature = featureById(id);
      if (!feature) return;
      const props = feature.properties;
      const modal = document.getElementById("route-modal");
      const panel = document.getElementById("route-modal-body");
      const modalTitle = document.getElementById("route-modal-title");
      const metrics = [
        ["Distanz", metricValue(props.brouter_km, "km")],
        ["Höhenmeter", metricValue(props.brouter_hm, "hm")]
      ];
      modal.hidden = false;
      if (modalTitle) modalTitle.textContent = `${{props.day_label}} · ${{props.difficulty}}`;
      panel.innerHTML = `<div class="detail-head">
          <div class="detail-kicker">
            <span>${{htmlEscape(props.day_label)}}</span>
            <span class="${{difficultyClass(props.difficulty)}}">${{props.difficulty}}</span>
          </div>
          <h2>${{htmlEscape(props.title)}}</h2>
        </div>
        <div class="detail-body">
          <p class="detail-description">${{htmlEscape(props.description)}}</p>
          <div class="metrics">
            ${{metrics.map(([label, value]) => `<div class="metric"><span>${{htmlEscape(label)}}</span><strong>${{htmlEscape(value)}}</strong></div>`).join("")}}
          </div>
          ${{profileSvg(feature)}}
          <div class="detail-block-title">Highlights</div>
          <ul class="highlight-list">
            ${{props.highlights.map(item => `<li>${{htmlEscape(item)}}</li>`).join("")}}
          </ul>
          ${{passCardsHtml(props.passes)}}
          <div class="detail-block-title">Fotospots</div>
          <div class="photo-strip">
            ${{props.photo_spots.map(item => `<div class="photo-tile"><span>Fotospot</span><strong>${{htmlEscape(item)}}</strong></div>`).join("")}}
          </div>
          <div class="detail-actions">
            <a class="button-link" href="${{htmlEscape(props.gpx_file || '#')}}" download>GPX</a>
          </div>
        </div>`;
      const closeButton = document.getElementById("route-modal-close");
      if (closeButton) closeButton.focus();
    }}

    function closeRouteDetail() {{
      const modal = document.getElementById("route-modal");
      if (!modal) return;
      modal.hidden = true;
    }}

    function renderControls() {{
      const container = document.getElementById("layers");
      const grouped = new Map();
      for (const feature of routeData.features) {{
        const props = feature.properties;
        if (!grouped.has(props.day)) grouped.set(props.day, []);
        grouped.get(props.day).push(feature);
      }}
      container.innerHTML = "";
      for (const [day, features] of grouped.entries()) {{
        features.sort((a, b) => a.properties.difficulty_order - b.properties.difficulty_order);
        const section = document.createElement("section");
        section.className = "day";
        const dayLabel = features[0]?.properties.day_label || day;
        section.innerHTML = `<div class="day-title"><span class="swatch" style="background:${{dayColors[day]}}"></span>${{dayLabel}}</div>`;
        for (const feature of features) {{
          const props = feature.properties;
          const meta = `${{props.brouter_km}} km / ${{props.brouter_hm}} hm`;
          const label = document.createElement("label");
          label.className = "route";
          label.innerHTML = `<input type="radio" name="route-${{htmlEscape(props.day)}}" data-route-id="${{props.id}}">
            <span>
              <strong><span class="${{difficultyClass(props.difficulty)}}">${{props.difficulty}}</span>${{htmlEscape(props.title)}}</strong>
              <span class="meta">${{htmlEscape(meta)}}</span>
              ${{miniProfileSvg(feature)}}
              <span class="route-actions" onclick="event.stopPropagation()">
                <a href="${{htmlEscape(props.gpx_file || '#')}}" download>GPX</a>
                <button type="button" class="route-detail-button" data-route-id="${{htmlEscape(props.id)}}">Details</button>
              </span>
            </span>`;
          const detailButton = label.querySelector(".route-detail-button");
          if (detailButton) {{
            detailButton.addEventListener("click", event => {{
              event.preventDefault();
              event.stopPropagation();
              showRouteDetail(props.id);
            }});
          }}
          section.appendChild(label);
        }}
        container.appendChild(section);
      }}
      container.addEventListener("change", event => {{
        const target = event.target;
        if (target.matches("input[data-route-id]")) {{
          selectRoute(target.dataset.routeId);
        }}
      }});
    }}

    function htmlEscape(value) {{
      return String(value).replace(/[&<>"']/g, char => ({{
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      }}[char]));
    }}

    for (const button of document.querySelectorAll(".filter-grid button[data-preset]")) {{
      button.addEventListener("click", () => selectPreset(button.dataset.preset));
    }}
    document.getElementById("fit").addEventListener("click", fitRoutes);
    document.getElementById("route-modal-close").addEventListener("click", closeRouteDetail);
    document.getElementById("route-modal").addEventListener("click", event => {{
      if (event.target.id === "route-modal") closeRouteDetail();
    }});
    document.addEventListener("keydown", event => {{
      if (event.key === "Escape") closeRouteDetail();
    }});

    renderControls();
    updatePresetTotals();
    selectPreset("MEDIUM");
    fitRoutes();
  </script>
</body>
</html>
"""


def main() -> None:
    geojson = build_geojson()
    write_gpx_files(geojson)
    GEOJSON_OUT.write_text(json.dumps(geojson, ensure_ascii=False, indent=2), encoding="utf-8")
    HTML_OUT.write_text(make_html(geojson), encoding="utf-8")
    print(f"Wrote {GPX_ZIP_OUT}")
    print(f"Wrote {GEOJSON_OUT}")
    print(f"Wrote {HTML_OUT}")


if __name__ == "__main__":
    main()
