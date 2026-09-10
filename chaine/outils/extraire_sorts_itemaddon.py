# -*- coding: utf-8 -*-
r"""Extrait les SPELLID d'ItemAddon.dbc (colonnes c40/c43/c47, repérées
par sondage le 22/07/2026 — témoin : 330032 « Keeper's Scroll:
Khaz'goroth » porte 993955 en c40) -> sources/dbc/itemaddon_sorts.json
{id: [spellids]}.

Les valeurs non-sorts éventuelles sont inoffensives : l'addon ignore tout
identifiant absent de DB_Sorts au moment d'aligner.

Usage : python outils/extraire_sorts_itemaddon.py
"""
import io
import json
import os
import struct
import sys

from mpyq import MPQArchive

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MPQ = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Data\patch-M.MPQ"
SORTIE = os.path.join(BASE, "sources", "dbc", "itemaddon_sorts.json")
COLONNES = (40, 43, 47)

archive = MPQArchive(MPQ, listfile=True)
donnees = archive.read_file(b"DBFilesClient\\ItemAddon.dbc")
if not donnees:
    raise SystemExit("ItemAddon.dbc introuvable dans patch-M")
_, n_enr, n_champs, taille_enr, _ = struct.unpack("<4s4I", donnees[:20])
n32 = taille_enr // 4
base = 20

sortie = {}
for i in range(n_enr):
    pos = base + i * taille_enr
    valeurs = struct.unpack("<%dI" % n32, donnees[pos:pos + n32 * 4])
    sorts = []
    for k in COLONNES:
        v = valeurs[k]
        if v > 100 and v not in sorts:
            sorts.append(v)
    if sorts:
        sortie[str(valeurs[0])] = sorts

with io.open(SORTIE, "w", encoding="utf-8") as f:
    json.dump(sortie, f, ensure_ascii=False)
print("objets avec sorts :", len(sortie), "/", n_enr)
print("témoin 330032 :", sortie.get("330032"))
