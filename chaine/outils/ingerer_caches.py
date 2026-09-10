# -*- coding: utf-8 -*-
"""
Verse les caches envoyés par les joueurs dans l'usine de traduction.

Le Compagnon (v1.5+) joint au rapport un fichier caches_*.json.gz : les
textes anglais que le client du joueur garde en cache (quêtes, PNJ, objets…),
déjà parsés au format de parser_wdb. Ce script :

  1. lit les rapports/auto_*_caches_*.json.gz pas encore traités ;
  2. valide et filtre (royaume Conquest of Azeroth, clés numériques,
     champs attendus uniquement — rien d'inconnu n'entre dans l'usine) ;
  3. fusionne le tout dans rapports/caches/fusion/<base>.json — le dossier
     que generateur_db superpose aux extraits locaux (priorité au local).

La traduction elle-même reste le travail de l'usine (traducteur_fr) : ici on
ne fait qu'apporter la matière première. Idempotent : chaque fichier n'est
versé qu'une fois (mémoire dans rapports/caches/ingeres.json).

Usage : python outils/ingerer_caches.py [--dry]
"""
import glob
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ecriture_sure import ecrire_json  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAPPORTS = os.path.join(BASE, "rapports")
DOSSIER_FUSION = os.path.join(RAPPORTS, "caches", "fusion")
MEMOIRE = os.path.join(RAPPORTS, "caches", "ingeres.json")

# Bases attendues et champs autorisés (miroir de parser_wdb) : tout champ
# inconnu est jeté. Toutes les clés sont des identifiants numériques.
BASES = {
    "quetes":       {"Title", "Objectives", "Details", "EndText",
                     "CompletedText", "ObjectiveTexts"},
    "objets":       {"Name", "Description", "Spells"},
    "creatures":    {"Name", "SubName"},
    "objets_monde": {"Name", "CastBarCaption"},
    "textes_pnj":   {"Texts"},
    "pages":        {"Text", "NextPage"},
}


def nettoyer(base, entrees):
    """Ne garde que les entrées saines : clé numérique, valeur dict, champs
    de la liste blanche, types simples (str / int / liste)."""
    champs = BASES[base]
    propres = {}
    for cle, valeur in entrees.items():
        if not isinstance(cle, str) or not cle.isdigit():
            continue
        if not isinstance(valeur, dict):
            continue
        garde = {}
        for champ, v in valeur.items():
            if champ in champs and isinstance(v, (str, int, list)):
                garde[champ] = v
        if garde:
            propres[cle] = garde
    return propres


def main():
    dry = "--dry" in sys.argv
    fichiers = sorted(glob.glob(os.path.join(RAPPORTS,
                                             "auto_*caches_*.json.gz")))
    deja = set()
    if os.path.isfile(MEMOIRE):
        with open(MEMOIRE, encoding="utf-8") as f:
            deja = set(json.load(f))
    nouveaux = [f for f in fichiers if os.path.basename(f) not in deja]
    if not nouveaux:
        print("Caches des joueurs : rien de nouveau.")
        print("@@BILAN " + json.dumps({"tentees": 0, "traduites": 0,
                                       "refusees": 0,
                                       "ecartees": len(deja)}))
        return 0

    # La fusion existante, enrichie fichier par fichier (dernier arrivé
    # gagne entre joueurs ; le local de Dan gagnera toujours à la lecture,
    # voir generateur_db.ex()).
    fusion = {}
    for base in BASES:
        chemin = os.path.join(DOSSIER_FUSION, base + ".json")
        if os.path.isfile(chemin):
            with open(chemin, encoding="utf-8") as f:
                fusion[base] = json.load(f)
        else:
            fusion[base] = {}

    lus, neuves = 0, 0
    for chemin in nouveaux:
        nom = os.path.basename(chemin)
        deja.add(nom)              # même illisible : on ne retente pas sans fin
        try:
            with gzip.open(chemin, "rt", encoding="utf-8") as f:
                paquet = json.load(f)
        except Exception as e:
            print("  ! illisible %s : %s" % (nom, e))
            continue
        # On accepte TOUS les royaumes Ascension (Rexxar/Vol'jin = Conquest
        # of Azeroth, Darkmoon Wildcard, Dawnrise Freepick, saisonniers…).
        # La validation par liste blanche de champs + clés numériques
        # (nettoyer()) suffit à écarter le bruit ; et le local de Dan reste
        # prioritaire à la lecture (generateur_db.ex()). On exige juste le
        # bon format et un royaume non vide (un paquet sans royaume est
        # probablement corrompu). Avant, seul « Conquest of Azeroth » passait
        # -> les rapports de Darkmoon/Dawnrise étaient jetés (25/07/2026).
        royaume = str(paquet.get("royaume", "")).strip()
        if paquet.get("format") != 1 or not royaume:
            print("  - écarté (format inconnu ou royaume vide) : %s" % nom)
            continue
        apport = 0
        for base, entrees in (paquet.get("extraits") or {}).items():
            if base not in BASES or not isinstance(entrees, dict):
                continue
            for cle, valeur in nettoyer(base, entrees).items():
                if cle not in fusion[base]:
                    neuves += 1
                    apport += 1
                fusion[base][cle] = valeur
        lus += 1
        print("  + %s [%s] : %d entrée(s) inédite(s)" % (nom, royaume, apport))

    if not dry:
        # Atomiques (programme 31, bloc B) : la fusion D'ABORD, la mémoire
        # d'idempotence APRÈS — une coupure entre les deux re-verse au pire
        # un fichier déjà versé (bénin), jamais l'inverse.
        for base, entrees in fusion.items():
            ecrire_json(os.path.join(DOSSIER_FUSION, base + ".json"),
                        entrees)
        ecrire_json(MEMOIRE, sorted(deja), ensure_ascii=True)

    print("%d fichier(s) de caches lu(s), %d texte(s) de jeu versé(s) à "
          "l'usine." % (lus, neuves))
    # Les comptes du passage (programme 31, bloc F ; unités corrigées au
    # 32, bloc C) : on compte des FICHIERS des deux côtés — tentés = gz
    # nouveaux, faits = lus. Les TEXTES versés (11 810 un jour de vague)
    # restent dans la ligne humaine ci-dessus : mélanger les deux unités
    # faisait un verdict « 11810/2160 » et une règle de majorité absurde.
    print("@@BILAN " + json.dumps(
        {"tentees": len(nouveaux), "traduites": lus,
         "refusees": len(nouveaux) - lus,
         "ecartees": len(deja) - lus}))
    if neuves and not dry:
        print("Prochaine étape : lancer « Traduction FR - Ascension » "
              "(l'usine) pour traduire ces nouveautés.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
