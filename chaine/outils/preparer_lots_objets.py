# -*- coding: utf-8 -*-
"""Prépare les DEUX lots approuvés par Dan (22/07) :

1. VANITY : les textes d'obtention distincts (VanityCollection) ->
   a_traduire/vanity.json — le top le plus vu est traduit MAIN ailleurs.
2. ITEMADDON : la table des objets d'Ascension (id = id d'objet).
   - adoption d'abord : noms déjà connus du pont ObjetsNoms (officiel) ;
   - le reste (noms + descriptions distincts) -> a_traduire/objets_dbc_*.

Sortie aussi : sources/dbc/itemaddon_par_id.json {id: {N, D}} compact,
consommé par generateur_db pour poser les entrées par identifiant.
"""
import io
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(BASE, "sources", "dbc")


def charger(c):
    return json.load(io.open(c, encoding="utf-8"))


def main():
    # --- 1. Vanity ---
    v = charger(os.path.join(D, "vanitycollection.json"))
    obtention = Counter()
    for ligne in v["lignes"]:
        for c in ("c7", "c8", "c9", "c10", "c11", "c42"):
            t = ligne.get(c)
            if t and len(t) > 2:
                obtention[t.strip()] += 1
    deja = charger(os.path.join(BASE, "traductions",
                                "vanity_obtention.json")) \
        if os.path.exists(os.path.join(BASE, "traductions",
                                       "vanity_obtention.json")) \
        else {"paires": {}}
    file_vanity = [t for t in obtention
                   if t not in deja["paires"]]
    with io.open(os.path.join(BASE, "a_traduire", "vanity.json"), "w",
                 encoding="utf-8") as f:
        json.dump(sorted(file_vanity), f, ensure_ascii=False, indent=1)
    print("vanity : %d textes distincts, %d à traduire"
          % (len(obtention), len(file_vanity)))

    # --- 2. ItemAddon ---
    ia = charger(os.path.join(D, "itemaddon.json"))["lignes"]
    par_id = {}
    for ligne in ia:
        entree = {}
        if ligne.get("c2"):
            entree["N"] = ligne["c2"]
        if ligne.get("c19"):
            entree["D"] = ligne["c19"]
        if entree:
            par_id[ligne["id"]] = entree
    with io.open(os.path.join(D, "itemaddon_par_id.json"), "w",
                 encoding="utf-8") as f:
        json.dump(par_id, f, ensure_ascii=False)
    print("itemaddon : %d objets avec texte" % len(par_id))

    # Pont officiel des noms d'objets (DB_ObjetsNoms : DB["EN"]="FR")
    pont = {}
    chemin_pont = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface"
                   r"\AddOns\AscensionFR\DB\DB_ObjetsNoms.lua")
    for m in re.finditer(r'^DB\["((?:\\.|[^"\\])*)"\]="((?:\\.|[^"\\])*)"',
                         io.open(chemin_pont, encoding="utf-8").read(),
                         re.M):
        pont[m.group(1).replace('\\"', '"').replace("\\\\", "\\")] = 1

    cache_chemin = os.path.join(BASE, "traductions", "objets_dbc.json")
    cache = charger(cache_chemin) if os.path.exists(cache_chemin) \
        else {"noms": {}, "descriptions": {}}
    noms, descs = set(), set()
    for entree in par_id.values():
        n = entree.get("N")
        if n and n not in pont and n not in cache["noms"]:
            noms.add(n)
        d_ = entree.get("D")
        if d_ and d_ not in cache["descriptions"]:
            descs.add(d_)
    with io.open(os.path.join(BASE, "a_traduire", "objets_dbc_noms.json"),
                 "w", encoding="utf-8") as f:
        json.dump(sorted(noms), f, ensure_ascii=False, indent=1)
    with io.open(os.path.join(BASE, "a_traduire",
                              "objets_dbc_descriptions.json"), "w",
                 encoding="utf-8") as f:
        json.dump(sorted(descs), f, ensure_ascii=False, indent=1)
    print("files : %d noms + %d descriptions à traduire"
          % (len(noms), len(descs)))


if __name__ == "__main__":
    main()
