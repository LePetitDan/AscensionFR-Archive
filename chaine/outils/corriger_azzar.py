# -*- coding: utf-8 -*-
"""Normalise le nom propre « Azzar Faire » -> « Foire d'Azzar » dans les
VALEURS françaises des bases (le côté droit), jamais dans les clés anglaises
de recherche (le côté gauche, qui sert au pont EN->FR).

Le glossaire (traduire_gisement.py) corrige déjà les FUTURES traductions ;
ce script rattrape ce qui est DÉJÀ dans les bases livrées.

Formes fautives corrigées :
  « Azzar Faire » (ordre anglais), « Faire Azzar » (inversé),
  « foire Azzar » / « Foire Azzar » (sans le « d' »)  ->  « Foire d'Azzar »
On laisse « Foire d'Azzar » / « foire d'Azzar » (déjà français, corrects).

DEUX formats de base, deux traitements :
  - PLAT (DB["clé"]="valeur", [id]={N=,D=}) : on épargne la clé (suivie de
    « ]= ») et on corrige tout le reste.
  - PARESSEUX (DB_ObjetsNoms, DB_SortsNoms) : les seaux C[...] sont des CLÉS
    anglaises — JAMAIS touchés. Seul le côté droit des paires ["clé"]="valeur"
    des blocs M[...] est corrigé.

Vérification : chaque .lua modifié est recompilé (lupa) ; on n'écrit que si
tout compile.

Usage : python outils/corriger_azzar.py [--ecrire]
"""
import io
import os
import re
import sys

import lupa.lua51 as lupa_mod

ECRIRE = "--ecrire" in sys.argv

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORES = os.path.join(BASE, "traductions")
DB = os.path.join(r"D:\AscensionFR\WOW_Priv\resources\ascension-live",
                  r"Interface\AddOns\AscensionFR\DB")

PARESSEUX = {"DB_ObjetsNoms.lua", "DB_SortsNoms.lua"}

REMPLACEMENTS = [
    (re.compile(r"\bAzzar Faire\b"), "Foire d'Azzar"),
    (re.compile(r"\bFaire Azzar\b"), "Foire d'Azzar"),
    (re.compile(r"\bfoire Azzar\b"), "Foire d'Azzar"),
    (re.compile(r"\bFoire Azzar\b"), "Foire d'Azzar"),
]


def corrige(valeur):
    for motif, remplacant in REMPLACEMENTS:
        valeur = motif.sub(remplacant, valeur)
    return valeur


# --- chaîne « "..." » ; on la répare seulement si ce n'est pas une clé ------
CHAINE = re.compile(r'"((?:[^"\\]|\\.)*)"')


def corrige_plat(texte):
    n = [0]

    def rempl(m):
        contenu = m.group(1)
        # Une clé de table string est immédiatement suivie de « ] ».
        if texte[m.end():m.end() + 1] == "]":
            return m.group(0)
        neuf = corrige(contenu)
        if neuf != contenu:
            n[0] += 1
            return '"' + neuf + '"'
        return m.group(0)

    return CHAINE.sub(rempl, texte), n[0]


# --- paresseux : ne corriger que la VALEUR (après « ]=" ») des blocs M -----
VALEUR_M = re.compile(r'(\]=")((?:[^"\\]|\\.)*)(")')


def corrige_paresseux(texte):
    n = [0]
    resultat = []
    for ligne in texte.splitlines(keepends=True):
        if ligne.startswith("C["):
            # Seau de CLÉS anglaises : intouchable.
            resultat.append(ligne)
            continue

        def rempl(m):
            neuf = corrige(m.group(2))
            if neuf != m.group(2):
                n[0] += 1
                return m.group(1) + neuf + m.group(3)
            return m.group(0)

        resultat.append(VALEUR_M.sub(rempl, ligne))
    return "".join(resultat), n[0]


def compile_ok(texte, nom):
    # « constant table overflow » est INTERMITTENT chez lupa sur les gros
    # fichiers (25 Mo) — pas un vrai defaut (le jeu compile chaque seau
    # separement). On reessaie plusieurs fois : une compilation propre finit
    # par passer. Sur une VRAIE faute de syntaxe, les 5 essais echouent.
    derniere = ""
    for _ in range(5):
        try:
            lupa_mod.LuaRuntime().compile(texte)
            return True
        except Exception as e:
            derniere = str(e)[:80]
            if "constant table overflow" not in derniere:
                break                  # vraie erreur : inutile de reessayer
    print("  !! %s ne compile plus : %s" % (nom, derniere))
    return False


total = 0

print("=== bases (.lua) ===")
for nom in sorted(os.listdir(DB)):
    if not nom.endswith(".lua"):
        continue
    chemin = os.path.join(DB, nom)
    texte = io.open(chemin, encoding="utf-8").read()
    if nom in PARESSEUX:
        neuf, n = corrige_paresseux(texte)
    else:
        neuf, n = corrige_plat(texte)
    if n:
        ok = compile_ok(neuf, nom)
        etat = "compile OK" if ok else "REFUSÉ (non écrit)"
        print("  %-28s %3d valeur(s)   %s" % (nom, n, etat))
        if ok:
            if ECRIRE:
                io.open(chemin, "w", encoding="utf-8",
                        newline="").write(neuf)
            total += n          # ne compter QUE ce qui est réellement bon

print("")
print("=== magasins (.json), pour la durabilité ===")
import json
for nom in sorted(os.listdir(STORES)):
    if not nom.endswith(".json"):
        continue
    chemin = os.path.join(STORES, nom)
    try:
        donnees = json.load(io.open(chemin, encoding="utf-8"))
    except ValueError:
        continue
    if not isinstance(donnees, dict):
        continue
    n = 0
    for cle, val in list(donnees.items()):
        if isinstance(val, str):
            neuf = corrige(val)
            if neuf != val:
                donnees[cle] = neuf
                n += 1
    if n:
        print("  %-28s %3d valeur(s)" % (nom, n))
        if ECRIRE:
            io.open(chemin, "w", encoding="utf-8", newline="").write(
                json.dumps(donnees, ensure_ascii=False, indent=1,
                           sort_keys=True))
        total += n

print("")
print("TOTAL : %d corrections" % total)
print("MODE : " + ("ÉCRITURE" if ECRIRE else "APERÇU (rien écrit)"))
