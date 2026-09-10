# -*- coding: utf-8 -*-
r"""Corrige les entrées du pont DB_SortsNoms que la révélation Wildcard
peut afficher et qui CONTREDISENT le français officiel UNANIME de leurs
homonymes Blizzard (lot 14 §2 — mesure du sceptique, m4_poison_filtre.py :
33 entrées le 28/07/2026, dont 2 corrompues « Vendetta » ->
« VenVerrouillage de la cibleetta » et « Vengeance » -> « FrÃ©nÃ©sie »).

LE DÉGÂT, MESURÉ
----------------
Les 33 noms fautifs ont tous un français officiel unanime IDENTIQUE à
l'anglais (« Absolution » -> « Absolution », « Blizzard » -> « Blizzard »…).
Or `generer_noms_sorts.poser()` écarte les paires identité (en == fr) : la
couche officielle ne les pose donc JAMAIS dans le pont, et les couches
basses remplissent le vide avec le français de l'ANCIEN nom du sort renommé
par Ascension (le piège documenté de la jointure par identifiant) :
  - 10 valeurs viennent de NOTRE cache `traductions/sorts.json` (section
    « noms »), via le N de DB_Sorts.lua ;
  - 23 viennent du PackFR (`sources/packfr_sorts.json`, en lecture seule).
Provenance rejouée couche par couche le 28/07/2026 — aucun cas Glayna posé
(mais Glayna PEUT remplir un trou après correction : couche 4 hors filtre
POISON, voir la simulation).

LA CORRECTION
-------------
1. Le CACHE (la source que nous possédons) : chaque clé fautive présente
   dans `traductions/sorts.json`/noms est CORRIGÉE vers le français officiel
   unanime. Comme cet officiel est l'identité, le pont régénéré n'en portera
   simplement plus la clé — et le libellé affichera le nom officiel.
2. Le PACKFR (qu'on ne possède pas) : filtré À LA LECTURE par la table
   POISON_LOT14 de `outils/noms_empoisonnes.py` (mêmes principes que les
   lots 9/10/13 : porteurs légitimes mesurés, jamais devinés).
3. La PREUVE : l'outil rejoue les QUATRE couches du générateur (témoin sans
   lot 14 / corrigée avec) et prédit le pont d'après-régénération — les
   clés fautives doivent en sortir, et tout retrait collatéral est listé.

CE QUE L'OUTIL N'ÉCRIT PAS
--------------------------
  - `sources/` (ré-extractible, une correction s'y perdrait) ;
  - les bases DB_*.lua (la régénération appartient à la chaîne complète) ;
  - la table POISON elle-même (curatée à la main, avec ses pourquoi).

Usage :
    python outils/purger_pont_cartes.py               # simulation
    python outils/purger_pont_cartes.py --appliquer   # corrige (+ sauvegarde)
"""
import argparse
import io
import json
import os
import re
import shutil
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from garde_packfr import texte_sain  # noqa: E402
from generateur_db import polir  # noqa: E402
import noms_empoisonnes  # noqa: E402

SRC = os.path.join(BASE, "sources", "dbc")
DBDIR = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface\AddOns"
         r"\AscensionFR\DB")
CHEMIN_CACHE = os.path.join(BASE, "traductions", "sorts.json")
RAPPORT = os.path.join(BASE, "rapports", "pont_cartes_lot14.txt")

# Le même filtre d'anglais résiduel que generer_noms_sorts (couche PackFR).
RE_ANGLAIS = re.compile(
    r"\b(the|of|and|your|to|strike|blade|bolt|shield|blast)\b", re.I)


def charger(chemin):
    with io.open(chemin, encoding="utf-8") as f:
        return json.load(f)


def plat(s):
    """Sans accents ni casse — pour écarter les fausses divergences
    d'accent (le piège des 401, mémoire du projet)."""
    return (unicodedata.normalize("NFD", s).encode("ascii", "ignore")
            .decode("ascii").lower())


def lire_pont():
    """Le pont RÉEL livré (paresseux par texte : les paires restent
    lisibles en clair dans les seaux)."""
    txt = io.open(os.path.join(DBDIR, "DB_SortsNoms.lua"),
                  encoding="utf-8").read()

    def de(s):
        return s.replace('\\"', '"').replace("\\\\", "\\")
    return {de(k): de(v) for k, v in
            re.findall(r'\["((?:[^"\\]|\\.)*)"\]="((?:[^"\\]|\\.)*)"', txt)}


