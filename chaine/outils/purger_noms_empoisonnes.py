# -*- coding: utf-8 -*-
r"""Purge les noms empoisonnés de `traductions/`.

La table, le discriminant et le POURQUOI sont dans `outils/noms_empoisonnes.py`
— à lire avant de toucher à quoi que ce soit ici.

CE QUE CE SCRIPT PURGE
----------------------
  1. `traductions/sorts.json` section « noms » — la clé est SUPPRIMÉE, pas
     vidée : une chaîne vide serait un nom vide en jeu, alors qu'une clé
     absente laisse simplement l'anglais en place.
  2. `traductions/objets_dbc.json` section « noms » — les objets COMPOSÉS dont
     le nom reprend celui d'un sort empoisonné (« Mystic Scroll: Charged Ice »
     -> « Parchemin mystique : Epreuve de la Foi »). Ils sont fabriqués à
     partir du nom du sort : purger le sort sans eux laisserait 27 objets
     porter un nom que plus rien ne justifie.

CE QUE CE SCRIPT NE PURGE PAS, ET POURQUOI
------------------------------------------
  - `sources/packfr_sorts.json` (1 793 identifiants empoisonnés) : `sources/`
    est ré-extractible, une correction y disparaîtrait en silence. Le PackFR
    est filtré À LA LECTURE, dans `generer_noms_sorts.poser()`.
  - `sources/dbc/spells_frFR.json` : ses 5 occurrences sont l'officiel
    Blizzard, elles sont LÉGITIMES.
  - Les descriptions abîmées : elles se REPRENNENT depuis une sauvegarde, pas
    se suppriment (voir `--descriptions`).

SAUVEGARDES
-----------
Horodatées et INCONDITIONNELLES. Les outils du dépôt écrivent en général
« if not os.path.exists(sauvegarde) », ce qui veut dire qu'un second passage
ne sauvegarde plus rien : la deuxième purge écraserait alors l'état d'avant la
première sans filet. Ici chaque passage laisse sa propre copie.

Usage :
    python outils/purger_noms_empoisonnes.py                 # simulation
    python outils/purger_noms_empoisonnes.py --appliquer     # purge
    python outils/purger_noms_empoisonnes.py --descriptions  # les 3 abîmées
"""
import argparse
import io
import json
import os
import shutil
import sys
from collections import Counter
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from noms_empoisonnes import POISON, empoisonne  # noqa: E402
from accents_majuscules import corriger_tete  # noqa: E402

RAPPORT = os.path.join(BASE, "rapports", "purge_noms_empoisonnes.txt")
# La sauvegarde d'où l'on REPREND les descriptions abîmées : elle date d'avant
# la passe du 23/07 qui a incrusté le poison dans le texte.
REPLI_DESC = os.path.join(BASE, "traductions",
                          "sorts_avant_reparation_noms.json")

# La passe du 23/07 a fait DEUX choses en même temps : elle a incrusté le
# poison (le dégât) et elle a traduit de vrais noms de sorts (le progrès).
# Reprendre la sauvegarde annule les deux. On réapplique donc à la main les
# améliorations légitimes, sinon la réparation serait une régression sur les
# noms. Deux paires seulement, toutes deux vérifiées : ce sont les noms
# officiels Blizzard de Revenge et de Payback.
RETOUCHES = [
    ("|cFFFFFFFFRevenge|r", "|cFFFFFFFFVengeance|r"),
    ("|cFFFFFFFFPayback|r", "|cFFFFFFFFReprésailles|r"),
]


def charger(chemin):
    with io.open(chemin, encoding="utf-8") as f:
        return json.load(f)


def sauvegarder(chemin):
    """Copie horodatée, à chaque passage. Rend le chemin de la copie."""
    quand = datetime.now().strftime("%Y%m%d-%H%M%S")
    copie = chemin.replace(".json", "_avant_purge_%s.json" % quand)
    shutil.copy2(chemin, copie)
    return copie


def ecrire(chemin, donnees):
    with io.open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=1, sort_keys=True)


