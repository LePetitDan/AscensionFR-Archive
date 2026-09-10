# -*- coding: utf-8 -*-
"""
Prépare les 5 504 chaînes d'interface maison pour la traduction.

Deux économies, dans cet ordre :

1. **Dédoublonner par VALEUR.** Ascension répète le même texte sur des clés
   différentes (`ABILITY_INFO_DWARF5_REALM_3/_4/_11` sont identiques au signe
   près). Un texte unique ne se traduit qu'une fois, quel que soit le nombre
   de clés qui le portent — c'est déjà la règle pour les sorts.

2. **Découper les lots SUR LE DISQUE.** Au premier essai (429 fiches de
   classe), chaque agent lisait le fichier ENTIER pour n'en prendre qu'un
   douzième : 1,6 million de jetons pour 429 chaînes. Chaque agent ne doit
   voir que son lot.

Produit  a_traduire/gisement/lot_NN.json  ({ texteAnglais: "" } à remplir)
Usage    python outils/preparer_gisement.py [--lots N]
"""
import json
import math
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(BASE, "a_traduire", "interface_maison.json")
LOTS = os.path.join(BASE, "a_traduire", "gisement")
DEJA = os.path.join(BASE, "traductions", "interface_maison.json")


def main():
    nb_lots = 20
    if "--lots" in sys.argv:
        nb_lots = int(sys.argv[sys.argv.index("--lots") + 1])

    with open(SOURCE, encoding="utf-8") as f:
        chaines = json.load(f)

    # Ce qui est déjà traduit ne repart pas : on peut relancer sans perte.
    faites = {}
    if os.path.exists(DEJA):
        with open(DEJA, encoding="utf-8") as f:
            faites = json.load(f)

    uniques = sorted({v for v in chaines.values() if v not in faites})
    print("Clés à couvrir        : %d" % len(chaines))
    print("Textes uniques        : %d" % len({v for v in chaines.values()}))
    print("Déjà traduits         : %d" % len(faites))
    print("Restant à traduire    : %d (%d signes)"
          % (len(uniques), sum(len(t) for t in uniques)))
    if not uniques:
        print("Rien à faire.")
        return 0

    os.makedirs(LOTS, exist_ok=True)
    for ancien in os.listdir(LOTS):
        if ancien.endswith(".json"):
            os.remove(os.path.join(LOTS, ancien))

    taille = int(math.ceil(len(uniques) / float(nb_lots)))
    for i in range(nb_lots):
        tranche = uniques[i * taille:(i + 1) * taille]
        if not tranche:
            break
        chemin = os.path.join(LOTS, "lot_%02d.json" % i)
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump({t: "" for t in tranche}, f, ensure_ascii=False,
                      indent=1, sort_keys=True)
    ecrits = len([n for n in os.listdir(LOTS) if n.endswith(".json")])
    print()
    print("%d lots de ~%d textes -> %s" % (ecrits, taille, LOTS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
