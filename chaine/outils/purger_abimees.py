# -*- coding: utf-8 -*-
"""
Repère et purge les traductions dont les variables ont été abîmées.

Cause : la liste des codes protégés à la traduction avait divergé de celle que
l'addon reconnaît. « $<percent> », « $*15;s1 »... n'étaient pas protégés, donc
le traducteur automatique les a détruits. En jeu, le joueur voyait alors un
« $ » à la place d'un chiffre.

Une traduction est saine si elle contient exactement les mêmes variables que
son texte anglais d'origine. Sinon on la supprime : elle sera refaite au
prochain passage du compagnon, avec la protection corrigée.

Usage : python purger_abimees.py [--verifier]   (--verifier = ne rien écrire)
"""
import json
import os
import re
import sys
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
from traducteur_fr import MOTIFS_PROTEGES  # noqa: E402

DBC = os.path.join(BASE, "sources", "dbc", "spells_Ascension.json")
SORTS = os.path.join(BASE, "traductions", "sorts.json")

# Seuls les codes de variables comptent ici : les couleurs et textures peuvent
# légitimement se déplacer, pas les valeurs numériques.
VARIABLE = re.compile(r"\$[^\s|]*")


def variables(texte):
    """Multi-ensemble des codes de variable d'un texte.

    Les marqueurs @...@ d'Ascension comptent comme des variables : le client
    les résout, donc un marqueur abîmé (« @ext : » avec insécable, « @learns »
    traduit en « @apprend ») condamne l'alignement autant qu'un $ perdu.
    """
    c = Counter()
    for m in MOTIFS_PROTEGES.finditer(texte or ""):
        jeton = m.group(0)
        if jeton.startswith(("$", "@", ":")):
            c[jeton] += 1
    return c


def dollars_libres(texte):
    """Nombre de « $ » qui ne font partie d'aucun code reconnu.

    C'est le signe d'une variable détruite : « $<percent> » devenu « $ ».
    """
    reste = MOTIFS_PROTEGES.sub("", texte or "")
    return reste.count("$")


def main():
    verifier = "--verifier" in sys.argv
    with open(DBC, encoding="utf-8") as f:
        asc = json.load(f)
    with open(SORTS, encoding="utf-8") as f:
        trad = json.load(f)

    descriptions = trad.get("descriptions", {})
    noms = trad.get("noms", {})

    abimees, causes = [], Counter()
    for en, fr in list(descriptions.items()):
        v_en, v_fr = variables(en), variables(fr)
        libres_en, libres_fr = dollars_libres(en), dollars_libres(fr)
        if v_en != v_fr:
            manquantes = [k for k in v_en if v_fr.get(k, 0) < v_en[k]]
            abimees.append(en)
            for m in manquantes[:1]:
                causes[re.sub(r"\d+", "<n>", m)] += 1
        elif libres_fr > libres_en:
            # Une variable a fondu en « $ » nu sans que le compte change
            abimees.append(en)
            causes["$ nu ajouté"] += 1

    print("Descriptions traduites      : %d" % len(descriptions))
    print("Descriptions abîmées        : %d (%.1f %%)"
          % (len(abimees), 100.0 * len(abimees) / max(len(descriptions), 1)))
    if causes:
        print()
        print("=== Variables perdues ===")
        for forme, n in causes.most_common(10):
            print("   %-16s %d" % (forme, n))

    # Mêmes contrôles pour les noms de sorts
    abimes_noms = [en for en, fr in noms.items()
                   if variables(en) != variables(fr)
                   or dollars_libres(fr) > dollars_libres(en)]
    print()
    print("Noms abîmés                 : %d / %d"
          % (len(abimes_noms), len(noms)))

    if verifier:
        print()
        print("(--verifier : rien n'a été modifié)")
        sys.exit(1 if (abimees or abimes_noms) else 0)

    for en in abimees:
        del descriptions[en]
    for en in abimes_noms:
        del noms[en]
    with open(SORTS, "w", encoding="utf-8") as f:
        json.dump(trad, f, ensure_ascii=False, indent=1, sort_keys=True)
    print()
    print("Purgé : %d traductions supprimées. Elles seront refaites au"
          % (len(abimees) + len(abimes_noms)))
    print("prochain passage du compagnon (python traducteur_fr.py --sorts).")


if __name__ == "__main__":
    main()
