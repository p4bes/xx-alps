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

ROAD_BIKE_SVG = """<svg viewBox="0 0 120 80" focusable="false">
  <circle cx="28" cy="58" r="20"></circle>
  <circle cx="92" cy="58" r="20"></circle>
  <path d="M28 58 L48 28 L58 58 L28 58 M48 28 H76 L92 58 M76 28 L58 58 M58 58 H92"></path>
  <path d="M48 28 L43 16 H30"></path>
  <path d="M76 28 L82 16 H91 C99 16 104 23 100 30 C97 36 90 35 88 29"></path>
  <circle cx="58" cy="58" r="6"></circle>
  <path d="M58 58 L66 69 M66 69 L72 65"></path>
</svg>"""


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

DAY_LABELS_EN = {
    "J1": "Stage 1",
    "J2": "Stage 2",
    "J3": "Stage 3",
    "J4": "Stage 4",
    "J5": "Stage 5",
}


DAY_ENDPOINTS = {
    "J1": ("Cordon", "Flumet"),
    "J2": ("Flumet", "Beaufort"),
    "J3": ("Beaufort", "Brides-les-Bains"),
    "J4": ("Brides-les-Bains", "St-Michel"),
    "J5": ("St-Michel", "Briançon"),
}


DIFFICULTY_ORDER = {"LIGHT": 1, "MEDIUM": 2, "STRONG": 3}


def commons_file_url(file_name: str, width: int = 900) -> str:
    encoded = urllib.parse.quote(file_name.replace(" ", "_"), safe="()@-'_.")
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}?width={width}"


def commons_file_page(file_name: str) -> str:
    encoded = urllib.parse.quote(file_name.replace(" ", "_"), safe="()@-'_.")
    return f"https://commons.wikimedia.org/wiki/File:{encoded}"


def commons_image(file_name: str, credit: str, license_label: str) -> dict:
    return {
        "url": commons_file_url(file_name),
        "source_url": commons_file_page(file_name),
        "credit": credit,
        "license": license_label,
    }


PLACE_INFO = {
    "Megève": {
        "summary": "Eleganter Alpenort im Mont-Blanc-Blickfeld; guter leichter Einstieg mit Cafés und Ortskulisse.",
        "summary_en": "Elegant Alpine town with Mont Blanc views; a gentle opener with cafes and village scenery.",
        "url": "https://www.megeve-tourisme.fr/",
        "url_en": "https://www.megeve-tourisme.fr/en/",
    },
    "Le Grand-Bornand": {
        "summary": "Traditioneller Aravis-Ort mit Chalets, Reblochon-Kultur und guter Pause nach der Colombière.",
        "summary_en": "Traditional Aravis village with chalet scenery, Reblochon culture and a useful stop after Colombière.",
        "url": "https://www.legrandbornand.com/",
        "url_en": "https://en.legrandbornand.com/",
        "image": commons_image("Le Grand-Bornand 74.JPG", "Anthospace / Wikimedia Commons", "CC BY-SA 3.0"),
    },
    "Col de la Colombière": {
        "summary": "Früher Route-des-Grandes-Alpes-Test: kurz, steil genug und mit starkem Blick auf Aravis und Bargy.",
        "summary_en": "An early Route des Grandes Alpes test: compact, steep enough and framed by the Aravis and Bargy ranges.",
        "url": "https://www.routedesgrandesalpes.com/grands-cols/col-de-la-colombiere",
        "url_en": "https://en.routedesgrandesalpes.com/grands-cols/col-de-la-colombiere",
        "image": commons_image("Col de la Colombière @ Le Grand-Bornand (51026609812).jpg", "Guilhem Vellut / Wikimedia Commons", "CC BY 2.0"),
    },
    "Col des Aravis": {
        "summary": "Fotogener Übergang zwischen La Clusaz und Val d'Arly; oben öffnet sich der Blick zum Mont Blanc.",
        "summary_en": "Photogenic pass between La Clusaz and Val d'Arly; the summit opens up towards Mont Blanc.",
        "url": "https://www.routedesgrandesalpes.com/grands-cols/col-des-aravis",
        "url_en": "https://en.routedesgrandesalpes.com/grands-cols/col-des-aravis",
        "image": commons_image("Col des Aravis.jpg", "Helene / Wikimedia Commons", "CC BY 2.0"),
    },
    "Col des Saisies": {
        "summary": "Übergang vom Val d'Arly ins Beaufortain; olympischer Stationsort, Beaufort-Käse und Mont-Blanc-Blicke.",
        "summary_en": "Pass from Val d'Arly into Beaufortain; Olympic resort setting, Beaufort cheese and Mont Blanc views.",
        "url": "https://www.routedesgrandesalpes.com/grands-cols/col-des-saisies",
        "url_en": "https://en.routedesgrandesalpes.com/grands-cols/col-des-saisies",
    },
    "Col du Joly": {
        "summary": "Panorama-Stichfahrt über Hauteluce mit sehr starkem Blick Richtung Mont-Blanc-Massiv.",
        "summary_en": "Panoramic out-and-back above Hauteluce with standout views towards the Mont Blanc massif.",
        "url": "https://commons.wikimedia.org/wiki/Category:Col_du_Joly",
        "url_en": "https://commons.wikimedia.org/wiki/Category:Col_du_Joly",
        "image": commons_image("Col-du-Joly-1.jpg", "SchiDD / Wikimedia Commons", "freie Lizenz laut Commons"),
    },
    "Lac de Roselend": {
        "summary": "Türkisfarbener Beaufortain-Stausee mit Staumauer, Kapelle und einer der stärksten Fotostellen der Reise.",
        "summary_en": "Turquoise Beaufortain reservoir with dam, chapel and one of the strongest photo stops of the trip.",
        "url": "https://www.routedesgrandesalpes.com/grands-cols/cormet-de-roselend",
        "url_en": "https://en.routedesgrandesalpes.com/grands-cols/cormet-de-roselend",
        "image": commons_image("Barrage de Roselend.jpg", "Nabla01 / Wikimedia Commons", "Public Domain"),
    },
    "Cormet de Roselend": {
        "summary": "Großer Beaufortain-Übergang über Seen, Almen und Hochalpenlandschaft Richtung Tarentaise.",
        "summary_en": "Major Beaufortain crossing over lakes, alpine pastures and high-mountain scenery towards Tarentaise.",
        "url": "https://www.routedesgrandesalpes.com/grands-cols/cormet-de-roselend",
        "url_en": "https://en.routedesgrandesalpes.com/grands-cols/cormet-de-roselend",
        "image": commons_image("Barrage et Lac de Roselend.JPG", "Nono vlf / Wikimedia Commons", "CC BY-SA 3.0"),
    },
    "Bourg-Saint-Maurice": {
        "summary": "Größter Versorgungs- und Talort nach Roselend; guter Schnittpunkt vor der Tarentaise-Rollstrecke.",
        "summary_en": "Largest valley and resupply town after Roselend; a useful reset before the Tarentaise transfer.",
        "url": "https://www.bourgsaintmaurice.fr/",
        "url_en": "https://en.lesarcs.com/bourg-saint-maurice",
    },
    "Col de la Loze": {
        "summary": "Moderner Tour-de-France-Mythos mit Radweg-Rampen, die deutlich brutaler sind als ein normaler Alpenpass.",
        "summary_en": "Modern Tour de France myth with cycle-path ramps that feel far harsher than a conventional Alpine pass.",
        "url": "https://www.routedesgrandesalpes.com/grands-cols//col-de-la-loze",
        "url_en": "https://www.routedesgrandesalpes.com/grands-cols//col-de-la-loze",
    },
    "Col de la Madeleine": {
        "summary": "Eines der großen Alpenmonumente: lang, offen, hoch und seit Jahrzehnten ein Tour-de-France-Schauplatz.",
        "summary_en": "One of the great Alpine monuments: long, open, high and a Tour de France stage setting for decades.",
        "url": "https://www.routedesgrandesalpes.com/grands-cols/col-de-la-madeleine",
        "url_en": "https://en.routedesgrandesalpes.com/grands-cols/col-de-la-madeleine",
        "image": commons_image("Col de la Madeleine - 2014-08 - 28IMG 6056.jpg", "Poudou99 / Wikimedia Commons", "CC BY-SA 3.0"),
    },
    "Lacets de Montvernier": {
        "summary": "Achtzehn enge Kehren an der Felswand; kurzer Anstieg, aber extrem starkes Social- und Fotomotiv.",
        "summary_en": "Eighteen tight hairpins on the cliffside; a short climb but a huge social and photo highlight.",
        "url": "https://www.maurienne-tourisme.com/visiter_bouger/boucle-des-lacets-de-montvernier-5588742/",
        "url_en": "https://www.cycling-french-alps.com/explore/lacets-de-montvernier-and-col-du-chaussy/",
        "image": commons_image("Lacets de Montvernier depuis A43 (1).JPG", "Florian Pepellin / Wikimedia Commons", "CC BY-SA 3.0"),
    },
    "Col du Chaussy": {
        "summary": "Ruhiger Maurienne-Pass über den Lacets; ideal, wenn J4 mehr Charakter als Taltransfer haben soll.",
        "summary_en": "Quiet Maurienne pass above the Lacets; ideal when stage 4 should feel more characterful than a valley transfer.",
        "url": "https://www.velo-maurienne.com/explorer/lacets-de-montvernier-et-col-du-chaussy/",
        "url_en": "https://www.cycling-french-alps.com/explore/lacets-de-montvernier-and-col-du-chaussy/",
    },
    "Col du Galibier": {
        "summary": "Der Hochalpenklassiker schlechthin: Galibier steht seit 1911 für Tour-de-France-Mythos und Wetterrespekt.",
        "summary_en": "The high-Alpine classic: Galibier has meant Tour de France myth and serious weather respect since 1911.",
        "url": "https://www.routedesgrandesalpes.com/grands-cols/col-du-galibier",
        "url_en": "https://en.routedesgrandesalpes.com/grands-cols/col-du-galibier",
        "image": commons_image("Col du galibier.jpg", "Benoit Kornmann / Wikimedia Commons", "CC BY-SA 3.0"),
    },
    "Briançon": {
        "summary": "UNESCO-geprägte Festungsstadt und starker Abschlussort nach Galibier, Granon oder Izoard.",
        "summary_en": "UNESCO-flavoured fortified town and a strong finish after Galibier, Granon or Izoard.",
        "url": "https://www.serre-chevalier.com/en/briancon/",
        "url_en": "https://www.serre-chevalier.com/en/briancon/",
    },
    "Col du Granon": {
        "summary": "Steiler Stich über Briançon/Saint-Chaffrey; wenig Erholung, dafür ein sehr klares Finalsegment.",
        "summary_en": "Steep out-and-back above Briançon/Saint-Chaffrey; little recovery, but a very clear finale segment.",
        "url": "https://commons.wikimedia.org/wiki/Category:Col_du_Granon",
        "url_en": "https://commons.wikimedia.org/wiki/Category:Col_du_Granon",
    },
    "Col d'Izoard": {
        "summary": "Hochalpenmonument im Queyras; die Nordrampe ab Briançon/Cervières ist ein würdiger Finalbonus.",
        "summary_en": "High-Alpine monument in the Queyras; the north side from Briançon/Cervières is a worthy final bonus.",
        "url": "https://www.routedesgrandesalpes.com/grands-cols/col-izoard",
        "url_en": "https://en.routedesgrandesalpes.com/grands-cols/col-izoard",
        "image": commons_image("2014 Mountain pass cycling milestone - Col d'Izoard Briancon.jpg", "Cyclingralph / Wikimedia Commons", "CC BY-SA 4.0"),
    },
}


