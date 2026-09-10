# -*- coding: utf-8 -*-
r"""Génère DB\DB_ObjetsNoms.lua : le PONT nom anglais -> nom français des
objets. Jointure par identifiant :
- anglais : item_template du TDB officiel (sources\TDB_full_*.sql, colonne
  name en 5e position du tuple) ;
- français : traductions\objets.json (id -> {N}).
Sert aux textes qui ne portent que le NOM (objectifs de collecte du suivi,
messages jaunes, popups de destruction, bulles de monstres).
Doublons anglais à français DIVERGENT : neutralisés (prudence).
"""
import glob
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chemin_client import DB as _DB, exiger_client  # noqa: E402

exiger_client("generer_noms_objets (pont des noms d'objets)")
SQL = glob.glob(r"D:\AscensionFR\WorkFlow\sources\TDB_full_*.sql")[0]
SORTIE = os.path.join(_DB, "DB_ObjetsNoms.lua")

# 1. Français par id : l'OFFICIEL d'abord (item_template_locale), puis nos
# traductions custom par-dessus (objets.json prime — plus récent).
francais = {}
officiel = json.load(io.open(
    r"D:\AscensionFR\WorkFlow\sources\frFR\item_template_locale.json",
    encoding="utf-8"))
for cle, v in officiel.items():
    if isinstance(v, dict) and v.get("Name"):
        try:
            francais[int(cle)] = v["Name"]
        except ValueError:
            pass
print("noms français officiels :", len(francais))
objets = json.load(io.open(r"D:\AscensionFR\WorkFlow\traductions\objets.json",
                           encoding="utf-8"))
for cle, v in objets.items():
    if isinstance(v, dict) and v.get("N"):
        try:
            francais[int(cle)] = v["N"]
        except ValueError:
            pass
print("avec nos customs :", len(francais))

# 2. Anglais par id depuis item_template (streaming, tuples SQL)
def tuples_sql(ligne):
    """Découpe les tuples (...) d'une ligne INSERT en champs bruts."""
    i, n = ligne.find("("), len(ligne)
    while 0 <= i < n:
        champs, courant, en_chaine, echappe = [], [], False, False
        j = i + 1
        while j < n:
            c = ligne[j]
            if en_chaine:
                if echappe:
                    courant.append(c)
                    echappe = False
                elif c == "\\":
                    echappe = True
                elif c == "'":
                    en_chaine = False
                else:
                    courant.append(c)
            else:
                if c == "'":
                    en_chaine = True
                elif c == ",":
                    champs.append("".join(courant))
                    courant = []
                elif c == ")":
                    champs.append("".join(courant))
                    yield champs
                    break
                else:
                    courant.append(c)
            j += 1
        i = ligne.find("(", j)

anglais = {}
with io.open(SQL, encoding="utf-8", errors="replace") as f:
    for ligne in f:
        if not ligne.startswith("INSERT INTO `item_template`"):
            continue
        for champs in tuples_sql(ligne):
            if len(champs) > 4:
                try:
                    anglais[int(champs[0])] = champs[4]
                except ValueError:
                    pass
print("noms anglais (item_template) :", len(anglais))

# 3. Jointure + neutralisation des doublons divergents
import sys as _sys
_sys.path.insert(0, r"D:\AscensionFR\WorkFlow\outils")
from generateur_db import polir  # noqa: E402

pont = {}
for iid, en in anglais.items():
    fr = francais.get(iid)
    if not fr or not en or en == fr:
        continue
    # Le français vient de sources/frFR/item_template_locale.json, l'officiel
    # 3.3.5a, qui n'accentuait pas les majuscules initiales (515 noms mesurés).
    fr = polir(fr, anglais=en)
    deja = pont.get(en)
    if deja is None:
        pont[en] = fr
    elif deja != fr:
        pont[en] = False
print("paires par ID :", sum(1 for v in pont.values() if v),
      "| doublons neutralisés :", sum(1 for v in pont.values() if not v))

# 3 bis (22/07/2026) : le MÉGA-LOT ItemAddon (traductions/objets_dbc.json,
# paires texte directes, purgées des codes internes). Les jointures par ID
# priment : le lot ne remplit que les trous.
import sys
sys.path.insert(0, r"D:\AscensionFR\WorkFlow\outils")
from garde_packfr import texte_sain
lot = json.load(io.open(
    r"D:\AscensionFR\WorkFlow\traductions\objets_dbc.json",
    encoding="utf-8"))
n_lot = 0
for en, fr in lot.get("noms", {}).items():
    if len(en) < 3 or not fr or en == fr or en in pont:
        continue
    if not texte_sain(fr):
        continue
    # Même traitement que la jointure par ID : sans lui, la moitié du pont
    # serait accentuée et l'autre non.
    pont[en] = polir(fr, anglais=en)
    n_lot += 1
print("paires du méga-lot ajoutées :", n_lot)

retenus = [(en, fr) for en, fr in pont.items() if fr]
retenus.sort()
print("paires du pont :", len(retenus))

def echapper(t):
    return t.replace("\\", "\\\\").replace('"', '\\"')

lignes = ["-- Fichier GÉNÉRÉ par outils/generer_noms_objets.py — pont",
          "-- [nom anglais] = nom français des objets (TDB × objets.json).",
          "local DB = AscensionFR.DB.ObjetsNoms"]
for en, fr in retenus:
    lignes.append('DB["%s"]="%s"' % (echapper(en), echapper(fr)))
print("paires à poser : %d" % len(retenus))

# Base PARESSEUSE par texte (22/07 : avec le méga-lot, des centaines de
# milliers de noms résidents pèseraient sur le ménage du jeu).
# On ne pose JAMAIS la version plate sur le chemin livré : à ~388 000
# constantes, elle dépasse de 48 % ce que Lua 5.1 accepte, donc elle ne se
# charge pas. paresseux_textes.poser() écrit à côté et ne déplace qu'en cas
# de succès — avant, une conversion ratée laissait ce fichier mort en place
# en affichant « la base plate reste valable ».
import paresseux_textes  # noqa: E402
if not paresseux_textes.poser(SORTIE, "\n".join(lignes) + "\n",
                              "AscensionFR.DB.ObjetsNoms"):
    raise SystemExit(1)
