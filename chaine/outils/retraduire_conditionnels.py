# -*- coding: utf-8 -*-
"""retraduire_conditionnels.py — dégèle les « $?…[texte][texte] » restés anglais.

POURQUOI (25/07/2026)
---------------------
Le bouclier du traducteur cachait le conditionnel EN ENTIER, crochets compris
(traducteur_fr.MOTIFS_PROTEGES, ancienne lecture). Google ne voyait donc jamais
le texte des branches : il revenait tel quel, en anglais, et le français en
gardait une copie mot pour mot. En jeu, le joueur lisait une description
française qui basculait en anglais au milieu d'une phrase.

Le bouclier est corrigé (traducteur_fr.MOTIF_BOUCLIER : on ne protège plus que
le SÉLECTEUR « $?s704635 »). Mais les traductions DÉJÀ faites, elles, restent
figées : rien ne les repasse. C'est le travail de cet outil, une fois.

CE QU'IL FAIT, ET SURTOUT CE QU'IL NE FAIT PAS
----------------------------------------------
Il ne retraduit PAS la description entière : le français déjà en place a pu
être relu, corrigé à la main, arbitré par Dan. Il ne touche QUE le conditionnel
figé, qu'il remplace à l'identique de position dans le texte français.

Usage :
    python outils/retraduire_conditionnels.py --echantillon 20   # montre, n'écrit rien
    python outils/retraduire_conditionnels.py                    # répare et écrit
"""
import argparse
import concurrent.futures
import io
import json
import os
import re
import shutil
import sys

# Cet outil imprime du texte de jeu traduit : la console de Dan est en cp1252,
# et un seul caractère hors de cette table lève UnicodeEncodeError et TUE le
# script. Règle valable pour tout outil du pipeline.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
from traducteur_fr import (MOTIF_BOUCLIER, PARALLELE,  # noqa: E402
                           traduire_google)

# Un conditionnel COMPLET. Le sélecteur ne contient pas d'espace ; les branches
# peuvent en contenir, et il y en a une ou deux.
COND = re.compile(r"\$\?[^\[\s]*(?:\[[^\]]*\])+")
BRANCHE = re.compile(r"\[([^\]]*)\]")
MOT = re.compile(r"[A-Za-z]{3}")

FICHIERS = ("sorts.json", "objets.json", "quetes.json", "divers.json",
            "objets_dbc.json", "sorts_recoltes.json", "creatures.json",
            "gossip.json", "pages.json", "objets_monde.json")


def a_traduire(conditionnel):
    """Une branche porte-t-elle du VRAI texte, une fois les codes ôtés ?

    « $?a704575[|cffffffff][|cffff3232] » n'a que des couleurs : rien à faire.
    """
    for branche in BRANCHE.findall(conditionnel):
        if MOT.search(MOTIF_BOUCLIER.sub("", branche)):
            return True
    return False


def figes(anglais, francais):
    """Les conditionnels de l'anglais recopiés tels quels dans le français."""
    vus, sortie = set(), []
    for c in COND.findall(anglais):
        if c not in vus and a_traduire(c) and c in francais:
            vus.add(c)
            sortie.append(c)
    return sortie


def recenser(data, chemin=()):
    """Parcourt un JSON de traduction -> (chemin, anglais, français)."""
    if not isinstance(data, dict):
        return
    for cle, valeur in data.items():
        if isinstance(valeur, str):
            if "$?" in cle:
                yield chemin, cle, valeur
        else:
            for x in recenser(valeur, chemin + (cle,)):
                yield x


def collecter(base):
    """Tous les cas à réparer, tous fichiers confondus."""
    cas = []
    for nom in FICHIERS:
        chemin = os.path.join(base, "traductions", nom)
        if not os.path.exists(chemin):
            continue
        with io.open(chemin, encoding="utf-8") as f:
            data = json.load(f)
        for sous_chemin, anglais, francais in recenser(data):
            bloques = figes(anglais, francais)
            if bloques:
                cas.append({"fichier": nom, "chemin": sous_chemin,
                            "en": anglais, "fr": francais,
                            "figes": bloques})
    return cas


