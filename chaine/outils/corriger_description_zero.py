# -*- coding: utf-8 -*-
r"""Retire la paire de description « 0 » -> « 0 » du méga-lot ItemAddon.

LE MAL, ET D'OÙ IL VIENT
------------------------
Cinq objets livrés affichaient `D="0"` dans `DB_Objets.lua` (« Le chasseur :
Hawk Eye », « L'Œil : Arcanes Résistance »…). Ce n'est PAS la maladie du
PackFR : la description ANGLAISE de ces objets vaut littéralement « 0 » dans
l'ItemAddon.dbc d'Ascension — leur marqueur de « pas de description ». Le
moulin a fidèlement « traduit » « 0 » par « 0 »
(`objets_dbc.json/descriptions["0"] = "0"`), et `generateur_db` a posé cette
description sur chaque objet dont l'anglais dit « 0 ».

UNE seule paire de cache produit donc les cinq lignes livrées — et en
produira d'autres à chaque objet nouveau portant ce marqueur. La retirer
suffit : sans français pour « 0 », `generateur_db` ne pose plus de champ D,
et notre addon cesse d'endosser le bouche-trou d'Ascension.

CE QU'ON NE TOUCHE PAS : les 34 autres paires sans lettre du même fichier
(« @10-19@ » -> « @10-19@ », la suite de Fibonacci d'un objet-blague, « ??? »).
Ce sont des échos volontaires de contenus voulus tels quels — les retirer ne
corrigerait rien et ferait diverger le cache de sa source.

Usage :
    python outils/corriger_description_zero.py              # simulation
    python outils/corriger_description_zero.py --appliquer  # écrit
"""
import argparse
import io
import json
import os
import shutil
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN = os.path.join(BASE, "traductions", "objets_dbc.json")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--appliquer", action="store_true")
    args = p.parse_args()

    with io.open(CHEMIN, encoding="utf-8") as f:
        donnees = json.load(f)

    valeur = donnees.get("descriptions", {}).get("0")
    if valeur is None:
        print("Rien à faire : la paire « 0 » n'existe plus.")
        return 0
    print("paire trouvée : descriptions[\"0\"] = %r  -> à SUPPRIMER" % valeur)

    if not args.appliquer:
        print("SIMULATION — rien n'a été écrit. --appliquer pour corriger.")
        return 0

    copie = CHEMIN.replace(".json", "_avant_zero_%s.json"
                           % datetime.now().strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(CHEMIN, copie)
    del donnees["descriptions"]["0"]
    with io.open(CHEMIN, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("écrit : objets_dbc.json  (sauvegarde : %s)"
          % os.path.basename(copie))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
