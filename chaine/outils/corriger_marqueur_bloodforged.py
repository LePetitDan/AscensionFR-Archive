# -*- coding: utf-8 -*-
"""Restaure le marqueur « Bloodforged » qu'on avait traduit à tort.

Le client d'Ascension affiche un tag `@|cFFCC0000Bloodforged|r@` sur ~40 000
objets ameliores. C'est une DIRECTIVE DU CLIENT (marqueur @...@), pas de la
prose : le client la reconnait a son texte EXACT anglais. On l'avait traduite
en « Bloodforgé » -> le client ne la reconnait plus -> elle fuit a l'ecran
(signalement de Dan, 24/07/2026).

Verifie : « Bloodforgé » n'apparait QUE dans ce marqueur (39 102 fois, forme
unique). Le remplacement est donc sans risque pour les noms d'objets (qui
disent « forge par le sang », pas « Bloodforge »).

Meme famille de piege que la case « Search » des metiers, les filtres de
l'HdV, ONEQUIP : un texte relu par le client comme cle ne se traduit pas.

Usage : python outils/corriger_marqueur_bloodforged.py [--ecrire]
"""
import io
import os
import sys

import lupa.lua51 as lupa_mod

ECRIRE = "--ecrire" in sys.argv

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(r"D:\AscensionFR\WOW_Priv\resources\ascension-live",
                  r"Interface\AddOns\AscensionFR\DB")
STORES = os.path.join(BASE, "traductions")

CASSE = "@|cFFCC0000Bloodforgé|r@"
BON = "@|cFFCC0000Bloodforged|r@"


def compile_ok(texte):
    for _ in range(5):
        try:
            lupa_mod.LuaRuntime().compile(texte)
            return True
        except Exception as e:
            if "constant table overflow" not in str(e):
                return False
    return False


total = 0
print("=== bases (.lua) ===")
for nom in sorted(os.listdir(DB)):
    if not nom.endswith(".lua"):
        continue
    chemin = os.path.join(DB, nom)
    texte = io.open(chemin, encoding="utf-8").read()
    n = texte.count(CASSE)
    if n:
        neuf = texte.replace(CASSE, BON)
        ok = compile_ok(neuf)
        print("  %-24s %6d marqueur(s)  %s"
              % (nom, n, "compile OK" if ok else "REFUSÉ"))
        if ok:
            if ECRIRE:
                io.open(chemin, "w", encoding="utf-8", newline="").write(neuf)
            total += n

print("")
print("=== magasins (.json) — texte brut, remplacement direct ===")
for nom in sorted(os.listdir(STORES)):
    if not nom.endswith(".json"):
        continue
    chemin = os.path.join(STORES, nom)
    texte = io.open(chemin, encoding="utf-8").read()
    # Dans le JSON, l'apostrophe des accents est encodee telle quelle ; le
    # marqueur y est donc identique. Remplacement brut sur le fichier.
    n = texte.count(CASSE)
    if n:
        print("  %-24s %6d marqueur(s)" % (nom, n))
        if ECRIRE:
            io.open(chemin, "w", encoding="utf-8", newline="").write(
                texte.replace(CASSE, BON))
        total += n

print("")
print("TOTAL : %d marqueurs restaurés" % total)
print("MODE : " + ("ÉCRITURE" if ECRIRE else "APERÇU"))