TRAVEL_DAYS = {
    "ARRIVAL": {
        "label": "Anreise",
        "tab": "Anreise",
        "date": "2026-06-27",
        "start": "Anreise",
        "finish": "Cordon",
        "start_hotel": "Individuelle Anreise nach Cordon",
        "finish_hotel": "Hotel Le Chamois d'Or****, Cordon",
        "luggage": "Vélorizons-Gepäckanhänger vorbereiten; Hauptgepäck max. 20 kg und Tagesrucksack für Begleitfahrzeug sortieren.",
        "checkin": "Anreise/Check-in im Hotel Le Chamois d'Or ab 16:00 Uhr; Bike-Aufbau, Akkus laden, GPX prüfen.",
        "support": "Tourbegleiter und Guide treffen die Gruppe am 28.06. um 08:30 Uhr vor dem Hotel Le Chamois d'Or.",
        "weather_point": "Cordon",
        "briefing": "Zusatznacht in Cordon. Kein Etappendruck, aber Gepäcklabel, Tagesrucksack, Radcheck und Treffpunkt für den ersten Radtag festziehen.",
        "accommodation": {
            "name": "Hotel Le Chamois d'Or****",
            "address": "4080 Route de Cordon, 74700 Cordon",
            "phone": "+33 4 50 58 05 16",
            "service": "Übernachtung mit Frühstück",
            "note": "Anreise am Samstag, 27.06.2026 ab 16:00 Uhr.",
            "service_en": "Overnight stay with breakfast",
            "note_en": "Arrival on Saturday, 27 June 2026 from 16:00.",
        },
        "label_en": "Arrival",
        "tab_en": "Arrival",
        "start_hotel_en": "Individual arrival in Cordon",
        "finish_hotel_en": "Hotel Le Chamois d'Or****, Cordon",
        "luggage_en": "Prepare Vélorizons luggage tag; sort main luggage max. 20 kg and day pack for the support vehicle.",
        "checkin_en": "Arrival/check-in at Hotel Le Chamois d'Or from 16:00; build bikes, charge batteries and check GPX files.",
        "support_en": "Tour leader and guide meet the group on 28 June at 08:30 in front of Hotel Le Chamois d'Or.",
        "briefing_en": "Extra night in Cordon. No stage pressure yet, but lock in luggage tag, day pack, bike check and stage 1 meeting point.",
    },
    "DEPARTURE": {
        "label": "Abreise",
        "tab": "Abreise",
        "date": "2026-07-03",
        "start": "Briançon",
        "finish": "Abreise",
        "start_hotel": "Hotel Vauban, Briançon",
        "finish_hotel": "Individuelle Abreise",
        "luggage": "Gepäck vollständig, Räder und Wertsachen für Rücktransfer nach Cordon bereitstellen.",
        "checkin": "Treffpunkt am 03.07. um 08:30 Uhr vor dem Hotel Vauban; Rücktransfer nach Cordon mit Rädern und Gepäck.",
        "support": "Autocars Résalp übernimmt den Rücktransfer; Ankunft in Cordon laut Einladung gegen Mittag.",
        "weather_point": "Briançon",
        "briefing": "Abreisetag ohne Radetappe. Fokus auf pünktlichen Transfer, vollständiges Gepäck und sauberen Abschluss der Woche.",
        "transfer": {
            "name": "Autocars Résalp",
            "phone": "+33 4 92 20 47 50",
            "emergency": "+33 6 02 13 68 00",
            "note": "Rücktransfer Briançon - Cordon am 03.07. um 08:30 Uhr vor dem Hotel Vauban mit Rädern und Gepäck.",
            "note_en": "Return transfer Briançon - Cordon on 3 July at 08:30 in front of Hotel Vauban with bikes and luggage.",
        },
        "label_en": "Departure",
        "tab_en": "Departure",
        "start_hotel_en": "Hotel Vauban, Briançon",
        "finish_hotel_en": "Individual departure",
        "luggage_en": "Check all luggage, bikes and valuables for the return transfer to Cordon.",
        "checkin_en": "Meeting point on 3 July at 08:30 in front of Hotel Vauban; return transfer to Cordon with bikes and luggage.",
        "support_en": "Autocars Résalp handles the return transfer; invitation states arrival in Cordon around noon.",
        "briefing_en": "Departure day without a ride stage. Focus on punctual transfer, complete luggage and a clean finish to the week.",
    },
}


TRIP_DAYS = {
    "J1": {
        "date": "2026-06-28",
        "start_hotel": "Hotel Le Chamois d'Or****, Cordon",
        "finish_hotel": "Hôtel Le Mont-Blanc, Flumet",
        "luggage": "08:30 Uhr vor Hotel Le Chamois d'Or: Gepäckübergabe an Tourbegleiter; Tagesrucksack ins Begleitfahrzeug.",
        "checkin": "Übernachtung und Abendessen im Hôtel Le Mont-Blanc, Flumet.",
        "support": "08:30 Uhr Treffen mit Tourbegleiter Emmanuel Cron und Guide Luc Millithaler vor dem Hotel Le Chamois d'Or.",
        "weather_point": "Col des Aravis",
        "briefing": "Auftakt im Aravis-Massiv. Startbriefing und Gepäckübergabe sind Teil des 08:30-Treffens.",
        "accommodation": {
            "name": "Hôtel Le Mont-Blanc",
            "address": "97 Rue du Mont Blanc, 73590 Flumet",
            "phone": "+33 9 70 70 40 90",
            "service": "Übernachtung mit Frühstück",
            "note": "Auch Abendessen im selben Hotel.",
            "service_en": "Overnight stay with breakfast",
            "note_en": "Dinner is also booked at the same hotel.",
        },
        "dinner": {
            "name": "Hôtel Le Mont-Blanc",
            "address": "97 Rue du Mont Blanc, 73590 Flumet",
            "phone": "+33 9 70 70 40 90",
            "note": "Abendessen im Hotel.",
            "note_en": "Dinner at the hotel.",
        },
        "start_hotel_en": "Hotel Le Chamois d'Or****, Cordon",
        "finish_hotel_en": "Hôtel Le Mont-Blanc, Flumet",
        "luggage_en": "08:30 in front of Hotel Le Chamois d'Or: hand luggage to the tour leader; day pack into the support vehicle.",
        "checkin_en": "Overnight stay and dinner at Hôtel Le Mont-Blanc, Flumet.",
        "support_en": "08:30 meeting with tour leader Emmanuel Cron and guide Luc Millithaler in front of Hotel Le Chamois d'Or.",
        "briefing_en": "Opening stage in the Aravis range. Start briefing and luggage handover are part of the 08:30 meeting.",
    },
    "J2": {
        "date": "2026-06-29",
        "start_hotel": "Hôtel Le Mont-Blanc, Flumet",
        "finish_hotel": "Hotel La Roche****, Beaufort",
        "luggage": "Gepäck morgens für den Transport bereitstellen; Hauptgepäck max. 20 kg, Tagesrucksack im Begleitfahrzeug.",
        "checkin": "Hotel La Roche: Check-in ab 15:00 Uhr, Check-out vor 11:00 Uhr; Abendessen im Hotel.",
        "support": "Support über Vélorizons/Bike Frankreich; Beaufort ist guter Versorgungs- und Regenerationsort.",
        "weather_point": "Col des Saisies",
        "briefing": "Panoramatag im Beaufortain. Hotel-Check-in ist ab 15:00 Uhr möglich.",
        "accommodation": {
            "name": "Hotel La Roche****",
            "address": "34 avenue du Capitaine Bulle, 73270 Beaufort",
            "phone": "+33 4 58 23 02 22",
            "service": "Übernachtung mit Frühstück",
            "note": "Check-in ab 15:00 Uhr, Check-out vor 11:00 Uhr.",
            "service_en": "Overnight stay with breakfast",
            "note_en": "Check-in from 15:00, check-out before 11:00.",
        },
        "dinner": {
            "name": "Hotel La Roche****",
            "address": "34 avenue du Capitaine Bulle, 73270 Beaufort",
            "phone": "+33 4 58 23 02 22",
            "note": "Abendessen im Hotel.",
            "note_en": "Dinner at the hotel.",
        },
        "start_hotel_en": "Hôtel Le Mont-Blanc, Flumet",
        "finish_hotel_en": "Hotel La Roche****, Beaufort",
        "luggage_en": "Place luggage for transport in the morning; main luggage max. 20 kg, day pack in the support vehicle.",
        "checkin_en": "Hotel La Roche: check-in from 15:00, check-out before 11:00; dinner at the hotel.",
        "support_en": "Support via Vélorizons/Bike Frankreich; Beaufort is a useful resupply and recovery town.",
        "briefing_en": "Panorama day in Beaufortain. Joly is an out-and-back and can be skipped if weather turns.",
    },
    "J3": {
        "date": "2026-06-30",
        "start_hotel": "Hotel La Roche****, Beaufort",
        "finish_hotel": "B&B Home Brides les Bains****",
        "luggage": "Gepäck früh für den Transfer bereitstellen; lange Etappe und Hotelwechsel nach Brides-les-Bains.",
        "checkin": "Übernachtung und Abendessen im B&B Home Brides les Bains****.",
        "support": "Support über Vélorizons/Bike Frankreich; Versorgung in Bourg-Saint-Maurice und Moûtiers einplanen.",
        "weather_point": "Cormet de Roselend",
        "briefing": "Großer Roselend-Tag. Wetter, Müdigkeit und Uhrzeit entscheiden, ob die Loze-Schleife sinnvoll ist.",
        "accommodation": {
            "name": "B&B Home Brides les Bains****",
            "address": "1 Allée du Parc, 73570 Brides-les-Bains",
            "phone": "+33 8 92 23 33 57",
            "service": "Übernachtung mit Frühstück",
            "note": "Auch Abendessen im selben Hotel.",
            "service_en": "Overnight stay with breakfast",
            "note_en": "Dinner is also booked at the same hotel.",
        },
        "dinner": {
            "name": "B&B Home Brides les Bains****",
            "address": "1 Allée du Parc, 73570 Brides-les-Bains",
            "phone": "+33 8 92 23 33 57",
            "note": "Abendessen im Hotel.",
            "note_en": "Dinner at the hotel.",
        },
        "start_hotel_en": "Hotel La Roche****, Beaufort",
        "finish_hotel_en": "B&B Home Brides les Bains****",
        "luggage_en": "Place luggage early for transfer; long ride and hotel change to Brides-les-Bains.",
        "checkin_en": "Overnight stay and dinner at B&B Home Brides les Bains****.",
        "support_en": "Support via Vélorizons/Bike Frankreich; plan resupply in Bourg-Saint-Maurice and Moûtiers.",
        "briefing_en": "Big Roselend day. Weather, fatigue and time decide whether the Loze loop makes sense.",
    },
    "J4": {
        "date": "2026-07-01",
        "start_hotel": "B&B Home Brides les Bains****",
        "finish_hotel": "Hôtel Le Marintan***, Saint-Michel-de-Maurienne",
        "luggage": "Gepäck morgens für den Transfer bereitstellen; nach Madeleine die Zeit für Chaussy/Lacets realistisch prüfen.",
        "checkin": "Hôtel Le Marintan: Check-in ab 15:00 Uhr, Check-out vor 11:00 Uhr.",
        "support": "Abendessen um 19:30 Uhr im Grill du Savoy in Saint-Michel-de-Maurienne.",
        "weather_point": "Col de la Madeleine",
        "briefing": "Madeleine als Pflichtprogramm. Für Abendessen um 19:30 Uhr genug Puffer nach Saint-Michel lassen.",
        "accommodation": {
            "name": "Hôtel Le Marintan***",
            "address": "1 rue de la Provalière, 73140 Saint-Michel-de-Maurienne",
            "phone": "+33 4 79 59 16 91",
            "service": "Übernachtung mit Frühstück",
            "note": "Check-in ab 15:00 Uhr, Check-out vor 11:00 Uhr.",
            "service_en": "Overnight stay with breakfast",
            "note_en": "Check-in from 15:00, check-out before 11:00.",
        },
        "dinner": {
            "name": "Grill du Savoy",
            "address": "25 Rue Général Ferrié, 73140 Saint-Michel-de-Maurienne",
            "phone": "+33 4 79 56 55 12",
            "time": "19:30",
            "note": "Abendessen um 19:30 Uhr.",
            "note_en": "Dinner at 19:30.",
        },
        "start_hotel_en": "B&B Home Brides les Bains****",
        "finish_hotel_en": "Hôtel Le Marintan***, Saint-Michel-de-Maurienne",
        "luggage_en": "Place luggage for transfer in the morning; after Madeleine, check time realistically for Chaussy/Lacets.",
        "checkin_en": "Hôtel Le Marintan: check-in from 15:00, check-out before 11:00.",
        "support_en": "Dinner at 19:30 at Grill du Savoy in Saint-Michel-de-Maurienne.",
        "briefing_en": "Madeleine is the main commitment. Chaussy/Lacets are the optional character and social part.",
    },
    "J5": {
        "date": "2026-07-02",
        "start_hotel": "Hôtel Le Marintan***, Saint-Michel-de-Maurienne",
        "finish_hotel": "Hotel Vauban, Briançon",
        "luggage": "Gepäck morgens für den finalen Hoteltransfer bereitstellen; warme Kleidung für Briançon erreichbar halten.",
        "checkin": "Übernachtung mit Frühstück im Hotel Vauban, Briançon; am Folgetag Rücktransfer um 08:30 Uhr.",
        "support": "Galibier-Finale mit exponierter Hochalpenlage; Rücktransfer am 03.07. ab Hotel Vauban.",
        "weather_point": "Col du Galibier",
        "briefing": "Königsetappe zum Abschluss. Hotel Vauban ist auch Treffpunkt für den Rücktransfer am 03.07. um 08:30 Uhr.",
        "accommodation": {
            "name": "Hotel Vauban",
            "address": "13 av du Général de Gaulle, 05100 Briançon",
            "phone": "+33 4 92 21 12 11",
            "service": "Übernachtung mit Frühstück",
            "note": "Treffpunkt Rücktransfer am 03.07. um 08:30 Uhr vor dem Hotel.",
            "service_en": "Overnight stay with breakfast",
            "note_en": "Return transfer meeting point on 3 July at 08:30 in front of the hotel.",
        },
        "start_hotel_en": "Hôtel Le Marintan***, Saint-Michel-de-Maurienne",
        "finish_hotel_en": "Hotel Vauban, Briançon",
        "luggage_en": "Place luggage for the final hotel transfer in the morning; keep warm clothes accessible for Briançon.",
        "checkin_en": "Overnight stay with breakfast at Hotel Vauban, Briançon; return transfer the next day at 08:30.",
        "support_en": "Galibier finale in exposed high-Alpine terrain; return transfer on 3 July from Hotel Vauban.",
        "briefing_en": "Queen stage to close the trip. Take the Galibier weather window seriously; Izoard only in very stable conditions.",
    },
}


