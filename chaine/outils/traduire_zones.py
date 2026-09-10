# -*- coding: utf-8 -*-
r"""Génère DB\DB_Zones.lua : noms de zones anglais -> français officiel.

Sources :
- AreaTable.dbc des archives du client (via lire_dbc_libre de
  traduire_epreuves) : la liste des zones RÉELLEMENT présentes ;
- ZONES_OFFICIELLES ci-dessous : le frFR officiel du jeu de base, écrit à la
  main (vocabulaire figé depuis 2005 — Orneval, Les Tarides, Gangrebois...).

On n'écrit une paire QUE si le nom anglais existe dans le client (pas de
poids mort), plus les paires custom sûres (cohérence avec nos créatures).
Quand Dan aura sourcé AreaTable_frFR.dbc (tâche #30), l'appariement par ID
remplacera cette table pour les sous-zones restantes.
"""
import glob
import io
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from traduire_epreuves import DATA, parait_lisible  # noqa: E402
from generateur_db import polir  # noqa: E402

SORTIE = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
          r"\AscensionFR\DB\DB_Zones.lua")
OBJETS_MONDE = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
                r"\AscensionFR\DB\DB_ObjetsMonde.lua")


def lire_areatable_union():
    """UNION des chaînes d'AreaTable.dbc de TOUTES les archives (la base
    porte les zones classiques, les patchs les customs — lire_dbc_libre ne
    gardait que le dernier patch)."""
    noms = set()
    for chemin in sorted(glob.glob(os.path.join(DATA, "*.MPQ"))):
        try:
            from mpyq import MPQArchive
            archive = MPQArchive(chemin, listfile=True)
            fichiers = archive.files or []
        except Exception:
            continue
        for nom in fichiers:
            if isinstance(nom, bytes):
                nom = nom.decode("latin-1")
            if not nom.lower().endswith("areatable.dbc"):
                continue
            try:
                d = archive.read_file(nom)
            except Exception:
                continue
            if not d or d[:4] != b"WDBC":
                continue
            nb, champs, taille, bloc = struct.unpack("<4I", d[4:20])
            debut = 20 + nb * taille
            chaines = d[debut:debut + bloc]
            for morceau in chaines.split(b"\0"):
                try:
                    texte = morceau.decode("utf-8").strip()
                except UnicodeDecodeError:
                    continue
                if texte and len(texte) < 60 and parait_lisible(texte):
                    noms.add(texte)
    return noms


def paires_panneaux(zones_client):
    """[NE] = N depuis les PANNEAUX de DB_ObjetsMonde (frFR officiel
    récolté), retenus seulement si NE est un nom de zone du client.
    Doublons divergents neutralisés."""
    texte = io.open(OBJETS_MONDE, encoding="utf-8").read()
    panneaux = {}
    for n, ne in re.findall(
            r'N="((?:\\.|[^"\\])*)",NE="((?:\\.|[^"\\])*)"', texte):
        if ne in zones_client and ne != n:
            deja = panneaux.get(ne)
            if deja is None:
                panneaux[ne] = n
            elif deja != n:
                panneaux[ne] = False
    return {ne: n for ne, n in panneaux.items() if n}

