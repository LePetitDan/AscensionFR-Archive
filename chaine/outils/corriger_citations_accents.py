# -*- coding: utf-8 -*-
r"""Rattrape les TEXTES de traductions/ qui citent un nom accentué sans son
accent (« Vous apprend Eclair de givre » → « … Éclair de givre »).

Le revers de la règle des accents du lot 7, programmé au bloc 2b du
28/07/2026. LA RÈGLE VIT DANS accents_majuscules.corriger_citations(),
appliquée par generateur_db.polir() à l'écriture des bases (toutes couches,
l'OFFICIELLE comprise — c'est elle qui porte le gros des citations non
accentuées). Cette passe-ci corrige le même défaut dans traductions/*.json,
sinon la forme fautive revient à chaque tour par les caches du moulin —
même doctrine que la règle des têtes.

Aperçu par défaut ; --ecrire applique, avec sauvegarde horodatée des
fichiers modifiés, puis RECOMPTE (le compte doit tomber à zéro).

Usage : python outils/corriger_citations_accents.py [--ecrire]
"""
import io
import json
import os
import shutil
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import accents_majuscules as am  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAD = os.path.join(BASE, "traductions")

# Les fichiers de traductions dont les VALEURS partent dans les bases.
# (gisement_brut et les caches de travail restent hors passe : ce sont des
# dépôts intermédiaires, pas des textes livrés.)
FICHIERS = [
    "sorts.json", "objets.json", "creatures.json", "quetes.json",
    "objets_monde.json", "textes_pnj.json", "gossip.json", "pages.json",
    "hautsfaits.json", "epreuves.json", "zones.json", "emotes.json",
    "ensembles.json", "libelles.json", "objets_dbc.json",
    "vanity_obtention.json", "boss.json", "interface_maison.json",
]


def textes_francais(donnees):
    """Itère (conteneur, clé, valeur_str) sur toutes les VALEURS textes d'un
    JSON de traductions, quelle que soit sa forme. Les CLÉS (anglaises) ne
    sont jamais touchées."""
    if isinstance(donnees, dict):
        for cle, valeur in donnees.items():
            if isinstance(valeur, str):
                yield donnees, cle, valeur
            elif isinstance(valeur, (dict, list)):
                yield from textes_francais(valeur)
    elif isinstance(donnees, list):
        for i, valeur in enumerate(donnees):
            if isinstance(valeur, str):
                yield donnees, i, valeur
            elif isinstance(valeur, (dict, list)):
                yield from textes_francais(valeur)


def main():
    ecrire = "--ecrire" in sys.argv
    table = am._table_citations()
    print("noms cités connus (≥ 2 mots, toutes sources) :", len(table))

    horodatage = time.strftime("%Y%m%d-%H%M%S")
    dossier_sauve = os.path.join(TRAD, "sauvegardes",
                                 "citations_accents_" + horodatage)
    total_textes = 0
    exemples = []
    for nom_fichier in FICHIERS:
        chemin = os.path.join(TRAD, nom_fichier)
        if not os.path.isfile(chemin):
            continue
        donnees = json.load(io.open(chemin, encoding="utf-8"))
        modifies = 0
        for conteneur, cle, valeur in list(textes_francais(donnees)):
            neuf = am.corriger_citations(valeur)
            if neuf != valeur:
                modifies += 1
                if len(exemples) < 5:
                    exemples.append((nom_fichier, valeur, neuf))
                if ecrire:
                    conteneur[cle] = neuf
        if modifies:
            print("  %-24s %4d texte(s)" % (nom_fichier, modifies))
            total_textes += modifies
            if ecrire:
                os.makedirs(dossier_sauve, exist_ok=True)
                shutil.copy2(chemin, os.path.join(dossier_sauve, nom_fichier))
                with io.open(chemin, "w", encoding="utf-8") as f:
                    json.dump(donnees, f, ensure_ascii=False, indent=1)
    print("TOTAL : %d texte(s) corrigés" % total_textes)
    for fichier, avant, apres in exemples:
        for a, b in zip(avant.split("\n"), apres.split("\n")):
            if a != b:
                print("  ex (%s) : %s" % (fichier, a.strip()[:90]))
                print("        -> : %s" % b.strip()[:90])
                break
    if not ecrire:
        print("\nAPERÇU seulement. Ajoute --ecrire pour appliquer "
              "(sauvegarde horodatée automatique).")
        return 0
    print("\nsauvegardes :", dossier_sauve)
    # RECOMPTE : la même passe relue doit rendre zéro.
    restants = 0
    for nom_fichier in FICHIERS:
        chemin = os.path.join(TRAD, nom_fichier)
        if not os.path.isfile(chemin):
            continue
        donnees = json.load(io.open(chemin, encoding="utf-8"))
        for _c, _k, valeur in textes_francais(donnees):
            if am.corriger_citations(valeur) != valeur:
                restants += 1
    print("RECOMPTE après passe : %d texte(s) restants (attendu : 0)"
          % restants)
    return 0 if restants == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