ORGANIZER_INFO = {
    "booking": {
        "code": "CY98-DG-1",
        "trip": "Französische Nordalpen MTB & Road Special (Exxeta)",
        "dates": "27.06.-03.07.2026",
        "service": "Bike Frankreich - Vélorizons",
        "address": "273 rue Branmafan, 73230 Barby, Frankreich",
        "office_phone": "+33 4 58 140 445",
        "emergency_phone": "+33 4 58 140 800",
        "service_en": "Bike Frankreich - Vélorizons",
        "address_en": "273 rue Branmafan, 73230 Barby, France",
    },
    "contacts": [
        {
            "role": "Tourbegleitung",
            "role_en": "Tour leader",
            "name": "Emmanuel Cron",
            "phone": "+33 7 85 21 79 46",
        },
        {
            "role": "Rennrad-Guide",
            "role_en": "Road cycling guide",
            "name": "Luc Millithaler",
            "phone": "+33 6 13 67 72 84",
            "note": "Kontakt laut Einladung erst ab Tag 1 der Tour nutzen.",
            "note_en": "Invitation asks to use this contact only from day 1 of the tour.",
        },
        {
            "role": "24/7 Notfallnummer",
            "role_en": "24/7 emergency number",
            "name": "Bike Frankreich - Vélorizons",
            "phone": "+33 4 58 140 800",
        },
    ],
    "rules": [
        {
            "title": "Formalitäten",
            "title_en": "Formalities",
            "text": "Personalausweis oder Reisepass sowie Auslandskranken-/Reiseversicherungsunterlagen mitführen.",
            "text_en": "Carry ID card or passport and international health/travel insurance documents.",
        },
        {
            "title": "Gepäck",
            "title_en": "Luggage",
            "text": "Zwei Gepäckstücke sind vorgesehen: Hauptgepäck max. 20 kg plus kleiner Tagesrucksack im Begleitfahrzeug.",
            "text_en": "Two luggage pieces are planned: main luggage max. 20 kg plus small day pack in the support vehicle.",
        },
        {
            "title": "Gepäckanhänger",
            "title_en": "Luggage tag",
            "text": "Vélorizons-Gepäckanhänger herunterladen, ausdrucken und mit Name sowie Telefonnummer im internationalen Format ausfüllen.",
            "text_en": "Download and print the Vélorizons luggage tag, then add name and phone number in international format.",
            "download": "assets/gepaeckanhaenger.pdf",
            "download_label": "Gepäckanhänger herunterladen",
            "download_label_en": "Download luggage tag",
        },
        {
            "title": "Navigation",
            "title_en": "Navigation",
            "text": "GPX-Tracks vorab auf Radcomputer/App laden und Kompatibilität prüfen.",
            "text_en": "Load GPX tracks onto bike computer/app in advance and check compatibility.",
        },
    ],
}


DASHBOARD_ORDER = ["ARRIVAL", "J1", "J2", "J3", "J4", "J5", "DEPARTURE"]


SUPPLY_POINTS = [
    {"day": "J1", "point": "Cluses", "name": "Cluses", "kind": "Shop/Café", "kind_en": "Shop/cafe", "note": "größerer Ort vor Romme/Colombière; gute Stelle zum Auffüllen", "note_en": "larger town before Romme/Colombière; good place to refill"},
    {"day": "J1", "point": "Le Grand-Bornand", "name": "Le Grand-Bornand", "kind": "Café/Wasser", "kind_en": "Cafe/water", "note": "Pause nach Colombière, vor La Clusaz/Aravis", "note_en": "break after Colombière, before La Clusaz/Aravis"},
    {"day": "J1", "point": "La Clusaz", "name": "La Clusaz", "kind": "Café/Wasser", "kind_en": "Cafe/water", "note": "letzte größere Versorgung vor dem Col des Aravis", "note_en": "last larger resupply before Col des Aravis"},
    {"day": "J2", "point": "Crest-Voland", "name": "Crest-Voland", "kind": "Café/Wasser", "kind_en": "Cafe/water", "note": "ruhiger Ort vor Saisies/Joly", "note_en": "quiet village before Saisies/Joly"},
    {"day": "J2", "point": "Col des Saisies", "name": "Les Saisies", "kind": "Café/Wasser", "kind_en": "Cafe/water", "note": "Wintersportort mit mehreren Pausenoptionen", "note_en": "resort village with several break options"},
    {"day": "J2", "point": "Hauteluce", "name": "Hauteluce", "kind": "Wasser/Café", "kind_en": "Water/cafe", "note": "Basis für die Joly-Stichfahrt", "note_en": "base for the Joly out-and-back"},
    {"day": "J3", "point": "Arêches", "name": "Arêches", "kind": "Café/Wasser", "kind_en": "Cafe/water", "note": "vor Col du Pré, wenn MEDIUM/STRONG gefahren wird", "note_en": "before Col du Pré if MEDIUM/STRONG is ridden"},
    {"day": "J3", "point": "Bourg-Saint-Maurice", "name": "Bourg-Saint-Maurice", "kind": "Shop/Café", "kind_en": "Shop/cafe", "note": "größter Versorgungsort nach Roselend", "note_en": "largest resupply town after Roselend"},
    {"day": "J3", "point": "Moûtiers", "name": "Moûtiers", "kind": "Shop/Wasser", "kind_en": "Shop/water", "note": "letzter größerer Ort vor Brides-les-Bains", "note_en": "last larger town before Brides-les-Bains"},
    {"day": "J4", "point": "Aigueblanche", "name": "Aigueblanche", "kind": "Shop/Wasser", "kind_en": "Shop/water", "note": "vor dem Madeleine-Anstieg", "note_en": "before the Madeleine climb"},
    {"day": "J4", "point": "La Chambre", "name": "La Chambre", "kind": "Café/Wasser", "kind_en": "Cafe/water", "note": "nach Madeleine, vor Chaussy/Lacets-Entscheidung", "note_en": "after Madeleine, before the Chaussy/Lacets decision"},
    {"day": "J4", "point": "Saint-Jean-de-Maurienne", "name": "Saint-Jean-de-Maurienne", "kind": "Shop/Café", "kind_en": "Shop/cafe", "note": "sicherer Versorgungsort im Maurienne-Tal", "note_en": "safe resupply town in the Maurienne valley"},
    {"day": "J5", "point": "Valloire", "name": "Valloire", "kind": "Café/Wasser", "kind_en": "Cafe/water", "note": "wichtiger Stopp vor Plan Lachat/Galibier", "note_en": "important stop before Plan Lachat/Galibier"},
    {"day": "J5", "point": "Col du Lautaret", "name": "Col du Lautaret", "kind": "Café/Wasser", "kind_en": "Cafe/water", "note": "Hochalpen-Versorgung nach dem Galibier", "note_en": "high-Alpine resupply after Galibier"},
    {"day": "J5", "point": "Le Monêtier-les-Bains", "name": "Le Monêtier-les-Bains", "kind": "Shop/Café", "kind_en": "Shop/cafe", "note": "Auffüllen vor Briançon oder Zusatzanstieg", "note_en": "refill before Briançon or the optional climb"},
]


GENERAL_PACKING_LIST = [
    "Reisepass/Personalausweis",
    "Kreditkarte, etwas Bargeld, Krankenversicherungskarte",
    "Ladegeräte für Handy, Radcomputer, Licht und Schaltung",
    "Freizeitkleidung für Hotelwechsel und Abende",
    "Waschbeutel, persönliche Medikamente, Ohrstöpsel",
    "Ersatz-Trikots, Bibs, Socken, Handschuhe",
    "Gepäcklabel und kleine Wäschetüte",
    "Bike-Transporttasche oder Schutzmaterial, falls benötigt",
]

GENERAL_PACKING_LIST_EN = [
    "Passport/ID card",
    "Credit card, some cash, health insurance card",
    "Chargers for phone, bike computer, lights and shifting",
    "Casual clothes for hotel changes and evenings",
    "Wash bag, personal medication, earplugs",
    "Spare jerseys, bibs, socks, gloves",
    "Luggage label and small laundry bag",
    "Bike travel bag or protection material if needed",
]


DAY_PACKING_LIST = [
    "2 volle Bidons",
    "Regenjacke und warme Schicht",
    "Armlinge/Beinlinge oder Weste",
    "Riegel/Gel für mindestens 3 Stunden",
    "Ausweis, Kreditkarte, etwas Bargeld",
    "Handy geladen, GPX geladen, Powerbank bei Bedarf",
    "Ersatzschlauch, CO2/Pumpe, Reifenheber, Multitool",
    "Sonnencreme und Brille",
    "Gepäcklabel dran, nichts im Zimmer vergessen",
]

DAY_PACKING_LIST_EN = [
    "2 full bottles",
    "Rain jacket and warm layer",
    "Arm/leg warmers or vest",
    "Bars/gels for at least 3 hours",
    "ID, credit card, some cash",
    "Phone charged, GPX loaded, power bank if needed",
    "Spare tube, CO2/pump, tire levers, multitool",
    "Sunscreen and glasses",
    "Luggage label attached, nothing left in the room",
]


