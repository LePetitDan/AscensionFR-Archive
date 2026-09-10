# -*- coding: utf-8 -*-
"""Répare les traductions livrées par la passe « l'officiel Blizzard gagne ».

CE QUI S'EST PASSÉ
------------------
Une passe d'adoption automatique (`appliquer_divergences_officielles.py`) a
retrouvé le français officiel PAR ID, en croisant `spells_Ascension.json` (nom
anglais) et `spells_frFR.json` (français Blizzard) au même identifiant — sans
vérifier que Blizzard nommait ce sort comme Ascension le nomme. Or Ascension
RENOMME des sorts Blizzard EN PLACE : l'ID ne bouge pas, le nom si, et le
français récupéré traduit alors l'ANCIEN nom.

Sur les 45 corrections appliquées, 4 sont des contresens vivants en jeu
(mesure du lot 5, 26/07/2026). Le garde-fou est posé depuis dans
`garde_appariement.py` : ce script-ci ne répare que les dégâts déjà livrés.

  ID 38299 : Blizzard disait « HoTs on Heals », Ascension l'a rebaptisé
             « Fel Reaver's Piston » -> on a récupéré « Soins sur la durée
             sur les soins ». La bonne valeur est prouvée trois fois : le
             journal de la passe (`divergences_officielles_appliquees.txt`,
             ligne « avant »), la source officielle de l'OBJET 30619
             (`sources/frFR/item_template_locale.json`), et l'addon livré
             (DB_Objets.lua). Cinq sauvegardes concordent.
  ID 33886-33890 : Blizzard disait « Empowered Rejuvenation » -> on a récupéré
             « Récupération surpuissante » pour « Nature's Rejuvenation ».
  ID 13318 : Blizzard disait « Rend » -> on a récupéré « Pourfendre », qui est
             DÉJÀ le nom de Rend chez nous (138 IDs) : deux sorts du même nom.
             « Shanked! » n'était PAS traduit avant la passe : ce n'est donc
             pas une restauration, c'est une traduction neuve.
  ID 2842  : Blizzard disait « Poisons » -> le « Mastery » s'est perdu.

DEUX CORRECTIONS EN PLUS, ET POURQUOI
-------------------------------------
Renommer « Nature's Rejuvenation » oblige à suivre sur les 2 cartes de
compétence qui portent le nom du sort, sinon le joueur voit deux noms pour la
même chose (`corriger_cartes_competence.py` ne les rattraperait pas : sa
mesure de ressemblance tombe à 0,33, sous son seuil de 0,5).
Et l'objet 30619 s'écrit « gangrène » chez nous alors que l'officiel Blizzard
écrit « gangrené » : une lettre, mais elle ferait diverger le nom du sort et
celui de l'objet dont il vient.

Usage :
    python outils/corriger_appariement_faux.py              # simulation
    python outils/corriger_appariement_faux.py --appliquer  # écrit
"""
import argparse
import io
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (fichier, chemin dans le JSON, valeurs ATTENDUES avant, valeur voulue, pourquoi)
#
# Les valeurs attendues sont vérifiées AVANT d'écrire : si on trouve autre
# chose, on refuse et on le dit. Sans ça, un rejeu après une autre passe
# écraserait en silence un travail plus récent — et ce script existe
# précisément parce qu'une écriture automatique non vérifiée a fait des dégâts.
#
# Une correction peut accepter PLUSIEURS valeurs de départ : c'est le cas de
# « Shanked! », que j'avais d'abord rendu « Suriné ! » et que Dan a tranché en
# « Coup de surin ! ». Le script reste ainsi rejouable depuis l'un ou l'autre
# état, au lieu de refuser tout net sur celui du milieu.
CORRECTIONS = [
    ("sorts.json", ("noms", "Fel Reaver's Piston"),
     ["Soins sur la durée sur les soins"], "Piston de saccageur gangrené",
     "français de « HoTs on Heals » (ID 38299), le nom Blizzard d'avant"),
    ("sorts.json", ("noms", "Nature's Rejuvenation"),
     ["Récupération surpuissante"], "Récupération de la nature",
     "français d'« Empowered Rejuvenation » (IDs 33886-33890)"),
    ("sorts.json", ("noms", "Shanked!"),
     ["Pourfendre", "Suriné !"], "Coup de surin !",
     "arbitrage de Dan : le substantif « surin » est attesté chez Blizzard "
     "(6 objets « Shank » sur 7), le participe ne l'est pas, et « Suriner » "
     "est déjà le nom de Gouge"),
    ("sorts.json", ("noms", "Poison Mastery"),
     ["Poisons"], "Maîtrise du poison",
     "nom Blizzard de l'ID 2842 ; le « Mastery » avait disparu"),

    ("objets_dbc.json", ("noms", "Golden Skill Card - Nature's Rejuvenation"),
     ["Carte de compétence dorée - Rajeunissement de la nature"],
     "Carte de compétence dorée - Récupération de la nature",
     "la carte doit dire le même nom que le sort qu'elle enseigne"),
    ("objets_dbc.json", ("noms", "Skill Card - Nature's Rejuvenation"),
     ["Carte de compétence - Rajeunissement de la nature"],
     "Carte de compétence - Récupération de la nature",
     "idem — concordance de mots entre la carte et le sort"),

    ("objets.json", ("30619", "N"),
     ["Piston de saccageur gangrène"], "Piston de saccageur gangrené",
     "coquille d'accent : l'officiel Blizzard écrit « gangrené »"),
]


def charger(chemin):
    with io.open(chemin, encoding="utf-8") as f:
        return json.load(f)


def lire(donnees, route):
    for etape in route:
        if not isinstance(donnees, dict) or etape not in donnees:
            return None
        donnees = donnees[etape]
    return donnees


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--appliquer", action="store_true")
    args = parser.parse_args()

    par_fichier = {}
    refus = 0
    for nom, route, avants, apres, pourquoi in CORRECTIONS:
        chemin = os.path.join(BASE, "traductions", nom)
        donnees = par_fichier.setdefault(chemin, charger(chemin))
        actuel = lire(donnees, route)

        if actuel == apres:
            print("  déjà fait   %-14s %s" % (nom, " / ".join(route)))
            continue
        if actuel not in avants:
            print("  REFUS       %-14s %s" % (nom, " / ".join(route)))
            print("              attendu : %s"
                  % " ou ".join(repr(a) for a in avants))
            print("              trouvé  : %r" % actuel)
            refus += 1
            continue

        print("  %-14s %s" % (nom, " / ".join(route)))
        print("      - %s" % actuel)
        print("      + %s   (%s)" % (apres, pourquoi))
        table = donnees
        for etape in route[:-1]:
            table = table[etape]
        table[route[-1]] = apres

    if refus:
        print("\n%d correction(s) refusée(s) : la valeur de départ n'est plus "
              "celle attendue.\nRien n'a été écrit — vérifie avant de forcer."
              % refus)
        return 1

    if not args.appliquer:
        print("\nSIMULATION — rien n'a été écrit. --appliquer pour livrer.")
        return 0

    for chemin, donnees in par_fichier.items():
        secours = chemin.replace(".json", "_avant_appariement.json")
        if not os.path.exists(secours):
            shutil.copy2(chemin, secours)
        with io.open(chemin, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=1, sort_keys=True)
        print("  écrit : %s" % os.path.basename(chemin))
    print("\nFait. Régénère les bases pour que l'addon en profite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
