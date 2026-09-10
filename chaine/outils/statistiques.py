# -*- coding: utf-8 -*-
"""
Combien de monde utilise la traduction ? Les chiffres qu'on peut connaître
SANS rien espionner.

Aucune télémétrie n'est embarquée dans le Compagnon — c'est une promesse
écrite dans l'application et dans le dépôt. On s'appuie donc uniquement sur
des compteurs publics ou sur ce que les joueurs nous envoient d'eux-mêmes.

Usage : python outils/statistiques.py
"""
import io
import json
import os
import re
import urllib.request
from collections import Counter

DEPOT = "LePetitDan/AscensionFR"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAPPORTS = os.path.join(BASE, "rapports")


def api_github(chemin):
    req = urllib.request.Request(
        "https://api.github.com/repos/" + DEPOT + chemin,
        headers={"User-Agent": "AscensionFR-Stats",
                 "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def telechargements():
    print("=== Téléchargements (compteur public GitHub) ===")
    total_addon, total_compagnon = 0, 0
    for release in api_github("/releases"):
        print("  %s  (%s)" % (release["tag_name"], release["published_at"][:10]))
        for asset in release.get("assets", []):
            n = asset.get("download_count", 0)
            print("      %-34s %5d" % (asset["name"], n))
            if asset["name"].lower().endswith(".exe"):
                total_compagnon += n
            elif asset["name"].lower().endswith(".zip"):
                total_addon += n
    print()
    print("  TOTAL Compagnon (.exe)      : %d" % total_compagnon)
    print("  TOTAL addon manuel (.zip)   : %d" % total_addon)
    return total_compagnon, total_addon


def contributeurs():
    """Les rapports reçus. Anonymes : on ne compte que des fichiers, et le
    nombre de comptes de jeu distincts qu'ils mentionnent — jamais un pseudo."""
    print()
    print("=== Rapports reçus (ce que les joueurs envoient) ===")
    auto = [f for f in os.listdir(RAPPORTS)
            if f.startswith("auto_") and f.endswith(".txt")]
    caches = [f for f in os.listdir(RAPPORTS)
              if f.startswith("auto_") and f.endswith(".json.gz")]
    manuels = [f for f in os.listdir(RAPPORTS)
               if not f.startswith("auto_") and f.endswith(".txt")
               and not f.startswith("ids_")]
    print("  rapports envoyés par le Compagnon : %d" % len(auto))
    print("  dont accompagnés des caches de jeu : %d" % len(caches))
    print("  rapports déposés à la main         : %d" % len(manuels))

    versions = Counter()
    for nom in auto + manuels:
        try:
            texte = io.open(os.path.join(RAPPORTS, nom), encoding="utf-8",
                            errors="replace").read(400)
        except OSError:
            continue
        m = re.search(r"AscensionFR (\d+\.\d+)", texte)
        if m:
            versions[m.group(1)] += 1
    if versions:
        print("  versions de l'addon vues dans les rapports :")
        for version, n in sorted(versions.items()):
            print("      %-8s %3d rapport(s)" % (version, n))


def main():
    telechargements()
    contributeurs()
    print()
    print("Rappel : un téléchargement n'est pas un joueur (mises à jour,")
    print("essais, curieux). C'est un ordre de grandeur, pas un décompte.")


if __name__ == "__main__":
    main()