ROUTE_DETAILS = {
    "j1-alt": {
        "difficulty": "LIGHT",
        "title": "via Megève",
        "description": "Die ruhige Ankommenslinie durch das Arve-Tal und über Megève. Gute Wahl bei später Anreise, müden Beinen oder unsicherem Wetter.",
        "description_en": "The calm arrival line through the Arve valley and via Megève. A good choice for a late start, tired legs or uncertain weather.",
        "highlights": ["Combloux", "Megève", "Praz-sur-Arly", "Blick Richtung Mont Blanc"],
        "photo_spots": ["Combloux", "Megève", "Praz-sur-Arly"],
    },
    "j1-v2": {
        "difficulty": "MEDIUM",
        "title": "via Colombière + Aravis",
        "description": "Der saubere Auftakt mit zwei echten Klassikern. Erst über die Colombière ins Aravis-Massiv, danach über La Clusaz und den Col des Aravis nach Flumet.",
        "description_en": "A clean opener with two real classics: Colombière into the Aravis range, then La Clusaz and Col des Aravis towards Flumet.",
        "highlights": ["Col de la Colombière", "Le Grand-Bornand", "La Clusaz", "Col des Aravis"],
        "photo_spots": ["Col de la Colombière", "Le Grand-Bornand", "Col des Aravis"],
    },
    "j1-v3": {
        "difficulty": "STRONG",
        "title": "via Romme + Colombière + Aravis",
        "description": "Die sportliche Eröffnung: Col de Romme nimmt früh Körner, macht die Zufahrt zur Colombière aber deutlich ruhiger und charaktervoller.",
        "description_en": "The sporty opener: Col de Romme costs energy early, but makes the approach to Colombière quieter and more characterful.",
        "highlights": ["Col de Romme", "Le Reposoir", "Col de la Colombière", "Col des Aravis"],
        "photo_spots": ["Col de Romme", "Le Reposoir", "Col des Aravis"],
    },
    "j2-alt": {
        "difficulty": "LIGHT",
        "title": "via Saisies direkt",
        "description": "Kurze Regenerationsvariante über den Col des Saisies ohne Joly-Stichfahrt. Ideal, wenn J3 und J4 voll gefahren werden sollen.",
        "description_en": "Short recovery variant over Col des Saisies without the Joly out-and-back. Ideal if stages 3 and 4 should be ridden in full.",
        "highlights": ["Notre-Dame-de-Bellecombe", "Crest-Voland", "Col des Saisies", "Hauteluce"],
        "photo_spots": ["Crest-Voland", "Col des Saisies", "Hauteluce"],
    },
    "j2-v2": {
        "difficulty": "MEDIUM",
        "title": "via Saisies + Col du Joly",
        "description": "Kompakte Panoramatour mit starker Mont-Blanc-Perspektive. Der Col du Joly ist eine Stichfahrt, lohnt sich aber landschaftlich klar.",
        "description_en": "Compact panorama route with strong Mont Blanc views. Col du Joly is an out-and-back, but clearly worth it for the scenery.",
        "highlights": ["Col des Saisies", "Hauteluce", "Col du Joly", "Beaufortain"],
        "photo_spots": ["Col des Saisies", "Col du Joly", "Beaufort"],
    },
    "j2-v3": {
        "difficulty": "STRONG",
        "title": "via Ugine + Saisies/Joly",
        "description": "Die lange Beaufortain-Variante mit Zusatzschleife über Ugine und Crest-Voland. Deutlich mehr Strecke, dafür eine rundere Tagesroute.",
        "description_en": "The long Beaufortain variant with an additional loop via Ugine and Crest-Voland. More distance, but a more rounded day route.",
        "highlights": ["Ugine", "Crest-Voland", "Col des Saisies", "Col du Joly"],
        "photo_spots": ["Crest-Voland", "Col du Joly", "Beaufort"],
    },
    "j3-v2": {
        "difficulty": "LIGHT",
        "title": "via Roselend direkt",
        "description": "Die kontrollierteste Linie des Tages: Roselend bleibt als landschaftlicher Höhepunkt drin, Col du Pré und Col du Tra werden ausgelassen.",
        "description_en": "The most controlled line of the day: Roselend stays in as the scenic highlight, while Col du Pré and Col du Tra are skipped.",
        "highlights": ["Lac de Roselend", "Cormet de Roselend", "Les Chapieux", "Bourg-Saint-Maurice"],
        "photo_spots": ["Lac de Roselend", "Cormet de Roselend", "Les Chapieux"],
    },
    "j3-v3": {
        "difficulty": "MEDIUM",
        "title": "via Pré + Roselend",
        "description": "Die landschaftliche Königslinie durch das Beaufortain mit Col du Pré, Lac de Roselend und Cormet de Roselend.",
        "description_en": "The scenic queen line through Beaufortain with Col du Pré, Lac de Roselend and Cormet de Roselend.",
        "highlights": ["Col du Pré", "Lac de Roselend", "Cormet de Roselend", "Bourg-Saint-Maurice"],
        "photo_spots": ["Lac de Roselend", "Cormet de Roselend", "Bourg-Saint-Maurice"],
    },
    "j3-loze": {
        "difficulty": "STRONG",
        "title": "via Pré + Roselend + Loze",
        "description": "Die Eskalation: Pré, Roselend und danach die brutale Loze-Schleife ab Brides. Nur bei stabilem Wetter und sehr guter Tagesform sinnvoll.",
        "description_en": "The escalation: Pré, Roselend and then the brutal Loze loop from Brides. Only sensible with stable weather and very strong legs.",
        "highlights": ["Col du Pré", "Cormet de Roselend", "Méribel", "Col de la Loze"],
        "photo_spots": ["Lac de Roselend", "Méribel", "Col de la Loze"],
    },
    "j4-v2": {
        "difficulty": "LIGHT",
        "title": "via Madeleine",
        "description": "Der belastbare Standard nach dem langen Vortag: ein großer Pass, danach direkter Transfer durch die Maurienne.",
        "description_en": "The reliable standard after the long previous day: one major pass, then a direct transfer through the Maurienne valley.",
        "highlights": ["La Léchère", "Celliers", "Col de la Madeleine", "Maurienne"],
        "photo_spots": ["Celliers", "Col de la Madeleine", "Saint-Jean-de-Maurienne"],
    },
    "j4-alt": {
        "difficulty": "MEDIUM",
        "title": "via Madeleine + Chaussy",
        "description": "Die Anbieterlinie als mittlere J4-Option: Madeleine plus Chaussy, mit den Lacets eher in der Abfahrtsrichtung.",
        "description_en": "The operator line as the medium stage 4 option: Madeleine plus Chaussy, with the Lacets mostly in the downhill direction.",
        "highlights": ["Col de la Madeleine", "Col du Chaussy", "Montvernier", "Lacets de Montvernier"],
        "photo_spots": ["Col de la Madeleine", "Col du Chaussy", "Lacets de Montvernier"],
    },
    "j4-v3": {
        "difficulty": "STRONG",
        "title": "via Madeleine + Lacets + Chaussy",
        "description": "Die schönere, aber harte Richtung: Lacets bergauf fahren, danach Chaussy und zurück ins Maurienne-Tal.",
        "description_en": "The prettier but harder direction: climb the Lacets, continue over Chaussy and return into the Maurienne valley.",
        "highlights": ["Col de la Madeleine", "Lacets de Montvernier", "Col du Chaussy", "Saint-Michel-de-Maurienne"],
        "photo_spots": ["Lacets de Montvernier", "Col du Chaussy", "Maurienne"],
    },
    "j5-light": {
        "difficulty": "LIGHT",
        "title": "via Télégraphe + Galibier",
        "description": "Der klassische Abschluss ab Saint-Michel mit Télégraphe und Galibier. In der neuen Staffelung ist das die leichteste vollständige Radetappe bis Briançon.",
        "description_en": "The classic finale from Saint-Michel with Télégraphe and Galibier. In the new structure, this is the easiest complete ride to Briançon.",
        "highlights": ["Col du Télégraphe", "Valloire", "Col du Galibier", "Col du Lautaret"],
        "photo_spots": ["Col du Télégraphe", "Plan Lachat", "Col du Galibier"],
    },
    "j5-v2": {
        "difficulty": "MEDIUM",
        "title": "via Télégraphe + Galibier + Granon",
        "description": "Galibier plus der steile Granon als Stichfahrt vor Briançon. Das ist die mittlere J5-Option für Gruppen, die am Finaltag noch einen harten Zusatzanstieg wollen.",
        "description_en": "Galibier plus the steep Granon out-and-back before Briançon. The medium stage 5 option for riders who still want a hard final climb.",
        "highlights": ["Col du Télégraphe", "Col du Galibier", "Col du Granon", "Briançon"],
        "photo_spots": ["Col du Galibier", "Col du Granon", "Briançon"],
    },
    "j5-v3": {
        "difficulty": "STRONG",
        "title": "via Télégraphe + Galibier + Izoard",
        "description": "Die neue Topvariante ohne Granon: erst Télégraphe und Galibier, dann ab Briançon/Cervières noch die ikonische Nordrampe zum Col d'Izoard als finales Monument.",
        "description_en": "The new top variant without Granon: Télégraphe and Galibier first, then the iconic north ramp to Col d'Izoard from Briançon/Cervières.",
        "highlights": ["Col du Télégraphe", "Col du Galibier", "Cervières", "Col d'Izoard"],
        "photo_spots": ["Col du Galibier", "Cervières", "Col d'Izoard"],
    },
}