def noms_revelables():
    """Les noms que la révélation Wildcard peut composer en « X (Rank n) » :
    colonne c47 de characteradvancement.json (mesure du sceptique)."""
    ca = charger(os.path.join(SRC, "characteradvancement.json"))
    noms = set()
    for ligne in ca["lignes"]:
        n = ligne.get("c47")
        if isinstance(n, str) and n.strip():
            noms.add(n.strip())
    return noms


def officiel_par_nom():
    """{nom EN -> ensemble des frFR officiels des homonymes Blizzard}."""
    enus = charger(os.path.join(SRC, "spells_enUS.json"))
    frfr = charger(os.path.join(SRC, "spells_frFR.json"))
    par_nom = defaultdict(set)
    for sid, fiche in enus.items():
        f = frfr.get(sid)
        if f and fiche.get("N") and f.get("N"):
            par_nom[fiche["N"]].add(f["N"])
    return par_nom


def mesurer_fautives(pont, revelables, par_nom):
    """Les entrées du pont qui contredisent TOUT l'officiel homonyme,
    accents et casse filtrés — la mesure de m4_poison_filtre.py, rejouée
    ici pour que l'outil reste rejouable sans liste codée en dur."""
    fautives = []
    for nom in sorted(revelables):
        if nom not in pont:
            continue
        offi = par_nom.get(nom)
        if not offi:
            continue
        valeur = pont[nom]
        if valeur in offi or valeur == nom:
            continue
        if any(plat(valeur) == plat(o) for o in offi):
            continue
        fautives.append({"nom": nom, "pont": valeur, "officiel": sorted(offi)})
    return fautives


def _empoisonne(en, fr, table, cles_verrou):
    """Le discriminant de noms_empoisonnes.empoisonne, sur une table et un
    verrou par clé au choix — nécessaire pour rejouer le TÉMOIN « sans
    lot 14 » face à la version corrigée."""
    if not fr:
        return False
    if (en or "").strip() in cles_verrou and fr.strip() != (en or "").strip():
        return True
    legitimes = table.get(fr.strip())
    if legitimes is None:
        return False
    return (en or "").strip() not in legitimes