ZONES_OFFICIELLES = {
    # Continents
    "Eastern Kingdoms": "Royaumes de l'est", "Outland": "Outreterre",
    "Northrend": "Norfendre",
    # Royaumes de l'est
    "Elwynn Forest": "Forêt d'Elwynn", "Westfall": "Marche de l'Ouest",
    "Redridge Mountains": "Les Carmines",
    "Duskwood": "Bois de la Pénombre",
    "Stranglethorn Vale": "Vallée de Strangleronce",
    "Swamp of Sorrows": "Marais des Chagrins",
    "Blasted Lands": "Terres foudroyées",
    "Burning Steppes": "Steppes ardentes",
    "Searing Gorge": "Gorge des Vents brûlants",
    "Badlands": "Terres ingrates", "Wetlands": "Les Paluns",
    "Arathi Highlands": "Hautes-terres Arathies",
    "Hillsbrad Foothills": "Contreforts de Hautebrande",
    "Alterac Mountains": "Montagnes d'Alterac",
    "Silverpine Forest": "Forêt des Pins-Argentés",
    "Tirisfal Glades": "Clairières de Tirisfal",
    "Western Plaguelands": "Maleterres de l'ouest",
    "Eastern Plaguelands": "Maleterres de l'est",
    "The Hinterlands": "Les Hinterlands",
    "Ghostlands": "Les Terres fantômes",
    "Eversong Woods": "Bois des Chants éternels",
    "Isle of Quel'Danas": "Île de Quel'Danas",
    "Deadwind Pass": "Défilé de Deuillevent",
    "Stormwind City": "Hurlevent", "Ironforge": "Forgefer",
    "Undercity": "Fossoyeuse", "Silvermoon City": "Lune-d'argent",
    # Kalimdor
    "The Barrens": "Les Tarides", "Darkshore": "Sombrivage",
    "Ashenvale": "Orneval",
    "Stonetalon Mountains": "Les Serres-Rocheuses",
    "Desolace": "Désolace", "Feralas": "Féralas",
    "Thousand Needles": "Mille pointes",
    "Un'Goro Crater": "Cratère d'Un'Goro",
    "Felwood": "Gangrebois",
    "Winterspring": "Berceau-de-l'Hiver", "Moonglade": "Reflet-de-Lune",
    "Dustwallow Marsh": "Marécage d'Âprefange",
    "Thunder Bluff": "Les Pitons-du-Tonnerre",
    "The Exodar": "L'Exodar",
    "Azuremyst Isle": "Île de Brume-azur",
    "Bloodmyst Isle": "Île de Brume-sang",
    # Outreterre
    "Hellfire Peninsula": "Péninsule des Flammes infernales",
    "Zangarmarsh": "Marécage de Zangar",
    "Terokkar Forest": "Forêt de Terokkar",
    "Blade's Edge Mountains": "Les Tranchantes",
    "Netherstorm": "Raz-de-Néant",
    "Shadowmoon Valley": "Vallée d'Ombrelune",
    "Shattrath City": "Shattrath",
    # Norfendre
    "Borean Tundra": "Toundra Boréenne", "Howling Fjord": "Fjord Hurlant",
    "Dragonblight": "Désolation des dragons",
    "Grizzly Hills": "Les Grisonnes",
    "Sholazar Basin": "Bassin de Sholazar",
    "The Storm Peaks": "Les pics Foudroyés",
    "Icecrown": "La Couronne de glace",
    "Wintergrasp": "Joug-d'hiver",
    "Crystalsong Forest": "Forêt du Chant de cristal",
    "Hrothgar's Landing": "Débarcadère d'Hrothgar",
    # Donjons et raids
    "The Deadmines": "Les Mortemines", "Deadmines": "Les Mortemines",
    "Shadowfang Keep": "Donjon d'Ombrecroc",
    "The Stockade": "La Prison", "Gnomeregan": "Gnomeregan",
    "Razorfen Kraul": "Kraal de Tranchebauge",
    "Razorfen Downs": "Souilles de Tranchebauge",
    "Scarlet Monastery": "Monastère écarlate",
    "Wailing Caverns": "Cavernes des lamentations",
    "Blackfathom Deeps": "Profondeurs de Brassenoire",
    "Blackrock Depths": "Profondeurs de Rochenoire",
    "Blackrock Spire": "Pic Rochenoire",
    "Dire Maul": "Hache-tripes",
    "Molten Core": "Cœur du Magma",
    "Blackwing Lair": "Repaire de l'Aile noire",
    "Onyxia's Lair": "Repaire d'Onyxia",
    "Ruins of Ahn'Qiraj": "Ruines d'Ahn'Qiraj",
    "Temple of Ahn'Qiraj": "Temple d'Ahn'Qiraj",
    "The Culling of Stratholme": "L'Épuration de Stratholme",
    "Trial of the Champion": "L'épreuve du champion",
    "Trial of the Crusader": "L'épreuve du croisé",
    "The Forge of Souls": "La Forge des âmes",
    "Pit of Saron": "La Fosse de Saron",
    "Halls of Reflection": "Salles des Reflets",
    "Halls of Stone": "Salles de Pierre",
    "Halls of Lightning": "Salles de Foudre",
    "Utgarde Keep": "Donjon d'Utgarde",
    "Utgarde Pinnacle": "Cime d'Utgarde",
    "The Nexus": "Le Nexus", "The Oculus": "L'Oculus",
    "The Obsidian Sanctum": "Le sanctum Obsidien",
    "The Eye of Eternity": "L'Œil de l'éternité",
    "Vault of Archavon": "Caveau d'Archavon",
    "Icecrown Citadel": "Citadelle de la Couronne de glace",
    # Sous-zones et villages très fréquentés
    "Goldshire": "Comté-de-l'or", "Northshire": "Comté-du-nord",
    "Northshire Valley": "Vallée de Comté-du-nord",
    "The Crossroads": "La Croisée", "Ratchet": "Cabestan",
    "Booty Bay": "Baie-du-Butin", "Gadgetzan": "Gadgetzan",
    "Everlook": "Long-Guet", "Astranaar": "Astranaar",
    "Auberdine": "Auberdine",
    "Menethil Harbor": "Port de Menethil",
    "Southshore": "Austrivage", "Tarren Mill": "Moulin-de-Tarren",
    "Brill": "Brill", "Sen'jin Village": "Village de Sen'jin",
    "Razor Hill": "Tranchecolline",
    "Bloodhoof Village": "Village Sabot-de-Sang",
    "Dolanaar": "Dolanaar", "Kharanos": "Kharanos",
    "Lakeshire": "Comté-du-lac", "Darkshire": "Sombre-Comté",
    "Sentinel Hill": "Colline des Sentinelles",
    "Camp Taurajo": "Camp Taurajo", "Camp Mojache": "Camp Mojache",
    "Nijel's Point": "Combe de Nijel",
    "Theramore Isle": "Île de Theramore",
    "Grom'gol Base Camp": "Camp de base de Grom'gol",
    "Light's Hope Chapel": "Chapelle de l'Espoir de Lumière",
    "Refuge Pointe": "Refuge de l'Ornière",
    "Hammerfall": "Trépas-d'Orgrim",
    "Stonewrought Dam": "Barrage de Formepierre",
    "Thelsamar": "Thelsamar",
    # Customs d'Ascension (cohérence avec nos créatures)
    "Greenpaw Village": "Village Patte-verte",
}

