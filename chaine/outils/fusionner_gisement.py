# -*- coding: utf-8 -*-
"""
Rassemble les lots traduits du gisement et les contrôle avant livraison.

Le chemin : lots (texteAnglais -> texteFrançais) -> traductions/
interface_maison.json (étiquette -> texteFrançais), que generateur_db greffe
sur DB_Interface. `Modules\\InterfaceUI.lua` s'occupe du reste : il ne pose
une chaîne que si sa signature de format est identique, et jamais si elle est
en liste noire.

Trois contrôles ici, chacun né d'un vrai dégât :
  - **format** : un %s en trop fait planter le jeu (jumelle du contrôle Lua) ;
  - **anglais résiduel** : Haiku rendait « Feu de l'enfer: Weave powerful
    spell casts » — le contrôle de format, lui, était content ;
  - **non traduites** : une valeur vide ou identique à l'anglais.

Rien de douteux n'entre : mieux vaut l'anglais qu'un texte à moitié français.

Usage : python outils/fusionner_gisement.py [--ecrire]
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generateur_glue import signature_compatible  # noqa: E402
from ecriture_sure import ecrire_json  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(BASE, "a_traduire", "interface_maison.json")
BRUT = os.path.join(BASE, "traductions", "gisement_brut.json")
SORTIE = os.path.join(BASE, "traductions", "interface_maison.json")

# Mots anglais SANS JUMEAU FRANÇAIS : leur présence prouve un texte inachevé.
#
# Le choix de cette liste est tout le sujet. Un mot qui existe aussi en
# français y crée un faux coupable, et un faux coupable coûte une traduction
# juste : « chance », « note », « point », « long », « double », « rare »,
# « ancien », « important », « final » sont français. Écartés, donc.
# Restent les mots-outils anglais, qui n'ont pas d'homographe français et que
# toute phrase anglaise porte forcément.
ANGLAIS = re.compile(
    r"\b(?:the|your|you|with|and|that|this|from|their|them|will|"
    r"enemies|allies|abilities|while|into|upon|through|when|have|"
    r"increased|contains|guarantee|which|there|these|those|been|being)\b",
    re.I)

# Les noms propres du jeu restent anglais en français : « The Burning
# Crusade » n'est pas un texte inachevé. Ils sortent du texte avant l'examen,
# sinon leur « The » fait condamner une traduction juste.
NOMS_PROPRES = re.compile(
    r"The Burning Crusade|Wrath of the Lich King|World of Warcraft|"
    r"Rise of the Zandalari|Trial of the (?:Crusader|Champion)|"
    r"Call of the Crusade|Fury of the Sunwell|Secrets of Ulduar|"
    r"The Manastorm|Wildcard|Manastorm|Ascension", re.I)


def temoins():
    cas = [
        ("Augmente vos chances de coup critique.", False),
        ("- Increased Critical Strike Chance with Maces.", True),
        ("Contient 5 cartes d'aptitude aléatoires.", False),
        ("Feu de l'enfer: Weave powerful spell casts and tear enemies.", True),
        ("Aptitudes", False),
        ("Essence d'aptitude : %s", False),
        # Les faux coupables vécus le 17/07 : du français pur que la
        # première version du détecteur accusait.
        ("Note de critique %d (+%.2f%% chance de critique)", False),
        ("Le royaume principal d'Ascension ! Actuellement en test.", False),
        ("Domaine progressif au rythme modéré.", False),
        ("Lance instantanément %d parchemins, chacun donnant une chance "
         "de butin rare.", False),
        # Noms d'extension : anglais en français aussi.
        ("Actuellement dans le contenu de The Burning Crusade.", False),
        ("Royaume de test pour Wrath of the Lich King.", False),
        # Vraie coupable, vécue : Google a laissé une phrase entière.
        ("Êtes-vous sûr de vouloir révéler %s ?\n\nUncollected cards will "
         "appear for you to reveal.", True),
    ]
    for texte, attendu in cas:
        if bool(ANGLAIS.search(NOMS_PROPRES.sub("", texte))) != attendu:
            return False, texte
    return True, None


def main():
    ok, rate = temoins()
    if not ok:
        print("! détecteur déréglé sur le témoin : %r — verdict NON publié"
              % rate)
        return 1

    with open(SOURCE, encoding="utf-8") as f:
        chaines = json.load(f)          # étiquette -> anglais
    with open(BRUT, encoding="utf-8") as f:
        traduits = json.load(f)         # anglais -> français (dédoublonné)

    retenus, vides, residus, formats = {}, [], [], []
    for etiquette, en in chaines.items():
        fr = traduits.get(en)
        if not fr or fr == en:
            vides.append(en)
            continue
        if not signature_compatible(en, fr):
            formats.append(etiquette)
            continue
        if ANGLAIS.search(NOMS_PROPRES.sub("", fr)):
            residus.append(etiquette)
            continue
        retenus[etiquette] = fr

    print("Clés du gisement    : %d" % len(chaines))
    print("Textes traduits     : %d uniques" % len(traduits))
    print("  -> clés retenues  : %d" % len(retenus))
    print("  non traduites     : %d" % len(set(vides)))
    print("  anglais résiduel  : %d" % len(residus))
    print("  format abîmé      : %d" % len(formats))
    for titre, liste in (("ANGLAIS RÉSIDUEL", residus),
                         ("FORMAT ABÎMÉ", formats)):
        if liste:
            print("\n%s (%d), échantillon :" % (titre, len(liste)))
            for e in sorted(liste)[:6]:
                print("   %-30s %s" % (e, traduits[chaines[e]][:46]))

    if "--ecrire" in sys.argv:
        # Atomique (programme 31, bloc B) : c'était l'écriture « sans
        # filet » relevée au programme 29 — le store dérivé se réécrit en
        # entier, une coupure le tronquait.
        ecrire_json(SORTIE, retenus)
        print("\n%d clés -> %s" % (len(retenus), SORTIE))
    else:
        print("\nRapport seul. --ecrire pour livrer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