PASS_INFO = {
    "Col de Romme": {
        "status": "steiler Auftaktklassiker",
        "status_en": "steep opener",
        "palmares": "Tour-de-France-Bergwertung; oft in Kombination mit der Colombière gefahren.",
        "palmares_en": "Tour de France mountain classification climb; often paired with Colombière.",
        "segment_query": "Col de Romme climb",
        "info_url": "https://fr.wikipedia.org/wiki/Col_de_Romme",
        "info_url_en": "https://en.wikipedia.org/wiki/Col_de_Romme",
    },
    "Col de la Colombière": {
        "status": "Tour-Klassiker",
        "status_en": "Tour classic",
        "palmares": "Großer Aravis-Pass mit langer Profi-Historie und vielen Strava-Climb-Varianten.",
        "palmares_en": "Major Aravis pass with deep pro-racing history and many Strava climb variants.",
        "segment_query": "Col de la Colombiere climb",
        "info_url": "https://www.routedesgrandesalpes.com/grands-cols/col-de-la-colombiere",
        "info_url_en": "https://en.routedesgrandesalpes.com/grands-cols/col-de-la-colombiere",
    },
    "Col des Aravis": {
        "status": "Aravis-Klassiker",
        "status_en": "Aravis classic",
        "palmares": "Bekannter Übergang zwischen La Clusaz und Flumet; starker Social-/Foto-Pass.",
        "palmares_en": "Well-known crossing between La Clusaz and Flumet; strong social and photo pass.",
        "segment_query": "Col des Aravis climb",
        "info_url": "https://www.routedesgrandesalpes.com/grands-cols/col-des-aravis",
        "info_url_en": "https://en.routedesgrandesalpes.com/grands-cols/col-des-aravis",
    },
    "Col des Saisies": {
        "status": "Beaufortain-Pass",
        "status_en": "Beaufortain pass",
        "palmares": "Regelmäßiger Rennrad- und Tour-de-France-Ort im Beaufortain.",
        "palmares_en": "Regular road-cycling and Tour de France location in Beaufortain.",
        "segment_query": "Col des Saisies climb",
        "info_url": "https://www.routedesgrandesalpes.com/grands-cols/col-des-saisies",
        "info_url_en": "https://en.routedesgrandesalpes.com/grands-cols/col-des-saisies",
    },
    "Col du Joly": {
        "status": "Panorama-Stichfahrt",
        "status_en": "panorama out-and-back",
        "palmares": "Weniger Profi-Palmarès, aber sehr stark für Aussicht und Segment-Jagd.",
        "palmares_en": "Less pro-racing pedigree, but excellent for views and segment hunting.",
        "segment_query": "Col du Joly climb",
        "info_url": "https://commons.wikimedia.org/wiki/Category:Col_du_Joly",
        "info_url_en": "https://commons.wikimedia.org/wiki/Category:Col_du_Joly",
    },
    "Col du Pré": {
        "status": "Beaufortain-Juwel",
        "status_en": "Beaufortain gem",
        "palmares": "Einer der schönsten Zufahrten zum Lac de Roselend; klare Kletter-Etappe.",
        "palmares_en": "One of the most beautiful approaches to Lac de Roselend; a true climbing section.",
        "segment_query": "Col du Pre Beaufortain climb",
        "info_url": "https://www.routedesgrandesalpes.com/grands-cols/cormet-de-roselend",
        "info_url_en": "https://en.routedesgrandesalpes.com/grands-cols/cormet-de-roselend",
    },
    "Cormet de Roselend": {
        "status": "Tour-Klassiker",
        "status_en": "Tour classic",
        "palmares": "Großer Alpenpass über dem Lac de Roselend; sehr bekannter Rennrad- und Tour-Pass.",
        "palmares_en": "Major Alpine pass above Lac de Roselend; a very well-known road-cycling and Tour pass.",
        "segment_query": "Cormet de Roselend climb",
        "info_url": "https://www.routedesgrandesalpes.com/grands-cols/cormet-de-roselend",
        "info_url_en": "https://en.routedesgrandesalpes.com/grands-cols/cormet-de-roselend",
    },
    "Col du Tra": {
        "status": "ruhige Nebenlinie",
        "status_en": "quiet side line",
        "palmares": "Eher lokale Alternative zur Talroute; interessant für ruhige Gruppenlinien.",
        "palmares_en": "More of a local alternative to the valley road; useful for quieter group routing.",
        "segment_query": "Col du Tra climb",
    },
    "Col de la Loze": {
        "status": "moderner Mythos",
        "status_en": "modern myth",
        "palmares": "Extrem steiler, moderner Tour-de-France-Schlussanstieg mit brutalen Rampen.",
        "palmares_en": "Extremely steep modern Tour de France summit climb with brutal ramps.",
        "segment_query": "Col de la Loze Meribel climb",
        "info_url": "https://www.routedesgrandesalpes.com/grands-cols//col-de-la-loze",
        "info_url_en": "https://www.routedesgrandesalpes.com/grands-cols//col-de-la-loze",
    },
    "Col de la Madeleine": {
        "status": "Monument",
        "status_en": "monument",
        "palmares": "Einer der großen Alpenklassiker der Tour de France und Dauphiné.",
        "palmares_en": "One of the great Alpine classics of the Tour de France and Dauphiné.",
        "segment_query": "Col de la Madeleine climb",
        "info_url": "https://www.routedesgrandesalpes.com/grands-cols/col-de-la-madeleine",
        "info_url_en": "https://en.routedesgrandesalpes.com/grands-cols/col-de-la-madeleine",
    },
    "Lacets de Montvernier": {
        "status": "Social-Highlight",
        "status_en": "social highlight",
        "palmares": "Ikonische Serpentinen, eher kurz, aber extrem fotogen und sehr segmenttauglich.",
        "palmares_en": "Iconic hairpins; short, but extremely photogenic and very segment-friendly.",
        "segment_query": "Lacets de Montvernier climb",
        "info_url": "https://www.maurienne-tourisme.com/visiter_bouger/boucle-des-lacets-de-montvernier-5588742/",
        "info_url_en": "https://www.cycling-french-alps.com/explore/lacets-de-montvernier-and-col-du-chaussy/",
    },
    "Col du Chaussy": {
        "status": "Maurienne-Klassiker",
        "status_en": "Maurienne classic",
        "palmares": "Ruhiger, harter Maurienne-Pass; oft mit den Lacets kombiniert.",
        "palmares_en": "Quiet, hard Maurienne pass; often combined with the Lacets.",
        "segment_query": "Col du Chaussy climb",
        "info_url": "https://www.velo-maurienne.com/explorer/lacets-de-montvernier-et-col-du-chaussy/",
        "info_url_en": "https://www.cycling-french-alps.com/explore/lacets-de-montvernier-and-col-du-chaussy/",
    },
    "Col du Télégraphe": {
        "status": "Galibier-Zubringer",
        "status_en": "Galibier gateway",
        "palmares": "Klassischer Auftakt zum Galibier; historischer Bestandteil vieler Tour-Etappen.",
        "palmares_en": "Classic gateway to Galibier and a historic part of many Tour stages.",
        "segment_query": "Col du Telegraphe climb",
        "info_url": "https://fr.wikipedia.org/wiki/Col_du_T%C3%A9l%C3%A9graphe",
        "info_url_en": "https://en.wikipedia.org/wiki/Col_du_T%C3%A9l%C3%A9graphe",
    },
    "Col du Galibier": {
        "status": "Monument",
        "status_en": "monument",
        "palmares": "Einer der berühmtesten Alpenpässe überhaupt; Tour-de-France-Mythos.",
        "palmares_en": "One of the most famous Alpine passes; pure Tour de France mythology.",
        "segment_query": "Col du Galibier climb",
        "info_url": "https://www.routedesgrandesalpes.com/grands-cols/col-du-galibier",
        "info_url_en": "https://en.routedesgrandesalpes.com/grands-cols/col-du-galibier",
    },
    "Col du Lautaret": {
        "status": "Hochalpen-Übergang",
        "status_en": "high-Alpine crossing",
        "palmares": "Wichtiger Übergang am Galibier-Fuß; oft Teil großer Alpenetappen.",
        "palmares_en": "Important crossing at the foot of Galibier; often part of major Alpine stages.",
        "segment_query": "Col du Lautaret climb",
        "info_url": "https://fr.wikipedia.org/wiki/Col_du_Lautaret",
        "info_url_en": "https://en.wikipedia.org/wiki/Col_du_Lautaret",
    },
    "Col du Granon": {
        "status": "brutaler Stich",
        "status_en": "brutal out-and-back",
        "palmares": "Steiler Abschlussanstieg über Briançon; starkes Finale für die Topgruppe.",
        "palmares_en": "Steep final climb above Briançon; a strong finale for the top group.",
        "segment_query": "Col du Granon climb",
        "info_url": "https://commons.wikimedia.org/wiki/Category:Col_du_Granon",
        "info_url_en": "https://commons.wikimedia.org/wiki/Category:Col_du_Granon",
    },
    "Col d'Izoard": {
        "status": "Tour-Monument",
        "status_en": "Tour monument",
        "palmares": "Ikonischer Tour-de-France-Pass im Queyras; von Briançon/Cervières als harte Nordrampe gefahren.",
        "palmares_en": "Iconic Tour de France pass in the Queyras; from Briançon/Cervières it is a hard north-side climb.",
        "segment_query": "Col d'Izoard Briancon climb",
        "info_url": "https://www.routedesgrandesalpes.com/grands-cols/col-izoard",
        "info_url_en": "https://en.routedesgrandesalpes.com/grands-cols/col-izoard",
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


def place_payload(name: str) -> dict | None:
    info = PLACE_INFO.get(name)
    if not info:
        return None
    payload = {
        "name": name,
        "summary": info["summary"],
        "summary_en": info.get("summary_en", info["summary"]),
        "url": info.get("url"),
        "url_en": info.get("url_en", info.get("url")),
    }
    if "image" in info:
        payload["image"] = info["image"]
    return payload


def route_tourism_items(route: dict, details: dict, limit: int = 5) -> list[dict]:
    items = []
    seen = set()
    candidate_names = [
        *details.get("photo_spots", []),
        *details.get("highlights", []),
        *route.get("waypoints", []),
    ]
    for name in candidate_names:
        if name in seen:
            continue
        payload = place_payload(name)
        if payload:
            items.append(payload)
            seen.add(name)
        if len(items) >= limit:
            break
    return items


def route_photo_items(route: dict, details: dict, limit: int = 3) -> list[dict]:
    items = []
    seen = set()
    candidate_names = [
        *details.get("photo_spots", []),
        *details.get("highlights", []),
        *route.get("waypoints", []),
    ]
    for name in candidate_names:
        if name in seen:
            continue
        payload = place_payload(name)
        if payload and payload.get("image"):
            items.append(payload)
            seen.add(name)
        if len(items) >= limit:
            break
    return items


def route_properties(route: dict, brouter_km: float | None, brouter_hm: int | None) -> dict:
    details = ROUTE_DETAILS[route["id"]]
    difficulty = details["difficulty"]
    start, finish = DAY_ENDPOINTS[route["day"]]
    day_label = f"{DAY_LABELS[route['day']]} - {start} nach {finish}"
    day_label_en = f"{DAY_LABELS_EN[route['day']]} - {start} to {finish}"
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
        "day_label_en": day_label_en,
        "base_day_label": DAY_LABELS[route["day"]],
        "base_day_label_en": DAY_LABELS_EN[route["day"]],
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
        "description_en": details.get("description_en", details["description"]),
        "highlights": details["highlights"],
        "photo_spots": details["photo_spots"],
        "photo_items": route_photo_items(route, details),
        "tourism_items": route_tourism_items(route, details),
        "passes": passes,
        "default": difficulty == "MEDIUM",
        "color": DAY_COLORS[route["day"]],
        "waypoints": route["waypoints"],
        "waypoint_coords": [
            {"name": name, "lat": POINTS[name][0], "lon": POINTS[name][1]}
            for name in route["waypoints"]
        ],
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


def supply_payload() -> list[dict]:
    payload = []
    for item in SUPPLY_POINTS:
        lat, lon = POINTS[item["point"]]
        payload.append({**item, "lat": lat, "lon": lon})
    return payload


def day_info_payload() -> dict:
    payload = {}
    supplies_by_day: dict[str, list[dict]] = {}
    for item in supply_payload():
        supplies_by_day.setdefault(item["day"], []).append(item)
    for day in DASHBOARD_ORDER:
        info = TRIP_DAYS.get(day) or TRAVEL_DAYS[day]
        weather_lat, weather_lon = POINTS[info["weather_point"]]
        if day in DAY_ENDPOINTS:
            start, finish = DAY_ENDPOINTS[day]
        else:
            start, finish = info["start"], info["finish"]
        payload[day] = {
            **info,
            "label": info.get("label", DAY_LABELS.get(day, day)),
            "tab": info.get("tab", f"E{day[1:]}"),
            "start": start,
            "finish": finish,
            "kind": "ride" if day.startswith("J") else "travel",
            "weather_lat": weather_lat,
            "weather_lon": weather_lon,
            "supplies": supplies_by_day.get(day, []),
        }
    return payload


def make_html(geojson: dict) -> str:
    route_json = json.dumps(geojson, ensure_ascii=False)
    markers_json = json.dumps(
        marker_payload(MAJOR_STOPS, "stop") + marker_payload(COLS, "col"), ensure_ascii=False
    )
    supply_json = json.dumps(supply_payload(), ensure_ascii=False)
    day_info_json = json.dumps(day_info_payload(), ensure_ascii=False)
    organizer_json = json.dumps(ORGANIZER_INFO, ensure_ascii=False)
    general_packing_json = json.dumps(GENERAL_PACKING_LIST, ensure_ascii=False)
    general_packing_en_json = json.dumps(GENERAL_PACKING_LIST_EN, ensure_ascii=False)
    day_packing_json = json.dumps(DAY_PACKING_LIST, ensure_ascii=False)
    day_packing_en_json = json.dumps(DAY_PACKING_LIST_EN, ensure_ascii=False)
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
    .brand-actions {{
      display: flex;
      align-items: center;
      gap: 8px;
      position: relative;
      z-index: 1;
    }}
    .language-toggle {{
      display: inline-grid;
      grid-template-columns: 1fr 1fr;
      border: 1px solid var(--white);
      background: var(--black);
    }}
    .language-toggle button {{
      min-height: 28px;
      border: 0;
      border-right: 1px solid var(--white);
      color: var(--white);
      background: var(--black);
      padding: 0 7px;
      font-size: 10px;
      font-weight: 700;
      line-height: 1;
    }}
    .language-toggle button:last-child {{
      border-right: 0;
    }}
    .language-toggle button.active {{
      background: var(--white);
      color: var(--black);
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
      right: 12px;
      bottom: 8px;
      width: 132px;
      height: 88px;
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
      stroke-width: 5.4;
      stroke-linecap: round;
      stroke-linejoin: round;
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
    .dashboard {{
      border-bottom: 2px solid var(--black);
      background: var(--white);
    }}
    .dashboard-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 12px 16px 8px;
      border-bottom: 1px solid var(--grey-300);
    }}
    .dashboard-head h2 {{
      margin: 0;
      font-family: "Bandeins Strange", Arial, sans-serif;
      font-size: 23px;
      line-height: 1;
      letter-spacing: 0;
    }}
    .dashboard-date {{
      border: 1px solid var(--black);
      padding: 4px 6px 3px;
      font-size: 10px;
      font-weight: 700;
      white-space: nowrap;
    }}
    .dashboard-tabs {{
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      border-bottom: 1px solid var(--black);
    }}
    .dashboard-tabs button {{
      min-height: 34px;
      padding: 0 4px;
      border-bottom: 0;
      font-size: 9px;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .dashboard-tabs button.active {{
      background: var(--black);
      color: var(--white);
    }}
    .dashboard-body {{
      padding: 12px 16px 14px;
    }}
    .dashboard-briefing {{
      margin: 0 0 10px;
      color: var(--grey-800);
      font-size: 12px;
      line-height: 1.4;
    }}
    .info-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      border: 1px solid var(--black);
      margin-bottom: 10px;
    }}
    .info-cell {{
      padding: 8px;
      border-right: 1px solid var(--black);
      border-bottom: 1px solid var(--black);
      min-width: 0;
    }}
    .info-cell:nth-child(2n) {{
      border-right: 0;
    }}
    .info-cell:nth-last-child(-n + 2) {{
      border-bottom: 0;
    }}
    .info-cell span,
    .weather-card span {{
      display: block;
      color: var(--grey-600);
      font-size: 9px;
      font-weight: 700;
      text-transform: uppercase;
      margin-bottom: 3px;
    }}
    .info-cell strong,
    .weather-card strong {{
      display: block;
      font-size: 12px;
      line-height: 1.25;
    }}
    .weather-card {{
      border: 1px solid var(--black);
      padding: 8px;
      margin-bottom: 10px;
    }}
    .weather-values {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin-top: 7px;
    }}
    .weather-values strong {{
      font-size: 14px;
    }}
    .dashboard-list {{
      margin: 0;
      padding: 0;
      list-style: none;
      border-top: 1px solid var(--grey-300);
    }}
    .dashboard-list li {{
      border-bottom: 1px solid var(--grey-300);
      padding: 6px 0;
      font-size: 12px;
      line-height: 1.35;
    }}
    .dashboard-list strong {{
      font-size: 12px;
    }}
    .pack-list {{
      display: grid;
      gap: 5px;
      margin-top: 6px;
    }}
    .organizer-panel,
    .packing-panel {{
      border-bottom: 2px solid var(--black);
      background: var(--white);
    }}
    .organizer-panel summary,
    .packing-panel summary {{
      cursor: pointer;
      list-style: none;
      padding: 11px 16px;
      border-bottom: 1px solid var(--black);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .organizer-panel summary::-webkit-details-marker,
    .packing-panel summary::-webkit-details-marker {{
      display: none;
    }}
    .organizer-panel summary::after,
    .packing-panel summary::after {{
      content: "+";
      float: right;
      font-size: 14px;
      line-height: 1;
    }}
    .organizer-panel[open] summary::after,
    .packing-panel[open] summary::after {{
      content: "-";
    }}
    .organizer-body,
    .packing-body {{
      display: grid;
      gap: 12px;
      padding: 12px 16px 14px;
    }}
    .organizer-card {{
      border: 1px solid var(--black);
      padding: 9px;
      background: var(--white);
    }}
    .organizer-card strong {{
      display: block;
      font-size: 13px;
      line-height: 1.15;
    }}
    .organizer-card p {{
      margin: 6px 0 0;
      color: var(--grey-800);
      font-size: 12px;
      line-height: 1.35;
    }}
    .organizer-card a {{
      color: var(--black);
      font-weight: 700;
      text-decoration: none;
    }}
    .organizer-card a:hover {{
      text-decoration: underline;
    }}
    .day-booking-grid {{
      display: grid;
      gap: 8px;
      margin-bottom: 10px;
    }}
    .contact-list {{
      margin: 0;
      padding: 0;
      list-style: none;
      border-top: 1px solid var(--grey-300);
    }}
    .contact-list li {{
      border-bottom: 1px solid var(--grey-300);
      padding: 7px 0;
      font-size: 12px;
      line-height: 1.35;
    }}
    .contact-list span {{
      display: block;
      color: var(--grey-600);
      font-size: 9px;
      font-weight: 700;
      text-transform: uppercase;
      margin-bottom: 2px;
    }}
    .rule-download {{
      display: inline-block;
      margin-top: 6px;
      color: var(--black);
      font-weight: 800;
      text-decoration: none;
    }}
    .rule-download:hover {{
      text-decoration: underline;
    }}
    .pack-item {{
      display: grid;
      grid-template-columns: 18px 1fr;
      gap: 6px;
      align-items: start;
      font-size: 12px;
      line-height: 1.25;
    }}
    .pack-item input {{
      margin: 1px 0 0;
      accent-color: var(--black);
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
      width: 28px;
      height: 19px;
      flex: 0 0 auto;
    }}
    .bike-icon svg {{
      stroke-width: 6.2;
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
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: flex-start;
      gap: 8px;
      margin: 0;
      padding: 11px 16px;
      font-weight: 700;
      font-size: 14px;
      min-height: 0;
      border: 0;
      border-bottom: 1px solid var(--black);
      text-transform: uppercase;
      text-align: left;
      background: var(--white);
      color: var(--black);
    }}
    .day-title:hover {{
      background: var(--black);
      color: var(--white);
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
      padding: 8px 6px 6px;
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
      height: 146px;
      overflow: visible;
      font-family: "Sen", Arial, sans-serif;
    }}
    .profile-axis {{
      fill: var(--grey-600);
      font-size: 8px;
      font-weight: 700;
    }}
    .profile-label {{
      fill: var(--black);
      font-size: 7px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .profile-label-muted {{
      fill: var(--grey-600);
      font-size: 6px;
      font-weight: 700;
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
    .pass-card-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}
    .segment-link:hover {{
      background: var(--black);
      color: var(--white);
    }}
    .photo-strip {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 8px;
      margin-top: 6px;
    }}
    .photo-card {{
      border: 1px solid var(--black);
      background: var(--grey-150);
      color: var(--black);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      text-decoration: none;
    }}
    .photo-card img {{
      width: 100%;
      aspect-ratio: 4 / 3;
      object-fit: cover;
      display: block;
      background: var(--grey-150);
      border-bottom: 1px solid var(--black);
    }}
    .photo-card-body {{
      padding: 7px;
    }}
    .photo-card span {{
      font-size: 9px;
      font-weight: 700;
      text-transform: uppercase;
      color: var(--grey-600);
    }}
    .photo-card strong {{
      display: block;
      font-size: 11px;
      line-height: 1.1;
      margin-top: 2px;
    }}
    .photo-card small {{
      display: block;
      margin-top: 5px;
      color: var(--grey-600);
      font-size: 9px;
      line-height: 1.25;
    }}
    .tourism-list {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 8px;
      margin-top: 6px;
    }}
    .tourism-card {{
      border: 1px solid var(--black);
      padding: 9px;
      background: var(--white);
    }}
    .tourism-card strong {{
      display: block;
      font-size: 13px;
      line-height: 1.15;
    }}
    .tourism-card p {{
      margin: 6px 0 8px;
      color: var(--grey-800);
      font-size: 12px;
      line-height: 1.35;
    }}
    .tourism-card a {{
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
    .tourism-card a:hover {{
      background: var(--black);
      color: var(--white);
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
      height: 230px;
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
    .map-marker.supply {{
      background: var(--white);
      border-color: var(--black);
      transform: rotate(45deg);
      position: relative;
    }}
    .map-marker.supply::after {{
      content: "";
      position: absolute;
      inset: 3px;
      background: var(--black);
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
          <div class="brand-actions">
            <span class="brand-tag" data-i18n="routeDesk">Route Desk</span>
            <div class="language-toggle" role="group" aria-label="Sprache wählen">
              <button type="button" data-lang="de" aria-pressed="true">DE</button>
              <button type="button" data-lang="en" aria-pressed="false">EN</button>
            </div>
          </div>
        </div>
        <h1 data-i18n="mainTitle">Rennrad-Etappen Französische Alpen</h1>
        <div class="ride-art" aria-hidden="true">{ROAD_BIKE_SVG}</div>
      </section>
      <div class="toolbar">
        <button id="fit" data-i18n="fitRoute">Auf Route zoomen</button>
        <a class="button-link" href="alpen_etappen_gpx.zip" download>
          <svg aria-hidden="true" viewBox="0 0 24 24">
            <path d="M12 3v10m0 0 4-4m-4 4-4-4M5 17v3h14v-3"></path>
          </svg>
          <span data-i18n="allGpx">Alle GPX</span>
        </a>
      </div>
      <section class="dashboard" aria-label="Tagesdashboard">
        <div class="dashboard-head">
          <h2 data-i18n="dashboard">Tagesdashboard</h2>
          <span class="dashboard-date" id="dashboard-date">-</span>
        </div>
        <div class="dashboard-tabs" id="dashboard-tabs"></div>
        <div class="dashboard-body" id="dashboard-body"></div>
      </section>
      <details class="organizer-panel" open>
        <summary data-i18n="organizerPanel">Veranstalter & Notfall</summary>
        <div class="organizer-body" id="organizer-body"></div>
      </details>
      <details class="packing-panel">
        <summary data-i18n="packing">Packlisten</summary>
        <div class="packing-body" id="packing-body"></div>
      </details>
      <section class="filters" aria-label="Routenfilter">
        <div class="filters-title">
          <span class="bike-icon" aria-hidden="true">{ROAD_BIKE_SVG}</span>
          <span data-i18n="variantFilter">Variantenfilter</span>
        </div>
        <div class="filter-grid">
          <button id="preset-light" type="button" data-preset="LIGHT" aria-pressed="false"><span class="preset-name">LIGHT</span><span class="preset-total"></span></button>
          <button id="preset-medium" type="button" data-preset="MEDIUM" aria-pressed="true"><span class="preset-name">MEDIUM</span><span class="preset-total"></span></button>
          <button id="preset-strong" type="button" data-preset="STRONG" aria-pressed="false"><span class="preset-name">STRONG</span><span class="preset-total"></span></button>
        </div>
        <div class="current-total"><span data-i18n="currentSelection">Aktuelle Auswahl</span><strong id="current-total">-</strong></div>
      </section>
      <div id="layers"></div>
    </aside>
    <main id="map"></main>
  </div>
  <div class="modal-backdrop" id="route-modal" hidden>
    <article class="route-modal" role="dialog" aria-modal="true" aria-labelledby="route-modal-title">
      <header class="modal-head">
        <div class="modal-title" id="route-modal-title">Details</div>
        <button class="modal-close" id="route-modal-close" type="button" aria-label="Details schließen" data-i18n-aria="closeDetails">×</button>
      </header>
      <section class="modal-body" id="route-modal-body"></section>
    </article>
  </div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const routeData = {route_json};
    const markerData = {markers_json};
    const supplyData = {supply_json};
    const dayInfo = {day_info_json};
    const organizerInfo = {organizer_json};
    const generalPackingList = {general_packing_json};
    const generalPackingListEn = {general_packing_en_json};
    const dayPackingList = {day_packing_json};
    const dayPackingListEn = {day_packing_en_json};
    const dayColors = {json.dumps(DAY_COLORS)};
    const weatherCache = new Map();
    let activeDashboardDay = "ARRIVAL";
    let activeModalRouteId = null;
    let currentLang = localStorage.getItem("xx-alps-lang") || "de";

    const i18n = {{
      de: {{
        routeDesk: "Route Desk",
        mainTitle: "Rennrad-Etappen Französische Alpen",
        fitRoute: "Auf Route zoomen",
        allGpx: "Alle GPX",
        dashboard: "Tagesdashboard",
        organizerPanel: "Veranstalter & Notfall",
        bookingInfo: "Buchung",
        contacts: "Kontakte",
        tripRules: "Wichtig",
        office: "Büro",
        emergency: "Notfall",
        phone: "Telefon",
        accommodation: "Unterkunft",
        dinner: "Abendessen",
        transfer: "Transfer",
        packing: "Packlisten",
        variantFilter: "Variantenfilter",
        currentSelection: "Aktuelle Auswahl",
        closeDetails: "Details schließen",
        noProfile: "Keine Profildaten",
        routeProfile: "Streckenprofil",
        distance: "Distanz",
        elevation: "Höhenmeter",
        highlights: "Highlights",
        passes: "Pässe & Segmente",
        strava: "Strava Segmente suchen",
        info: "Info öffnen",
        tourism: "Touristische Infos",
        photoSpots: "Fotospots",
        photoSpot: "Fotospot",
        imageSource: "Bildquelle",
        gpx: "GPX",
        details: "Details",
        unavailable: "offen",
        start: "Start",
        finish: "Ziel",
        luggage: "Gepäck",
        support: "Support",
        hotelCheckin: "Hotel & Check-in",
        supplies: "Verpflegung & Wasser",
        weather: "Wetter",
        weatherLoading: "Wetter wird geladen...",
        weatherOutside: "Forecast ab ca. 16 Tage vorher verfügbar",
        weatherError: "Wetter konnte nicht geladen werden",
        temperature: "Temperatur",
        rain: "Regen",
        gusts: "Böen",
        tripPacking: "Für den Trip",
        dayPacking: "Tagesfahrt",
        meters: "m",
        km: "km",
        hm: "hm",
        weatherCodes: {{
          0: "klar", 1: "leicht bewölkt", 2: "bewölkt", 3: "bedeckt",
          45: "Nebel", 48: "Nebel", 51: "Niesel", 53: "Niesel", 55: "Niesel",
          61: "Regen", 63: "Regen", 65: "starker Regen", 71: "Schnee",
          73: "Schnee", 75: "starker Schnee", 80: "Schauer", 81: "Schauer",
          82: "starke Schauer", 95: "Gewitter", 96: "Gewitter", 99: "Gewitter"
        }}
      }},
      en: {{
        routeDesk: "Route Desk",
        mainTitle: "French Alps Road Stages",
        fitRoute: "Zoom to route",
        allGpx: "All GPX",
        dashboard: "Day Dashboard",
        organizerPanel: "Operator & Emergency",
        bookingInfo: "Booking",
        contacts: "Contacts",
        tripRules: "Important",
        office: "Office",
        emergency: "Emergency",
        phone: "Phone",
        accommodation: "Accommodation",
        dinner: "Dinner",
        transfer: "Transfer",
        packing: "Packing Lists",
        variantFilter: "Variant Filter",
        currentSelection: "Current selection",
        closeDetails: "Close details",
        noProfile: "No profile data",
        routeProfile: "Elevation profile",
        distance: "Distance",
        elevation: "Elevation gain",
        highlights: "Highlights",
        passes: "Passes & Segments",
        strava: "Search Strava segments",
        info: "Open info",
        tourism: "Tourist Info",
        photoSpots: "Photo Spots",
        photoSpot: "Photo spot",
        imageSource: "Image source",
        gpx: "GPX",
        details: "Details",
        unavailable: "open",
        start: "Start",
        finish: "Finish",
        luggage: "Luggage",
        support: "Support",
        hotelCheckin: "Hotel & Check-in",
        supplies: "Food & Water",
        weather: "Weather",
        weatherLoading: "Loading weather...",
        weatherOutside: "Forecast available approx. 16 days before",
        weatherError: "Weather could not be loaded",
        temperature: "Temperature",
        rain: "Rain",
        gusts: "Gusts",
        tripPacking: "Whole trip",
        dayPacking: "Day ride",
        meters: "m",
        km: "km",
        hm: "m",
        weatherCodes: {{
          0: "clear", 1: "mainly clear", 2: "cloudy", 3: "overcast",
          45: "fog", 48: "fog", 51: "drizzle", 53: "drizzle", 55: "drizzle",
          61: "rain", 63: "rain", 65: "heavy rain", 71: "snow",
          73: "snow", 75: "heavy snow", 80: "showers", 81: "showers",
          82: "heavy showers", 95: "thunderstorm", 96: "thunderstorm", 99: "thunderstorm"
        }}
      }}
    }};

    function t(key) {{
      return i18n[currentLang]?.[key] ?? i18n.de[key] ?? key;
    }}

    function locale() {{
      return currentLang === "en" ? "en-GB" : "de-DE";
    }}

    function localizedField(object, field) {{
      if (currentLang === "en" && object?.[`${{field}}_en`]) return object[`${{field}}_en`];
      return object?.[field];
    }}

    function localizedUrl(object) {{
      if (currentLang === "en" && object?.url_en) return object.url_en;
      return object?.url;
    }}

    function passInfoUrl(pass) {{
      if (currentLang === "en" && pass?.info_url_en) return pass.info_url_en;
      return pass?.info_url;
    }}

    function dayLabel(props) {{
      return currentLang === "en" ? (props.day_label_en || props.day_label) : props.day_label;
    }}

    function routeDescription(props) {{
      return currentLang === "en" ? (props.description_en || props.description) : props.description;
    }}

    function routeTitle(props) {{
      return currentLang === "en" ? (props.title_en || props.title) : props.title;
    }}

    function translateStaticUi() {{
      document.documentElement.lang = currentLang;
      for (const element of document.querySelectorAll("[data-i18n]")) {{
        element.textContent = t(element.dataset.i18n);
      }}
      for (const element of document.querySelectorAll("[data-i18n-aria]")) {{
        element.setAttribute("aria-label", t(element.dataset.i18nAria));
      }}
      for (const button of document.querySelectorAll(".language-toggle button[data-lang]")) {{
        const active = button.dataset.lang === currentLang;
        button.classList.toggle("active", active);
        button.setAttribute("aria-pressed", String(active));
      }}
    }}

    const map = L.map("map", {{ preferCanvas: true }}).setView([45.55, 6.42], 9);
    L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);

    const layers = new Map();
    const allBounds = L.latLngBounds([]);
    const selectedByDay = new Map();

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
        onEachFeature: (_, routeLayer) => routeLayer.on("click", event => {{
          L.DomEvent.stopPropagation(event);
          showRouteDetail(props.id);
        }})
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
    function supplyPopupHtml(marker) {{
      return `<div class="popup-title">${{htmlEscape(marker.name)}} · ${{t("supplies")}}</div><div class="popup-meta">${{htmlEscape(localizedField(marker, "kind"))}}<br>${{htmlEscape(localizedField(marker, "note"))}}</div>`;
    }}
    for (const marker of supplyData) {{
      const icon = L.divIcon({{
        className: "",
        html: `<span class="map-marker supply"></span>`,
        iconSize: [13, 13],
        iconAnchor: [6, 6]
      }});
      L.marker([marker.lat, marker.lon], {{ icon }})
        .bindTooltip(`${{marker.name}} · ${{localizedField(marker, "kind")}}`, {{ direction: "top", offset: [0, -4] }})
        .bindPopup(() => supplyPopupHtml(marker))
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
      return `${{km.toLocaleString(locale(), {{ maximumFractionDigits: 1, minimumFractionDigits: 1 }})}} ${{t("km")}} / ${{Math.round(hm).toLocaleString(locale())}} ${{t("hm")}}`;
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
        return {{ distance, elevation: coord[2], lon: coord[0], lat: coord[1] }};
      }});
      const elevations = points.map(point => point.elevation);
      return {{
        points,
        distance,
        min: Math.round(Math.min(...elevations)),
        max: Math.round(Math.max(...elevations))
      }};
    }}

    const profileTownNames = new Set([
      "Megève",
      "Le Grand-Bornand",
      "La Clusaz",
      "Hauteluce",
      "Beaufort",
      "Bourg-Saint-Maurice",
      "Moûtiers",
      "Saint-Jean-de-Maurienne",
      "Valloire",
      "Briançon"
    ]);

    function nearestProfilePoint(stats, waypoint) {{
      let best = null;
      let bestDistance = Infinity;
      for (const point of stats.points) {{
        const d = haversineKm([point.lon, point.lat], [waypoint.lon, waypoint.lat]);
        if (d < bestDistance) {{
          best = point;
          bestDistance = d;
        }}
      }}
      return best;
    }}

    function profileLandmarks(feature, stats) {{
      const props = feature.properties;
      const passNames = new Set((props.passes || []).map(pass => pass.name));
      const raw = [];
      for (const waypoint of props.waypoint_coords || []) {{
        let kind = null;
        if (passNames.has(waypoint.name)) kind = "col";
        else if (waypoint.name === props.start || waypoint.name === props.finish) kind = "town";
        else if (profileTownNames.has(waypoint.name)) kind = "town";
        if (!kind) continue;
        const nearest = nearestProfilePoint(stats, waypoint);
        if (nearest) raw.push({{ ...nearest, name: waypoint.name, kind }});
      }}
      raw.sort((a, b) => a.distance - b.distance);
      const filtered = [];
      const minGap = Math.max(1.4, stats.distance * 0.025);
      for (const item of raw) {{
        const tooClose = filtered.some(existing => Math.abs(existing.distance - item.distance) < minGap);
        if (!tooClose || item.kind === "col") filtered.push(item);
      }}
      return filtered.slice(0, 8);
    }}

    function profileSvg(feature) {{
      const stats = elevationStats(feature);
      if (!stats) return `<div class="profile-wrap">${{t("noProfile")}}</div>`;
      const width = 720;
      const height = 260;
      const plotLeft = 42;
      const plotRight = 8;
      const plotTop = 26;
      const plotBottom = 34;
      const range = Math.max(1, stats.max - stats.min);
      const step = Math.max(1, Math.floor(stats.points.length / 180));
      const sampled = stats.points.filter((_, index) => index % step === 0);
      if (sampled[sampled.length - 1] !== stats.points[stats.points.length - 1]) {{
        sampled.push(stats.points[stats.points.length - 1]);
      }}
      const scaleX = distance => plotLeft + (distance / Math.max(1, stats.distance)) * (width - plotLeft - plotRight);
      const scaleY = elevation => height - plotBottom - ((elevation - stats.min) / range) * (height - plotTop - plotBottom);
      const xy = point => {{
        const x = scaleX(point.distance);
        const y = scaleY(point.elevation);
        return `${{x.toFixed(1)}},${{y.toFixed(1)}}`;
      }};
      const line = sampled.map(xy).join(" ");
      const baseY = height - plotBottom;
      const area = `${{plotLeft}},${{baseY}} ${{line}} ${{width - plotRight}},${{baseY}}`;
      const ticks = [stats.min, Math.round((stats.min + stats.max) / 2), stats.max];
      const grid = ticks.map(value => {{
        const y = scaleY(value);
        return `<line x1="${{plotLeft}}" y1="${{y.toFixed(1)}}" x2="${{width - plotRight}}" y2="${{y.toFixed(1)}}" stroke="#d6d6d6" stroke-width="1"></line>
          <text class="profile-axis" x="${{plotLeft - 6}}" y="${{(y + 3).toFixed(1)}}" text-anchor="end">${{Math.round(value)}} ${{t("meters")}}</text>`;
      }}).join("");
      const landmarks = profileLandmarks(feature, stats).map((landmark, index) => {{
        const x = scaleX(landmark.distance);
        const y = scaleY(landmark.elevation);
        const isCol = landmark.kind === "col";
        const label = isCol ? `${{landmark.name}} · ${{Math.round(landmark.elevation)}} ${{t("meters")}}` : landmark.name;
        const labelY = isCol ? 11 + (index % 2) * 12 : height - 10 - (index % 2) * 10;
        const anchor = x > width - 120 ? "end" : x < plotLeft + 60 ? "start" : "middle";
        const textX = anchor === "end" ? x - 3 : anchor === "start" ? x + 3 : x;
        return `<g>
          <line x1="${{x.toFixed(1)}}" y1="${{plotTop}}" x2="${{x.toFixed(1)}}" y2="${{baseY}}" stroke="${{isCol ? "#000000" : "#999999"}}" stroke-width="${{isCol ? 1.2 : 0.8}}" stroke-dasharray="${{isCol ? "0" : "3 3"}}"></line>
          <circle cx="${{x.toFixed(1)}}" cy="${{y.toFixed(1)}}" r="${{isCol ? 4 : 2.8}}" fill="#ffffff" stroke="#000000" stroke-width="${{isCol ? 2 : 1.2}}"></circle>
          <text class="${{isCol ? "profile-label" : "profile-label-muted"}}" x="${{textX.toFixed(1)}}" y="${{labelY}}" text-anchor="${{anchor}}">${{htmlEscape(label)}}</text>
        </g>`;
      }}).join("");
      return `<div class="profile-wrap">
        <div class="profile-title"><span>${{t("routeProfile")}}</span><span>${{stats.min}}-${{stats.max}} ${{t("meters")}}</span></div>
        <svg class="profile-svg" viewBox="0 0 ${{width}} ${{height}}" role="img" aria-label="${{t("routeProfile")}}">
          ${{grid}}
          <polygon points="${{area}}" fill="#eeeeee"></polygon>
          <polyline points="${{line}}" fill="none" stroke="#000000" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"></polyline>
          <line x1="${{plotLeft}}" y1="${{baseY}}" x2="${{width - plotRight}}" y2="${{baseY}}" stroke="#000000" stroke-width="1.2"></line>
          <text class="profile-axis" x="${{plotLeft}}" y="${{height - 8}}" text-anchor="start">0 ${{t("km")}}</text>
          <text class="profile-axis" x="${{width - plotRight}}" y="${{height - 8}}" text-anchor="end">${{stats.distance.toFixed(0)}} ${{t("km")}}</text>
          ${{landmarks}}
        </svg>
      </div>`;
    }}

    function miniProfileSvg(feature) {{
      const stats = elevationStats(feature);
      if (!stats) return "";
      const width = 300;
      const height = 44;
      const padX = 1;
      const padY = 3;
      const range = Math.max(1, stats.max - stats.min);
      const step = Math.max(1, Math.floor(stats.points.length / 82));
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
      if (value === null || value === undefined) return t("unavailable");
      const number = Number(value);
      const formatted = Number.isInteger(number)
        ? number.toLocaleString(locale())
        : number.toLocaleString(locale(), {{ maximumFractionDigits: 1 }});
      return `${{formatted}} ${{suffix}}`;
    }}

    function stravaSegmentUrl(query) {{
      return `https://www.strava.com/segments/search?keywords=${{encodeURIComponent(query)}}`;
    }}

    function passCardsHtml(passes) {{
      if (!passes || !passes.length) return "";
      return `<div class="detail-block-title">${{t("passes")}}</div>
        <div class="pass-list">
          ${{passes.map(pass => `<article class="pass-card">
            <strong>${{htmlEscape(pass.name)}}</strong>
            <span>${{htmlEscape(localizedField(pass, "status"))}}</span>
            <p>${{htmlEscape(localizedField(pass, "palmares"))}}</p>
            <div class="pass-card-actions">
              <a class="segment-link" href="${{htmlEscape(stravaSegmentUrl(pass.segment_query))}}" target="_blank" rel="noopener">${{t("strava")}}</a>
              ${{passInfoUrl(pass) ? `<a class="segment-link" href="${{htmlEscape(passInfoUrl(pass))}}" target="_blank" rel="noopener">${{t("info")}}</a>` : ""}}
            </div>
          </article>`).join("")}}
        </div>`;
    }}

    function photoCardsHtml(items) {{
      if (!items || !items.length) return "";
      return `<div class="detail-block-title">${{t("photoSpots")}}</div>
        <div class="photo-strip">
          ${{items.map(item => {{
            const image = item.image || {{}};
            return `<a class="photo-card" href="${{htmlEscape(image.source_url || localizedUrl(item) || "#")}}" target="_blank" rel="noopener">
              <img src="${{htmlEscape(image.url || "")}}" alt="${{htmlEscape(item.name)}}" loading="lazy">
              <div class="photo-card-body">
                <span>${{t("photoSpot")}}</span>
                <strong>${{htmlEscape(item.name)}}</strong>
                <small>${{t("imageSource")}}: ${{htmlEscape(image.credit || "Wikimedia Commons")}} · ${{htmlEscape(image.license || "")}}</small>
              </div>
            </a>`;
          }}).join("")}}
        </div>`;
    }}

    function tourismCardsHtml(items) {{
      if (!items || !items.length) return "";
      return `<div class="detail-block-title">${{t("tourism")}}</div>
        <div class="tourism-list">
          ${{items.map(item => `<article class="tourism-card">
            <strong>${{htmlEscape(item.name)}}</strong>
            <p>${{htmlEscape(localizedField(item, "summary"))}}</p>
            ${{localizedUrl(item) ? `<a href="${{htmlEscape(localizedUrl(item))}}" target="_blank" rel="noopener">${{t("info")}}</a>` : ""}}
          </article>`).join("")}}
        </div>`;
    }}

    function formatTripDate(value) {{
      return new Date(`${{value}}T12:00:00`).toLocaleDateString(locale(), {{
        weekday: "short",
        day: "2-digit",
        month: "2-digit"
      }});
    }}

    function weatherCodeText(code) {{
      return i18n[currentLang]?.weatherCodes?.[code] || t("weather");
    }}

    function weatherUrl(info) {{
      const params = new URLSearchParams();
      params.set("latitude", info.weather_lat);
      params.set("longitude", info.weather_lon);
      params.set("daily", "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,wind_gusts_10m_max");
      params.set("timezone", "Europe/Paris");
      params.set("forecast_days", "16");
      return "https://api.open-meteo.com/v1/forecast?" + params.toString();
    }}

    async function weatherForDay(day) {{
      if (weatherCache.has(day)) return weatherCache.get(day);
      const info = dayInfo[day];
      const promise = fetch(weatherUrl(info))
        .then(response => {{
          if (!response.ok) throw new Error("weather request failed");
          return response.json();
        }})
        .then(data => {{
          const index = data.daily?.time?.indexOf(info.date);
          if (index === undefined || index < 0) {{
            return {{ status: "outside", source: info.weather_point }};
          }}
          return {{
            status: "ok",
            source: info.weather_point,
            code: data.daily.weather_code[index],
            tempMax: data.daily.temperature_2m_max[index],
            tempMin: data.daily.temperature_2m_min[index],
            rainProbability: data.daily.precipitation_probability_max[index],
            rain: data.daily.precipitation_sum[index],
            gusts: data.daily.wind_gusts_10m_max[index]
          }};
        }})
        .catch(() => ({{ status: "error", source: info.weather_point }}));
      weatherCache.set(day, promise);
      return promise;
    }}

    function weatherHtml(result, info) {{
      if (!result) {{
        return `<span>${{t("weather")}}</span><strong>${{t("weatherLoading")}}</strong>`;
      }}
      if (result.status === "outside") {{
        return `<span>${{t("weather")}} · ${{htmlEscape(info.weather_point)}}</span><strong>${{t("weatherOutside")}}</strong>`;
      }}
      if (result.status === "error") {{
        return `<span>${{t("weather")}} · ${{htmlEscape(info.weather_point)}}</span><strong>${{t("weatherError")}}</strong>`;
      }}
      return `<span>${{t("weather")}} · ${{htmlEscape(info.weather_point)}} · Open-Meteo</span>
        <strong>${{htmlEscape(weatherCodeText(result.code))}}</strong>
        <div class="weather-values">
          <div><span>${{t("temperature")}}</span><strong>${{Math.round(result.tempMin)}}-${{Math.round(result.tempMax)}} °C</strong></div>
          <div><span>${{t("rain")}}</span><strong>${{Math.round(result.rainProbability || 0)}}% · ${{Number(result.rain || 0).toFixed(1)}} mm</strong></div>
          <div><span>${{t("gusts")}}</span><strong>${{Math.round(result.gusts || 0)}} km/h</strong></div>
        </div>`;
    }}

    function packingKey(scope, index) {{
      return `xx-alps-pack-${{scope}}-${{index}}`;
    }}

    function checklistHtml(title, items, scope) {{
      return `<section>
        <div class="detail-block-title">${{htmlEscape(title)}}</div>
        <div class="pack-list">
          ${{items.map((item, index) => {{
            const checked = localStorage.getItem(packingKey(scope, index)) === "1" ? " checked" : "";
            return `<label class="pack-item"><input type="checkbox" data-pack-scope="${{htmlEscape(scope)}}" data-pack-index="${{index}}"${{checked}}><span>${{htmlEscape(item)}}</span></label>`;
          }}).join("")}}
        </div>
      </section>`;
    }}

    function renderPackingPanel() {{
      const panel = document.getElementById("packing-body");
      if (!panel) return;
      const tripItems = currentLang === "en" ? generalPackingListEn : generalPackingList;
      const rideItems = currentLang === "en" ? dayPackingListEn : dayPackingList;
      panel.innerHTML = [
        checklistHtml(t("tripPacking"), tripItems, "trip"),
        checklistHtml(t("dayPacking"), rideItems, "day")
      ].join("");
      attachPackingHandlers(panel);
    }}

    function suppliesHtml(info) {{
      if (!info.supplies?.length) return "";
      return `<div class="detail-block-title">${{t("supplies")}}</div>
        <ul class="dashboard-list">
          ${{info.supplies.map(item => `<li><strong>${{htmlEscape(item.name)}}</strong> · ${{htmlEscape(localizedField(item, "kind"))}}<br>${{htmlEscape(localizedField(item, "note"))}}</li>`).join("")}}
        </ul>`;
    }}

    function telHref(phone) {{
      return `tel:${{String(phone || "").replace(/[^+0-9]/g, "")}}`;
    }}

    function phoneLink(phone) {{
      if (!phone) return "";
      return `<a href="${{htmlEscape(telHref(phone))}}">${{htmlEscape(phone)}}</a>`;
    }}

    function bookingCardHtml(title, item) {{
      if (!item) return "";
      const rows = [
        item.address ? htmlEscape(item.address) : "",
        item.phone ? `${{t("phone")}}: ${{phoneLink(item.phone)}}` : "",
        item.time ? `${{htmlEscape(item.time)}}` : "",
        localizedField(item, "service") ? htmlEscape(localizedField(item, "service")) : "",
        localizedField(item, "note") ? htmlEscape(localizedField(item, "note")) : "",
        item.emergency ? `${{t("emergency")}}: ${{phoneLink(item.emergency)}}` : ""
      ].filter(Boolean);
      return `<article class="organizer-card">
        <strong>${{htmlEscape(title)}} · ${{htmlEscape(item.name)}}</strong>
        <p>${{rows.join("<br>")}}</p>
      </article>`;
    }}

    function dayBookingHtml(info) {{
      const cards = [
        bookingCardHtml(t("accommodation"), info.accommodation),
        bookingCardHtml(t("dinner"), info.dinner),
        bookingCardHtml(t("transfer"), info.transfer)
      ].filter(Boolean);
      if (!cards.length) return "";
      return `<div class="day-booking-grid">${{cards.join("")}}</div>`;
    }}

    function renderOrganizerPanel() {{
      const panel = document.getElementById("organizer-body");
      if (!panel) return;
      const booking = organizerInfo.booking;
      const ruleHtml = (rule) => {{
        const download = rule.download
          ? `<br><a class="rule-download" href="${{htmlEscape(rule.download)}}" download>${{htmlEscape(localizedField(rule, "download_label"))}}</a>`
          : "";
        return `<li>
          <span>${{htmlEscape(localizedField(rule, "title"))}}</span>
          ${{htmlEscape(localizedField(rule, "text"))}}${{download}}
        </li>`;
      }};
      panel.innerHTML = `<article class="organizer-card">
          <strong>${{t("bookingInfo")}} · ${{htmlEscape(booking.code)}}</strong>
          <p>${{htmlEscape(booking.trip)}}<br>${{htmlEscape(booking.dates)}}<br>${{htmlEscape(localizedField(booking, "service"))}}<br>${{htmlEscape(localizedField(booking, "address"))}}<br>${{t("office")}}: ${{phoneLink(booking.office_phone)}}<br>${{t("emergency")}}: ${{phoneLink(booking.emergency_phone)}}</p>
        </article>
        <section>
          <div class="detail-block-title">${{t("contacts")}}</div>
          <ul class="contact-list">
            ${{organizerInfo.contacts.map(contact => `<li>
              <span>${{htmlEscape(localizedField(contact, "role"))}}</span>
              <strong>${{htmlEscape(contact.name)}}</strong><br>
              ${{phoneLink(contact.phone)}}
              ${{localizedField(contact, "note") ? `<br>${{htmlEscape(localizedField(contact, "note"))}}` : ""}}
            </li>`).join("")}}
          </ul>
        </section>
        <section>
          <div class="detail-block-title">${{t("tripRules")}}</div>
          <ul class="contact-list">
            ${{organizerInfo.rules.map(ruleHtml).join("")}}
          </ul>
        </section>`;
    }}

    function attachPackingHandlers(container) {{
      for (const checkbox of container.querySelectorAll("input[data-pack-index]")) {{
        checkbox.addEventListener("change", () => {{
          localStorage.setItem(packingKey(checkbox.dataset.packScope, checkbox.dataset.packIndex), checkbox.checked ? "1" : "0");
        }});
      }}
    }}

    function renderDashboardTabs() {{
      const tabs = document.getElementById("dashboard-tabs");
      tabs.innerHTML = Object.entries(dayInfo).map(([day, info]) => (
        `<button type="button" data-dashboard-day="${{day}}">${{htmlEscape(localizedField(info, "tab"))}}</button>`
      )).join("");
      tabs.onclick = event => {{
        const button = event.target.closest("button[data-dashboard-day]");
        if (button) renderDashboard(button.dataset.dashboardDay);
      }};
    }}

    async function renderDashboard(day) {{
      activeDashboardDay = day;
      const info = dayInfo[day];
      const body = document.getElementById("dashboard-body");
      const date = document.getElementById("dashboard-date");
      if (!info || !body || !date) return;
      for (const button of document.querySelectorAll("button[data-dashboard-day]")) {{
        button.classList.toggle("active", button.dataset.dashboardDay === day);
      }}
      date.textContent = formatTripDate(info.date);
      body.innerHTML = `<p class="dashboard-briefing">${{htmlEscape(localizedField(info, "briefing"))}}</p>
        <div class="info-grid">
          <div class="info-cell"><span>${{t("start")}}</span><strong>${{htmlEscape(localizedField(info, "start_hotel"))}}</strong></div>
          <div class="info-cell"><span>${{t("finish")}}</span><strong>${{htmlEscape(localizedField(info, "finish_hotel"))}}</strong></div>
          <div class="info-cell"><span>${{t("luggage")}}</span><strong>${{htmlEscape(localizedField(info, "luggage"))}}</strong></div>
          <div class="info-cell"><span>${{t("support")}}</span><strong>${{htmlEscape(localizedField(info, "support"))}}</strong></div>
        </div>
        <div class="weather-card" id="weather-card">${{weatherHtml(null, info)}}</div>
        ${{dayBookingHtml(info)}}
        ${{suppliesHtml(info)}}
        <div class="detail-block-title">${{t("hotelCheckin")}}</div>
        <ul class="dashboard-list">
          <li>${{htmlEscape(localizedField(info, "checkin"))}}</li>
        </ul>`;
      const weatherCard = document.getElementById("weather-card");
      const result = await weatherForDay(day);
      if (weatherCard && activeDashboardDay === day) {{
        weatherCard.innerHTML = weatherHtml(result, info);
      }}
    }}

    function showRouteDetail(id) {{
      const feature = featureById(id);
      if (!feature) return;
      const props = feature.properties;
      activeModalRouteId = id;
      const modal = document.getElementById("route-modal");
      const panel = document.getElementById("route-modal-body");
      const modalTitle = document.getElementById("route-modal-title");
      const metrics = [
        [t("distance"), metricValue(props.brouter_km, t("km"))],
        [t("elevation"), metricValue(props.brouter_hm, t("hm"))]
      ];
      modal.hidden = false;
      if (modalTitle) modalTitle.textContent = `${{dayLabel(props)}} · ${{props.difficulty}}`;
      panel.innerHTML = `<div class="detail-head">
          <div class="detail-kicker">
            <span>${{htmlEscape(dayLabel(props))}}</span>
            <span class="${{difficultyClass(props.difficulty)}}">${{props.difficulty}}</span>
          </div>
          <h2>${{htmlEscape(routeTitle(props))}}</h2>
        </div>
        <div class="detail-body">
          <p class="detail-description">${{htmlEscape(routeDescription(props))}}</p>
          <div class="metrics">
            ${{metrics.map(([label, value]) => `<div class="metric"><span>${{htmlEscape(label)}}</span><strong>${{htmlEscape(value)}}</strong></div>`).join("")}}
          </div>
          ${{profileSvg(feature)}}
          <div class="detail-block-title">${{t("highlights")}}</div>
          <ul class="highlight-list">
            ${{props.highlights.map(item => `<li>${{htmlEscape(item)}}</li>`).join("")}}
          </ul>
          ${{passCardsHtml(props.passes)}}
          ${{tourismCardsHtml(props.tourism_items)}}
          ${{photoCardsHtml(props.photo_items)}}
          <div class="detail-actions">
            <a class="button-link" href="${{htmlEscape(props.gpx_file || '#')}}" download>${{t("gpx")}}</a>
          </div>
        </div>`;
      const closeButton = document.getElementById("route-modal-close");
      if (closeButton) closeButton.focus();
    }}

    function closeRouteDetail() {{
      const modal = document.getElementById("route-modal");
      if (!modal) return;
      modal.hidden = true;
      activeModalRouteId = null;
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
        const sectionDayLabel = features[0] ? dayLabel(features[0].properties) : day;
        section.innerHTML = `<button class="day-title" type="button" data-day="${{htmlEscape(day)}}"><span class="swatch" style="background:${{dayColors[day]}}"></span>${{htmlEscape(sectionDayLabel)}}</button>`;
        for (const feature of features) {{
          const props = feature.properties;
          const meta = `${{props.brouter_km}} ${{t("km")}} / ${{props.brouter_hm}} ${{t("hm")}}`;
          const label = document.createElement("label");
          label.className = "route";
          label.innerHTML = `<input type="radio" name="route-${{htmlEscape(props.day)}}" data-route-id="${{props.id}}">
            <span>
              <strong><span class="${{difficultyClass(props.difficulty)}}">${{props.difficulty}}</span>${{htmlEscape(routeTitle(props))}}</strong>
              <span class="meta">${{htmlEscape(meta)}}</span>
              ${{miniProfileSvg(feature)}}
              <span class="route-actions" onclick="event.stopPropagation()">
                <a href="${{htmlEscape(props.gpx_file || '#')}}" download>${{t("gpx")}}</a>
                <button type="button" class="route-detail-button" data-route-id="${{htmlEscape(props.id)}}">${{t("details")}}</button>
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
      container.onchange = event => {{
        const target = event.target;
        if (target.matches("input[data-route-id]")) {{
          selectRoute(target.dataset.routeId);
        }}
      }};
      container.onclick = event => {{
        const target = event.target.closest("button[data-day]");
        if (target) renderDashboard(target.dataset.day);
      }};
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

    function refreshLocalizedView() {{
      translateStaticUi();
      renderDashboardTabs();
      renderDashboard(activeDashboardDay);
      renderOrganizerPanel();
      renderPackingPanel();
      renderControls();
      for (const id of selectedByDay.values()) {{
        setRouteVisibility(id, true);
      }}
      updatePresetTotals();
      updateCurrentTotal();
      updateActivePresetFromSelection();
      if (activeModalRouteId) showRouteDetail(activeModalRouteId);
    }}

    function setLanguage(lang) {{
      currentLang = lang === "en" ? "en" : "de";
      localStorage.setItem("xx-alps-lang", currentLang);
      refreshLocalizedView();
    }}

    for (const button of document.querySelectorAll(".filter-grid button[data-preset]")) {{
      button.addEventListener("click", () => selectPreset(button.dataset.preset));
    }}
    for (const button of document.querySelectorAll(".language-toggle button[data-lang]")) {{
      button.addEventListener("click", () => setLanguage(button.dataset.lang));
    }}
    document.getElementById("fit").addEventListener("click", fitRoutes);
    document.getElementById("route-modal-close").addEventListener("click", closeRouteDetail);
    document.getElementById("route-modal").addEventListener("click", event => {{
      if (event.target.id === "route-modal") closeRouteDetail();
    }});
    document.addEventListener("keydown", event => {{
      if (event.key === "Escape") closeRouteDetail();
    }});

    translateStaticUi();
    renderDashboardTabs();
    renderDashboard("ARRIVAL");
    renderOrganizerPanel();
    renderPackingPanel();
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
