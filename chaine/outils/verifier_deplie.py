# -*- coding: utf-8 -*-
"""
Banc de l'aligneur des textes DÉPLIÉS (AFR.AlignerDeplie, Sorts.lua).
=====================================================================
Écrit AVANT le branchement en jeu — leçon de la greffe chimère du
23/07/2026 au matin : « ça marche sur une capture » n'est pas une
validation. Ici : cas nominal, ambiguïté, désaccord de comptes, « $ » nu
du client, ligne étrangère — l'aligneur doit réussir le nominal et
REFUSER tout le reste (tout-ou-rien).

Usage : python outils/verifier_deplie.py
"""
import io
import os
import sys

import lupa.lua51 as lupa_mod

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verifier_sorts import STUBS, ADDON  # noqa: E402

EN = ("Unleash a whirling strike, dealing $s1% Weapon Damage to nearby "
      "enemies.\n"
      "Consumes your Oaths, dealing $s2 additional damage for each "
      "consumed.")
FR = ("Déchaîne une frappe tournoyante et inflige $s1 % de dégâts d'arme "
      "aux ennemis proches.\n"
      "Consomme vos Serments et inflige $s2 points de dégâts "
      "supplémentaires par Serment consommé.")

CAS = [
    ("nominal : 2e paragraphe, valeurs de l'écran reprises",
     "Consumes your Oaths, dealing 25 additional damage for each "
     "consumed.",
     EN, FR,
     "Consomme vos Serments et inflige 25 points de dégâts "
     "supplémentaires par Serment consommé."),
    ("nominal : 1er paragraphe",
     "Unleash a whirling strike, dealing 100% Weapon Damage to nearby "
     "enemies.",
     EN, FR,
     "Déchaîne une frappe tournoyante et inflige 100 % de dégâts d'arme "
     "aux ennemis proches."),
    ("comptes de paragraphes différents -> refus",
     "Consumes your Oaths, dealing 25 additional damage for each "
     "consumed.",
     EN, "Un seul paragraphe français.", None),
    ("ambiguïté (deux paragraphes anglais identiques) -> refus",
     "Deals 10 damage.",
     "Deals $s1 damage.\nDeals $s1 damage.",
     "Inflige $s1 points de dégâts.\nInflige $s1 points de dégâts.",
     None),
    ("« $ » nu laissé par le client -> RECOPIÉ tel quel (doctrine "
     "805409 : même nombre de $ des deux côtés, c'est correct)",
     "dealing 100% Weapon Damage plus $ damage to nearby enemies.",
     "dealing $s1% Weapon Damage plus ${$m2*2} damage to nearby "
     "enemies.",
     "inflige $s1 % de dégâts d'arme plus ${$m2*2} points de dégâts aux "
     "ennemis proches.",
     "inflige 100 % de dégâts d'arme plus $ points de dégâts aux "
     "ennemis proches."),
    ("ligne étrangère au modèle -> refus",
     "Rank 0/1", EN, FR, None),
    ("chimère impossible : jamais de sortie mélangée",
     "Consumes your Oaths, dealing twenty-five additional damage.",
     EN, FR, None),
]


def main():
    lua = lupa_mod.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(STUBS)
    with io.open(ADDON, encoding="utf-8") as f:
        lua.execute(f.read())
    aligner = lua.globals().AscensionFR.AlignerDeplie

    echecs = 0
    for titre, affiche, en, fr, attendu in CAS:
        obtenu = aligner(affiche, en, fr)
        if obtenu == attendu:
            print("ok      %s" % titre)
        else:
            echecs += 1
            print("ÉCHEC   %s" % titre)
            print("        attendu :", repr(attendu)[:90])
            print("        obtenu  :", repr(obtenu)[:90])
    print()
    print("%d échec(s)" % echecs)
    return 1 if echecs else 0


if __name__ == "__main__":
    raise SystemExit(main())
