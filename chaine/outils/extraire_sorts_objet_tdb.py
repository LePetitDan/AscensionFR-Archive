# -*- coding: utf-8 -*-
"""Extrait, du TDB item_template, tous les sorts references par des objets
(spellid_1..5), puis croise pour trouver ceux qui MANQUENT a DB_Sorts et qui
ONT un texte a afficher.

Positions (1-indexees) dans item_template : entry=1, spellid_1=67, _2=74,
_3=81, _4=88, _5=95. Chaque objet a jusqu'a 5 sorts (a l'usage, a l'equipement,
en proc...). L'effet « Utiliser : ... » est la DESCRIPTION du sort.
"""
import io
import json
import os
import re

SQL = (r"D:\AscensionFR\WorkFlow\sources"
       r"\TDB_full_world_335.25101_2025_10_21.sql")
CLIENT = r"D:\AscensionFR\WorkFlow\sources\dbc\spells_Ascension.json"
DB_SORTS = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
            r"\AscensionFR\DB\DB_Sorts.lua")

POS_SPELLS = (67, 74, 81, 88, 95)   # colonnes spellid_1..5


def champs(tuple_str):
    """Decoupe un tuple SQL en champs, en respectant les chaines '...'."""
    out, i, n = [], 0, len(tuple_str)
    cur = []
    dans_chaine = False
    while i < n:
        c = tuple_str[i]
        if dans_chaine:
            if c == "\\":
                cur.append(c)
                if i + 1 < n:
                    cur.append(tuple_str[i + 1])
                    i += 2
                    continue
            elif c == "'":
                if i + 1 < n and tuple_str[i + 1] == "'":   # '' echappe
                    cur.append("'")
                    i += 2
                    continue
                dans_chaine = False
                i += 1
                continue
            cur.append(c)
            i += 1
        else:
            if c == "'":
                dans_chaine = True
                i += 1
            elif c == ",":
                out.append("".join(cur))
                cur = []
                i += 1
            else:
                cur.append(c)
                i += 1
    out.append("".join(cur))
    return out


# --- 1. sorts references par les objets ----------------------------------
refs = set()
dans_dump = False
lignes_traitees = 0
TUPLE = re.compile(r"\(((?:[^()']|'(?:[^'\\]|\\.|'')*')*)\)")
with io.open(SQL, encoding="utf-8", errors="replace") as f:
    for ligne in f:
        if "LOCK TABLES `item_template`" in ligne:
            dans_dump = True
        if dans_dump and "UNLOCK TABLES" in ligne:
            break
        if not dans_dump or "INSERT INTO `item_template`" not in ligne:
            continue
        for m in TUPLE.finditer(ligne):
            ch = champs(m.group(1))
            if len(ch) < 95:
                continue
            for pos in POS_SPELLS:
                try:
                    sid = int(ch[pos - 1])
                except (ValueError, IndexError):
                    continue
                if sid > 0:
                    refs.add(sid)
        lignes_traitees += 1

print("lignes INSERT item_template traitees : %d" % lignes_traitees)
print("sorts DISTINCTS references par des objets : %d" % len(refs))

# --- 2. lesquels ont un texte a afficher (client) ------------------------
client = json.load(io.open(CLIENT, encoding="utf-8"))
avec_texte = {s for s in refs
              if str(s) in client and (client[str(s)].get("D")
                                       or client[str(s)].get("T"))}
print("  dont AVEC description/bulle : %d" % len(avec_texte))

# --- 3. lesquels manquent a DB_Sorts -------------------------------------
presents = set()
with io.open(DB_SORTS, encoding="utf-8", errors="replace") as f:
    for ligne in f:
        for m in re.finditer(r"\[(\d+)\]=", ligne):
            presents.add(int(m.group(1)))
manquants = sorted(avec_texte - presents)
print("  dont MANQUANTS a DB_Sorts   : %d" % len(manquants))

# --- 4. echantillon + sauvegarde -----------------------------------------
print("")
print("=== echantillon des sorts d'objet manquants ===")
for s in manquants[:15]:
    v = client[str(s)]
    print("  %-8s %-26s %s" % (s, (v.get("N") or "")[:25],
                               (v.get("D") or v.get("T") or "")[:50]))

# Dans rapports/, comme tout relevé — jamais un chemin de machine en dur
# (l'ancien pointait un dossier temporaire personnel : parti avec le prog. 33).
sortie = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "rapports", "sorts_objet_manquants.json")
os.makedirs(os.path.dirname(sortie), exist_ok=True)
io.open(sortie, "w", encoding="utf-8").write(
    json.dumps(manquants, ensure_ascii=False))
print("")
print("liste -> " + sortie)
