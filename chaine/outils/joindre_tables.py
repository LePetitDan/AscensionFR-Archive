# -*- coding: utf-8 -*-
"""Apparie enUS x frFR par identifiant pour les tables extraites par
extraire_dbc_texte (chantier complétude) -> traductions/<sortie>.json
{ paires: {EN: FR} }. Mêmes règles partout : identiques écartés,
ambigus rejetés sauf majorité nette (2/3)."""
import io
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(BASE, "sources", "dbc")

TABLES = [
    ("areapoi", "poi_carte"),
    ("dungeonencounter", "boss"),
    ("itemset", "ensembles"),
]


def textes_par_id(chemin):
    d = json.load(io.open(chemin, encoding="utf-8"))
    # La colonne LOCALISÉE = la plus remplie (taux max) hors c1/c2
    # (souvent des noms internes) ; en repli, la plus remplie tout court.
    colonnes = {int(c): v for c, v in d["colonnes"].items()}
    candidates = sorted(colonnes, key=lambda c: -colonnes[c])
    haut = [c for c in candidates if c > 2] or candidates
    principale = "c%d" % haut[0]
    sortie = {}
    for ligne in d["lignes"]:
        t = ligne.get(principale)
        if t:
            sortie[ligne["id"]] = t
    return sortie


def main():
    for table, nom_sortie in TABLES:
        en = textes_par_id(os.path.join(D, table + ".json"))
        fr = textes_par_id(os.path.join(D, table + "_frfr.json"))
        votes = {}
        for ident, t_en in en.items():
            t_fr = fr.get(ident)
            if t_fr and t_fr != t_en:
                votes.setdefault(t_en, Counter())[t_fr] += 1
        paires, ambigus = {}, 0
        for t_en, compte in votes.items():
            if len(compte) == 1:
                paires[t_en] = next(iter(compte))
            else:
                (meilleur, n1) = compte.most_common(1)[0]
                if n1 * 3 >= sum(compte.values()) * 2:
                    paires[t_en] = meilleur
                else:
                    ambigus += 1
        chemin = os.path.join(BASE, "traductions",
                              nom_sortie + ".json")
        with io.open(chemin, "w", encoding="utf-8") as f:
            json.dump({"paires": paires}, f, ensure_ascii=False,
                      indent=1, sort_keys=True)
        exemple = next(iter(paires.items())) if paires else ("", "")
        print("%-18s : %4d paires (%d ambigus) | ex : %s -> %s"
              % (nom_sortie, len(paires), ambigus,
                 exemple[0][:32], exemple[1][:32]))


if __name__ == "__main__":
    main()