def paires_blizzard():
    """{nom EN officiel -> ses frFR officiels} — le juge de paix.

    La PAIRE, pas le seul nom : « la clé est connue de Blizzard » ne suffit
    pas. Une clé peut être un vrai nom Blizzard ET porter chez nous une
    valeur qui n'est pas la sienne — c'est même la définition du poison.
    On ne garde que si l'officiel traduit EXACTEMENT ce nom par cette valeur
    (le cas « Test of Faith » -> « Epreuve de la Foi »).
    """
    enus = charger(os.path.join(BASE, "sources", "dbc", "spells_enUS.json"))
    frfr = charger(os.path.join(BASE, "sources", "dbc", "spells_frFR.json"))

    def nom(d, sid):
        v = d.get(sid)
        return (v.get("N") if isinstance(v, dict) else v) or None

    out = {}
    for sid in enus:
        en, fr = nom(enus, sid), nom(frfr, sid)
        if en and fr:
            out.setdefault(en, set()).add(fr)
    return out


def purger_sorts(sorts, paires, journal):
    """Les clés de sorts.json/noms à supprimer. Rend (supprimées, gardées)."""
    a_jeter, gardees = [], []
    for cle, valeur in sorts["noms"].items():
        if valeur not in POISON:
            continue
        if not empoisonne(cle, valeur):
            gardees.append((cle, valeur))
            continue
        # Ceinture et bretelles : la table du module liste les porteurs
        # légitimes à la main ; on revérifie ici sur la SOURCE, pour qu'une
        # table mal remplie ne puisse pas jeter un vrai nom. La condition est
        # la PAIRE officielle exacte, pas la seule présence du nom chez
        # Blizzard — une clé Blizzard portant une valeur qui n'est pas la
        # sienne est du poison, pas un porteur. MODULO notre règle d'accent :
        # l'officiel écrit « Eclair de feu », nous « Éclair de feu » (lot 7) ;
        # sans ça, « Firebolt » serait purgé de sa propre traduction.
        officiels = paires.get(cle, ())
        if valeur in officiels or any(corriger_tete(o) == valeur
                                      for o in officiels):
            gardees.append((cle, valeur))
            journal.append("GARDÉ (paire officielle) : %r -> %r"
                           % (cle, valeur))
            continue
        a_jeter.append((cle, valeur))
    return a_jeter, gardees


def purger_objets(objets, poisons_sorts, journal):
    """Les objets COMPOSÉS dont le nom reprend celui d'un sort purgé.

    On ne se fie pas à la valeur seule : on exige que le SUFFIXE de la clé
    anglaise (après « : ») soit l'un des sorts qu'on vient de purger. Sans ça
    on jetterait un objet qui porterait légitimement ce nom.
    """
    a_jeter = []
    for cle, valeur in objets.get("noms", {}).items():
        if not isinstance(valeur, str):
            continue
        fin = valeur.rsplit(" : ", 1)[-1].strip()
        if fin not in POISON:
            continue
        suffixe = cle.split(": ", 1)[-1].strip()
        if suffixe in poisons_sorts:
            a_jeter.append((cle, valeur))
        else:
            journal.append("OBJET GARDÉ (sort non purgé) : %r -> %r"
                           % (cle, valeur))
    return a_jeter


