# -*- coding: utf-8 -*-
r"""Purge les descriptions de sorts au FRANGLAIS (bloc C du programme 3,
29/07/2026) : un mot-outil anglais pur (« and », « the », « your »…) resté
dans un texte par ailleurs français. Le joueur lit une phrase à moitié
traduite ; l'anglais entier vaut mieux, et la file s'en occupe.

LA VOIE DU LOT 13, sans inventer de mécanisme :
  1. la paire est retirée de traductions/sorts.json (« descriptions ») —
     à la prochaine génération, le texte repart en file de traduction ;
  2. sa clé anglaise est inscrite dans
     traductions/cles_interdites_readoption.json, la liste que
     `adopter_packfr_cache` consulte déjà : le PackFR ne peut pas la
     réintroduire au passage suivant. Une purge sans cette inscription
     est défaite en silence (lot 14).

« gain »/« gains » ne comptent plus comme franglais depuis ce même bloc
(ce sont de vrais mots français — 112 faux signalements sur 262).

Usage : python outils/purger_franglais_descriptions.py [--appliquer]
"""
import io
import json
import os
import shutil
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from noms_empoisonnes import mot_anglais  # noqa: E402
from adopter_packfr_cache import structure_divergente  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTS = os.path.join(BASE, "traductions", "sorts.json")
INTERDITES = os.path.join(BASE, "traductions",
                          "cles_interdites_readoption.json")
DBDIR = (r"D:\AscensionFR\WOW_Priv\resources\ascension-live\Interface"
         r"\AddOns\AscensionFR\DB")
MOTIF = "purge bloc C (29/07/2026) — franglais : mot-outil anglais resté"


def charger(chemin, defaut=None):
    if not os.path.exists(chemin):
        return defaut if defaut is not None else {}
    with io.open(chemin, encoding="utf-8") as f:
        return json.load(f)


def des_actifs():
    """Les modèles anglais (DE) réellement consommés par les bases : c'est
    ce qui distingue une entrée qui SERT l'écran d'une entrée dormante."""
    import re
    rendu = set()
    re_de = re.compile(r'[,{]DE="((?:\\.|[^"\\])*)"')
    for fichier in ("DB_Sorts.lua", "DB_SortsCorrections.lua"):
        chemin = os.path.join(DBDIR, fichier)
        if not os.path.exists(chemin):
            continue
        brut = io.open(chemin, encoding="utf-8", errors="replace").read()
        for m in re_de.finditer(brut):
            v = (m.group(1).replace("\\\\", "\\").replace('\\"', '"')
                 .replace("\\n", "\n").replace("\\r", "\r"))
            rendu.add(v)
    return rendu


def main():
    appliquer = "--appliquer" in sys.argv
    data = charger(SORTS)
    descriptions = data.get("descriptions", {})
    actifs = des_actifs()

    fautives = []
    for en, fr in descriptions.items():
        if not isinstance(fr, str) or not fr.strip():
            continue
        # une clé dont la STRUCTURE diverge est déjà traitée au bloc D :
        # on ne la compte pas deux fois
        if structure_divergente(en, fr):
            continue
        mot = mot_anglais(fr)
        if mot:
            fautives.append((en, fr, mot, en in actifs))

    servies = sum(1 for f in fautives if f[3])
    print("descriptions au franglais : %d (dont %d servent l'écran)"
          % (len(fautives), servies))
    from collections import Counter
    c = Counter(f[2].lower() for f in fautives)
    print("par mot :", dict(c.most_common()))
    print()
    for en, fr, mot, sert in fautives[:6]:
        print("  [%s] « %s »" % ("SERVI  " if sert else "dormant", mot))
        print("      FR : %s" % fr[:110].replace("\n", " "))

    if not fautives:
        print("rien à purger.")
        return 0
    if not appliquer:
        print("\nSIMULATION — rien n'a été écrit. --appliquer pour purger.")
        return 0

    horodatage = time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(SORTS, SORTS.replace(".json",
                                      "_avant_blocC_%s.json" % horodatage))
    for en, _fr, _mot, _sert in fautives:
        descriptions.pop(en, None)
    with io.open(SORTS, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=True)

    interdites = charger(INTERDITES)
    avant = len(interdites)
    for en, _fr, mot, _sert in fautives:
        interdites.setdefault(en, "%s (« %s »)" % (MOTIF, mot))
    with io.open(INTERDITES, "w", encoding="utf-8") as f:
        json.dump(interdites, f, ensure_ascii=False, indent=1, sort_keys=True)

    print("\n>>> PURGÉ %d description(s) de sorts.json." % len(fautives))
    print(">>> INTERDITES de ré-adoption : %d -> %d clés (le PackFR ne peut "
          "plus les réintroduire)." % (avant, len(interdites)))
    print("    Les textes repartent en file à la prochaine génération.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
