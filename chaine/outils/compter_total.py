# -*- coding: utf-8 -*-
"""Compte le VRAI nombre de textes traduits et le grave dans DB_Meta.lua.

POURQUOI (24/07/2026, question de Dan). L'addon calculait son total au login
avec pairs() sur AFR.DB. Or les 4 plus grosses bases sont PARESSEUSES
(Objets, ObjetsNoms, SortsNoms, Repliques) : vides au login, invisibles a
pairs(). Le total ratait ~770 000 textes — plus de la moitie.

La bonne source, c'est la FABRICATION : ici on connait chaque base en entier.
On compte les VALEURS francaises (une fiche de sort {N,D,T,R} = 4 textes) et
on ecrit AscensionFR.TotalTextes = N. L'addon lit cette constante : exact
et gratuit a l'affichage.

Ce compte EXCLUT :
  - les cles anglaises (cote gauche, et seaux C[] des bases paresseuses) ;
  - les references d'identifiants S={"710"} (ne sont pas apres un «=»).

Usage : python outils/compter_total.py [--ecrire]
"""
import io
import os
import re
import sys

ECRIRE = "--ecrire" in sys.argv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chemin_client import DB, exiger_client  # noqa: E402

# Script à exécution au niveau module : la garde vit ici, avant le compte.
exiger_client("compter_total (DB_Meta)")
META = os.path.join(DB, "DB_Meta.lua")

# Une valeur francaise : chaine apres «=», jamais suivie de «]» (une cle
# string se termine par «"]»).
VALEUR = re.compile(r'=("(?:[^"\\]|\\.)*")')


def compte_fichier(texte):
    n = 0
    for ligne in texte.splitlines():
        # Seaux de CLES anglaises des bases paresseuses : jamais des textes.
        if ligne.startswith("C["):
            continue
        for m in VALEUR.finditer(ligne):
            # Exclut la cle « ["...."]=... » : le «=» d'apres «]» est deja
            # gere par la regex (elle capte la valeur, pas la cle).
            n += 1
    return n


total = 0
print("%-26s %s" % ("base", "textes"))
print("-" * 40)
for nom in sorted(os.listdir(DB)):
    if not nom.endswith(".lua") or nom == "DB_Meta.lua":
        continue
    texte = io.open(os.path.join(DB, nom), encoding="utf-8").read()
    n = compte_fichier(texte)
    total += n
    if n:
        print("%-26s %d" % (nom, n))

print("-" * 40)
print("%-26s %d" % ("TOTAL", total))

contenu = (
    "-- Fichier genere par outils/compter_total.py - NE PAS EDITER.\n"
    "-- Le nombre EXACT de textes traduits, compte a la fabrication.\n"
    "-- (pairs() au login ratait les bases paresseuses : ~770k de moins.)\n"
    "--\n"
    "-- Sur AscensionFR (racine), PAS sur AscensionFR.DB : DB ne doit contenir\n"
    "-- que des TABLES (plusieurs modules font pairs() sur chaque membre de\n"
    "-- DB ; un nombre les ferait planter -- vecu, Minimap.lua le 24/07).\n"
    "AscensionFR.TotalTextes = %d\n" % total)

if ECRIRE:
    io.open(META, "w", encoding="utf-8", newline="").write(contenu)
    print("")
    print("ecrit -> " + META)
else:
    print("")
    print("APERCU. --ecrire pour graver DB_Meta.lua")
