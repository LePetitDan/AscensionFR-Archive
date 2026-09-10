# -*- coding: utf-8 -*-
"""
Cherche l'origine d'une contamination (« taint ») causée par la traduction
des GlobalStrings.

Principe : une variable globale écrite par un addon devient « contaminée ».
Si du code protégé de Blizzard la LIT ensuite, tout le chemin d'exécution
devient contaminé et l'appel protégé (UseAction, CastSpell...) est bloqué.

Les chaînes littérales entre guillemets ne comptent pas : seules les vraies
lectures de variables sont dangereuses.

Usage : python diagnostic_taint.py <fichier.lua> [<fichier.lua> ...]
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagnostic_gs import charger  # noqa: E402

FRFR = r"D:\AscensionFR\WorkFlow\sources\GlobalStrings_frFR.lua"

CHAINE_DOUBLE = re.compile(r'"(?:[^"\\]|\\.)*"')
CHAINE_SIMPLE = re.compile(r"'(?:[^'\\]|\\.)*'")
COMMENTAIRE_BLOC = re.compile(r"--\[\[.*?\]\]", re.S)
COMMENTAIRE = re.compile(r"--[^\n]*")
IDENTIFIANT = re.compile(r"\b([A-Z][A-Z0-9_]{2,})\b")


def code_seul(source):
    """Retire chaînes littérales et commentaires : ne reste que du code."""
    s = COMMENTAIRE_BLOC.sub("", source)
    s = COMMENTAIRE.sub("", s)
    s = CHAINE_DOUBLE.sub('""', s)
    s = CHAINE_SIMPLE.sub("''", s)
    return s


def analyser(chemin, traduites):
    with open(chemin, encoding="utf-8", errors="ignore") as f:
        source = f.read()
    lus = set(IDENTIFIANT.findall(code_seul(source)))
    return sorted(lus & traduites)


if __name__ == "__main__":
    traduites = set(charger(FRFR))
    total = []
    for chemin in sys.argv[1:]:
        dangereux = analyser(chemin, traduites)
        print("=== %s" % os.path.basename(chemin))
        if dangereux:
            for d in dangereux:
                print("   RISQUE : %s (lu comme variable par du code protégé)"
                      % d)
            total.extend(dangereux)
        else:
            print("   aucune globale traduite lue comme variable")
    print()
    print("%d globale(s) à risque" % len(set(total)))
