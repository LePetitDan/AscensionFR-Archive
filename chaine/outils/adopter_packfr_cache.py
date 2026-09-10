# -*- coding: utf-8 -*-
"""Verse le français HUMAIN du PackFR dans le cache de traduction des sorts
(traductions/sorts.json, clés « noms » et « descriptions », indexées par le
texte anglais exact d'Ascension).

Pourquoi le cache et pas la base : generateur_sorts.py ne produit d'entrée
que pour les sorts VISIBLES par le joueur (classes, talents, métiers,
objets, récoltes). En nourrissant le cache, chaque texte du pack profite
automatiquement à tout sort présent ou futur qui l'affiche, sans faire
gonfler DB_Sorts.lua de dizaines de milliers de sorts internes invisibles.

Gardes (les mêmes que la moisson PackFR d'origine) :
  - jetons $ IDENTIQUES (ensemble) entre le FR du pack et l'anglais actuel
    d'Ascension — un texte d'époque dont les variables ont bougé est rejeté ;
  - pas d'anglais résiduel dans le FR ;
  - FR différent de l'EN (sinon ce n'est pas une traduction) ;
  - un même texte EN revendiqué par plusieurs FR différents = ambigu, rejeté ;
  - ne JAMAIS écraser une entrée déjà présente dans le cache (nos choix
    faits main ou arbitrés par Dan restent maîtres).

Sauvegarde avant écriture : rapports/sorts_cache_avant_packfr.json
"""
import io
import json
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from garde_packfr import texte_sain  # noqa: E402
from noms_empoisonnes import (SEUIL_PORTEURS, TOLERES,  # noqa: E402
                              empoisonne, mot_anglais, parente,
                              structure_divergente)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RE_JETON = re.compile(r"\$\{[^}]*\}|\$[/;]?[A-Za-z][A-Za-z0-9]*")
RE_ANGLAIS = re.compile(
    r"\b(the|and|your|with|damage|target|enemy|you|for|when|while|deals"
    r"|causes|increases|reduces)\b", re.I)


def charger(chemin):
    with io.open(chemin, encoding="utf-8") as f:
        return json.load(f)


def jetons(texte):
    return sorted(RE_JETON.findall(texte or ""))


