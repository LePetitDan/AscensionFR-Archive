# -*- coding: utf-8 -*-
"""
Étend les cibles de traduction aux SORTS RÉFÉRENCÉS par nos sorts cibles.
=========================================================================
(Chantier du 24/07/2026 — les blocs d'aura incrustés des talents :
« Scarlet Hammer », « Sacred Restraint »… restaient anglais parce que ces
sorts, non lançables par le joueur, échappaient au filtre SkillLine.)

Deux gisements de références, relevés dans les MODÈLES ANGLAIS (DE) des
sorts déjà ciblés (DB_Sorts.lua) :
  1. les NOMS COLORÉS |cff……|r — résolus en identifiants via l'index
     nom -> id de l'extraction complète (toutes les homonymies sont
     prises : une cible de trop ne coûte qu'une traduction) ;
  2. les renvois DIRECTS @s:<id> et $@spelldesc<id>.

Sortie : traductions/sorts_references.json (liste d'identifiants), lue
par generateur_sorts.py comme les récoltes.
Usage : python outils/extraire_sorts_references.py
"""
import io
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_SORTS = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
            r"\AscensionFR\DB\DB_Sorts.lua")
EXTRACTION = os.path.join(BASE, "sources", "dbc", "spells_Ascension.json")
SORTIE = os.path.join(BASE, "traductions", "sorts_references.json")

RE_ENTREE = re.compile(r'^DB\[(\d+)\]=')
RE_DE = re.compile(r'DE="((?:\\.|[^"\\])*)"')
RE_COLORE = re.compile(r"\|c[fF]{2}[0-9a-fA-F]{6}([^|]{2,60})\|r")
RE_RENVOI = re.compile(r"@s:(\d+)|\$@spelldesc(\d+)")


def main():
    with io.open(EXTRACTION, encoding="utf-8") as f:
        extraction = json.load(f)
    par_nom = {}
    for sid, fiche in extraction.items():
        nom = (fiche.get("N") or "").strip()
        if len(nom) >= 3:
            par_nom.setdefault(nom, []).append(sid)

    deja = set()
    references = set()
    with io.open(DB_SORTS, encoding="utf-8") as f:
        for ligne in f:
            m = RE_ENTREE.match(ligne)
            if not m:
                continue
            deja.add(m.group(1))
            de = RE_DE.search(ligne)
            if not de:
                continue
            texte = de.group(1)
            for a, b in RE_RENVOI.findall(texte):
                references.add(a or b)
            for morceau in RE_COLORE.findall(texte):
                for sid in par_nom.get(morceau.strip(), ()):
                    references.add(sid)

    nouvelles = sorted(references - deja, key=int)
    with io.open(SORTIE, "w", encoding="utf-8") as f:
        json.dump(nouvelles, f, indent=1)
    print("sorts déjà ciblés        :", len(deja))
    print("références relevées      :", len(references))
    print("NOUVELLES cibles écrites :", len(nouvelles))
    print("sortie :", SORTIE)


if __name__ == "__main__":
    main()
