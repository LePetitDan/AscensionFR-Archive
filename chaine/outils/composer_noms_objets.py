# -*- coding: utf-8 -*-
"""COMPOSEUR de noms d'objets (22/07 — accélérer SANS dégrader) :

Les noms en file sont massivement des COMPOSITIONS : base connue +
suffixe (« Sword of the Bear ») ou préfixe à deux-points (« Scroll of
Knowledge: X »). Le corpus OFFICIEL (item_template enUS x frFR par id)
enseigne les morceaux :
  1. paires de bases (nom officiel EN -> FR) ;
  2. paires de SUFFIXES apprises par décomposition du corpus, au vote
     majoritaire (« of the Bear » -> « de l'Ours ») ;
  3. paires de PRÉFIXES à deux-points, même méthode.
Puis on compose la file : qualité OFFICIELLE, zéro Google.

À lancer MOULIN ARRÊTÉ (écrit dans objets_dbc.json). --ecrire pour
appliquer.
"""
import io
import json
import os
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def charger(chemin):
    return json.load(io.open(chemin, encoding="utf-8"))


def main():
    ecrire = "--ecrire" in sys.argv
    en_i = charger(os.path.join(BASE, "sources", "enUS",
                                "item_template.json"))
    fr_i = charger(os.path.join(BASE, "sources", "frFR",
                                "item_template_locale.json"))

    officiel = {}
    for iid, loc in fr_i.items():
        nom_fr = loc.get("Name")
        e = en_i.get(iid, {})
        nom_en = e.get("name")
        if nom_fr and nom_en and nom_fr != nom_en:
            officiel.setdefault(nom_en, nom_fr)
    print("paires officielles de base :", len(officiel))

    # Apprentissage des suffixes : pour chaque paire officielle dont le
    # nom EN commence par une AUTRE base officielle + espace, le reste
    # des deux côtés forme une paire de suffixe candidate.
    suffixes = {}
    prefixes = {}
    for nom_en, nom_fr in officiel.items():
        # préfixe à deux-points : « Pattern: X » / « Patron : X »
        if ": " in nom_en:
            p_en, reste_en = nom_en.split(": ", 1)
            if " : " in nom_fr:
                p_fr, reste_fr = nom_fr.split(" : ", 1)
            elif ": " in nom_fr:
                p_fr, reste_fr = nom_fr.split(": ", 1)
            else:
                p_fr = None
            if p_fr and officiel.get(reste_en) == reste_fr:
                prefixes.setdefault(p_en, Counter())[p_fr] += 1
        # suffixe : « Base of the X »
        morceaux = nom_en.split(" ")
        for coupe in range(len(morceaux) - 1, 0, -1):
            base_en = " ".join(morceaux[:coupe])
            base_fr = officiel.get(base_en)
            if not base_fr:
                continue
            if not nom_fr.startswith(base_fr + " "):
                continue
            s_en = nom_en[len(base_en):]
            s_fr = nom_fr[len(base_fr):]
            if s_en and s_fr:
                suffixes.setdefault(s_en, Counter())[s_fr] += 1
            break

    def trancher(votes, minimum):
        sortie = {}
        for cle, compte in votes.items():
            (meilleur, n1) = compte.most_common(1)[0]
            if n1 >= minimum and n1 * 3 >= sum(compte.values()) * 2:
                sortie[cle] = meilleur
        return sortie

    suffixes = trancher(suffixes, 2)
    prefixes = trancher(prefixes, 2)
    print("suffixes appris :", len(suffixes),
          "| préfixes appris :", len(prefixes))
    for s in list(suffixes)[:5]:
        print("   %r -> %r" % (s, suffixes[s]))

    # Composition de la file
    file_ = charger(os.path.join(BASE, "a_traduire",
                                 "objets_dbc_noms.json"))
    cache_chemin = os.path.join(BASE, "traductions", "objets_dbc.json")
    cache = charger(cache_chemin)
    noms = cache["noms"]

    composes = {}
    for nom in file_:
        if nom in noms:
            continue
        fr = officiel.get(nom)
        if fr:
            composes[nom] = fr
            continue
        # préfixe « X: reste »
        if ": " in nom:
            p_en, reste = nom.split(": ", 1)
            p_fr = prefixes.get(p_en)
            reste_fr = officiel.get(reste) or noms.get(reste) \
                or composes.get(reste)
            if p_fr and reste_fr:
                composes[nom] = p_fr + " : " + reste_fr
                continue
        # base + suffixe (le plus long suffixe connu d'abord)
        for s_en in sorted(suffixes, key=len, reverse=True):
            if nom.endswith(s_en):
                base_en = nom[:-len(s_en)]
                base_fr = officiel.get(base_en) or noms.get(base_en) \
                    or composes.get(base_en)
                if base_fr:
                    composes[nom] = base_fr + suffixes[s_en]
                    break

    print("noms COMPOSABLES immédiatement :", len(composes),
          "sur", len([n for n in file_ if n not in noms]), "restants")
    for n in list(composes)[:6]:
        print("   %r -> %r" % (n[:50], composes[n][:60]))

    if ecrire:
        noms.update(composes)
        with io.open(cache_chemin, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=1,
                      sort_keys=True)
        print("écrit : %d compositions versées au réservoir"
              % len(composes))
    else:
        print("APERÇU seulement — relance avec --ecrire (moulin arrêté !)")


if __name__ == "__main__":
    main()