def table_zones(journal=None):
    """{ nom anglais: nom français } — les MÊMES paires que DB_Zones.lua.

    Servie aussi à generateur_glue.py : l'écran de connexion ne charge pas
    les DB de l'addon, le Glue embarque donc ces paires. Une seule source
    de vérité (règle d'or) : cette fonction, jamais le fichier généré.
    """
    dire = journal or (lambda *a: None)
    zones_client = lire_areatable_union()
    dire("noms de zones du client (union des archives) : %d"
         % len(zones_client))

    # Les PANNEAUX priment sur la table écrite de mémoire : l'audit du 20/07
    # a prouvé que la mémoire se trompe (7/120) et pas les panneaux.
    officiels = paires_panneaux(zones_client)
    dire("paires tirées des panneaux : %d" % len(officiels))

    fusion = {}
    # -1. Points de vol (TaxiNodes, via outils/traduire_taxinodes.py) : couche
    #     de BASE. Les zones et panneaux officiels gardent le dernier mot (donc
    #     pas de « marche » qui écraserait « Marche de l'Ouest »). Les noms
    #     COMPLETS de nœud (« Stormwind, Elwynn ») ne sont pas des zones : ils
    #     survivent et couvrent le crochet de vol (Plaques.lua).
    CHEMIN_TAXI = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "traductions", "taxinodes.json")
    if os.path.exists(CHEMIN_TAXI):
        import json as _json_taxi
        with io.open(CHEMIN_TAXI, encoding="utf-8") as f:
            for en, fr in _json_taxi.load(f).items():
                if en and fr and en != fr:
                    fusion[en] = fr
        dire("points de vol (TaxiNodes) chargés : %d" % len(fusion))

    # 0. la jointure PAR ID des AreaTable (enUS du jeu x patch-frFR-3.MPQ,
    #    tâche #30 débloquée le 21/07/2026) : le frFR officiel de TOUTES
    #    les zones et sous-zones classiques. Couche de base : la table à
    #    la main et les panneaux gardent le dernier mot.
    CHEMIN_ID = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "traductions",
        "zones_officielles_id.json")
    if os.path.exists(CHEMIN_ID):
        import json
        with io.open(CHEMIN_ID, encoding="utf-8") as f:
            par_id = json.load(f)
        n = 0
        for en, fr in par_id.items():
            if en in zones_client and fr and en != fr:
                fusion[en] = fr
                n += 1
        dire("paires par ID (AreaTable frFR) retenues : %d" % n)
    for en, fr in ZONES_OFFICIELLES.items():
        if en != fr:
            fusion[en] = fr
    conflits = []
    for en, fr in officiels.items():
        if en in fusion and fusion[en] != fr:
            conflits.append("%s : mémoire « %s » -> panneau « %s »"
                            % (en, fusion[en], fr))
        fusion[en] = fr
    for c in sorted(conflits):
        dire("  panneau prime : %s" % c)
    return fusion


def main():
    fusion = table_zones(journal=print)
    paires = sorted(fusion.items())
    absents = []

    lignes = ["-- Fichier GÉNÉRÉ par outils/traduire_zones.py — ne pas",
              "-- éditer à la main : la source est la table",
              "-- ZONES_OFFICIELLES de l'outil (frFR officiel figé).",
              "-- Indexé par le nom ANGLAIS affiché.",
              "local DB = AscensionFR.DB.Zones"]
    for en, fr in paires:
        # Filet : un panneau récolté en jeu peut ramener « bassin d'Arathi ».
        lignes.append('DB["%s"]="%s"'
                      % (en.replace('"', '\\"'),
                         polir(fr, anglais=en).replace('"', '\\"')))
    with io.open(SORTIE, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    print("écrit : DB_Zones.lua (%d zones)" % len(paires))
    if absents:
        print("hors client (non écrites) :", ", ".join(absents[:10]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
