# -*- coding: utf-8 -*-
"""Extrait la liste des RÉGLAGES d'interface depuis un taint.log, et écrit
DB/DB_Reglages.lua.

Pourquoi cet outil existe
-------------------------
Le panneau d'options du client fait, pour chaque case à cocher :

    Interface\\SharedXML\\Settings\\OptionsPanelTemplates.lua:375   lit  OPTION_TOOLTIP_<NOM>
    Interface\\SharedXML\\Settings\\OptionsPanelTemplates.lua:379   lit  <NOM>        <-- le réglage

Si nous traduisons l'une de ces deux globales, nous la « souillons » (taint) :
l'exécution du panneau devient souillée, la souillure se propage au réglage,
puis à TargetFrame, puis à UseAction() — et le joueur ne peut plus lancer ses
sorts en combat (signalé par <joueur> et Sleyzer, 18-19/07/2026).

Deux correctifs successifs (1.6.1, 1.6.2) ont tenté de RECONNAÎTRE un réglage
par déduction. Les deux ont échoué : une déduction fausse ne se déclenche
jamais, et rien ne le signale. On ne déduit donc plus — on relève ce que le
client a lui-même écrit dans son journal, ligne 379.

Usage :
    python outils/extraire_reglages.py [chemin/vers/taint.log ...]

Sans argument, prend le taint.log du client de développement. Les noms déjà
présents dans DB_Reglages.lua sont CONSERVÉS : un journal ne montre que les
options que le joueur a effectivement ouvertes, la liste ne fait que grandir.
"""
import io
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JEU = r"D:\AscensionFR\WOW_Priv\resources\ascension-live"
TAINT_PAR_DEFAUT = os.path.join(JEU, "Logs", "taint.log")
SORTIE = os.path.join(JEU, "Interface", "AddOns", "AscensionFR",
                      "DB", "DB_Reglages.lua")

# La ligne 379 est le site de lecture du réglage lui-même (le « uvar »).
LIGNE_REGLAGE = re.compile(
    r"while reading ([A-Za-z_][A-Za-z_0-9]*) - .*OptionsPanelTemplates\.lua:379")


def lire_journal(chemin):
    """Noms de réglages relevés dans un taint.log."""
    noms = set()
    with io.open(chemin, encoding="utf-8", errors="replace") as f:
        for ligne in f:
            trouve = LIGNE_REGLAGE.search(ligne)
            if trouve:
                noms.add(trouve.group(1))
    return noms


def deja_connus(chemin):
    """Noms déjà listés dans un DB_Reglages.lua existant."""
    if not os.path.exists(chemin):
        return set()
    texte = io.open(chemin, encoding="utf-8").read()
    return set(re.findall(r'\["([A-Za-z_0-9]+)"\]=true', texte))


def ecrire(noms, chemin):
    lignes = [
        "-- Réglages d'interface : NE JAMAIS TRADUIRE.",
        "-- Le panneau d'options LIT ces globales (OptionsPanelTemplates.lua:379).",
        "-- Les traduire souille le panneau, puis TargetFrame, puis UseAction() :",
        "-- le joueur ne peut plus lancer ses sorts en combat.",
        "-- Fichier généré par outils/extraire_reglages.py — ne pas éditer à la main.",
        "local DB = AscensionFR.DB.Reglages",
    ]
    for nom in sorted(noms):
        lignes.append('DB["%s"]=true' % nom)
    io.open(chemin, "w", encoding="utf-8", newline="\n").write(
        "\n".join(lignes) + "\n")


def main():
    journaux = sys.argv[1:] or [TAINT_PAR_DEFAUT]
    anciens = deja_connus(SORTIE)
    nouveaux = set()
    for journal in journaux:
        if not os.path.exists(journal):
            print("journal introuvable, ignoré :", journal)
            continue
        trouves = lire_journal(journal)
        print("%-55s %5d réglages" % (os.path.basename(journal), len(trouves)))
        nouveaux |= trouves

    total = anciens | nouveaux
    if not total:
        print("Aucun réglage relevé — rien écrit. Le journal est-il vide ?")
        print("Activez-le en jeu avec : /console taintLog 2")
        return 1

    ecrire(total, SORTIE)
    print()
    print("déjà connus : %d | relevés : %d | ajoutés : %d | total : %d"
          % (len(anciens), len(nouveaux), len(total - anciens), len(total)))
    print("écrit :", SORTIE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
