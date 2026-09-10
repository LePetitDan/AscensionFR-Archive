# -*- coding: utf-8 -*-
"""
Que reste-t-il à traduire dans les 14 280 chaînes maison d'Ascension ?

`GlobalStrings.dbc` (patch-M.MPQ) est le fichier de textes d'interface
d'Ascension : leur client en fait des variables globales Lua, en jeu comme
sur les écrans d'avant. Notre addon sait déjà remplacer ces globales
(Modules\\InterfaceUI.lua) — il le fait pour 7 898 d'entre elles à partir du
frFR officiel de Blizzard.

Cet outil répond à une seule question : combien de ces chaînes n'ont PAS
d'équivalent officiel, c'est-à-dire combien de texte d'interface maison
reste réellement à traduire, et à quel prix.

Usage : python outils/auditer_gisement.py [--lister]
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extraire_globalstrings_dbc import lire, COPIE  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GS_FR = os.path.join(BASE, "sources", "GlobalStrings_frFR.lua")
GLUE_FR = os.path.join(BASE, "sources", "GlueStrings_frFR.lua")
SORTIE = os.path.join(BASE, "a_traduire", "interface_maison.json")

CLE_RE = re.compile(r'^([A-Z_0-9]+) *= *"((?:[^"\\]|\\.)*)"', re.M)


def lire_lua(chemin):
    if not os.path.exists(chemin):
        return {}
    with open(chemin, encoding="utf-8", errors="ignore") as f:
        return dict(CLE_RE.findall(f.read()))


def main():
    if not os.path.exists(COPIE):
        print("Lancez d'abord : python outils/extraire_globalstrings_dbc.py")
        return 1
    with open(COPIE, "rb") as f:
        maison, _, _, _ = lire(f.read())

    officiel = lire_lua(GS_FR)
    officiel.update(lire_lua(GLUE_FR))

    couvertes = {k: v for k, v in maison.items() if k in officiel}
    orphelines = {k: v for k, v in maison.items() if k not in officiel}

    # Ce qui n'a pas besoin d'être traduit : codes, nombres, symboles.
    def a_traduire(texte):
        return len(texte) > 2 and re.search(r"[A-Za-z]{3}", texte)

    utiles = {k: v for k, v in orphelines.items() if a_traduire(v)}
    inutiles = len(orphelines) - len(utiles)

    signes = sum(len(v) for v in utiles.values())
    print("Chaînes maison d'Ascension (GlobalStrings.dbc) : %d" % len(maison))
    print("  couvertes par le frFR officiel de Blizzard   : %d" % len(couvertes))
    print("  sans équivalent officiel                     : %d" % len(orphelines))
    print("     dont codes/symboles (rien à traduire)     : %d" % inutiles)
    print("     dont vrai texte à traduire                : %d" % len(utiles))
    print()
    print("Volume : %d signes (~%d mots)" % (signes, signes // 6))
    print("  Google (gratuit, ~6/s)  : ~%d min" % (len(utiles) / 6 / 60 + 1))

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as f:
        json.dump(utiles, f, ensure_ascii=False, indent=1, sort_keys=True)
    print()
    print("-> %s" % SORTIE)

    if "--lister" in sys.argv:
        print()
        print("--- échantillon ---")
        for k in sorted(utiles)[:20]:
            print("   %-34s %s" % (k, utiles[k][:48]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
