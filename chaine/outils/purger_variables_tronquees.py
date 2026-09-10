# -*- coding: utf-8 -*-
r"""Purge les descriptions dont le français porte une variable TRONQUÉE
(bloc D du programme 4, 29/07/2026).

CE QUE LA MESURE A DIT. Sur 447 échecs du moteur, **335 meurent au
garde-fou du « $ »** : le français contient un dollar que l'affiché
anglais n'a plus. En regardant QUELS dollars restent dans les littéraux du
modèle français :
    83  « $ » tout seul          134 variables TRONQUÉES : le nom de la
    51  « $. »                        variable a disparu à la traduction
     7  « $/1000; »              opérande perdu
    ~15 « $+AP*0,36 »            virgule décimale française DANS une formule

Ce n'est pas un défaut du moteur : c'est de la DONNÉE abîmée — la même
maladie que les rejets chroniques du bloc B, vue de l'autre côté. Aucune
réparation mécanique n'est possible (on ne sait pas ce que la variable
disait) ; la voie est celle du lot 13 : la paire sort du cache, le texte
repart en file, et sa clé entre dans les interdits de ré-adoption pour que
le PackFR ne la réintroduise pas.

Ces entrées échouent DÉJÀ toutes : elles affichent l'anglais aujourd'hui.
Les purger ne peut donc rien dégrader — et la preuve par hachages sur la
population entière le vérifie quand même.

Usage : python outils/purger_variables_tronquees.py [--appliquer]
"""
import io
import json
import os
import re
import shutil
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reparer_alignement_sorts as rep  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTS = os.path.join(BASE, "traductions", "sorts.json")
INTERDITES = os.path.join(BASE, "traductions",
                          "cles_interdites_readoption.json")
RAPPORT = os.path.join(BASE, "rapports", "variables_tronquees_blocD.txt")

# Une variable tronquée : un « $ » que rien ne suit, ou suivi d'une
# ponctuation. Volontairement ÉTROIT — « $s1 », « $d » et toutes les
# formes connues sont des variables VALIDES, jamais visées.
# ⚠️ « ? » est EXCLU de cette classe : « $?s55451[…] » est un
# CONDITIONNEL parfaitement valide, et le premier jet le prenait pour une
# troncature (vu à l'examen des exemples, avant toute écriture).
RE_TRONQUEE = re.compile(r"\$(?=[\s.,;:!)\]]|$)")


def charger(chemin, defaut=None):
    if not os.path.exists(chemin):
        return {} if defaut is None else defaut
    with io.open(chemin, encoding="utf-8") as f:
        return json.load(f)


def main():
    appliquer = "--appliquer" in sys.argv
    lua = rep.charger_banc()
    g = lua.globals()
    verdicts, _hashes, total = rep.mesurer(lua)
    echecs = {i for i, (v, _) in verdicts.items() if v == "anglais"}
    print("banc : %d entrées, %d échecs" % (total, len(echecs)))

    # les DE des entrées EN ÉCHEC (c'est la clé du cache)
    de_en_echec = set()
    for sid in echecs:
        _d, de = rep.lire_champs(g, sid)
        if de:
            de_en_echec.add(de)
    print("clés (DE) en échec :", len(de_en_echec))

    data = charger(SORTS)
    descriptions = data.get("descriptions", {})
    fautives = []
    for en, fr in descriptions.items():
        if not isinstance(fr, str) or en not in de_en_echec:
            continue
        if RE_TRONQUEE.search(fr) and not RE_TRONQUEE.search(en):
            fautives.append((en, fr))
    print("descriptions à variable TRONQUÉE (et déjà en échec) : %d"
          % len(fautives))
    for en, fr in fautives[:5]:
        m = RE_TRONQUEE.search(fr)
        i = m.start()
        print("   …%s…" % fr[max(0, i - 45):i + 10].replace("\n", " "))

    if not fautives:
        print("rien à purger.")
        return 0
    if not appliquer:
        print("\nSIMULATION — rien n'a été écrit. --appliquer pour purger.")
        return 0

    horodatage = time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(SORTS, SORTS.replace(".json",
                                      "_avant_blocD4_%s.json" % horodatage))
    for en, _fr in fautives:
        descriptions.pop(en, None)
    from ecriture_sure import ecrire_json
    ecrire_json(SORTS, data)

    interdites = charger(INTERDITES)
    for en, _fr in fautives:
        interdites.setdefault(
            en, "purge bloc D (29/07/2026) — variable tronquée dans le "
                "français")
    ecrire_json(INTERDITES, interdites)

    os.makedirs(os.path.dirname(RAPPORT), exist_ok=True)
    with io.open(RAPPORT, "w", encoding="utf-8", newline="") as f:
        f.write("BLOC D — descriptions à variable tronquée (%d)\n%s\n\n"
                % (len(fautives), "=" * 50))
        for en, fr in fautives:
            f.write("EN : %s\nFR : %s\n\n" % (en[:200].replace("\n", " "),
                                              fr[:200].replace("\n", " ")))
    print("\n>>> PURGÉ %d description(s) ; interdites de ré-adoption : %d"
          % (len(fautives), len(interdites)))
    print("rapport :", RAPPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