def reparer_descriptions(sorts, journal, appliquer):
    """Reprend depuis la sauvegarde les descriptions où le poison s'est
    incrusté DANS le texte (le nom d'un sort cité a été remplacé par lui).

    On REPREND au lieu de substituer : les insertions portent plusieurs
    graphies et, sur au moins une description, elles ont écrasé DEUX noms
    anglais différents — une substitution ne saurait pas lequel rendre.
    """
    if not os.path.exists(REPLI_DESC):
        print("  ! sauvegarde de repli absente : %s" % REPLI_DESC)
        return 0
    vieux = charger(REPLI_DESC).get("descriptions", {})
    n = 0
    for cle, valeur in list(sorts["descriptions"].items()):
        if not isinstance(valeur, str):
            continue
        if not any(g in valeur for g in POISON):
            continue
        # Une description qui parle VRAIMENT du talent Test of Faith est
        # légitime : elle cite le sort, elle ne le remplace pas.
        if "Test of Faith" in cle:
            journal.append("DESCRIPTION GARDÉE (vrai Test of Faith) : %r"
                           % cle[:70])
            continue
        avant = vieux.get(cle)
        if not avant or any(g in avant for g in POISON):
            journal.append("DESCRIPTION NON REPRISE (pas de repli sain) : %r"
                           % cle[:70])
            continue
        repris = avant
        for source, cible in RETOUCHES:
            repris = repris.replace(source, cible)
        journal.append("DESCRIPTION REPRISE : %r" % cle[:70])
        journal.append("   - %s" % valeur[:150].replace("\n", "\\n"))
        journal.append("   + %s" % repris[:150].replace("\n", "\\n"))
        if repris != avant:
            journal.append("   (retouches réappliquées après reprise)")
        if appliquer:
            sorts["descriptions"][cle] = repris
        n += 1
    return n


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--appliquer", action="store_true")
    p.add_argument("--descriptions", action="store_true",
                   help="reprendre aussi les descriptions abîmées")
    args = p.parse_args()

    journal = []
    chemin_sorts = os.path.join(BASE, "traductions", "sorts.json")
    chemin_objets = os.path.join(BASE, "traductions", "objets_dbc.json")
    sorts, objets = charger(chemin_sorts), charger(chemin_objets)
    paires = paires_blizzard()
    print("paires officielles Blizzard (enUS x frFR) : %d" % len(paires))

    a_jeter, gardees = purger_sorts(sorts, paires, journal)
    print()
    print("sorts.json / noms")
    print("  entrées portant une valeur empoisonnée : %d"
          % (len(a_jeter) + len(gardees)))
    print("  À PURGER                               : %d" % len(a_jeter))
    print("  GARDÉES (porteur légitime)             : %d" % len(gardees))
    for cle, valeur in gardees:
        print("     %r -> %r" % (cle, valeur))
    par_valeur = Counter(v for _, v in a_jeter)
    for v, n in par_valeur.most_common():
        print("     %6d  %r" % (n, v))

    poisons_sorts = {c for c, _ in a_jeter}
    objets_jeter = purger_objets(objets, poisons_sorts, journal)
    print()
    print("objets_dbc.json / noms")
    print("  objets composés à purger : %d" % len(objets_jeter))
    for cle, valeur in objets_jeter[:5]:
        print("     %r -> %r" % (cle[:52], valeur[:52]))
    if len(objets_jeter) > 5:
        print("     … et %d autres" % (len(objets_jeter) - 5))

    n_desc = 0
    if args.descriptions:
        print()
        print("descriptions abîmées")
        n_desc = reparer_descriptions(sorts, journal, args.appliquer)
        print("  reprises depuis la sauvegarde : %d" % n_desc)

    for cle, _ in a_jeter:
        journal.append("PURGÉ sorts.json/noms : %r" % cle)
    for cle, _ in objets_jeter:
        journal.append("PURGÉ objets_dbc.json/noms : %r" % cle)

    os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)
    with io.open(RAPPORT, "w", encoding="utf-8") as f:
        f.write("PURGE DES NOMS EMPOISONNÉS — %s\n"
                % ("APPLIQUÉE" if args.appliquer else "SIMULATION"))
        f.write("sorts.json/noms purgés   : %d\n" % len(a_jeter))
        f.write("objets_dbc.json purgés   : %d\n" % len(objets_jeter))
        f.write("descriptions reprises    : %d\n\n" % n_desc)
        f.write("\n".join(journal))
    print()
    print("rapport : %s" % RAPPORT)

    if not args.appliquer:
        print("SIMULATION — rien n'a été écrit. --appliquer pour purger.")
        return 0

    print()
    print("  sauvegarde : %s"
          % os.path.basename(sauvegarder(chemin_sorts)))
    for cle, _ in a_jeter:
        del sorts["noms"][cle]
    ecrire(chemin_sorts, sorts)
    print("  écrit : sorts.json")

    if objets_jeter:
        print("  sauvegarde : %s"
              % os.path.basename(sauvegarder(chemin_objets)))
        for cle, _ in objets_jeter:
            del objets["noms"][cle]
        ecrire(chemin_objets, objets)
        print("  écrit : objets_dbc.json")

    print()
    print("Fait. Régénère DANS CET ORDRE — le pont relit DB_Sorts.lua, pas")
    print("sorts.json, donc l'ordre décide du résultat :")
    print("   1. generateur_sorts.py     (DB_Sorts.lua)")
    print("   2. generateur_db.py        (les autres bases)")
    print("   3. generer_noms_sorts.py   (DB_SortsNoms.lua)")
    print("   4. generer_noms_objets.py  (DB_ObjetsNoms.lua)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
