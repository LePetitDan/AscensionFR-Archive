# -*- coding: utf-8 -*-
"""SCANNER DE TROUS : repère tout le texte d'interface encore anglais que
nos bases ne couvrent pas, SANS lancer le jeu.

Deux gisements :
1. Le code d'interface d'Ascension (XML + Lua des patchs) : les textes
   écrits EN DUR (text="...", SetText("...")) — c'est là que vivent les
   fenêtres custom (talents CoA, garde-robe...). Un attribut text= tout
   en MAJUSCULES_SOULIGNÉES est une CLÉ GlobalStrings (déjà couverte par
   ce circuit-là) : ignoré.
2. Les tables .dbc : colonnes de texte localisées, comparées à ce qu'on
   a déjà moissonné (liste blanche des tables traitées).

Sortie : rapports/trous_interface.json + un résumé lisible.
"""
import glob
import io
import json
import os
import re
import struct
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
from mpyq import MPQArchive

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Data"
ADDON = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR")

# Tables déjà moissonnées / arbitrées (par nos outils au fil du projet).
TABLES_CONNUES = {
    "spell", "achievement", "achievement_criteria", "areatable",
    "globalstrings", "emotestext", "emotestextdata", "chrspecs",
    "chrspecialization", "skillline", "skilllineability", "talent",
    "talenttab", "chartitles", "spellitemenchantment", "map",
    "worldmaparea", "worldmapcontinent", "faction", "factiongroup",
    "chrclasses", "chrraces", "itemsubclass", "creaturefamily",
    "mailtemplate", "challenge", "currencytypes", "lock",
    "spellshapeshiftform", "gemproperties", "itemrandomproperties",
    "itemrandomsuffix",
}

RE_CLE = re.compile(r"^[A-Z][A-Z0-9_]+$")
RE_ANGLAIS_PLAUSIBLE = re.compile(r"[A-Za-z]{3}.*[ a-z]")


def collecter_couverture():
    """Tous les textes EN que nos bases connaissent déjà (clés des paires
    texte->texte + valeurs EN des entrées à champs)."""
    couverts = set()
    for chemin in glob.glob(os.path.join(ADDON, "DB", "*.lua")):
        t = io.open(chemin, encoding="utf-8").read()
        for m in re.finditer(r'^(?:DB|C|J|T)\["((?:\\.|[^"\\])*)"\]', t,
                             re.M):
            couverts.add(m.group(1).replace('\\"', '"')
                         .replace("\\n", "\n").replace("\\r", "\r")
                         .replace("\\\\", "\\"))
    return couverts


def scanner_code(chemins_mpq, couverts):
    """Littéraux affichables du XML/Lua d'interface des patchs."""
    litteraux = Counter()          # texte -> occurrences
    fichiers_par_texte = {}
    for chemin in chemins_mpq:
        try:
            archive = MPQArchive(chemin, listfile=True)
            noms = [n.decode("latin-1") if isinstance(n, bytes) else n
                    for n in (archive.files or [])]
        except Exception:
            continue
        for nom in noms:
            bas = nom.lower()
            if not (bas.startswith("interface") and
                    (bas.endswith(".xml") or bas.endswith(".lua"))):
                continue
            try:
                d = archive.read_file(nom)
            except Exception:
                continue
            if not d:
                continue
            texte = d.decode("utf-8", "replace")
            trouves = []
            if bas.endswith(".xml"):
                trouves += re.findall(r'\btext="([^"]{3,120})"', texte)
            else:
                trouves += re.findall(
                    r'Set(?:Text|FormattedText)\(\s*"([^"]{3,120})"',
                    texte)
                trouves += re.findall(r'\btext\s*=\s*"([^"]{3,120})"',
                                      texte)
            for t in trouves:
                if RE_CLE.match(t):           # clé GlobalStrings : couvert
                    continue
                if not RE_ANGLAIS_PLAUSIBLE.search(t):
                    continue
                if "\\" in t or "/" in t and t.count("/") > 1:
                    continue                   # chemins de fichiers
                if t in couverts:
                    continue
                litteraux[t] += 1
                fichiers_par_texte.setdefault(t, set()).add(
                    nom.split("\\")[-1])
    return litteraux, fichiers_par_texte


