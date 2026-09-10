# -*- coding: utf-8 -*-
"""
HARMONISATION des noms dans les descriptions réparées (24/07/2026).
===================================================================
Google rend parfois le nom substitué en QUASI-variante : apostrophe
typographique (« d’aube »), élision différente (« d'aube » pour
« de l'aube »), casse. Ces variantes sont du français — les passes de
réparation ne les voient plus. Cette passe hors-ligne (aucun réseau)
compare chaque morceau COLORÉ des descriptions à la table des noms via
une clé tolérante, et normalise vers la forme EXACTE de la table.

Clé tolérante : minuscules, ’ -> ', et équivalence « d'X » <-> « de l'X ».
Le remplacement n'a lieu que sur correspondance de clé COMPLÈTE — jamais
de rapprochement flou.

Usage : python outils/harmoniser_noms_repares.py
"""
import io
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTS = os.path.join(BASE, "traductions", "sorts.json")

RE_COLORE = re.compile(r"\|c[fF]{2}[0-9a-fA-F]{6}([^|]{2,60})\|r")


def cle_tolerante(texte):
    t = texte.strip().lower().replace("’", "'")
    # « de l'aube » et « d'aube » deviennent la même clé.
    t = re.sub(r"\bde l'", "d'", t)
    t = re.sub(r"\bde la ", "d'", t)
    t = re.sub(r"\s+", " ", t)
    return t


def main():
    with io.open(SORTS, encoding="utf-8") as f:
        donnees = json.load(f)
    noms = donnees.get("noms", {})
    descs = donnees.get("descriptions", {})

    # Plusieurs valeurs de la table peuvent partager la même clé tolérante
    # (« Guerrier d’aube » ET « Guerrier de l'aube » y cohabitent). On
    # garde la MEILLEURE forme : apostrophe droite d'abord, puis la plus
    # longue (élision complète « de l' » plutôt que « d' »).
    def score(v):
        return (0 if "’" in v else 1, len(v))

    canon = {}
    for fr in noms.values():
        cle = cle_tolerante(fr)
        if cle not in canon or score(fr) > score(canon[cle]):
            canon[cle] = fr

    remplaces = 0
    exemples = []
    for en, fr in descs.items():
        if "|c" not in fr:
            continue
        nouveau = fr
        for morceau in set(RE_COLORE.findall(fr)):
            brut = morceau.strip()
            bon = canon.get(cle_tolerante(brut))
            if bon and bon != brut:
                nouveau = nouveau.replace(morceau, bon)
        if nouveau != fr:
            descs[en] = nouveau
            remplaces += 1
            if len(exemples) < 5:
                exemples.append((fr[:70], nouveau[:70]))

    with io.open(SORTS, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("descriptions harmonisées :", remplaces)
    for avant, apres in exemples:
        print("  avant :", avant)
        print("  après :", apres)


if __name__ == "__main__":
    main()