def reparer(cas):
    """Traduit les conditionnels figés d'un cas. -> (français neuf, détail).

    Chaque détail est (anglais, français, motif) où motif vaut "traduit",
    "identique" (« [10 sec.][30 sec.] » : c'est déjà du français) ou
    "refuse" (traduire_google a rendu None — réseau coupé, ou un code
    technique abîmé par Google : mieux vaut l'anglais qu'un texte cassé).
    """
    neuf, detail = cas["fr"], []
    for conditionnel in cas["figes"]:
        traduit = traduire_google(conditionnel)
        if not traduit:
            detail.append((conditionnel, None, "refuse"))
        elif traduit == conditionnel:
            detail.append((conditionnel, None, "identique"))
        else:
            neuf = neuf.replace(conditionnel, traduit)
            detail.append((conditionnel, traduit, "traduit"))
    return neuf, detail


def ecrire(base, cas_repares):
    """Réécrit les fichiers, après sauvegarde de chacun."""
    par_fichier = {}
    for cas in cas_repares:
        par_fichier.setdefault(cas["fichier"], []).append(cas)
    for nom, liste in sorted(par_fichier.items()):
        chemin = os.path.join(base, "traductions", nom)
        secours = os.path.join(base, "traductions",
                               nom.replace(".json", "_avant_conditionnels.json"))
        if not os.path.exists(secours):
            shutil.copy2(chemin, secours)
            print("  sauvegarde -> %s" % os.path.basename(secours))
        with io.open(chemin, encoding="utf-8") as f:
            data = json.load(f)
        for cas in liste:
            table = data
            for etape in cas["chemin"]:
                table = table[etape]
            table[cas["en"]] = cas["neuf"]
        with io.open(chemin, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=True)
        print("  %-24s %d entrée(s) réparée(s)" % (nom, len(liste)))


EXPLICATION = {
    "identique": "(rien à traduire — c'est déjà du français)",
    "refuse": "(inchangé — Google a abîmé un code, l'anglais est conservé)",
}


def montrer(detail):
    court = lambda t: t.replace("\r", "").replace("\n", "\\n")  # noqa: E731
    for avant, apres, motif in detail:
        print("  EN : %s" % court(avant)[:300])
        print("  FR : %s" % (court(apres)[:300] if apres
                             else EXPLICATION[motif]))
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--echantillon", type=int, default=0,
                        help="n'en traite que N, et n'écrit rien")
    parser.add_argument("--base", default=BASE)
    args = parser.parse_args()

    cas = collecter(args.base)
    par_fichier = {}
    for c in cas:
        par_fichier[c["fichier"]] = par_fichier.get(c["fichier"], 0) + 1
    print("Conditionnels restés anglais : %d entrée(s)" % len(cas))
    for nom, n in sorted(par_fichier.items(), key=lambda x: -x[1]):
        print("  %-24s %d" % (nom, n))
    if not cas:
        return 0

    lot = cas[:args.echantillon] if args.echantillon else cas
    print()
    print("Traduction de %d entrée(s)%s..."
          % (len(lot), " (ÉCHANTILLON — rien ne sera écrit)"
             if args.echantillon else ""))
    print()

    with concurrent.futures.ThreadPoolExecutor(PARALLELE) as pool:
        resultats = list(pool.map(reparer, lot))

    repares, refuses, deja = [], 0, 0
    for c, (neuf, detail) in zip(lot, resultats):
        if args.echantillon:
            print("=== %s ===" % c["fichier"])
            montrer(detail)
        if neuf != c["fr"]:
            c["neuf"] = neuf
            repares.append(c)
        elif any(m == "refuse" for _, _, m in detail):
            refuses += 1
        else:
            deja += 1

    print("%d traduite(s), %d déjà en français, %d laissée(s) en anglais "
          "(Google a abîmé un code)." % (len(repares), deja, refuses))
    if args.echantillon:
        print()
        print("Échantillon : rien n'a été écrit. Relance sans --echantillon "
              "pour appliquer.")
        return 0
    print()
    ecrire(args.base, repares)
    print()
    print("Fait. Régénère les bases (generateur_sorts.py puis "
          "generateur_db.py) pour que l'addon en profite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