def scanner_dbc(chemins_mpq):
    """Tables .dbc à colonnes de texte, hors liste des tables connues."""
    tables = {}
    for chemin in chemins_mpq:
        try:
            archive = MPQArchive(chemin, listfile=True)
            noms = [n.decode("latin-1") if isinstance(n, bytes) else n
                    for n in (archive.files or [])]
        except Exception:
            continue
        for nom in noms:
            if not nom.lower().endswith(".dbc"):
                continue
            table = nom.split("\\")[-1][:-4].lower()
            if table.replace("_ascension", "") in TABLES_CONNUES \
                    or table in TABLES_CONNUES:
                continue
            try:
                d = archive.read_file(nom)
            except Exception:
                continue
            if not d or d[:4] != b"WDBC":
                continue
            nb, champs, taille, bloc = struct.unpack("<4I", d[4:20])
            if not nb or bloc < 64:
                continue
            debut = 20 + nb * taille
            chaines = d[debut:debut + bloc]

            def texte(v):
                if v <= 0 or v >= len(chaines):
                    return ""
                fin = chaines.find(b"\0", v)
                return chaines[v:fin].decode("utf-8", "replace")

            n_textes, exemples = 0, []
            pas = max(1, nb // 200)
            # Certaines tables ont des champs compactés (taille du record
            # < champs x 4) : on ne lit que les entiers COMPLETS présents.
            n32 = min(champs, taille // 4)
            if n32 < 2:
                continue
            for i in range(0, nb, pas):
                base_l = 20 + i * taille
                if base_l + n32 * 4 > len(d):
                    break
                vals = struct.unpack("<%dI" % n32,
                                     d[base_l:base_l + n32 * 4])
                for v in vals[1:]:
                    t = texte(v)
                    if len(t) > 3 and RE_ANGLAIS_PLAUSIBLE.search(t) \
                            and " " in t:
                        n_textes += 1
                        if len(exemples) < 3:
                            exemples.append(t[:70])
                        break
            if n_textes:
                estime = n_textes * pas
                deja = tables.get(table)
                if not deja or estime > deja["estime"]:
                    tables[table] = {"estime": estime,
                                     "exemples": exemples}
    return tables


def main():
    chemins = (sorted(glob.glob(os.path.join(DATA, "*.MPQ")))
               + sorted(glob.glob(os.path.join(DATA, "enUS", "*.MPQ"))))
    print("bases de couverture...", flush=True)
    couverts = collecter_couverture()
    print("  textes EN connus de nos bases :", len(couverts), flush=True)

    print("scan du code d'interface (XML/Lua des patchs)...", flush=True)
    litteraux, fichiers = scanner_code(chemins, couverts)
    print("  littéraux affichables NON couverts :", len(litteraux))
    for t, n in litteraux.most_common(15):
        print("   %2dx %-60s (%s)" % (n, t[:60],
                                      ", ".join(sorted(fichiers[t])[:2])))

    print("scan des tables .dbc hors liste connue...", flush=True)
    tables = scanner_dbc(chemins)
    for table, info in sorted(tables.items(),
                              key=lambda x: -x[1]["estime"])[:15]:
        print("   ~%5d textes | %-28s ex: %s"
              % (info["estime"], table, info["exemples"][:1]))

    with io.open(os.path.join(BASE, "rapports", "trous_interface.json"),
                 "w", encoding="utf-8") as f:
        json.dump({"litteraux": {t: {"n": n,
                                     "fichiers": sorted(fichiers[t])}
                                 for t, n in litteraux.items()},
                   "tables": tables}, f, ensure_ascii=False, indent=1)
    print("rapport : rapports/trous_interface.json")


if __name__ == "__main__":
    main()