def simuler_pont(poison, cles_verrou=frozenset(), remplace_n=None):
    """Rejoue les couches de generer_noms_sorts.py (1, 2, 2bis, 3 — la
    couche Glayna est retirée depuis le 29/07/2026) et rend les paires
    prédites. `remplace_n` : {nom EN -> N prédit après régénération
    de DB_Sorts} — la couche 2 lit les N du DB livré, qui ne bougera qu'à
    la régénération ; on substitue donc la prédiction issue du cache
    corrigé (une identité n'est jamais posée, comme dans le générateur)."""
    import unicodedata
    remplace_n = remplace_n or {}
    paires, divergents = {}, set()

    def plat(s):
        return "".join(
            c for c in unicodedata.normalize("NFD", (s or "").lower())
            if not unicodedata.combining(c))

    def poser(en, fr):
        en, fr = (en or "").strip(), (fr or "").strip()
        if not en or not fr or en == fr or en in divergents:
            return
        if _empoisonne(en, fr, poison, cles_verrou):
            return
        fr = polir(fr, anglais=en)
        deja = paires.get(en)
        if deja is None:
            paires[en] = fr
        elif deja != fr:
            # même règle que le générateur : deux graphies d'un même nom
            # ne se neutralisent pas, la couche haute garde la sienne
            if plat(deja) == plat(fr):
                return
            del paires[en]
            divergents.add(en)

    enus = charger(os.path.join(SRC, "spells_enUS.json"))
    frfr = charger(os.path.join(SRC, "spells_frFR.json"))
    for sid, fiche in enus.items():
        f = frfr.get(sid)
        if f:
            poser(fiche.get("N"), f.get("N"))

    ascension = charger(os.path.join(SRC, "spells_Ascension.json"))
    for fichier in ["DB_Sorts.lua", "DB_SortsCorrections.lua"]:
        texte = io.open(os.path.join(DBDIR, fichier), encoding="utf-8",
                        errors="replace").read()
        for ident, n_fr in re.findall(
                r'^DB\[(\d+)\]=\{[^\n]*?,N="((?:\\.|[^"\\])*)"', texte, re.M):
            fiche = ascension.get(ident)
            if not fiche:
                continue
            en = (fiche.get("N") or "").strip()
            fr = n_fr.replace('\\"', '"').replace("\\\\", "\\").strip()
            if en in remplace_n:
                fr = remplace_n[en]
            if en and fr and en != fr:
                poser(en, fr)

    # 2bis : la liste relue du bloc A, comme dans le générateur
    noms_dump = {(f.get("N") or "").strip() for f in ascension.values()}
    try:
        relus = charger(os.path.join(BASE, "traductions",
                                     "noms_pont_retraduits.json"))
    except OSError:
        relus = []
    for p in relus or []:
        en = (p.get("en") or "").strip()
        fr = (p.get("fr") or "").strip()
        if en in remplace_n:
            fr = remplace_n[en]
        if en and fr and en in noms_dump and en not in paires \
                and en not in divergents:
            poser(en, fr)

    packfr = charger(os.path.join(BASE, "sources", "packfr_sorts.json"))
    for ident, fiche in ascension.items():
        en = (fiche.get("N") or "").strip()
        if not en or en in paires or en in divergents:
            continue
        p = packfr.get(ident)
        fr = ((p or {}).get("N") or "").strip().replace(chr(160), " ")
        if fr and fr != en and not RE_ANGLAIS.search(fr) \
                and texte_sain(fr) and texte_sain(en):
            poser(en, fr)

    # Couche 4 (Glayna) : REPRODUITE TELLE QUELLE, y compris son angle
    # mort — elle ne passe PAS par poser(), donc PAS par le filtre POISON.
    # (Couche Glayna RETIRÉE le 29/07/2026, bloc A du programme 2 : le vrai
    # générateur ne l'a plus, la simulation ne doit pas l'avoir non plus —
    # une simulation qui garde une couche disparue MENT sur le pont réel.)
    return paires


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--appliquer", action="store_true")
    args = p.parse_args()
    journal = []

    pont = lire_pont()
    revelables = noms_revelables()
    par_nom = officiel_par_nom()
    fautives = mesurer_fautives(pont, revelables, par_nom)
    print("pont réel : %d paires | noms révélables (c47) : %d"
          % (len(pont), len(revelables)))
    print("entrées fautives mesurées : %d" % len(fautives))

    # L'officiel doit être UNANIME pour qu'on corrige ; sinon l'arbitrage
    # appartient à Dan (consigne du lot 14) — on laisse et on note.
    corrigees, laissees = [], []
    for f in fautives:
        (corrigees if len(f["officiel"]) == 1 else laissees).append(f)
    for f in laissees:
        journal.append("LAISSÉE (officiel non unanime) : %r -> %r | %r"
                       % (f["nom"], f["pont"], f["officiel"]))
    if laissees:
        print("laissées à l'arbitrage (officiel non unanime) : %d"
              % len(laissees))

    cache = charger(CHEMIN_CACHE)
    noms_cache = cache["noms"]
    ecritures = []          # (clé, avant, après) dans le cache
    for f in corrigees:
        officiel = f["officiel"][0]
        avant = noms_cache.get(f["nom"])
        if avant is not None and avant != officiel:
            ecritures.append((f["nom"], avant, officiel))
            journal.append("CACHE corrigé : %r : %r -> %r"
                           % (f["nom"], avant, officiel))
        elif avant == officiel:
            # Sans cette ligne, une relance APRÈS application réécrivait le
            # rapport avec « corrections : 0 » et les traces des corrections
            # réelles disparaissaient — le PV d'arbitrage devenait illisible
            # (défaut relevé au contrôle du lot 14).
            journal.append("DÉJÀ CORRIGÉE : %r = %r (l'officiel)"
                           % (f["nom"], officiel))
        elif avant is None:
            journal.append("HORS CACHE (couche PackFR/Glayna, voir POISON) :"
                           " %r -> %r" % (f["nom"], f["pont"]))
    print("corrections du cache traductions/sorts.json : %d" % len(ecritures))
    for cle, avant, apres in ecritures:
        print("   %-14r %r -> %r" % (cle, avant, apres))

    # ------------------------------------------------------------------
    # LA PREUVE PAR SIMULATION : témoin (sans lot 14) contre corrigée.
    # ------------------------------------------------------------------
    lot14 = getattr(noms_empoisonnes, "POISON_LOT14", {})
    verrou = getattr(noms_empoisonnes, "CLES_IDENTITE_OFFICIELLE",
                     frozenset())
    temoin_table = {v: c for v, c in noms_empoisonnes.POISON.items()
                    if v not in lot14}
    remplace = {cle: apres for cle, _, apres in ecritures}
    print("\nsimulation des 4 couches (témoin sans lot 14 / corrigée)…")
    temoin = simuler_pont(temoin_table)
    corrige = simuler_pont(dict(noms_empoisonnes.POISON), verrou, remplace)
    print("  témoin : %d paires | corrigée : %d paires"
          % (len(temoin), len(corrige)))

    non_couvertes = []
    for f in corrigees:
        officiel = f["officiel"][0]
        predit = corrige.get(f["nom"])
        if predit is None or predit == officiel \
                or plat(predit) == plat(officiel):
            etat = "SORT du pont" if predit is None else "-> %r" % predit
            journal.append("COUVERTE : %r (%r) %s"
                           % (f["nom"], f["pont"], etat))
        else:
            non_couvertes.append((f["nom"], f["pont"], predit))
            journal.append("NON COUVERTE : %r resterait %r après"
                           " régénération" % (f["nom"], predit))
    print("couvertes après régénération : %d / %d"
          % (len(corrigees) - len(non_couvertes), len(corrigees)))
    for nom, avant, predit in non_couvertes:
        print("   NON COUVERTE : %-14r %r -> resterait %r"
              % (nom, avant, predit))

    # Les retraits/changements COLLATÉRAUX : tout écart témoin/corrigée qui
    # n'est pas une clé fautive — chacun doit être un dégât connu (les
    # jointures folles voisines), jamais une paire saine.
    fautifs = {f["nom"] for f in corrigees}
    collateral = []
    for cle in sorted(set(temoin) | set(corrige)):
        if cle in fautifs:
            continue
        av, ap = temoin.get(cle), corrige.get(cle)
        if av != ap:
            collateral.append((cle, av, ap))
    print("collatéral (hors clés fautives) : %d" % len(collateral))
    for cle, av, ap in collateral:
        print("   %-28r %r -> %r" % (cle, av, ap))
        journal.append("COLLATÉRAL : %r : %r -> %r" % (cle, av, ap))

    os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)
    with io.open(RAPPORT, "w", encoding="utf-8", newline="") as f:
        f.write("CORRECTION DU PONT POUR LES CARTES (lot 14 §2) — %s\n"
                % ("APPLIQUÉE" if args.appliquer else "SIMULATION"))
        f.write("fautives mesurées : %d | corrections cache : %d | "
                "non couvertes : %d | collatéral : %d\n\n"
                % (len(fautives), len(ecritures), len(non_couvertes),
                   len(collateral)))
        f.write("\n".join(journal) + "\n")
    print("\nrapport : %s" % RAPPORT)

    if not args.appliquer:
        print("SIMULATION — rien n'a été écrit. --appliquer pour corriger.")
        return 0
    if not ecritures:
        print("rien à écrire (cache déjà corrigé).")
        return 0

    # Sauvegarde horodatée INCONDITIONNELLE (règle du dépôt depuis le
    # lot 9 : chaque passage laisse sa propre copie).
    quand = datetime.now().strftime("%Y%m%d-%H%M%S")
    copie = os.path.join(BASE, "traductions",
                         "sorts_avant_lot14_%s.json" % quand)
    shutil.copy2(CHEMIN_CACHE, copie)
    print("sauvegarde : %s" % os.path.basename(copie))
    for cle, _, apres in ecritures:
        noms_cache[cle] = apres
    with io.open(CHEMIN_CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("écrit : %s (%d corrections)" % (CHEMIN_CACHE, len(ecritures)))
    print("\nLa régénération appartient à la chaîne complète (ordre :")
    print("generateur_sorts, generateur_db, generer_noms_sorts,")
    print("generer_noms_objets) — rien d'autre n'est écrit ici.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
