# -*- coding: utf-8 -*-
r"""Génère DB\DB_QuetesObjectifs.lua : les OBJECTIFS-PHRASES de quêtes
(« Speak to Dirania Silvershine in Shadowglen. ») anglais -> français.
Jointure par identifiant : quest_template du TDB (colonne Objectives, la
position est lue dans le CREATE TABLE — jamais devinée) × le champ
Objectives de sources\frFR\quest_template_locale.json.
Consommé par l'intercepteur global : suivi de base, DragonUI, partout.
"""
import glob
import io
import json
import re

SQL = glob.glob(r"D:\AscensionFR\WorkFlow\sources\TDB_full_*.sql")[0]


def tuples_sql(ligne):
    """Découpe les tuples (...) d'une ligne INSERT en champs bruts.
    (Copie locale — importer generer_noms_objets exécuterait son script.)"""
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
SORTIE = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
          r"\AscensionFR\DB\DB_QuetesObjectifs.lua")

# 1. Position de la colonne Objectives, lue dans le CREATE TABLE
colonnes = []
with io.open(SQL, encoding="utf-8", errors="replace") as f:
    dans_table = False
    for ligne in f:
        if ligne.startswith("CREATE TABLE `quest_template`"):
            dans_table = True
            continue
        if dans_table:
            m = re.match(r"\s*`(\w+)`", ligne)
            if m:
                colonnes.append(m.group(1))
            elif ligne.strip().startswith(")"):
                break
# nommage moderne de ce TDB : ID + LogDescription (= le texte du suivi)
pos_entry = colonnes.index("ID")
pos_obj = colonnes.index("LogDescription")
print("colonnes quest_template :", len(colonnes),
      "| ID =", pos_entry, "| LogDescription =", pos_obj)

# 2. Anglais par id
anglais = {}
with io.open(SQL, encoding="utf-8", errors="replace") as f:
    for ligne in f:
        if not ligne.startswith("INSERT INTO `quest_template`"):
            continue
        for champs in tuples_sql(ligne):
            if len(champs) > pos_obj:
                try:
                    anglais[int(champs[pos_entry])] = champs[pos_obj]
                except ValueError:
                    pass
print("objectifs anglais :", len(anglais))

# 3. Français par id + jointure
locale = json.load(io.open(
    r"D:\AscensionFR\WorkFlow\sources\frFR\quest_template_locale.json",
    encoding="utf-8"))
pont = {}
for cle, v in locale.items():
    fr = isinstance(v, dict) and v.get("Objectives")
    if not fr:
        continue
    try:
        en = anglais.get(int(cle))
    except ValueError:
        continue
    if not en or not en.strip() or en == fr:
        continue
    en = en.strip()
    deja = pont.get(en)
    if deja is None:
        pont[en] = fr.strip()
    elif deja != fr.strip():
        pont[en] = False
retenus = sorted((en, fr) for en, fr in pont.items() if fr)
print("paires du pont :", len(retenus),
      "| doublons neutralisés :", sum(1 for v in pont.values() if not v))

def echapper(t):
    t = t.replace("\\", "\\\\").replace('"', '\\"')
    return t.replace("\r", "\\r").replace("\n", "\\n")

lignes = ["-- Fichier GÉNÉRÉ par outils/generer_objectifs_quetes.py — pont",
          "-- [objectif anglais] = objectif français (TDB × locale frFR).",
          "local DB = AscensionFR.DB.QuetesObjectifs"]
for en, fr in retenus:
    lignes.append('DB["%s"]="%s"' % (echapper(en), echapper(fr)))
with io.open(SORTIE, "w", encoding="utf-8") as f:
    f.write("\n".join(lignes) + "\n")
print("écrit : DB_QuetesObjectifs.lua")