def main():
    pack = charger(os.path.join(BASE, "sources", "packfr_sorts.json"))
    vivant = charger(os.path.join(BASE, "sources", "dbc",
                                  "spells_Ascension.json"))
    chemin_cache = os.path.join(BASE, "traductions", "sorts.json")
    cache = charger(chemin_cache) if os.path.exists(chemin_cache) \
        else {"noms": {}, "descriptions": {}}
    cache.setdefault("noms", {})
    cache.setdefault("descriptions", {})

    shutil.copy2(chemin_cache,
                 os.path.join(BASE, "rapports",
                              "sorts_cache_avant_packfr.json"))

    # 1. Candidats : par identifiant, joindre l'anglais actuel au FR du pack.
    candidats = {"noms": {}, "descriptions": {}}   # EN -> {FR: occurrences}
    for sid, a in vivant.items():
        p = pack.get(sid)
        if not p:
            continue
        for champ, cle_en, cle_fr in (("noms", "N", "N"),
                                      ("descriptions", "D", "D")):
            en = a.get(cle_en)
            fr = p.get(cle_fr)
            if not en or not fr or fr == en:
                continue
            if RE_ANGLAIS.search(fr):
                continue
            # Le pack contenait des réponses de robot, des codes internes
            # et de l'allemand (constat 21/07) : garde commune.
            if not texte_sain(fr) or not texte_sain(en):
                continue
            if jetons(fr) != jetons(en):
                continue
            candidats[champ].setdefault(en, {})
            candidats[champ][en][fr] = candidats[champ][en].get(fr, 0) + 1

    # 2. LA BARRIÈRE DU NOMBRE DE PORTEURS (lot 10, 27/07/2026) — noms
    # seulement : une description partagée est normale (1 364 enchantements
    # disent mot pour mot la même chose), un NOM partagé par des sorts sans
    # rapport est le poison même que ce fichier a injecté le 21/07.
    # On compte les porteurs SUR L'ÉTAT FINAL (cache existant + adoptions de
    # cette passe) : la barrière bloque aussi la croissance goutte à goutte
    # d'une famille déjà entamée, pas seulement l'arrivée en masse.
    porteurs = {}          # valeur -> [clés qui la porteraient après la passe]
    for en, fr in cache["noms"].items():
        porteurs.setdefault(fr, []).append(en)
    for en, votes in candidats["noms"].items():
        if en not in cache["noms"] and len(votes) == 1:
            porteurs.setdefault(next(iter(votes)), []).append(en)

    # Les clés purgées par reparer_alignement_sorts.py sont INTERDITES de
    # ré-adoption : leur français PackFR ne traduit pas la clé, mais 71 des
    # 222 purgées du lot 14 n'ont AUCUN défaut de structure — sans cette
    # liste, elles reviendraient à la passe suivante, purge annulée en
    # silence (même leçon qu'au lot 10 avec la table POISON).
    chemin_interdites = os.path.join(BASE, "traductions",
                                     "cles_interdites_readoption.json")
    interdites = charger(chemin_interdites) \
        if os.path.exists(chemin_interdites) else {}

    def barriere(en, fr):
        """Raison du refus, ou None si la paire peut entrer."""
        if empoisonne(en, fr):
            return "valeur de la table POISON"
        cles = porteurs.get(fr, [])
        if (len(cles) >= SEUIL_PORTEURS and fr not in TOLERES
                and not parente(cles)):
            return "%d porteurs sans parenté" % len(cles)
        return None

    # 3. Trancher : unanime -> adopté ; divergent -> rejeté (ambigu).
    stats = {}
    refus_barriere = {}
    for champ in ("noms", "descriptions"):
        adoptes, ambigus, deja = 0, 0, 0
        for en, votes in candidats[champ].items():
            if en in cache[champ]:
                deja += 1
                continue
            if len(votes) > 1:
                ambigus += 1
                continue
            fr = next(iter(votes))
            # Clé purgée par reparer_alignement_sorts : interdite de
            # ré-adoption, NOMS ET DESCRIPTIONS — 71 des 222 purgées du
            # lot 14 n'ont aucun défaut de structure, seule cette liste
            # les arrête.
            if en in interdites:
                refus_barriere.setdefault(
                    (fr, "clé interdite de ré-adoption"), []).append(en)
                continue
            # LA BARRIÈRE DE STRUCTURE (lot 14) : un FR dont les variables
            # divergent de sa clé EN (marqueur @…@ d'un seul côté, id de
            # variable ni présent ni décalé de +1 100 000) fait abandonner
            # TOUTE la description à l'affichage — le cas 3599 de Dan,
            # 2 433 sorts anglais mesurés au banc. Refus BRUYANT, comme la
            # barrière des porteurs. (Le filtre jetons() plus haut ne voit
            # ni les @marqueurs ni les $<id> numériques.)
            raison = structure_divergente(en, fr)
            if raison:
                refus_barriere.setdefault(
                    (fr, "structure : " + raison), []).append(en)
                continue
            if champ == "noms":
                raison = barriere(en, fr)
                if raison:
                    refus_barriere.setdefault((fr, raison), []).append(en)
                    continue
            cache[champ][en] = fr
            adoptes += 1
        stats[champ] = (adoptes, ambigus, deja)

    # La barrière DIT ce qu'elle refuse — un refus avalé en silence est
    # exactement le défaut qui a laissé ce poison invisible pendant 6 jours.
    if refus_barriere:
        total = sum(len(v) for v in refus_barriere.values())
        print()
        print("BARRIÈRE DES PORTEURS : %d adoption(s) refusée(s), %d valeur(s)"
              % (total, len(refus_barriere)))
        for (fr, raison), cles in sorted(refus_barriere.items(),
                                         key=lambda kv: -len(kv[1]))[:15]:
            print("   %-40r x%-5d %s" % (fr[:38], len(cles), raison))
            print("      ex : %s" % "; ".join(repr(c)[:40] for c in cles[:3]))
        if len(refus_barriere) > 15:
            print("   … et %d autres valeurs" % (len(refus_barriere) - 15))
        print()

    with io.open(chemin_cache, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1, sort_keys=True)

    for champ, (adoptes, ambigus, deja) in stats.items():
        print("%s : %d adoptés, %d ambigus rejetés, %d déjà couverts"
              % (champ, adoptes, ambigus, deja))

    # LA VIGIE DE SORTIE (lot 14, correctif du sceptique) : l'état FINAL des
    # descriptions est balayé, Y COMPRIS ce qui s'aligne — deux maux :
    #  - structure divergente de la clé (adoptions d'AVANT la barrière) ;
    #  - Franglais qui S'ALIGNE : la famille « Follow Up » (« …and gain
    #    Follow jusqu'à… ») passait le banc ET l'écran — 316 sorties
    #    « traduites » du banc du lot 14 portaient un mot-outil anglais.
    # Vigie seulement : elle compte et montre (rien en silence), l'arbitrage
    # des valeurs en place appartient à Dan.
    v_structure, v_franglais = [], []
    for en, fr in cache["descriptions"].items():
        raison = structure_divergente(en, fr)
        if raison:
            v_structure.append((en, raison))
        else:
            mot = mot_anglais(fr)
            if mot:
                v_franglais.append((en, mot))
    print()
    print("VIGIE DE SORTIE (descriptions du cache, état final) :")
    print("   structure divergente de la clé : %d" % len(v_structure))
    for en, raison in v_structure[:5]:
        print("      %r — %s" % (en[:50], raison))
    print("   mot-outil anglais dans le FR   : %d (sur-signale un peu :"
          " « gain » existe en français)" % len(v_franglais))
    for en, mot in v_franglais[:5]:
        print("      %r — « %s »" % (en[:50], mot))

    # 4. Effet sur la file d'attente actuelle
    chemin_attente = os.path.join(BASE, "a_traduire", "sorts_textes.json")
    if os.path.exists(chemin_attente):
        attente = charger(chemin_attente)
        for champ in ("noms", "descriptions"):
            textes = attente.get(champ, [])
            couverts = sum(1 for t in textes if t in cache[champ])
            print("file %s : %d/%d désormais couverts par le cache"
                  % (champ, couverts, len(textes)))


if __name__ == "__main__":
    main()
